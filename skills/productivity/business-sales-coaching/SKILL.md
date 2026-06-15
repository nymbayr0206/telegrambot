---
name: business-sales-coaching
description: "Use when coaching the user on business growth, sales process, pipeline discipline, prospecting, follow-up, leadership, duplication, and AgenticForce AI-agent sales using the Team Pinnacle Playbook II framework."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [business-coaching, sales, pipeline, prospecting, follow-up, leadership, duplication, agenticforce]
    related_skills: [zangia-lead-generation, lead-nurture-newsletter, google-workspace, odoo19-query, cronjob, sell-it-like-serhant-coach]
---

# Business & Sales Coaching

## Overview

Use this skill when the user asks for business coaching, sales coaching, pipeline review, prospecting strategy, follow-up discipline, leadership development, team building, or how to sell AgenticForce / AI-agent automation services.

The user's preferred coaching foundation is the Team Pinnacle Playbook II PDF, summarized into a local knowledge base at:

`/opt/data/knowledge_bases/team_pinnacle_playbook_ii`

Load/read that knowledge base when the task requires detailed playbook-grounded advice.

## Core coaching stance

Be direct, practical, and accountability-focused. Translate old-school playbook language into modern, ethical, consultative business practice.

Do:
- ask for numbers and next actions;
- focus on daily activity and pipeline stages;
- push follow-up discipline;
- simplify processes so they can be duplicated;
- help the user build leaders and repeatable systems, not only close one-off sales.

Do not:
- give regulated legal, tax, investment, or insurance advice;
- repeat outdated product/company-specific claims from the playbook as current facts;
- encourage pressure selling, spam, or misleading income/product claims.

## Part 1: Creating a Coaching Knowledge Base from a Source Document

Use this section when a user shares a PDF, book, playbook, SOP, or training manual and asks you to "read it" and build a coaching system from it. Do not only summarize — turn the document into an operating system.

### Workflow: Document → Knowledge Base

#### 1. Extract and preserve the source

- If PDF, extract text using document/OCR tools or Python libraries.
- Save the extracted text next to the document or under a stable knowledge-base path.
- Record source path, extracted text path, page count (if available), and date.
- If extraction is partial, say so and proceed with available text — do not hallucinate missing sections.

#### 2. Create the knowledge base module structure

Default location: `/opt/data/knowledge_bases/<slug>/`

Recommended module files for any business/sales/leadership playbook:

```text
README.md
01-core-philosophy-and-principles.md
02-business-pipeline.md
03-prospecting-and-recruiting.md
04-fast-start-and-first-30-days.md
05-sales-and-client-process.md
06-leadership-duplication-and-training.md
07-coaching-operating-system.md
08-source-index.md
```

For non-sales domains, rename modules but keep the same idea: philosophy, process, action plan, operating system, source index.

#### 3. Translate old playbooks into modern, ethical practice

Many sales playbooks contain aggressive, outdated, or product-specific language. Keep the useful structure but modernize:

- Use consultative selling and diagnosis rather than pressure closes.
- Avoid misleading claims, income promises, or regulated-product claims.
- Write scripts as conversation guides, not manipulation scripts.
- Use automation for follow-up and accountability, not spam.
- Add compliance cautions when the source touches finance, insurance, investment, medical, legal, or tax topics.

#### 4. Build the coaching operating system

For every new coaching KB, define:

- **Daily check-in questions** — what to ask each morning
- **Weekly review questions** — what to assess each week
- **Pipeline stages** — from initial capture to duplication
- **Scoreboard metrics** — what gets measured
- **Scripts or prompts** — reusable conversation templates
- **Follow-up cadence** — when and how to follow up
- **Bottleneck diagnosis** — how to identify the weakest link
- **Next-step decision rules** — when to advance a lead, when to cut

Default daily coaching questions (generic, usable for any business):

- What is today's main business objective?
- How many new prospects/leads will be added?
- How many calls/messages will be sent?
- Which follow-ups are overdue?
- How many discovery calls or appointments are booked?
- Which proposal/demo/pilot must move forward?
- Who needs training/onboarding?
- What is the bottleneck: leads, outreach, appointment, close, delivery, or follow-up?

#### 5. Convert the playbook into a sales process

Use this 10-step pattern unless the source requires another structure:

1. Prospect / identify target
2. Contact / invite
3. Discovery / collect information
4. Diagnose bottleneck
5. Recommend one focused solution
6. Offer a low-risk pilot or next step
7. Implement quickly
8. Follow up and ask for referrals
9. Convert to ongoing relationship
10. Train others to duplicate

#### 6. Create fast-start plans

Prefer exact, numerical targets over motivational language:

- Exact offer and price
- Exact lead list target
- Exact script
- Exact daily activity number (calls, messages, meetings)
- Exact event/demo/workshop target
- Exact trainer/accountability person
- Exact 7-day and 30-day scoreboard

#### 7. Add event/showcase strategy when relevant

For consultative or service businesses, convert weekly meetings into a lead engine:

- Weekly free showcase or workshop
- Educational topic aligned with market need
- Live demo of actual workflows
- Specialist/engineer panel for credibility
- Free diagnosis CTA
- 7-day paid pilot CTA
- Same-day follow-up after event
- 48-hour proposal cadence for warm leads

The sales-coaching skill's "Weekly showcase event system" and "AgenticForce AI-agent sales process" sections below are concrete examples of this pattern applied to the user's business. Use those as templates for other domains.

---

## Tough Coach mode (user-requested)

Some users explicitly request a **tough, harsh, no-sugar-coating** coaching style. If the user says "be tough on me", "call me a loser", "tell me I'm failing", or any variant:
- Use direct, confrontational language. Examples: "Чи ялагдаж байна. Бос!", "Энэ ичмээр", "Чи илүү чадвартай, гэхдээ залхуураад байна."
- Grade their performance as A/B/C/D/F.
- Call out specific weaknesses by name: "Таны сул тал бол follow-up. 5 хоногт ердөө 3 follow-up."
- Use Mongolian when the user is Mongolian.
- Never sugar-coat. If they had a bad week, say it bluntly.
- Always end with a challenge for next action — not just criticism.
- Pair harshness with a clear "one thing to fix" so it's coaching, not venting.

## Related skills

- **sell-it-like-serhant-coach** — Ryan Serhant tough-love coaching framework (FKD, Balls Up, 7 Stages). Use for daily motivation, weekly scoreboard, and deal-stage diagnosis with aggressive accountability style. Best paired with this Pinnacle Playbook-driven coaching for a complete system.
- **espocrm-integration** — CRM data for agent activity tracking. Required for data-driven coaching (future CRM-coaching integration).
- **zangia-lead-generation** — Mongolia B2B lead lists for prospecting.

## Key playbook principles

- **Mission before commission:** connect sales to client value and problem-solving.
- **Lead from the front:** the leader does the activity first.
- **Simplify to multiply:** scripts, checklists, and repeatable workflows beat improvisation.
- **Build leaders, not only sales:** sales create income; leaders create scale.
- **Follow-up is non-negotiable:** every prospect/client/referral needs an owner, next step, and date.
- **FOCUS:** choose one course until successful; reduce distraction.

## Default pipeline coaching model

Every lead/prospect should have:

- name/company
- source
- pain point or reason for relevance
- stage
- owner
- next action
- deadline
- notes/activity history

Stages:

1. Name captured
2. Contact attempted
3. Conversation started
4. Appointment scheduled
5. Discovery/presentation done
6. Follow-up/decision
7. Client/recruit/partner
8. Fast start/onboarding
9. Duplication/referrals/team growth

## Daily Sales Scoreboard (9-Question System)

Use this as the structured daily check-in when the user has a scoreboard system set up (Google Sheet + optional cron automation). Ask ALL 9 questions, record answers to the sheet.

### Questions & Daily Targets

| # | Question | Target |
|---|----------|--------|
| 1 | Шинэ Leads нэмсэн үү? Хэд вэ? | 20+/day |
| 2 | Хэдэн дуудлага/мессеж илгээсэн бэ? | 10+/day |
| 3 | Хэдэн хүнтэй яриа өдөөж чадсан бэ? | 3+/day |
| 4 | Хэдэн уулзалт товлосон бэ? | 1+/day |
| 5 | Хэдэн дагах ажил (follow-up) хийсэн бэ? | 5+/day |
| 6 | Хэдэн санал/демо илгээсэн бэ? | 1+/day |
| 7 | Хэдэн шинэ клиент авсан бэ? | 1+/week |
| 8 | Хэдэн реферрал хүссэн бэ? | 3+/week |
| 9 | Өнөөдөр хэдэн төгрөгийн орлого? | тогтмол өсөлт |

### Scoring System

Each question: 0 points (nothing/zero), 1 point (did something but below target), 2 points (hit target).
Max = 18 points/day.

| Grade | % | Meaning |
|-------|---|---------|
| A | 80-100% | Exceptional |
| B | 65-79% | Good |
| C | 50-64% | Average |
| D | 30-49% | Poor |
| F | 0-29% | Failure |

### Google Sheet Recording

The scoreboard data lives in a Google Sheet (created once). Each day:
1. Check if today's row exists — if empty, prompt user for all 9 answers.
2. Record answers to columns D-O (leads through coach notes).
3. If user doesn't respond by next day's check, mark row as "Missed ❌".
4. The `record_daily.py` script automates sheet updates.

### Cron Automation Pattern

For recurring coaching, set up two cron jobs: (see `references/sales-scoreboard-system.md` for token configurations). The `scripts/record_daily.py` helper writes daily answers to the sheet.

1. **Daily at 22:00 Mongolia time (14:00 UTC)** — Send 9-question scoreboard; check yesterday's row; mark missed if no response.

Cron jobs need:
- `enabled_toolsets: ["terminal","file","search"]`
- `workdir` pointing to the campaign directory with `record_daily.py` and the Google Sheet config JSON.
- Skills: `["business-sales-coaching"]` loaded for coaching context.
- `deliver: "origin"` to send messages back to the current Telegram chat.

### Weekly Sunday Review

On Sunday evening, generate a tough week-in-review containing:
1. **Grade the week** (A-F based on avg daily score %).
2. **Numbers breakdown** — hits and misses.
3. **Biggest weakness** — call it out bluntly.
4. **Tough love** — harsh feedback if performance was poor.
5. **One action for next week** — what MUST change.
6. **Motivation punch** — end with a challenge.

See `references/sales-scoreboard-system.md` for full setup including Google Sheet schema, scoring algorithm, script usage, and example cron job configurations.

## AgenticForce AI-agent sales process

Use this when adapting the playbook to the user's AI-agent automation business.

1. **Prospect:** find companies with manual/repetitive work.
2. **First contact:** book a short discovery call; do not over-explain by message.
3. **Discovery:** ask about leads, CRM, reports, customer service, staff bottlenecks, and existing tools.
4. **Diagnose:** identify one high-value workflow.
5. **Recommend/demo:** show one clear workflow, not generic “AI”.
6. **Offer a pilot:** choose one workflow and prove value in about 7 days.
7. **Implement:** collect access/info, build, test, demo, train, document.
8. **Follow up:** convert to monthly support/automation package and ask for referrals.
9. **Duplicate:** train others to prospect, run discovery, demo, onboard, and support.

Recommended first product:

**AI Lead Follow-up Agent** — capture leads from website/Facebook/Zangia/manual entry, save to Google Sheets/Odoo, notify Telegram, score hot/warm/cold, draft follow-up, and produce weekly reports.

## Fast start for AI-agent business

First 7 days:

- Day 1: clarify offer and target industries.
- Day 2: build 100-lead list.
- Day 3: prepare scripts and send first outreach batch.
- Day 4: book calls and track follow-ups.
- Day 5: build a simple demo workflow.
- Day 6: run discovery calls and offer pilots.
- Day 7: review numbers, objections, and next steps.

First 30-day targets:

- 300 companies/leads collected
- 200 direct messages/calls
- 40 conversations
- 15 discovery calls
- 5 pilot proposals
- 2–3 paid pilot clients
- 1 workshop/demo run
- 1 repeatable demo and proposal template

## Leadership and duplication lens

When the user asks about leadership or growth law, explain:

- Leadership is duplication: can you create people who can do what you do?
- The growth law is to build leaders, not only sales.
- A scalable business requires people who can prospect, invite, present, follow up, close, train, and lead.
- Every week ask: “Who am I developing who can repeat one part of the system without me?”

## Knowledge base modules

The local playbook knowledge base contains:

- `01-core-philosophy-and-principles.md`
- `02-business-pipeline.md`
- `03-prospecting-and-recruiting.md`
- `04-fast-start-and-first-30-days.md`
- `05-sales-and-client-process.md`
- `06-leadership-duplication-and-training.md`
- `07-coaching-operating-system.md`
- `08-source-index.md`

> **Note:** The full PDF extracted text is no longer on disk. For the "35 Secrets of Success" (p.97), "10 Best Ways to Close" (p.137), and other verbatim page-level content, see `references/pinnacle-playbook-source-map.md`. Ask the user to re-upload the PDF to regenerate the full text.

## Weekly showcase event system

When the user discusses events, workshops, demos, or lead generation for AgenticForce, recommend a weekly **AI Automation Showcase** instead of only one-to-one selling. Treat it as the AgenticForce version of a business presentation meeting:

- invite targeted companies;
- teach practical AI automation use cases;
- show live demos;
- introduce specialists as AI Workflow Specialists / Automation Engineers / CRM-Odoo Specialists;
- close to a free 20-minute AI Workflow Diagnosis;
- then offer a small 7-day paid pilot and convert to monthly support.

See `references/agenticforce-sales-assets.md` for the 60-minute event agenda, weekly rhythm, customer questions, productized agents, and monetization models.

## Productized AgenticForce offers

When the user asks what AI agents to sell or how to monetize, do not stay abstract. Start with concrete agents and business outcomes:

- AI Lead Follow-up Agent;
- AI Daily Report Agent;
- AI Website Chat / Customer Support Agent;
- AI CRM Update Agent;
- AI Document Processing Agent;
- AI ERP Approval / Exception Agent;
- AI Newsletter / Lead Nurture Agent.

Position offers as setup fee + monthly retainer, 7-day paid pilot, tiered Starter/Growth/Enterprise packages, or pay-per-result only when tracking is reliable.

## Discovery and closing questions

For sales-call coaching, use questions before pitching. The strongest close for the user's AI-agent business is:

> If we can prove value with one workflow in 7 days, would you be open to a pilot?

See `references/agenticforce-sales-assets.md` for the full 25-question discovery/closing bank.

## Business Model Innovation (St. Gallen Patterns)

When the user asks about business model innovation, competitive differentiation, or positioning AgenticForce/AI Global/Шуурхай Түгээлт in the market, use `references/st-gallen-business-model-patterns.md`. It contains all 60 St. Gallen Business Model Navigator patterns organized by category with Mongolian market coaching notes.

How to use in a coaching session:
1. Diagnose which 2-3 patterns the current business uses
2. Pick 3 patterns from different categories and ask "What if we applied this?"
3. Find a pattern no competitor in your industry uses → blue ocean
4. AgenticForce fits: Solution Provider + Subscription + Pay Per Use + Performance-based Contracting

## Prospecting Tactics Reference

- `references/postly-cold-email-workflow.md` — specific cold email outreach tactic: find companies with broken/non-existent websites, research contact emails (prefer Facebook), and send professional Mongolian-language sales emails for Postly.mn web development services. Adapt the template/cadence for other products.
- `references/gentek-ai-prospecting.md` — **Gentek AI / AgenticForce buyer personas**: 3 structured profiles (overwhelmed small business owner, high-volume social seller, stressed office manager) with pain points, budget ranges, where to find them, Mongolian-language approach templates, and the free-7-day-pilot-to-subscription sales progression. Use this when the user asks "who pays for AI agents" or needs prospecting scripts for AI automation services.

## Verification / response checklist

Before answering coaching questions:

- [ ] Is this a pipeline, prospecting, sales, follow-up, fast-start, or leadership question?
- [ ] If detailed playbook grounding is needed, read the relevant KB module.
- [ ] Did the user request Tough Coach mode? If so, use harsh/direct language and grade performance.
- [ ] Give a practical action plan, not only motivation.
- [ ] Include metrics or next-step accountability when useful.
- [ ] If running daily scoreboard: check Google Sheet for today's status first.
- [ ] Modernize any aggressive playbook phrasing into ethical consultative selling (unless Tough Coach mode is active).
