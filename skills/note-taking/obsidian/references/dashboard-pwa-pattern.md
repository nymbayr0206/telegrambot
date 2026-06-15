# Obsidian Dashboard & PWA Web Dashboard Patterns

When the user requests a "dashboard" for their notes / business overview:

## Option A: Dashboard Note in Obsidian (Preferred)

Create a `Dashboard.md` note with:

### Structure

```markdown
# 📊 Dashboard
*Last updated: YYYY-MM-DD*

---

## 🎯 Өнөөдөр
- [ ] Task 1
- [ ] Task 2

---

## 🔥 Идэвхтэй төслүүд
| Төсөл | Статус | Холбоос |
|-------|--------|---------|
| Project Name | 🟡 In Progress | `[[Project Note]]` |

---

## 📋 Quick Links
- `[[Todo-List]]` — Tasks
- `[[Note Name]]` — Description

---

## 📊 Энэ долоо хоног
### Lead
- Key metrics

### Санхүү
- Income/expense summary
```

### Best practices
- Use `[[wikilinks]]` to link to other notes in the vault
- Use checkbox lists `- [ ]` for today's tasks
- Use markdown tables for project status
- Keep it short — one screen, top-down: Today → Projects → Metrics → Quick Links
- Update the date manually each time the dashboard is refreshed
- Store at `Dashboard.md` (vault root) for quick access

## Option B: HTML Web Dashboard (When user asks for PWA)

Create an HTML file + PWA manifest in a `dashboard/` subfolder under the vault:

```
Obsidian Vault/
├── dashboard/
│   ├── index.html    # Dashboard HTML with inline CSS
│   ├── manifest.json  # PWA manifest for "Add to Home Screen"
│   └── sw.js          # Service worker (minimal)
```

### PWA manifest
```json
{
  "name": "Dashboard Name",
  "short_name": "Short Name",
  "display": "standalone",
  "background_color": "#0f0f23",
  "theme_color": "#1a1a2e",
  "icons": [{"src": "data:image/svg+xml,...", "sizes": "192x192", "type": "image/svg+xml"}]
}
```

### Serving options
1. **Python HTTP server** (for local access): `python3 -m http.server PORT --bind 0.0.0.0 -d "path/to/dashboard"`
2. **File URL** (no server): Open index.html directly in browser (no PWA support, no dynamic data)
3. **External hosting** (GitHub Pages, Vercel, etc.) if the server has public access

### Limitations
- PWA requires HTTPS or localhost — HTTP pages won't install as standalone apps
- Server firewall may block external port access. If `curl http://PUBLIC_IP:PORT` returns HTTP 000, the port is firewalled
- If port 80 is open but redirects to HTTPS and 443 is closed, the PWA can't be served externally
- Best alternative when serving fails: give the user the raw HTML file via MEDIA: tag in Telegram

## Source of this pattern

Created during a session where the user wanted:
- An Obsidian dashboard for projects/tasks/leads/finance
- A PWA-style mini app accessible from phone
- The server had ports 8899/8080/80 blocked or redirecting, so the HTML file was delivered directly via Telegram
