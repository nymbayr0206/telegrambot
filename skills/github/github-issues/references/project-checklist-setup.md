# Project Checklist: Initial Issue Setup

> Use this workflow when a user wants to create a fix/task checklist as GitHub Issues for a new or existing project. Bridges `github-repo-management` (repo creation) with `github-issues` (checklist population).

## Workflow

### 0. Let the user pick a tracking tool first

When a user asks for a "fix checklist" or "task list", do **not** assume GitHub Issues. Present options:

| Tool | When to suggest |
|------|----------------|
| **Google Sheets** | Quick shared view, no setup, team can edit directly |
| **Linear** | Pro dev tracking, lightweight, fast |
| **GitHub Issues** | Code-connected, already has repo, dev team |
| **Notion** | Notes + tracking combined |

Wait for their choice before proceeding. If they pick GitHub Issues, continue below.

### 1. Determine the target repo

| Scenario | Action |
|----------|--------|
| No repo yet | Create one via `github-repo-management` skill, then populate |
| Existing repo | Ensure inside the repo dir or have `OWNER/REPO` from remote URL |

### 2. Author the checklist first (in a scratch file)

Before creating issues, write the full checklist to a temp file so the user can review/adjust:

```markdown
## Fix Checklist

- [ ] Fix #1: General Manager can assign tasks to anyone
  - Permission logic broken — GM role lacks `task:assign` scope
  - DB: update user_role_permissions table
- [ ] Fix #2: Remove auto-logout (persistent session)
  - Session middleware timeout set to indefinite
  - Remove `expires` from JWT/session cookie config
```

### 3. Create issues in batch

**With gh (recommended — one at a time or loop):**

```bash
# Template per issue
gh issue create \
  --repo "$OWNER/$REPO" \
  --title "Fix #1: General Manager can assign tasks to anyone" \
  --body "## Problem
GM role cannot assign tasks to arbitrary users.

## Root Cause
Permission logic missing — user_role_permissions table lacks \`task:assign\` scope for GM.

## Acceptance Criteria
- [ ] GM can view all users in the system
- [ ] GM can select any user as task assignee
- [ ] Non-GM roles have no change" \
  --label "bug,permissions" \
  --assignee "@me"
```

**Bulk loop pattern:**

```bash
# For a list of issues, iterate
for title in \
  "Fix #1: General Manager can assign tasks" \
  "Fix #2: Remove auto-logout"; do
  gh issue create \
    --repo "$OWNER/$REPO" \
    --title "$title" \
    --body "See checklist for details" \
    --label "bug"
  sleep 1  # avoid rate limiting
done
```

### 4. Add project-level labels if needed

```bash
# Standard checklist labels
gh label create "priority:critical" --repo "$OWNER/$REPO" --color "b60205"
gh label create "priority:high" --repo "$OWNER/$REPO" --color "d93f0b"
gh label create "priority:medium" --repo "$OWNER/$REPO" --color "fbca04"
gh label create "priority:low" --repo "$OWNER/$REPO" --color "0e8a16"
gh label create "fix" --repo "$OWNER/$REPO" --color "5319e7"
gh label create "enhancement" --repo "$OWNER/$REPO" --color "1d76db"
```

### 5. Link issues via a milestone (optional)

```bash
# Create milestone
gh api repos/$OWNER/$REPO/milestones \
  --method POST \
  --field title="MVP v1.0" \
  --field description="Critical fixes for launch"

# Get milestone number from response, then edit issues
gh issue edit 1 --milestone "MVP v1.0" --repo "$OWNER/$REPO"
gh issue edit 2 --milestone "MVP v1.0" --repo "$OWNER/$REPO"
```

### 6. Verify

```bash
gh issue list --repo "$OWNER/$REPO" --label "fix" --state open
```

## Pitfalls

- **gh not installed:** Install via direct binary download: `curl -sL https://github.com/cli/cli/releases/download/v2.67.0/gh_2.67.0_linux_amd64.tar.gz -o /tmp/gh.tar.gz && tar -xzf /tmp/gh.tar.gz -C /tmp && cp /tmp/gh_2.67.0_linux_amd64/bin/gh /opt/data/.local/bin/gh && chmod +x /opt/data/.local/bin/gh`
- **gh not authenticated:** Run `gh auth login --with-token` with a user-generated PAT. If `gh auth login` fails with scope errors, try `export GH_TOKEN="<token>"` instead — this bypasses strict scope validation while still letting `gh` commands work.
- **Fine-grained PAT cannot create repos:** If the token starts with `github_pat_`, the `gh repo create` command will fail with `GraphQL: Resource not accessible by personal access token (createRepository)`. Ask the user for a Classic PAT (`ghp_...`) with `repo` scope, or have them create the repo on GitHub.com manually.
- **Rate limiting:** Space bulk creates by 1s intervals; use `sleep 1` between `gh issue create` calls
- **No labels exist yet:** Create them first before assigning in issue creation
- **Project notes already exist:** Read `/opt/data/projects/` for existing context before writing issues
