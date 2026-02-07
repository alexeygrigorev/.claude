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
   uv run python -m build
   ```

6. **Check distribution**:
   ```bash
   uv run twine check dist/*
   ```

7. **Publish to PyPI**:
   ```bash
   uv run twine upload dist/*
   ```

8. **Push to GitHub**:
   ```bash
   git push origin main
   ```

9. **Create GitHub release** with binaries from `dist/`:
   ```bash
   # Show commits since last tag for notes
   git log $(git describe --tags --abbrev=0)..HEAD --oneline

   # Create release with binaries + auto-generated notes
   gh release create X.Y.Z dist/* --title "X.Y.Z" --generate-notes
   ```

   Release notes should summarize:
   - New features
   - Bug fixes
   - Breaking changes (if any)
   - Dependencies updated

## Notes

- Make sure `twine` is installed: `uv pip install twine build`
- Use semantic versioning:
  - **Patch** (X.Y.Z): Bug fixes, small improvements
  - **Minor** (X.Y.0): New features, backward compatible
  - **Major** (X.0.0): Breaking changes
