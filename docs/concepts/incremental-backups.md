---
title: How incremental backups work
type: concept
tags: [restic, deduplication, incremental]
last_reviewed: 2026-11-04
---
# How incremental backups work

The first restic backup copies all your data. Later backups are much faster because restic copies only what changed. This topic explains how.

## Chunks and deduplication

Restic splits each file into variable-size chunks and gives every chunk an identifier based on its content. Before it stores a chunk, restic checks whether the repository already has a chunk with the same identifier. If it does, restic skips the copy. This process is called deduplication.

## What this means for each backup

- The first backup stores every chunk.
- A later backup reads your files again but stores only new chunks.
- A renamed or moved file adds almost no data, because its chunks already exist.

## Every snapshot is complete

Although restic stores only changed data, each snapshot describes the full set of files. To restore, you pick one snapshot. You never need to combine a full backup with a chain of smaller ones.

## Related topics

- [Repositories and snapshots](repositories-and-snapshots.md)
- [Back up files](../tasks/back-up-files.md)
