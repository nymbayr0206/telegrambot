# Goal Deadline Accountability Tracking

Combine a Google Calendar all-day event with a Hermes cron job to create daily accountability reminders for personal savings/earnings goals.

## Pattern

1. **Create an all-day Calendar event** on the target date with the goal written in the description
2. **Set popup reminders** (1 day before + day-of)
3. **Create a daily cron job** that counts down and asks "Did you earn/save toward this goal?"

## Step 1: All-Day Calendar Event with Goal

All-day events use `date` (not `dateTime`). The end date is exclusive (next day).

```python
import json, sys
sys.path.insert(0, '/opt/data/skills/productivity/google-workspace/scripts')
from google_api import build_service

service = build_service('calendar', 'v3')

created = service.events().insert(calendarId='primary', body={
    'summary': '🎯 Event Name — Goal Description',
    'description': 'GOAL: At least 1M M&T saved/earned\nDaily question: Did you make money? Did you save?',
    'start': {'date': '2026-07-04', 'timeZone': 'Asia/Ulaanbaatar'},
    'end':   {'date': '2026-07-05', 'timeZone': 'Asia/Ulaanbaatar'},
}).execute()

event_id = created['id']
```

### ⚠️ Pitfall: parameter name is `eventId`, not `event_id`

The Google Python API client uses `eventId` (camelCase) as the keyword argument to `events().patch()`, even though most other parameters use `snake_case`:

```python
# CORRECT:
patched = service.events().patch(
    calendarId='primary', eventId=event_id,  # eventId, NOT event_id
    body={'reminders': {'useDefault': False, 'overrides': [...]}}
).execute()

# WRONG — TypeError: Got an unexpected keyword argument event_id:
patched = service.events().patch(
    calendarId='primary', event_id=event_id, ...  # TypeError
).execute()
```

### Set Popup Reminders

```python
patched = service.events().patch(
    calendarId='primary', eventId=event_id,
    body={
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 1440},  # 1 day before
                {'method': 'popup', 'minutes': 0}       # day-of (midnight local)
            ]
        }
    }
).execute()
```

## Step 2: Daily Accountability Cron Job

Create a cron job that runs at the user's morning local time. The prompt must be self-contained (cron runs in a fresh session with no conversation context).

### Cron Prompt Template

```
You are a personal accountability reminder. Today is the current date.

The user has a goal deadline:

Event: {Event name}
Date: {target date}
Goal: {specific goal, e.g. "at least 1 million M&T"}

Your job is to send a daily morning reminder that:
1. States how many days remain until the target date
2. Reminds them of the goal
3. Asks directly: "Did you make money yesterday?" and "Did you save for this?"
4. Asks them to quickly reply with current progress

Make the tone direct and motivating — this is a personal project/goal.
If fewer than 7 days remain, make it more urgent.
If the target date has passed, say the event has passed and stop.

Do NOT use any tools — just output the reminder message directly as your final answer.
```

### Cron Schedule

For the user's Asia/Ulaanbaatar (UTC+8) morning at 08:00:

```
Schedule: "0 0 * * *"     # 00:00 UTC = 08:00 ULAT
```

## Full Workflow Example

1. Create Calendar event (all-day, July 4, with 1M M&T goal)
2. Patch popup reminders (1 day before + day-of)
3. Create cron job: `00:00 UTC daily` with the accountability prompt above
4. Cron auto-delivers to the user's chat every morning until the deadline passes

## When to Use This Pattern

- Savings goals tied to a specific date/event
- Business revenue targets before a trip or purchase
- Any personal deadline where daily verbal accountability helps
- "Put skin in the game" reminders for the user's own projects
