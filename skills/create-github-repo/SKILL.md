---
name: create-github-repo
description: Create a GitHub repository for the current project with gh and push the local code. Use when the user wants to publish the current directory as a new GitHub repo.
allowed-tools: Bash(git *), Bash(gh *)
---

# Create GitHub Repo

Use the GitHub CLI (`gh`) to create a new repository and push code.

## Ask the User

Before creating the repo, ask the user to choose the name source:

1. Current folder name
2. Suggested name derived from the project purpose
3. Custom name

Also confirm visibility if it is not obvious from context.

## Workflow

1. Check that the current directory is the intended project root.
2. Inspect the project briefly so the suggested repo name is sensible when needed.
3. Ensure `gh auth status` succeeds before trying to create the repository.
4. Create the repo with `gh repo create`.
5. Set `origin` and push `main` when `--push` was not used.

## Commands

```bash
# Create repo and push immediately
gh repo create my-repo-name --source=. --remote=origin --push

# Create private
gh repo create my-repo-name --source=. --remote=origin --push --private

# Create without pushing yet
gh repo create my-repo-name --source=. --remote=origin
git push -u origin main
```

## Notes

- Default branch is `main`.
- Use `--org=<org-name>` when the repo belongs under an organization.
- If the working tree is not committed yet, inspect the status and avoid surprising the user.
