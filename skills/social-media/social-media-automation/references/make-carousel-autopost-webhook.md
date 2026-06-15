# Make.com carousel autopost webhook pattern

Use this reference when the user gives a Make.com webhook to receive generated carousel images.

## Payload shape

Send `multipart/form-data` with metadata fields plus four image files:

```text
brand
campaign
carousel_number
topic
model
language
format
caption
slide1=@...jpg
slide2=@...jpg
slide3=@...jpg
slide4=@...jpg
```

The user prefers 4 separate carousel images, not an all-in-one contact sheet, when sending to automation webhooks.

## Curl pattern

```bash
curl -sS -X POST "$WEBHOOK_URL" \
  -F "brand=$BRAND" \
  -F "campaign=$CAMPAIGN" \
  -F "carousel_number=$N" \
  -F "topic=$TOPIC" \
  -F "model=gpt-image-2-text-to-image" \
  -F "language=mn" \
  -F "format=1:1 square carousel" \
  -F "caption=$CAPTION" \
  -F "slide1=@$SLIDE1;type=image/jpeg" \
  -F "slide2=@$SLIDE2;type=image/jpeg" \
  -F "slide3=@$SLIDE3;type=image/jpeg" \
  -F "slide4=@$SLIDE4;type=image/jpeg" \
  -w "\nHTTP_STATUS:%{http_code}\n"
```

Treat `HTTP_STATUS:200` with an accepted response as success. Advance any local state file only after webhook success.

## Scheduling note

If the user asks for a local-time schedule but cron uses UTC, convert explicitly. For Ulaanbaatar time (UTC+8), `09:00 Asia/Ulaanbaatar` is `01:00 UTC`, so cron is:

```text
0 1 * * *
```

## State-file pattern

Use a brand-local state file such as:

```text
/opt/data/social-content/brands/<brand>/automation/daily-carousel-state.json
```

Example fields:

```json
{
  "series_total": 18,
  "next_carousel": 1,
  "completed": [],
  "last_run_at": null,
  "last_status": null,
  "timezone": "Asia/Ulaanbaatar",
  "schedule": "daily 09:00"
}
```

Do not increment `next_carousel` if generation or webhook delivery fails.
