---
name: cleanup
description: Reclaim disk and de-clutter git repos by finding and removing merged git worktrees, their now-merged local branches, and plain scratch dirs (`.tmp` logs/run output/caches that aren't worktrees). Use when the disk is filling up, when `git worktree list` / `git branch` are bloated with stale agent or task worktrees (`agent-*`, `tester-*`, `issue-*`), or when asked to "clean up git" / free space. Full procedure is in worktrees.md.
---

# Cleanup

Removes **merged** git worktrees and their merged branches to reclaim disk and
de-clutter branch lists. Built for repos that accumulate dozens of throwaway
worktrees from coding agents. Safe because merged work is already reachable from
the default branch.

## Golden rules

- **Only remove worktrees whose work is committed AND merged into the default branch**
  (`origin/<default>`, usually `origin/main`). Both conditions, always.
- **Never discard uncommitted changes — never pass `--force`.** A worktree with
  uncommitted local edits is "dirty": leave it alone. Uncommitted edits are not stored
  by git, cannot be recovered once deleted, and may well be valuable. This is the
  hardest rule here.
- **Always use `git worktree remove`, never `rm -rf`.** `rm -rf` leaves dangling
  worktree registrations and stale branch refs; `git worktree remove` cleans both.
- **Deleting a merged branch is lossless** — its commits already live in the default
  branch.

## Reference

- **[worktrees.md](worktrees.md)** — copy-pasteable procedure: find the space hogs,
  list every worktree, classify each entry as a worktree (merged/unmerged/dirty) or
  plain scratch, remove only clean+merged worktrees (never dirty) and stale scratch
  (keeping caches/content/notes), prune stale entries, then delete the merged branches.
