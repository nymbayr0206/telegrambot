---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Setup / Initialize a Vault From Scratch

When the user asks to "set up Obsidian" or no vault exists anywhere, do the following:

### 1. Detect whether a vault already exists

```bash
echo "OBSIDIAN_VAULT_PATH=${OBSIDIAN_VAULT_PATH:-unset}"
ls -la ~/Documents/Obsidian\ Vault 2>/dev/null && echo "EXISTS" || echo "NOT_FOUND"
```

### 2. If no vault exists, create the directory structure

```bash
VAULT="/opt/data/home/Obsidian Vault"         # prefer under home
# or
VAULT="$HOME/Documents/Obsidian Vault"        # fallback
mkdir -p "$VAULT/.obsidian"
mkdir -p "$VAULT/Daily"    # for daily notes
mkdir -p "$VAULT/Projects" # for project notes
mkdir -p "$VAULT/Notes"    # for general notes
```

### 3. Initialize .obsidian config files (minimal viable config)

**`app.json`** — base editor settings:
```json
{
  "showLineNumber": true,
  "spellcheck": true,
  "strictLineBreaks": false,
  "alwaysUpdateLinks": true,
  "newFileLocation": "root",
  "newLinkFormat": "relative",
  "promptDelete": true,
  "attachmentFolderPath": "assets",
  "showUnsupportedFiles": true
}
```

**`core-plugins.json`** — enable daily-notes + file-explorer + search + graph:
```json
{
  "active": [
    "file-explorer","global-search","switcher","graph","backlink",
    "canvas","outgoing-link","tag-pane","page-preview","daily-notes",
    "templates","note-composer","command-palette","slash-command",
    "editor-status","bookmarks","markdown-importer","word-count",
    "file-recovery"
  ],
  "daily-notes": {
    "folder": "Daily",
    "format": "YYYY-MM-DD",
    "template": ""
  }
}
```

**`appearance.json`** — dark theme, gold accent, Inter font:
```json
{
  "accentColor": "#f59e0b",
  "baseTheme": "obsidian",
  "interfaceFontFamily": "Inter",
  "textFontFamily": "Inter",
  "monospaceFontFamily": "JetBrains Mono",
  "showViewHeader": true
}
```

Create all three with `write_file` at `$VAULT/.obsidian/<filename>`.

### 4. Create a Welcome note and daily-note template

**`Welcome.md`** — explain the vault structure with wikilinks.
**`Daily/Template.md`** — daily note scaffold:
```markdown
# {{date}}
## Өнөөдрийн зорилго
-
## Тэмдэглэл
-
## Хийх зүйлс
- [ ]
```

### 5. Persist `OBSIDIAN_VAULT_PATH`

Append to `~/.hermes/.env`:
```bash
echo 'export OBSIDIAN_VAULT_PATH="/path/to/vault"' >> ~/.hermes/.env
```

The env var is read on the next session start. Also set it in the current terminal session with `export OBSIDIAN_VAULT_PATH=...` so subsequent tool calls in this session can resolve it.

### 6. Verify

```bash
ls -la "$OBSIDIAN_VAULT_PATH/"
ls -la "$OBSIDIAN_VAULT_PATH/.obsidian/"
find "$OBSIDIAN_VAULT_PATH" -type f | sort
```

## GitHub Sync (Phone ↔ Server)

After the vault is set up, enable two-way sync via GitHub so the phone's Obsidian app always has the latest notes:

1. **Server → GitHub**: Run the `references/github-auto-sync.md` setup script to init git and push.
2. **Auto-sync cron**: Create a `no_agent: true` cron job that commits and pushes every hour.
3. **Phone → Obsidian**: Install "Obsidian Git" community plugin on the mobile app, point it at the same repo.
4. **Two-way**: Server pushes automatically; phone pulls/pushes via the plugin.

Full recipe: `references/github-auto-sync.md`

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Pitfalls

### PWA / remote access from phone
Obsidian vault served over plain HTTP will NOT work as a PWA (requires HTTPS + a valid certificate). The `display: standalone` manifest property is ignored by browsers on HTTP. Workarounds:
- **Obsidian mobile app** (recommended): sync vault via Obsidian Sync, iCloud, or a local network share.
- **Google Docs/Drive fallback**: create a Google Doc from the vault content when the user needs mobile access but can't install Obsidian.
- **Install Obsidian on the server**: requires a display server (X11/Wayland) — impractical for headless servers.

### Vault path conventions
Use the `OBSIDIAN_VAULT_PATH` environment variable (set in `~/.hermes/.env`). The fallback is `~/Documents/Obsidian Vault`. File tools do not expand shell variables — resolve the path before calling `read_file`/`write_file`/`search_files`.


## Dashboard Notes & PWA Web Dashboards

When the user asks for a "dashboard" or "PWA app" for their notes:
- Create a `Dashboard.md` note at vault root with project status, today's tasks, quick links, and metrics
- If they want a web app: create an HTML dashboard + `manifest.json` in a `dashboard/` subfolder
- Serve with `python3 -m http.server PORT --bind 0.0.0.0 -d "path"`
- Server firewall may block external ports; fallback = deliver the HTML file directly via MEDIA: in the reply
- If PWA doesn't work (HTTP needs HTTPS), recommend: (a) Obsidian mobile app, or (b) Google Docs/Drive copy of the content
- Full pattern in `references/dashboard-pwa-pattern.md`

## Dashboard Note Design
- One screen, top-down: Today → Projects → Key Metrics → Quick Links
- Use `[[wikilinks]]` to other vault notes
- Checkbox lists for daily tasks
- Markdown tables for project status rows
- Update the date manually on each refresh

## Reference & template files

- `references/debian-headless-setup.md` — installing Obsidian on headless Debian (no root, no FUSE, no display), plus vault path conventions for servers.
- `references/dashboard-pwa-pattern.md` — creating dashboard notes and PWA-style HTML web dashboards, including serving pitfalls.
- `templates/daily-note.md` — reusable daily-note scaffold (Mongolian + English). Copy and adapt when creating daily notes.
