# Worktree cleanup

Remove **merged** git worktrees and their merged branches across repos to reclaim
disk and de-clutter branch lists. Safe because merged work is already in the default
branch.

## 0. Find where the space went

```bash
df -h /                                                    # which filesystem is full
sudo du -h --max-depth=1 -x / 2>/dev/null | sort -rh | head     # top dirs on the root fs
du -h --max-depth=1 -x ~ 2>/dev/null | sort -rh | head -25     # top dirs in home
```

Worktrees are full working checkouts, so a repo with many of them (e.g. an agent
`worktrees/` dir holding 50+ × ~500 MB checkouts) can dominate `du` output.

## 1. List every worktree in a repo

```bash
cd <repo>
git fetch origin --quiet
git worktree list                               # authoritative: path + branch/HEAD
```

Worktrees can live anywhere — a shared `.worktrees/`, the repo's own `.tmp/worktrees/`,
`/tmp/`, even `~/git/<somewhere-else>`. `git worktree list` finds them all; a plain
`ls` does not. **This is exactly why `rm -rf` is wrong**: it deletes files but leaves
the git registration dangling. Always go through `git worktree remove`.

## 2. Classify each worktree: merged / unmerged / dirty

Default branch: `git symbolic-ref --short refs/remotes/origin/HEAD` (usually `main`).
Use `origin/<default>` as the merge target so the test reflects what's actually landed.

```bash
DEFAULT=origin/main
git worktree list --porcelain | awk '/^worktree /{print $2}' | while read -r path; do
  [ "$path" = "$(git rev-parse --show-toplevel)" ] && continue
  commit=$(git -C "$path" rev-parse HEAD 2>/dev/null) || { echo "MISSING-DIR  $path"; continue; }
  if git merge-base --is-ancestor "$commit" "$DEFAULT"; then s=MERGED; else s=UNMERGED; fi
  [ -n "$(git -C "$path" status --porcelain)" ] && s="$s (dirty)"
  printf '%-12s %s\n' "$s" "$path"
done
```

- `MERGED` → safe to remove (HEAD is an ancestor of the default branch).
- `UNMERGED` → **keep** (work not yet landed).
- `(dirty)` → has uncommitted local edits. **Do not remove it.** Leave it alone or ask
  the user — never `--force`. `--force` discards uncommitted changes, which git does not
  store and cannot recover.

## 3. Remove merged worktrees — clean ones only

A worktree is removable only if it is **clean** (no uncommitted changes) **and**
**merged** (HEAD is an ancestor of the default branch). If it is dirty, **skip it** —
do not pass `--force`.

```bash
git worktree remove <path>          # clean + merged ONLY
```

Loop, removing only clean merged worktrees and *reporting* (never removing) dirty ones:

```bash
DEFAULT=origin/main
git worktree list --porcelain | awk '/^worktree /{print $2}' | while read -r path; do
  [ "$path" = "$(git rev-parse --show-toplevel)" ] && continue
  commit=$(git -C "$path" rev-parse HEAD 2>/dev/null) || continue
  git merge-base --is-ancestor "$commit" "$DEFAULT" || continue   # only merged
  if [ -n "$(git -C "$path" status --porcelain)" ]; then
    echo "SKIP (dirty — uncommitted changes, NOT removed): $path"   # NEVER --force
  else
    git worktree remove "$path"                                    # clean merged
  fi
done
```

## 4. Prune worktrees whose directories are already gone

```bash
git worktree prune -v
```

## 5. Delete the now-merged local branches

Removing a worktree leaves its branch behind. Delete branches merged into the default
branch (lossless — commits are in the default branch). `git branch -d` refuses anything
unmerged or checked-out in a worktree; for branches merged into `origin/main` but not
into the current HEAD, confirm ancestry then `-D`:

```bash
DEFAULT=origin/main
git branch --merged "$DEFAULT" | sed 's/^[*+ ]*//' | grep -v '^main$' | while read -r b; do
  [ -z "$b" ] && continue
  git merge-base --is-ancestor "$b" "$DEFAULT" || continue   # belt-and-suspenders
  git branch -d "$b" 2>/dev/null || git branch -D "$b" 2>/dev/null || echo "kept $b (checked out)"
done
```

The `sed 's/^[*+ ]*//'` strips the `*` (current branch) and `+` (checked-out-in-worktree)
markers that `git branch` prints.

## 6. `.tmp` scratch dirs — two populations, don't conflate

A repo's `.tmp/` (or `worktrees/`) dir usually holds **two different things**:

1. **Registered git worktrees** (full checkouts tracked by `git worktree list`) — agents
   may be actively working in these right now.
2. **Plain scratch dirs** (logs, run artifacts, screenshots, caches, old test output) —
   not tracked by git at all.

They look identical in `ls`/`du`. Before deleting anything, classify each entry by
whether it appears in `git worktree list`:

```bash
cd <repo>
git worktree list --porcelain | awk '/^worktree /{print $2}' > /tmp/wt.txt
DEFAULT=origin/main
for d in .tmp/*/ ; do
  abspath="$(pwd)/${d%/}"
  if grep -qxF "$abspath" /tmp/wt.txt; then
    commit=$(git -C "$d" rev-parse HEAD 2>/dev/null)
    m=merged; git merge-base --is-ancestor "$commit" "$DEFAULT" 2>/dev/null || m=UNMERGED
    [ -n "$(git -C "$d" status --porcelain 2>/dev/null)" ] && m="$m+DIRTY"
    echo "WORKTREE($m)  $d"
  else
    echo "scratch       $d"
  fi
done
```

- **`scratch`** (not a worktree): safe to `rm -rf`, with the caveats below.
- **`WORKTREE(...)`**: handle per sections 2–3 — remove only if `merged` **and** not
  `DIRTY`. Never `rm -rf` a worktree; use `git worktree remove`.

### Removing plain scratch dirs

```bash
git worktree list --porcelain | awk '/^worktree /{print $2}' > /tmp/wt_now.txt   # re-fetch EVERY run, right before
for d in .tmp/*/ ; do
  abspath="$(pwd)/${d%/}"
  grep -qxF "$abspath" /tmp/wt_now.txt && continue                 # skip worktrees
  case "$(basename "$d")" in *memory*|*plan*|*wiki*|*spec*) continue;; esac   # keep note-like dirs
  rm -rf -- "$d"
done
```

Caveats:

- **Re-fetch `git worktree list` immediately before the loop.** Agents convert scratch
  dirs into worktrees (and back) while you work — a dir that was scratch a minute ago may
  now be a live worktree. Always re-check membership at removal time, not at analysis time.
- **Keep content / caches / note dirs** unless the user says otherwise: browser caches
  (`playwright-browsers` — removing just triggers a re-download), content data
  (`source-content`, `content-2-*`, `legacy-*`), and note-like dirs (`*memory*`,
  `*plan*`, `*wiki*`).
- **Never `rm -rf` a path that is in `git worktree list`.** That leaves a dangling
  registration; route worktrees through `git worktree remove` (sections 2–3).

## Don't

- **`--force` a dirty worktree, ever.** `git worktree remove --force` silently discards
  uncommitted changes — and git does not store them, so they are gone for good. If a
  worktree is dirty, skip it and ask. (This rule exists because force-removing ~36
  merged-but-dirty agent worktrees once destroyed uncommitted edits that may have been
  useful.)
- `rm -rf` a worktree directory — leaves a dangling registration. Always
  `git worktree remove` (then `git worktree prune` for any already-gone dirs).
- Delete branches still checked out in a worktree you're keeping — git refuses, and
  that refusal is the safety net.
- Force-delete (`-D`) without first confirming
  `git merge-base --is-ancestor <branch> origin/main`.
- Trust a directory listing over `git worktree list` — worktrees hide in `.tmp/`,
  `/tmp/`, and sibling dirs.

## Lesson learned (2026-08-13)

The clean merged worktrees and merged branches removed across `ai-shipping-labs`,
`aws-infra`, and `rustkyll` were removed safely and freed disk (root partition
21G → ~38G free). **But the operator also `--force`-removed ~36 worktrees that were
merged yet carried uncommitted local edits — destroying those edits** (e.g. uncommitted
changes to `payments/services/webhook_handlers.py`, `_docs/testing-guidelines.md`, and
others in `agent-*` / `tester-*` worktrees). That was wrong and is the reason for the
hard rules above: **dirty worktrees are never force-removed. The disk space is never
worth losing uncommitted work.**

Later that day the procedure was re-run *correctly* on `dtc-website/.tmp`: 64 plain
scratch dirs (~7.5 GB) and 46 stale (≥3-day-old) clean+merged worktrees (~43 GB) were
removed — while **22 dirty worktrees, 2 unmerged, and 44 touched-recently worktrees were
explicitly skipped**, so no uncommitted work was touched. Root partition went 21G → ~109G
free across the session. The key was treating `.tmp` as two populations (worktrees vs
scratch) and re-checking `git worktree list` immediately before every delete.
