---
title: Back up files
type: task
tags: [restic, backup, snapshot]
last_reviewed: 2026-11-04
tested_version: 0.19.1
---
# Back up files

Create a snapshot of a directory in an existing repository.

## Before you begin

- [Create a repository](create-repository.md). This topic uses `/tmp/restic-demo-repo`.

## Steps

1. Create a sample directory that contains one file:

    ```bash
    mkdir ~/docpilot-sample
    echo "hello" > ~/docpilot-sample/notes.txt
    ```

2. Run the backup command:

    ```bash
    restic backup ~/docpilot-sample --repo /tmp/restic-demo-repo
    ```

3. Enter the repository password when prompted.

    Restic prints a summary of new and changed files, then `snapshot` followed by the new snapshot ID and the word `saved`.

4. List the snapshots to confirm the backup:

    ```bash
    restic snapshots --repo /tmp/restic-demo-repo
    ```

    The table has the columns ID, Time, Host, Tags, Paths and Size, and lists one snapshot.

## Exclude files from a backup

Add the `--exclude` flag to skip files that match a pattern:

```bash
restic backup ~/docpilot-sample --exclude "*.tmp" --repo /tmp/restic-demo-repo
```

## Next steps

Continue with [Restore a snapshot](restore-snapshot.md).
