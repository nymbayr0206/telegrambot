# Calendar: Create Event + Popup Reminders

The `calendar create` subcommand does **not** support inline reminders. Use this two-step pattern: create the event (capture the ID from the JSON output), then patch reminders onto it.

## One-Shot Flow (Recommended)

Use a single Python script that creates the event with reminders atomically:

```python
import json, sys
sys.path.insert(0, '/opt/data/skills/productivity/google-workspace/scripts')
from google_api import build_service

service = build_service('calendar', 'v3')

# Create event first
created = service.events().insert(calendarId='primary', body={
    'summary': 'Therapy session',
    'start': {'dateTime': '2026-06-02T09:00:00', 'timeZone': 'Asia/Ulaanbaatar'},
    'end':   {'dateTime': '2026-06-02T09:30:00', 'timeZone': 'Asia/Ulaanbaatar'},
}).execute()
event_id = created['id']
print(f"Created: {event_id}")

# Patch reminders
patched = service.events().patch(
    calendarId='primary', eventId=event_id,
    body={
        'reminders': {
            'useDefault': False,
            'overrides': [{'method': 'popup', 'minutes': 30}]
        }
    }
).execute()
print(json.dumps({
    'status': 'created_with_reminders',
    'id': patched['id'],
    'summary': patched['summary'],
    'start': patched['start'],
    'end': patched['end'],
    'reminders': patched.get('reminders')
}, indent=2))
```

## Two-Step Flow (Using GAPI CLI)

```bash
# Step 1 — create and capture event ID
EVENT_JSON=$(python /opt/data/skills/productivity/google-workspace/scripts/google_api.py \
  calendar create \
  --summary "Therapy session" \
  --start 2026-06-02T09:00:00+08:00 \
  --end 2026-06-02T09:30:00+08:00)

EVENT_ID=$(echo "$EVENT_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Step 2 — patch reminders
python3 -c "
import json, sys
sys.path.insert(0, '/opt/data/skills/productivity/google-workspace/scripts')
from google_api import build_service
service = build_service('calendar', 'v3')
event = service.events().patch(
    calendarId='primary', eventId='$EVENT_ID',
    body={'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 30}]}}
).execute()
print(json.dumps({'status':'updated','id':event.get('id'),'reminders':event.get('reminders')}))
"
```

## Python Path Note

If the system `python3` lacks the Google API packages (`ModuleNotFoundError`), use the Hermes venv python instead:

```bash
/opt/hermes/.venv/bin/python3 -c "from google_api import build_service; ..."
```
