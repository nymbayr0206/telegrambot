# Gmail Draft Creation via Google API

Use this when the user asks to create/save an email draft instead of sending an email.

The bundled `google_api.py` may support `gmail send` and `gmail reply` but not a first-class `gmail draft` command. In that case, create the draft directly with the Gmail API client used by the skill.

## Plain-text draft

```python
import sys, json, base64
from email.message import EmailMessage

sys.path.insert(0, '/opt/data/skills/productivity/google-workspace/scripts')
from google_api import build_service

service = build_service('gmail', 'v1')

msg = EmailMessage()
msg['To'] = 'recipient@example.com'          # omit if user wants recipient blank
msg['Subject'] = 'Subject here'
msg.set_content('Email body here\n')

raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
draft = service.users().drafts().create(
    userId='me',
    body={'message': {'raw': raw}},
).execute()

print(json.dumps({
    'status': 'draft_created',
    'draft_id': draft.get('id'),
    'message_id': draft.get('message', {}).get('id'),
    'to': msg.get('To', ''),
    'subject': msg.get('Subject', ''),
}, indent=2))
```

## Rules

- Creating a draft is lower-risk than sending, but still modifies Gmail; make sure the user asked for a draft.
- If the user says "just write" or has not provided a recipient, it is acceptable to create a draft with the `To` field omitted so they can fill it in later.
- Never send the draft without explicit confirmation.
- In the final response, clearly say it was saved as a draft and not sent.
