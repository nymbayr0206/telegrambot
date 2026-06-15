# Converting Conversation Notes to GitHub Issues

## When to Use

The user says something like:
- "I had memory notes from that Friday conversation — save them as GitHub issues"
- "find my notes about project changes and create issues for them"
- "хөгжүүлэлтийн тэмдэглэл хөтөлж байна — GitHub issue үүсгэ" (keeping a dev log, create GitHub issues)
- "Хүн тус бүр дээр даалгавар үүсгэж болгох" (create tasks for each person)

## Workflow

### 1. Find the source notes — do systematic search BEFORE asking

When the user says they have a development log but doesn't specify where, search in this order:

1. **Obsidian vault** — check `Notes/` dir for dated notes, `Todo-List.md`, `Dashboard.md`. Search vault files for keywords: `засах`, `нэмэх`, `өөрчлөх`, `fix`, `add`, `change`, `issue`, `bug`, `feature`.
2. **This chat session** — check if the development log was posted IN the current conversation (user messages in session JSON).
3. **Project directories** — look in `repos/<project>/docs/`, `repos/<project>/`, any `CHANGELOG`, `TODO`, or `*.md` files in project roots.
4. **Other session transcripts** — use `session_search` with keywords from the user's description (date, topic, person, project name).

Only after exhausting ALL of the above should you ask the user once where the notes are.

### 2. Extract action items

Read the source notes and identify concrete action items, fix requests, or change tasks. Look for:

- User saying "I need to fix X, change Y, add Z"
- User mentioning feedback from someone (lawyer, client, partner)
- Bullet lists of tasks the user asked to do
- GitHub issues that were already discussed but not created yet
- Phrases like "засах", "өөрчлөх", "нэмэх", "change", "fix", "update", "add"

### 3. Identify the target repo

From `git remote -v` in cloned repos — ask the user which repo if ambiguous, or infer from context:
- `tengertech-webapp` / `aimongoliatushig-cloud/tengertech-webapp` — money-ciple financial system
- `tengertecherp` — municipal ERP (хот тохижилт)
- `agenticforceweb` / `aimongoliatushig-cloud/agenticforceweb` — agenticforce/Postly company site
- `postly.mn` / `postlyautovideo` — postly brand
- `supernova.mn` — supernova brand

**IMPORTANT:** If `gh` CLI is not installed, check for GITHUB_TOKEN in `~/.hermes/.env`, `~/.env`, or `env | grep GITHUB`. If none exists but SSH git auth works (`git fetch` succeeds), use `curl` against the GitHub REST API with a token from another source, or prompt the user to set up authentication.

### 4. Create issues in batch

Use `gh issue create` or `curl -X POST` for each item. Apply appropriate labels (documentation, bug, enhancement) based on the task type.

Structure: each action item = ONE issue. Do NOT combine multiple items into one issue.

When the user asks "create tasks for each person" ("хүн тус бүр дээр даалгавар"):
- Assign each issue to the relevant person (by GitHub username)
- If usernames are unknown, use the person's name in the issue title: `[<Person>] <Task description>`
- Label by type: `bug`, `enhancement`, `documentation`, `task`

### 5. Example: From conversation → issues

Source: Friday session about a "хөгжүүлэлтийн ажлын тайлан" (development report).

Lawyer's feedback → 4 issues: late reason + actual date; fix section 5 user roles; remove purchasing manager role, add Нярав; department head signatures.

Each gets its own issue with STATUS note:
```bash
gh issue create --repo owner/repo --title "Fix: Description" --label "documentation" --body "Context and status info"
```

### 6. Verify

Run `gh issue list --repo owner/repo` or the equivalent curl command to confirm all issues were created.

## Pitfalls

- **Don't ask repeatedly** — search systematically before asking where the notes are. The user expects you to find it.
- Don't create one issue with a list of items. Each action item gets its own issue.
- Include source context in the issue body so it's clear where the task came from.
- Mark "already done" status if the change was already applied (e.g., "Баасан гарагт засвар хийгдсэн ✅").
- Use descriptive Mongolian titles when the context is about Mongolian project documentation — it helps the user find issues later.
- For documentation fixes, use the `documentation` label. For code changes, use `bug` or `enhancement`.
- **No `gh` CLI / no GITHUB_TOKEN?** If only SSH git auth works, you cannot use the REST API directly. Options: (a) install `gh` and authenticate via browser/SSH, (b) create a PAT and export GITHUB_TOKEN, (c) prompt the user to set up credentials.
