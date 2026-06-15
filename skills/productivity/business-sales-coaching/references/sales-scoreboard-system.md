# Sales Scoreboard System — Reference

## Overview

This reference documents a complete daily sales scoreboard system set up for a Mongolian user (Battushig) who runs AgenticForce (AI-agent automation) and social media content businesses. The system uses Google Sheets for tracking, cron jobs for automation, and Brevo for mass email campaigns.

## Google Sheet Schema

### Sheet: "Daily Scoreboard"

| Col | Header | Type | Description |
|-----|--------|------|-------------|
| A | Date | YYYY-MM-DD | Auto-generated |
| B | Day | e.g. "Monday" | Auto-generated |
| C | Week | e.g. "Week 22" | ISO week number |
| D | Q1-New Leads | integer | New contacts added today |
| E | Q2-Calls/Messages | integer | Outreach activity |
| F | Q3-Conversations | integer | People who replied/engaged |
| G | Q4-Appointments Booked | integer | Calendar-dated meetings |
| H | Q5-Follow-ups Done | integer | Follow-ups completed |
| I | Q6-Proposals/Demos | integer | Proposals or demos sent |
| J | Q7-New Clients | integer | Clients signed today |
| K | Q8-Referrals Requested | integer | Referrals asked for |
| L | Q9-Revenue (₮) | integer | Revenue in MNT |
| M | Daily Score | string | e.g. "12/18 (67%)" |
| N | Response Status | string | "Answered ✅" or "Missed ❌" |
| O | Coach Notes | text | Free text notes |

### Sheet: "Weekly Reports"

| Col | Header | Description |
|-----|--------|-------------|
| A | Week # | Week number |
| B | Start Date | Monday date |
| C | End Date | Sunday date |
| D | Total Leads | Sum of Q1 for week |
| E | Total Calls | Sum of Q2 |
| F | Total Conversations | Sum of Q3 |
| G | Total Appointments | Sum of Q4 |
| H | Total Follow-ups | Sum of Q5 |
| I | Total Proposals | Sum of Q6 |
| J | Total Clients | Sum of Q7 |
| K | Total Referrals | Sum of Q8 |
| L | Total Revenue | Sum of Q9 |
| M | Avg Daily Score | Average of daily score % |
| N | Target Met? | Yes/No/Partial |
| O | Coach Summary | Tough feedback summary |

## Google Sheet ID

```
1vjrtCmkoQlCV7CdL44ucuh0MbT_UFU2MxBel4km9RnQ
```

Sheet URL: https://docs.google.com/spreadsheets/d/1vjrtCmkoQlCV7CdL44ucuh0MbT_UFU2MxBel4km9RnQ/edit

## Scoring Algorithm

Each of the 9 questions is scored:
- **0 points**: Nothing done (0 for that metric)
- **1 point**: Some activity but below target (e.g. 3 leads when target is 20)
- **2 points**: Met or exceeded target

Max = 18 points.

Grade thresholds:
- **A** (80-100%): 15-18 points — Exceptional
- **B** (65-79%): 12-14 points — Good
- **C** (50-64%): 9-11 points — Average
- **D** (30-49%): 5-8 points — Poor
- **F** (0-29%): 0-4 points — Failure

## Daily Targets

| Metric | Daily Target | Weekly Target |
|--------|-------------|---------------|
| New Leads | 20+ | 100+ |
| Calls/Messages | 10+ | 50+ |
| Conversations | 3+ | 15+ |
| Appointments Booked | 1+ | 5+ |
| Follow-ups Done | 5+ | 25+ |
| Proposals/Demos | 1+ | 5+ |
| New Clients | — | 1+ |
| Referrals Requested | — | 3+ |
| Revenue | — | consistent growth |

### Cron Job Configuration

### Job 1: Daily Sales Scoreboard (daily at 22:00 Ulaanbaatar = 14:00 UTC)

```json
{
  "action": "create",
  "name": "Daily Sales Scoreboard",
  "schedule": "0 14 * * *",
  "deliver": "origin",
  "enabled_toolsets": ["terminal", "file", "search"],
  "workdir": "/opt/data/email-campaign",
  "skills": ["business-sales-coaching"],
  "repeat": "forever"
}
```

### Job 2: Weekly Sales Review (Sunday at 21:00 Ulaanbaatar = 13:00 UTC)

```json
{
  "action": "create",
  "name": "Weekly Sales Review + Tough Coaching",
  "schedule": "0 13 * * 0",
  "deliver": "origin",
  "enabled_toolsets": ["terminal", "file", "search"],
  "workdir": "/opt/data/email-campaign",
  "skills": ["business-sales-coaching"],
  "repeat": "forever"
}
```

### Cron Delivery to Telegram Group Topics

When delivering cron responses to a **Telegram group with Topics**, use the `deliver` field with the format `telegram:chat_id:thread_id`:

```json
{
  "deliver": "telegram:-1001234567890:12345"
}
```

The `chat_id` is the Telegram group chat ID (a negative number; supergroups have IDs starting with `-100`) and the `thread_id` is the topic's message thread ID (visible in gateway logs when a message is sent to a topic).

**Pitfalls:**
- Only **supergroups** support Topics — regular groups do not. The group must first be converted to a supergroup (Group Management → Convert to Supergroup/Upgrade Group), then Topics enabled. A regular group has a short negative ID like `-5102303508`; a supergroup has a `-100` prefix like `-1001234567890`.
- The bot must be a **group admin** to read messages in a topics-enabled supergroup; otherwise the `can_send_messages: false` permission blocks delivery.
- Use `send_message(action='list')` to discover available chat IDs after the bot receives its first message from the group.
- When the bot first joins a group, its username may differ from the commonly known one. Always check `config.yaml` → `platforms.telegram.token` → use `getMe` on the Telegram API to find the actual bot username before telling the user to search for it.

## record_daily.py Usage

Script location: `/opt/data/email-campaign/record_daily.py`

```bash
# Record today's answers
python3 record_daily.py \
  --leads 15 \
  --calls 8 \
  --conversations 3 \
  --appointments 1 \
  --followups 5 \
  --proposals 1 \
  --clients 0 \
  --referrals 2 \
  --revenue 500000 \
  --notes "Good day, need more leads"

# Check if today has a row
python3 record_daily.py --check
```

The script:
1. Determines today's date in Mongolia time (UTC+8)
2. Checks if a row already exists for today
3. Creates a new row if none exists
4. Writes data to columns D-O
5. Calculates and returns the daily score and grade

## Tough Coach Guidelines

When the user has explicitly requested tough coaching:
- Use direct, confrontational language in Mongolian
- Grade their performance A-F
- Call out specific weaknesses
- Never sugar-coat
- Always end with a challenge: one thing to fix next

### Sample Tough Messages

**Bad week (all zeros / all missed):**
> "Чи энэ долоо хоногт юу ч хийгээгүй. Би чамайг илүү чадвартай гэдэгт итгэж байна. Ирэх долоо хоногт өөрчлөлт хийхгүй бол бидний коучингийн харилцаа утгагүй."

**Good but not great:**
> "Сайн, гэхдээ хангалтгүй. Дараа долоо хоногт 2 дахин их хий."

**Weak follow-up specifically:**
> "Таны сул тал бол follow-up. 5 хоногт ердөө 3 follow-up хийсэн. Энэ нь ичмээр."

## Mass Email via Brevo

For lead nurture campaigns (healthcare, sales, security leads):
- Brevo (brevo.com) chosen over Amazon SES for ease of setup and free tier (300 emails/day)
- Requires: API v3 key from Brevo dashboard (Settings > SMTP & API > Create API key)
- Requires: verified sender email in Brevo (Sender Identity > Add Domain/Email)
- 112 healthcare leads have emails ready for first campaign

Email template stored at: `/opt/data/email-campaign/healthcare-ai-seminar-email.html`

Topic: "AI ЖИШХЭН СЕМИНАР — Хиймэл Оюун Ухаан Эрүүл Мэндийн Салбарт"
CTA: Sign up for free online seminar at agenticforceweb.vercel.app/seminar
Language: Full Mongolian
