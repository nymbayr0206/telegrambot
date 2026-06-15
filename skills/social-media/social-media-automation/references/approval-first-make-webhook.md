# Approval-first Make.com autopost pattern

Use this reference when a brand automation generates social assets and posts through Make.com/webhook.

## Rule

For user-owned brand publishing, default to **approval-first** unless the user explicitly asks for fully automatic posting. The safe workflow is:

1. Generate assets.
2. Save local files and a manifest/pending approval JSON.
3. Deliver preview media to Telegram for review.
4. Do **not** call Make.com/webhook yet.
5. Wait for explicit approval such as `approve <brand> carousel`.
6. Only then send multipart form data to Make.com and advance the series/state.

## State pattern

Use two states:

- `pending_approval`: generated successfully, not sent.
- `success`: webhook accepted and state advanced.

Do not increment `next_carousel` or mark an item completed until the webhook succeeds after approval.

## Pending approval JSON fields

```json
{
  "brand": "supernova",
  "campaign": "...",
  "carousel_number": 1,
  "topic": "...",
  "caption": "...",
  "model": "gpt-image-2-text-to-image",
  "files": ["/absolute/path/slide1.jpg"],
  "output_dir": "/absolute/path",
  "webhook_config": "/absolute/path/to/make-webhook.json",
  "created_at": "ISO timestamp",
  "status": "pending_approval"
}
```

## Make.com multipart convention

Send fields such as:

- `brand`
- `campaign`
- `carousel_number`
- `topic`
- `model`
- `language`
- `format`
- `caption`
- `slide1` ... `slide4`

## Pitfall learned

A cron job that sends to Make.com directly violates the user's approval-first social automation preference. If a job was previously configured as `generate → send`, patch it to `generate → preview → pending approval`, and create a separate explicit approval sender script.