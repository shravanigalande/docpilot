---
title: Create a repository
type: task
tags: [restic, repository, init]
last_reviewed: 2026-11-04
tested_version: UNTESTED
---
# Create a repository

Create an encrypted repository in a local directory.

## Before you begin

- [Install restic](install-restic.md).
- Choose a strong password and store it in a password manager. You cannot recover data without it.

## Steps

1. Run the initialization command. The command creates the directory if it does not exist:

    ```bash
    restic init --repo /tmp/restic-demo-repo
    ```

2. Enter a password when restic prompts you, and enter it again to confirm.

    Restic prints a message that it created a repository at the path you chose.

3. List the repository directory to confirm that restic created its files:

    ```bash
    ls /tmp/restic-demo-repo
    ```

    The directory contains a `config` file and several subdirectories, including `data` and `snapshots`.

## Next steps

Continue with [Back up files](back-up-files.md).
