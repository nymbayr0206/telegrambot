---
name: hermes-visual-agent-system
description: Use when developing, reviewing, or documenting Hermes project visual agent workflows, Mongolian UI pages, visual QA, project process docs, decisions, and completed-work tracking.
---

# Hermes Visual Agent System

## Workflow

1. Inspect the existing Hermes app structure before editing.
2. Keep visible UI copy in Mongolian when the user asks for Mongolian UI.
3. Prefer the existing `web` app patterns: Vite, React, TypeScript, lucide icons, dashboard cards, page header context, and sidebar routes.
4. Track project process updates in `docs/work-log.md`, decisions in `docs/decisions.md`, and visual review notes in `docs/visual-qa.md`.
5. Validate with `npm run build` from `web/` after UI changes.

## Visual Agents

- Visual Designer Agent: layout, hierarchy, visual direction, brand consistency.
- Frontend Builder Agent: route, component, responsive implementation.
- Visual QA Agent: desktop/mobile review, overlap checks, readable text, screenshot-backed findings.
- Project Memory Agent: decisions, completed work, next actions, blockers.

## UI Standards

- Build operational dashboard screens, not landing pages.
- Keep cards for repeated items, QA lists, and framed tool panels.
- Use lucide icons for commands and role markers.
- Avoid oversized hero typography inside compact dashboard surfaces.
- Ensure Mongolian text can wrap without breaking button, badge, card, or sidebar layout.

## Required Artifacts

When creating or changing visual workflow features, update the relevant files:

- `docs/brief.md`
- `docs/work-log.md`
- `docs/decisions.md`
- `docs/visual-qa.md`
