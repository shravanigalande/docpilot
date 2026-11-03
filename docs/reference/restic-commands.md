---
title: Command reference
type: reference
tags: [restic, commands, reference]
last_reviewed: 2026-11-04
---
# Command reference

This topic lists the restic commands used in these docs. Run `restic help` for the complete list.

## Commands

| Command | Purpose |
|---|---|
| `restic init` | Create a new repository. |
| `restic backup` | Create a snapshot of files and directories. |
| `restic snapshots` | List the snapshots in a repository. |
| `restic restore` | Restore a snapshot to a target directory. |
| `restic forget` | Remove snapshot records, with optional retention rules. |
| `restic prune` | Delete data that no snapshot uses. |
| `restic check` | Verify the repository structure and optionally its data. |

## Common flags

| Flag | Applies to | Purpose |
|---|---|---|
| `--repo`, `-r` | All commands | Path or URL of the repository. |
| `--exclude`, `-e` | `backup`, `restore` | Skip files that match a pattern. |
| `--target`, `-t` | `restore` | Directory to restore into. |
| `--keep-last` | `forget` | Keep the given number of most recent snapshots. |
| `--prune` | `forget` | Delete unused data after forgetting snapshots. |
| `--dry-run`, `-n` | `backup`, `forget`, `prune` | Show what would happen without changing anything. |
| `--read-data` | `check` | Read and verify all stored data. |
