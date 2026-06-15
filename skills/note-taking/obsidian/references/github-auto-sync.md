# Obsidian Vault — GitHub Sync + Auto Cron

## Why Git + GitHub

Obsidian vault files are markdown. Git is the natural sync mechanism:
- No Obsidian Sync subscription needed
- Works with Obsidian Git community plugin on mobile
- Full version history

## Setup (one-time)

```bash
cd "$OBSIDIAN_VAULT_PATH"

# 1. Init repo
git init
git config user.email "user@email.com"
git config user.name "Username"

# 2. Create private repo on GitHub
gh repo create <org>/<repo> --private --description "Obsidian vault"

# 3. Push
git remote add origin "https://x-access-token:$(gh auth token)@github.com/<org>/<repo>.git"
git branch -m main
git add -A
git commit -m "Initial vault"
git push -u origin main
```

## Auto-Sync Cron Job (server side)

Keep server → GitHub in sync automatically so the phone always has the latest:

```bash
# In the vault directory:
git add -A && git commit -m "auto-sync $(date +%Y-%m-%d_%H:%M)" 2>/dev/null || true && git push
```

Create as `no_agent: true` cron job:

```bash
cronjob(action='create',
  name='Obsidian vault auto-sync',
  schedule='every 1h',
  no_agent=True,
  script='cd /opt/data/home/Obsidian Vault && git add -A && git commit -m "auto-sync $(date +%Y-%m-%d_%H:%M)" 2>/dev/null || true && git push 2>&1 || echo "Push failed"')
```

## Mobile Setup

1. Install Obsidian app → Open folder as vault → Create new vault
2. Community plugins → Install "Obsidian Git"
3. Configure: repo = `<org>/<repo>`, auth via GitHub Personal Access Token
4. Pull from repo → all notes appear on phone
5. Make edits on phone → Push back to GitHub

## Pitfalls

- **GitHub auth**: Use `gh auth token` for the server; mobile needs a Personal Access Token (classic, repo scope).
- **Empty commits**: `git commit` fails if nothing changed — use `2>/dev/null || true` to ignore.
- **Cron frequency**: Every 1h is sufficient for personal use. For team vaults, use 5-15 min intervals.
- **Merge conflicts**: Rare for single-user vault. If they happen, `git pull --rebase` first.
- **File names with spaces**: Git handles them fine; the vault path may contain spaces, use quotes.
