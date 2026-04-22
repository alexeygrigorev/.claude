---
name: release
description: Release the current package to the registry and GitHub, including version bumping, build validation, publish steps, and release notes. Use when the user wants to ship the current project.
allowed-tools: Bash(git *), Bash(gh *), Bash(uv *), Bash(make *)
---

# Release

Release the current changes to the package registry and GitHub.

## Prefer Makefile Targets

Check whether `Makefile` exposes release targets:

```bash
grep -E "^(publish-build|publish-test|publish|publish-clean)" Makefile
```

If those targets exist, prefer:

```bash
make publish-build
make publish-test
make publish
make publish-clean
```

## Manual Release Flow

If no suitable Makefile targets exist:

1. Check the current published version on PyPI.
2. Bump the version, defaulting to a patch release unless the user says otherwise.
3. Commit implementation changes if they are not already committed.
4. Commit the version bump.
5. Build the package.
6. Check the built distribution.
7. Publish to PyPI or TestPyPI as requested.
8. Push to GitHub.
9. Create or update the GitHub release with real release notes.

## Commands

```bash
uv run pip index versions <package-name>
uv run hatch build
uv run hatch check
uv run hatch publish
git push origin main
```

## Release Notes

Do not just paste commit messages. Inspect the actual changes:

```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
git diff $(git describe --tags --abbrev=0)..HEAD --stat
```

When necessary, inspect key file diffs and summarize:

- new features
- bug fixes
- performance changes
- refactors
- breaking changes

Then create the release:

```bash
gh release create X.Y.Z dist/* --title "X.Y.Z" --notes "YOUR_NOTES"
```

## Notes

- Use `hatch` rather than `twine`.
- Use semantic versioning.
- Confirm destructive publish steps with the user before executing them.
