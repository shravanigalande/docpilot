---
title: Remove old snapshots
type: task
tags: [restic, forget, prune, retention]
last_reviewed: 2026-11-04
tested_version: UNTESTED
---
# Remove old snapshots

Keep only the most recent snapshots and free the storage that older snapshots used.

## Before you begin

- Create at least four snapshots. Run [Back up files](back-up-files.md) several times.
- Understand that removed snapshots cannot be restored.

## Steps

1. Preview the result with a dry run. The dry run changes nothing:

    ```bash
    restic forget --keep-last 3 --dry-run --repo /tmp/restic-demo-repo
    ```

2. Review the list of snapshots that restic would keep and remove.

3. Run the command again without `--dry-run`, and add `--prune` to free the storage:

    ```bash
    restic forget --keep-last 3 --prune --repo /tmp/restic-demo-repo
    ```

4. List the snapshots to confirm that only three remain:

    ```bash
    restic snapshots --repo /tmp/restic-demo-repo
    ```

## Forget and prune

The `forget` command removes snapshot records. The `prune` command deletes stored data that no snapshot uses anymore. The `--prune` flag runs both in one step.
