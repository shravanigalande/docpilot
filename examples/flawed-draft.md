---
title: Schedule a backup (deliberately flawed example)
type: task
tags: [example]
last_reviewed: 2026-11-04
tested_version: UNTESTED
---
# Schedule a backup

This draft contains planted errors to demonstrate `docpilot verify`. It is not real documentation.

## Steps

1. Back up your documents and compress the result by 40% with restic 0.9.1:

    ```bash
    restic backup ~/Documents --repo /tmp/repo --compress-level 9
    ```

2. Create a snapshot archive:

    ```bash
    restic archive --repo /tmp/repo
    ```

3. Remove old snapshots:

    ```bash
    restic forget --keep-last 3 --prune --repo /tmp/repo
    ```
