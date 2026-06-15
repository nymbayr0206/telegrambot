# Real-Person AI Story Sources

For finding real-life stories of people using AI (vibe coding, AI agents, etc.) and how it changed their lives. Suitable for `aiglobal_success_story_v1` carousel content.

## Verified RSS Sources

| Source | URL | Format | Reliability | Notes |
|--------|-----|--------|-------------|-------|
| Hacker News Show HN | `https://hnrss.org/show` | RSS 2.0 | ✅ Excellent | People share products they built — always a human story behind each |
| Substack (AI, Max) | `https://maxturazzini.substack.com/feed` | RSS 2.0 | ✅ Good | "Vibe Coding Real Life Stories" series |
| Indie Hackers | `https://www.indiehackers.com/rss.xml` | RSS (cookie) | ⚠️ Cookie needed | Indie founders building with AI |

## Best-Found Example Stories (June 5, 2026)

### Alex Finn — $300k ARR, Zero Employees
- **Source:** Substack — "5 Builders Who Turned Vibe Coding Into Serious Money"
- **URL:** `https://iamjohnellison.substack.com/p/the-vibe-coding-wave-is-here-5-builders`
- **Story:** Non-technical founder. Used Claude Code to build Creator Buddy (AI X content tool). 10 months from zero to $300k ARR. 90% margins. 0 employees.
- **4-Slide Arc:** Before (struggling with content) → Solution (AI tool) → Result ($300k) → CTA

### Paulius — $9k MRR AI Agent Platform
- **Source:** Same Substack article
- **Story:** Started without knowing git. Built Vibed Agents. $9k MRR, 30k+ users.
- **Arc:** No coding skills → built first app → scaled to platform → monetized

### Sherry Jiang — $275k in 3 Hours
- **Source:** Same Substack article  
- **Story:** Ex-Google engineer. Built Peek.money prototype in 3 hours. Secured $275k accelerator funding.
- **Arc:** Lightning-fast prototyping → investor validation → teaching others

### Modest Mitkus — $23k MRR, Zero Coding Experience
- **Source:** Same Substack article
- **Story:** Complete non-coder. Built SaaS from scratch. Hit $23k MRR in one month.
- **Arc:** Zero coding → learned AI → built SaaS → explosive growth

## How to Automate (Twice a Week)

```yaml
# Cron job template
schedule: "Mon 09:00, Thu 09:00"
prompt: >
  Fetch latest from hnrss.org/show and substack vibe coding feeds.
  Find a real person story about using AI that changed their life.
  Generate a 4-slide storyline in Mongolian with BEFORE/AFTER/CTA structure.
  Present to user for approval before generating images.
```

## Key Insight

The most compelling stories follow this pattern:
1. **BEFORE** — Person struggled with something (no coding skills, content creation, business ops)
2. **TURNING POINT** — Discovered AI tools (Claude Code, Cursor, ChatGPT)
3. **AFTER** — Built something, made money, changed career
4. **CTA** — "You can do this too" → Learn AI at AI Global
