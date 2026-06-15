---
name: lead-nurture-newsletter
description: "Use when nurturing B2B leads with weekly AI/technology newsletters, tracked links, email engagement analytics, and lead scoring across Google Sheets/Odoo/website data."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [lead-nurture, newsletter, email, analytics, tracking, scoring, crm, odoo, google-sheets]
    related_skills: [google-workspace, odoo19-query, zangia-lead-generation]
---

# Lead Nurture Newsletter

## Overview

This skill designs and operates a lead-nurturing workflow for B2B leads. The goal is to send a weekly newsletter about AI, technology, and business updates, track engagement, score leads based on opens/clicks/replies/site visits, and optionally sync scores back to Google Sheets or Odoo CRM.

Use privacy-safe tracking. Avoid placing raw email addresses in URLs. Use per-contact IDs or signed tokens that map to leads in the database.

## When to Use

Use this when the user asks to:
- Send weekly newsletters to Zangia/Odoo/Google Sheet leads.
- Draft recurring AI/technology update emails.
- Track which leads opened or clicked newsletter links.
- Route clicks to the user's website while identifying campaign/contact source.
- Score leads based on engagement.
- Create analytics reports for email performance.

Do not use this to spam or bypass consent requirements. Ask for confirmation before sending any email or modifying CRM records.

## Recommended Architecture

### Minimum viable version

- **Lead source:** Google Sheet `Zangia Leads` or Odoo `crm.lead`.
- **Newsletter drafting:** Hermes generates weekly AI/technology newsletter draft.
- **Sending:** start with Gmail drafts/manual approval for small lists; use an email service provider for scale.
- **Tracking:** website redirect endpoint captures click events with a token.
- **Analytics:** Google Sheet or Odoo fields store last sent/open/click/score.

### Production version

Use an email platform/API such as Mailgun, SendGrid, Postmark, Mailchimp, Brevo, or Odoo Email Marketing/Marketing Automation. Gmail is not ideal for bulk newsletters because of sending limits, deliverability, unsubscribe handling, and tracking limitations.

## Data Model

### Leads table / sheet columns

- `lead_id`
- `company_name`
- `contact_name`
- `email`
- `phone`
- `source` such as `Zangia.mn`
- `source_url`
- `website`
- `status`
- `newsletter_opt_in`
- `last_sent_at`
- `last_opened_at`
- `last_clicked_at`
- `click_count`
- `open_count`
- `lead_score`
- `unsubscribe_token`

### Campaign table / sheet columns

- `campaign_id`
- `subject`
- `sent_at`
- `topic`
- `recipient_count`
- `delivered_count`
- `open_count`
- `click_count`
- `reply_count`
- `unsubscribe_count`

### Event table / sheet columns

- `event_id`
- `timestamp`
- `lead_id`
- `campaign_id`
- `event_type` (`sent`, `opened`, `clicked`, `replied`, `unsubscribed`, `bounced`)
- `url`
- `user_agent`
- `ip_hash` if needed, not raw IP unless necessary

## Tracking Design

### Click tracking

Rewrite newsletter links to a redirect URL on the user's website:

```text
https://yourdomain.mn/r?cid=<campaign_id>&lid=<lead_id>&t=<signed_token>&u=<encoded_destination>
```

Website behavior:
1. Verify signed token.
2. Record click event.
3. Update lead's `last_clicked_at`, `click_count`, and score.
4. Redirect to the real destination URL.

Do not expose raw email addresses in query params. Use a lead ID plus HMAC-signed token.

### Open tracking

A tracking pixel can be inserted:

```html
<img src="https://yourdomain.mn/o?cid=<campaign_id>&lid=<lead_id>&t=<signed_token>" width="1" height="1" style="display:none" />
```

Caveat: opens are unreliable because Apple Mail, Gmail image proxying, privacy protections, and blocked images distort open rates. Use clicks and replies as stronger buying signals.

## Lead Scoring Example

Base scoring:
- Email sent: `+1`
- Opened email: `+2` max once per campaign
- Clicked link: `+5` per unique campaign
- Multiple clicks: `+2` additional
- Replied: `+10`
- Visited pricing/contact page: `+8`
- Unsubscribed/bounced: set status `do_not_contact`, score `0`

Hot lead thresholds:
- `0-4`: cold
- `5-14`: warm
- `15+`: hot

## Weekly Workflow

1. Pull eligible leads from Google Sheets or Odoo.
2. Exclude invalid email, unsubscribed, bounced, or do-not-contact leads.
3. Research 3-5 AI/technology updates for the week.
4. Draft newsletter with short useful sections and one primary CTA to the user's website.
5. Generate tracked links per lead and campaign.
6. Create drafts or prepare send batch.
7. Ask user for approval before sending.
8. After sending, collect events and update analytics.
9. Send a weekly performance summary: sent, opens, clicks, hot leads, recommended follow-ups.

## Agentic Sales Follow-up Mode

When the user asks for Hermes to act like a salesperson that follows up with leads over time, treat it as an **AI Sales Follow-up Agent system**, not just a newsletter. Use a conservative, approval-first design unless the user explicitly approves automation rules.

Recommended components:
- `Leads` table/sheet: current lead state, score, status, latest touch timestamps, next follow-up date.
- `Activities` table/sheet: immutable log of every email, SMS, call, reply, meeting, website signup, enrollment, score change, and note.
- `Campaigns` table/sheet: message templates/campaign IDs and sent counts.
- `Rules` table/sheet or documented config: frequency caps, channel order, scoring, do-not-contact rules.
- Hermes cron jobs: one or two small runs per business day rather than constant polling.

Default safety rules for this user:
- Business hours: Asia/Ulaanbaatar, normally 09:00-18:00.
- One lead: max 1 touch/day and max 2 touches/week.
- Unanswered sequence: max 4 follow-ups, then pause/nurture instead of continuing.
- Always respect `do_not_contact`, unsubscribe, bounce, wrong number, or explicit “not interested”.
- SMS should be reserved for warm/hot leads or explicit consent; start with drafts/manual approval.
- Calls normally become reminders unless a call provider such as CallPro is integrated.
- Never send bulk email/SMS automatically in the first implementation; create Telegram approval summaries and Gmail/SMS drafts first.

Suggested scoring additions:
- Website signup: +5
- Academy enrollment / paid or committed course signup: +15
- Email present: +2
- Phone present: +2
- Email sent: +1
- SMS sent: +2
- Call attempted: +2
- Call answered/conversation: +5
- Reply: +8
- Meeting booked: +15
- Link click: +5
- Pricing/contact page visit: +8
- Unsubscribe/do-not-contact/bounce: score 0 and suppress future outreach

Cron pattern:
- Morning follow-up job: find `next_follow_up_at <= today`, prepare a capped batch of drafts/reminders, and send the user an approval list.
- Afternoon reply/hot-lead job: check Gmail/SMS/call events, update score/activity logs, and alert on hot leads.
- Weekly report: sent, replies, clicks, meetings, hot leads, recommended next actions.

## Scheduling with Hermes Cron

For weekly nurture workflows, use Hermes cron for drafting and reporting, not for unapproved bulk sending.

Recommended split:
- **Draft job:** weekly, researches AI/technology updates and sends the user a newsletter draft for approval.
- **Analytics job:** daily or weekly, summarizes opens/clicks/replies/site visits and identifies hot leads.
- **Send job:** only if the user has explicitly approved automated sending rules, recipient criteria, unsubscribe handling, and provider limits.

Cron prompts must be self-contained: include the lead source, timezone, approval rule, desired output, and safety constraints. Attach relevant skills such as `google-workspace`, `odoo19-query`, and this skill.

## Newsletter Content Rules

- Keep it concise and useful.
- Include one clear CTA to the user's website.
- Avoid exaggerated claims.
- Include unsubscribe or opt-out instructions.
- Personalize minimally: company name or industry if known.

## Industry AI Article Drafting

When the user asks for AI/technology news, industry examples, or use-case articles for lead nurturing/content marketing, prepare business-friendly Mongolian content from public/no-login sources by default.

Preferred outputs:
- Short daily article: 80–120 Mongolian words.
- Use-case article: ~250 Mongolian words.
- Include: title, industry, source link, how AI is used, what changed, how Mongolian companies can start, and an image prompt or generated image.
- Prioritize sectors relevant to the user's B2B leads: healthcare, education, mining, construction, retail/e-commerce, finance, HR/recruitment, manufacturing/logistics.
- Keep the article practical: avoid generic AI hype; anchor each piece in a concrete workflow such as patient follow-up, predictive maintenance, sales forecasting, construction reporting, fraud alerts, CV screening, or quality inspection.

See `references/industry-ai-article-workflow.md` for the source bank, article template, and pitfalls.

## Mass Email Provider Selection

When the user asks which mass email provider is cheapest/best for their lead list, use the comparison in `references/mass-email-providers-mongolia.md`.

Decision rule:
- **≤300 leads → Brevo** (free tier, 300/day, simple API)
- **300-5000 leads → Amazon SES** (cheapest at scale, ~₮40/1000 emails)
- **<100 leads, one-time → Gmail drafts** via google-workspace skill

Always explain pricing in Mongolian Tugrik (₮) when comparing. The user values cost transparency.

### Amazon SES Setup (pip-less environments)

In environments where `pip` / `pip3` is not available (common in Hermes servers), install `boto3` via `uv`:

```bash
uv pip install boto3
```

Then configure AWS credentials. If the user does not have AWS credentials ready, offer Brevo as a fallback (free tier covers up to 300 emails/day, no AWS account needed).

### Email Template Design

When the user asks you to design an email campaign for a specific industry (healthcare, education, etc.), use the pattern in `templates/healthcare-ai-seminar-email.html` as a reference (CTA URL is set to `agenticforceweb.vercel.app/seminar` as an example — confirm the actual landing page with the user before sending):

1. **Header**: Gradient background, campaign title in Mongolian, industry tagline
2. **Body**: Warm Mongolian greeting, problem statement + proposed solution
3. **Benefits section**: Numbered/grid of 3-4 concrete benefits with Mongolian labels
4. **CTA**: Bold button with a clear Mongolian action text (e.g. "ҮНЭГҮЙ БҮРТГҮҮЛЭХ"), linking to the user's signup/landing page
5. **About**: Brief company/organizer intro
6. **Footer**: Copyright + unsubscribe link

Always confirm the landing page URL with the user before hardcoding it. All email content must be in Mongolian unless the user specifies otherwise.

## Safety, Compliance, and Deliverability

- Use only leads with lawful basis/permission where required.
- Include opt-out/unsubscribe instructions.
- Do not send bulk campaigns from personal Gmail at scale.
- Use small batches and respect provider limits.
- Never send emails without explicit confirmation.
- Keep analytics transparent and privacy-safe.

## Verification Checklist

- [ ] Lead source has email addresses and opt-out status.
- [ ] Campaign has unique `campaign_id`.
- [ ] Links use signed tokens, not raw emails.
- [ ] Website endpoint records clicks and redirects correctly.
- [ ] Open tracking caveats are explained.
- [ ] User approves email content and recipients before sending.
- [ ] Analytics are written back to Google Sheets/Odoo.
