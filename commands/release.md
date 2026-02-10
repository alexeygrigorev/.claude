# Release

Release the current changes to package registry and GitHub.

## Check for Makefile

First, check if `Makefile` exists with publish targets:

```bash
grep -E "^(publish-build|publish-test|publish|publish-clean)" Makefile
```

If present, **use the Makefile targets**:
```bash
make publish-build   # Build
make publish-test    # Test the build
make publish         # Publish
make publish-clean   # Clean up
```

## Manual Release (No Makefile)

1. **Check current version** on PyPI:
   ```bash
   uv run pip index versions <package-name>
   ```

2. **Bump version** (default: patch version) in `<library_name>/__version__.py` or `pyproject.toml`:
   ```bash
   # Extract and increment patch version
   ```

3. **Commit changes** (if not already committed):
   ```bash
   git add -A
   git commit -m "Describe changes"
   ```

4. **Commit version bump**:
   ```bash
   git add <version-file>
   git commit -m "Bump version to X.Y.Z"
   ```

5. **Build package**:
   ```bash
   uv run hatch build
   ```

6. **Check distribution**:
   ```bash
   uv run hatch check
   ```

7. **Publish to PyPI**:
   ```bash
   uv run hatch publish
   ```

   (Or test first: `uv run hatch publish --repo test`)

8. **Push to GitHub**:
   ```bash
   git push origin main
   ```

9. **Create GitHub release** with binaries from `dist/`:

   First, analyze all changes to write comprehensive release notes:

   ```bash
   # Show commits since last tag
   git log $(git describe --tags --abbrev=0)..HEAD --oneline

   # Show file change statistics
   git diff $(git describe --tags --abbrev=0)..HEAD --stat

   # For significant changes, examine key file diffs
   git diff <last-tag>..<current> -- <file-path>

   # Read new modules to understand features
   # Use Read tool on new/changed files
   ```

   **Writing Release Notes:**

   - DO NOT just list commit messages - analyze what actually changed
   - Group changes by category (New Features, Performance, Bug Fixes, Breaking Changes)
   - For new modules: explain what they do and when to use them
   - For performance changes: describe what was optimized
   - For refactoring: explain the new structure and benefits
   - Include concrete examples of API changes

   Create the release:
   ```bash
   gh release create X.Y.Z dist/* --title "X.Y.Z" --notes "YOUR_NOTES"
   ```

   Or edit an existing release:
   ```bash
   gh release edit X.Y.Z --notes "YOUR_NOTES"
   ```

## Notes

- Use `hatch` for building and publishing (not `twine`)
- Add `hatch` to dev dependencies in `pyproject.toml`
- Use semantic versioning:
  - **Patch** (X.Y.Z): Bug fixes, small improvements
  - **Minor** (X.Y.0): New features, backward compatible
  - **Major** (X.0.0): Breaking changes
