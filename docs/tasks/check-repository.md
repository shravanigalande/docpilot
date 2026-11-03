---
title: Check a repository
type: task
tags: [restic, check, integrity]
last_reviewed: 2026-11-04
tested_version: UNTESTED
---
# Check a repository

Verify that the repository structure is consistent and has no errors.

## Before you begin

- [Create a repository](create-repository.md) and add at least one snapshot.

## Steps

1. Run the check command:

    ```bash
    restic check --repo /tmp/restic-demo-repo
    ```

2. Enter the repository password when prompted.

    If the repository is healthy, restic reports that it found no errors.

## Verify the stored data

By default, `check` verifies the repository structure but does not read every data file. To read and verify all data, add the `--read-data` flag. This check can take a long time on large repositories:

```bash
restic check --read-data --repo /tmp/restic-demo-repo
```
