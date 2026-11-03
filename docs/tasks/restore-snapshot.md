---
title: Restore a snapshot
type: task
tags: [restic, restore, snapshot]
last_reviewed: 2026-11-04
tested_version: UNTESTED
---
# Restore a snapshot

Restore the files from a snapshot into a new directory.

## Before you begin

- [Back up files](back-up-files.md) so that the repository contains at least one snapshot.

## Steps

1. Restore the latest snapshot to a target directory:

    ```bash
    restic restore latest --target /tmp/restic-restore-test --repo /tmp/restic-demo-repo
    ```

2. Enter the repository password when prompted.

3. List the restored files:

    ```bash
    find /tmp/restic-restore-test -name notes.txt
    ```

    Restic recreates the original directory path inside the target directory, so the file appears under that path.

## Restore a specific snapshot

Replace `latest` with a snapshot ID from the output of `restic snapshots`:

```bash
restic restore 1a2b3c4d --target /tmp/restic-restore-test --repo /tmp/restic-demo-repo
```
