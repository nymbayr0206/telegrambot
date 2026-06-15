# Clerk / Academy Signup → Hermes Lead Capture Webhook

Use this pattern when a website should notify Hermes about new signups and enrollments so Hermes can alert the user and save/update a lead record in Google Sheets or Odoo.

## Website outbound webhook contract

Environment variables on the website/server side:

```env
HERMES_WEBHOOK_URL=
HERMES_WEBHOOK_SECRET=
CLERK_WEBHOOK_SECRET=
```

Send a server-side `POST` to `HERMES_WEBHOOK_URL` for:
- Clerk `user.created`
- Academy enrollment creation / successful signup events

Headers:
- `Content-Type: application/json`
- `X-Hermes-Event: website.signup`
- `X-Idempotency-Key: <stable-key>` such as `clerk_user_created:<clerkUserId>` or `academy_enrollment:<enrollmentId>`
- `X-Hub-Signature-256: sha256=<hmac_sha256_hex>` where the HMAC is over the raw JSON body using `HERMES_WEBHOOK_SECRET`

## Normalized payload

```json
{
  "event": "website.signup",
  "source": "clerk",
  "occurred_at": "2026-05-23T10:00:00+08:00",
  "idempotency_key": "clerk_user_created:user_123",
  "user": {
    "id": "user_123",
    "email": "user@example.mn",
    "phone": "+976...",
    "first_name": "",
    "last_name": "",
    "full_name": "",
    "username": "",
    "image_url": ""
  },
  "academy": {
    "enrollment_id": "",
    "course_id": "",
    "course_name": "",
    "plan": "",
    "price": "",
    "currency": ""
  },
  "marketing": {
    "utm_source": "",
    "utm_medium": "",
    "utm_campaign": "",
    "utm_content": "",
    "utm_term": "",
    "referrer": "",
    "landing_page": ""
  },
  "metadata": {
    "ip_hash": "",
    "user_agent": "",
    "environment": "production"
  }
}
```

## Website implementation notes for Codex

- Verify Clerk/Svix webhook signatures before trusting Clerk payloads.
- Call Hermes only after the website has successfully created the user/enrollment record.
- Hermes failure must not break signup: use a short timeout (about 5s), log server-side, and continue.
- Keep secrets server-side only; never expose `HERMES_WEBHOOK_SECRET` to browser code.
- Use stable idempotency keys and avoid duplicate sends when possible.
- Add tests for normalization, HMAC signing, and Hermes-down behavior.

## Hermes subscription behavior

The Hermes webhook subscription prompt should:
1. Notify the user in Telegram with name, email, phone, source, course/enrollment, UTM/referrer.
2. Upsert the lead in the `Lead Tracking & Scoring` Google Sheet (match by email or phone before inserting).
3. Append an `Activities` row with event type `website_signup` or `academy_enrollment`.
4. Apply initial score:
   - website signup: +5
   - academy enrollment: +15
   - email present: +2
   - phone present: +2
   - UTM/referrer present: +1
5. Set status/temperature:
   - academy enrollment: enrolled/hot
   - basic Clerk signup: new/warm
6. Set `next_follow_up_at` to the next business day in Asia/Ulaanbaatar unless enrolled.
7. Do not send email/SMS automatically from the signup webhook; only record and notify unless the user separately approved automation.
