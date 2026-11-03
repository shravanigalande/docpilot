"""Docs chatbot: retrieval over your docs, grounded answers, evaluation and gap reports.

Retrieval uses TF-IDF with cosine similarity (standard library only). Embeddings are
the natural upgrade; see README for how to swap them in. Generation is optional and
only talks to a *local* Ollama server by default so no content leaves the machine.
"""
from __future__ import annotations

import json
import math
import re
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .mdutil import iter_md, parse_front_matter, slugify

STOPWORDS = set(
    "a an and are as at be by can do does for from how i in is it of on or that the this to "
    "what when which why with you your my should would could there their they we".split()
)
DEFAULT_THRESHOLD = 0.5
NOT_COVERED = "I could not find this in the docs. This question is logged as a content gap."


def stem(word: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[: -len(suffix)]
            break
    if word.endswith("e") and len(word) > 4:
        word = word[:-1]
    return word


def intent(question: str) -> str:
    """Guess which topic type a question wants: 'what/why' -> concept, 'how' -> task."""
    q = question.strip().lower()
    if re.match(r"(what|why)\b", q):
        return "concept"
    if re.match(r"how (do|can|to|should)\b", q):
        return "task"
    return ""


def tokenize(text: str) -> list[str]:
    return [stem(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]


@dataclass
class Chunk:
    path: str
    title: str
    heading: str
    body: str
    kind: str = ""

    @property
    def anchor(self) -> str:
        return f"{self.path}#{slugify(self.heading)}" if self.heading else self.path


def load_chunks(root: str | Path) -> list[Chunk]:
    """Split each topic into one chunk per H2 section, plus an intro chunk."""
    chunks: list[Chunk] = []
    base = Path(root)
    for md in iter_md(base):
        meta, body = parse_front_matter(md.read_text(encoding="utf-8"))
        title = meta.get("title", md.stem)
        kind = meta.get("type", "")
        rel = md.relative_to(base).as_posix() if base.is_dir() else md.name
        sections = re.split(r"(?m)^## +", body)
        intro = re.sub(r"(?m)^# .*$", "", sections[0]).strip()
        if intro:
            chunks.append(Chunk(rel, title, "", intro, kind))
        for section in sections[1:]:
            heading, _, rest = section.partition("\n")
            chunks.append(Chunk(rel, title, heading.strip(), rest.strip(), kind))
    return chunks


class Index:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        # Title and heading are repeated so they weigh more than body text.
        docs = [tokenize(f"{c.title} {c.heading} {c.heading} {c.heading} {c.body}") for c in chunks]
        self.token_sets = [set(doc) for doc in docs]
        n = len(docs)
        df = Counter(term for doc in docs for term in set(doc))
        self.idf = {t: math.log((1 + n) / (1 + d)) + 1 for t, d in df.items()}
        self.vectors = [self._vector(doc) for doc in docs]

    def _vector(self, tokens: list[str]) -> dict[str, float]:
        counts = Counter(t for t in tokens if t in self.idf)
        vec = {t: (1 + math.log(c)) * self.idf[t] for t, c in counts.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    def coverage(self, query: str, positions: list[int]) -> float:
        """Share of the question's meaning (IDF-weighted) found in the given chunks.

        Terms the docs never use count as maximally informative, so a question about
        'Azure' or 'cron' scores low even when it also says 'backup' and 'repository'.
        """
        terms = set(tokenize(query))
        if not terms:
            return 0.0
        unseen = max(self.idf.values()) if self.idf else 1.0
        weight = {t: self.idf.get(t, unseen) for t in terms}
        found = set().union(*(self.token_sets[i] for i in positions)) if positions else set()
        total = sum(weight.values())
        return sum(w for t, w in weight.items() if t in found) / total

    def search(self, query: str, k: int = 3) -> list[tuple[float, Chunk]]:
        q = self._vector(tokenize(query))
        want = intent(query)
        scored = [
            (sum(w * vec.get(t, 0.0) for t, w in q.items()) * (1.6 if want and self.chunks[i].kind == want else 1.0), i)
            for i, vec in enumerate(self.vectors)
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [(score, self.chunks[i]) for score, i in scored[:k]]

    def confidence(self, query: str, k: int = 3) -> float:
        q = self._vector(tokenize(query))
        top = self.search(query, k)
        positions = [self.chunks.index(c) for _, c in top]
        return self.coverage(query, positions)


def ensure_local(url: str) -> None:
    """Data-handling policy: never send doc content to a non-local model by accident."""
    host = urllib.parse.urlparse(url).hostname
    if host not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError(f"Refusing to send content to non-local host '{host}'. Use --allow-remote to override.")


def ask_ollama(question: str, context: str, model: str, url: str, allow_remote: bool = False) -> str:
    if not allow_remote:
        ensure_local(url)
    prompt = (
        "Answer the question using ONLY the documentation excerpt below. "
        "If the excerpt does not contain the answer, reply exactly: Not covered in the docs.\n\n"
        f"Documentation excerpt:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    request = urllib.request.Request(f"{url}/api/generate", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read())["response"].strip()


def answer(question: str, index: Index, threshold: float = DEFAULT_THRESHOLD, llm: dict | None = None) -> dict:
    results = index.search(question, k=3)
    best = results[0][1]
    best_score = index.confidence(question)
    if best_score < threshold:
        return {"answered": False, "score": best_score, "text": NOT_COVERED, "sources": []}
    context = "\n\n".join(f"{c.heading}\n{c.body}" for _, c in results[:2])
    if llm:
        text = ask_ollama(question, context, **llm)
    else:
        text = best.body if len(best.body) < 700 else best.body[:700].rsplit(" ", 1)[0] + " ..."
    return {"answered": True, "score": best_score, "text": text, "sources": [c.anchor for _, c in results]}


def evaluate(index: Index, questions: list[dict], threshold: float = DEFAULT_THRESHOLD) -> dict:
    """Score retrieval. Answerable questions need the right topic in the top results.
    Unanswerable questions should be rejected (confidence below the threshold)."""
    answerable = [q for q in questions if q.get("expected")]
    unanswerable = [q for q in questions if not q.get("expected")]
    hit1 = hit3 = 0
    misses, gaps = [], []
    for q in answerable:
        results = index.search(q["question"], k=3)
        top_paths = [c.path for _, c in results]
        expected = set(q["expected"])
        hit1 += top_paths[0] in expected
        hit3 += bool(expected & set(top_paths))
        if top_paths[0] not in expected:
            misses.append({"question": q["question"], "expected": q["expected"], "got": top_paths[0], "score": results[0][0]})
    correct_rejects = 0
    for q in unanswerable:
        score = index.confidence(q["question"])
        if score < threshold:
            correct_rejects += 1
        gaps.append({"question": q["question"], "score": score, "rejected": score < threshold})
    return {
        "answerable": len(answerable),
        "hit_at_1": hit1 / len(answerable) if answerable else 0.0,
        "hit_at_3": hit3 / len(answerable) if answerable else 0.0,
        "unanswerable": len(unanswerable),
        "correct_rejections": correct_rejects / len(unanswerable) if unanswerable else 1.0,
        "misses": misses,
        "gaps": gaps,
    }


def gap_report(result: dict, logged: list[str] | None = None) -> str:
    lines = ["# Content gap report", "", "Generated by `docpilot eval`. Use it to decide which topics to write next.", ""]
    lines += [
        "## Retrieval quality", "",
        f"- Answerable questions: {result['answerable']}",
        f"- Right topic ranked first: {result['hit_at_1']:.0%}",
        f"- Right topic in top three: {result['hit_at_3']:.0%}",
        f"- Unanswerable questions correctly rejected: {result['correct_rejections']:.0%}", "",
    ]
    lines += ["## Questions the docs do not answer", ""]
    lines += [f"- {g['question']} (best score {g['score']:.2f})" for g in result["gaps"]] or ["- None."]
    lines += ["", "## Questions where the wrong topic ranked first", ""]
    lines += [f"- {m['question']}: expected {', '.join(m['expected'])}, got {m['got']}" for m in result["misses"]] or ["- None."]
    if logged:
        lines += ["", "## Questions logged from real use", ""] + [f"- {q}" for q in logged]
    return "\n".join(lines) + "\n"
