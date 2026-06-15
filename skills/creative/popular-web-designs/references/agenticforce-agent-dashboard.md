# AgenticForce agent dashboard pattern

Use this reference when the user asks for an AI-agent analytics dashboard similar to the provided dark AgenticForce screenshot.

## Layout

- Left sticky sidebar with AgenticForce logo, tagline, and all AI agents as nav items with colored icons and green live status dots.
- Main topbar with title `Ерөнхий хяналтын самбар`, date range chip, channel filter chip, notification chip, and team/account chip.
- KPI row: 4 cards for total completed tasks, success rate, hours saved, and estimated generated revenue.
- Middle row: agent performance horizontal bars + task-status donut chart.
- Wide activity chart: daily bars for tasks/successful tasks plus line for success rate.
- Lower cards: channel performance, lead score distribution, time saved by agent.
- Bottom cards: recent completed jobs and top content performance.
- Final insight strip with one concise AI recommendation and a `Бүрэн тайлан татах` button.

## Visual style

- Dark SaaS dashboard: near-black background `#05070a`, panels `#0b0f14` / `#0f151d`.
- Subtle translucent cards: `rgba(255,255,255,.02-.05)` with `1px solid rgba(255,255,255,.08)`.
- Gold AgenticForce accent `#f6a900`, green success `#22c55e`, purple/blue/cyan/pink chart accents.
- Rounded cards 14-16px, chips 10px, agent rows 12px.
- Use Inter for UI text and JetBrains Mono for numbers/timestamps.
- Prefer Mongolian UI labels for this user; keep metrics and agent names readable in English where they are product names.

## Default agent list

- Lead Prospector Agent
- Lead Enrichment Agent
- Research Intelligence Agent
- Blog Writer Agent
- Newsletter Agent
- Email Marketing Agent
- SMS Outreach Agent
- Lead Scoring Agent
- Agentic CRM Agent
- Social Media Research Agent
- Content Planner Agent
- Content Ideation Agent
- Visual Designer Agent
- Post Generator Agent
- Visual QA Agent
- Social Publishing Agent
- Performance Reporting Agent

## Data integration mapping

- Lead/prospect counts: Google Sheets lead DB, Odoo CRM, website signup webhooks.
- Email opens/clicks/replies: Email Marketing Agent / campaign provider.
- SMS sends/replies: CallPro/SMS Outreach Agent.
- Website visits/article reads: web analytics or app events.
- CRM notes/status/scores: Odoo 19 / Agentic CRM Agent.
- Social/content performance: platform analytics and Social Publishing Agent.

## Build guidance

For a static mockup, generated HTML/CSS with inline sample data is fine. For the Vercel app, implement as a component/page with mock data first, then swap to API-backed metrics. Keep the left agent list and KPI/cards stable so the dashboard remains familiar while data sources are connected incrementally.
