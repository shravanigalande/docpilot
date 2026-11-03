---
title: Repositories and snapshots
type: concept
tags: [restic, repository, snapshot]
last_reviewed: 2026-11-04
---
# Repositories and snapshots

Restic stores your backups in a repository and records each backup run as a snapshot. Understanding these two terms makes every other restic task easier.

## What a repository is

A repository is the location where restic keeps all backup data. It can be a local directory, an external drive, or cloud storage. Restic encrypts everything in the repository with your password.

You choose the repository when you run a command, by using the `--repo` flag or the `RESTIC_REPOSITORY` environment variable.

## What a snapshot is

A snapshot is the state of your files at the moment a backup ran. Each snapshot has a short ID, a time, a host name and the paths it covers.

Restic stores a snapshot as a small record that points to the stored data. You can restore any snapshot completely, even though restic saves only changed data.

## Why the password matters

If you lose the repository password, you cannot recover the data. Restic cannot reset it. Store the password in a password manager.

## Related topics

- [How incremental backups work](incremental-backups.md)
- [Create a repository](../tasks/create-repository.md)
