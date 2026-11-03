---
title: Install restic
type: task
tags: [restic, install]
last_reviewed: 2026-11-04
tested_version: UNTESTED
---
# Install restic

Install the restic command-line program and confirm that it runs.

## Before you begin

- Use macOS, or a Debian-based Linux distribution such as Ubuntu.
- Make sure you have administrator access on Linux.

## Steps

1. Install restic with your package manager.

    On macOS:

    ```bash
    brew install restic
    ```

    On Ubuntu or Debian:

    ```bash
    sudo apt install restic
    ```

2. Check the installed version:

    ```bash
    restic version
    ```

    The output starts with `restic` followed by a version number.

## Next steps

Continue with [Create a repository](create-repository.md).
