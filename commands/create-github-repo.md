# Create GitHub Repo

Use the GitHub CLI (`gh`) to create a new repository and push code.

## Naming

When executing this command, Claude should **ask the user** to choose from:

1. **Current folder name** - Use the existing directory name
2. **Suggested name** - A name reflecting the project's purpose (Claude should analyze the codebase and propose a descriptive name)
3. **Custom** - User types their own

The repo name becomes part of the URL: `github.com/username/REPO-NAME`

## Create & Push

```bash
# Create repo (default branch is main)
gh repo create my-repo-name --source=. --remote=origin --push

# Or create private
gh repo create my-repo-name --source=. --remote=origin --push --private

# Or create without pushing yet
gh repo create my-repo-name --source=. --remote=origin
git push -u origin main
```

## Options

- `--source=.` - Use current directory as source
- `--remote=origin` - Set remote name
- `--push` - Push to remote immediately
- `--public` / `--private` - Set visibility
- `--description="..."` - Add description
- `--clone` - Clone instead of linking local dir

## Notes

- Default branch is **main** (not master)
- Run from existing project directory
- Creates repo under your GitHub account
- Use `--org=org-name` to create under an organization
