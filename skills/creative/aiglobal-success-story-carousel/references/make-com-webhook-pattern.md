# Make.com Webhook Pattern — AI Global Content Delivery

## Webhook URL
```
https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e
```

## Protocol

**Always send as multipart form-data**, not JSON. Base64-encoded JSON payloads exceed Make.com's size limit ("request entity too large" — 400 error).

## MANDATORY: content_type Parameter

Every webhook request **MUST** include the `content_type` field to tell Make.com what kind of content it is:

| Content Type | Field Value | Example Use |
|-------------|-------------|-------------|
| Poster / News Poster | `content_type=poster` | Single AI trend news poster, or 4 at once |
| Carousel (4 slides) | `content_type=carousel` | Success story or course promo carousel |
| Reel / Video | `content_type=reel` | Short form video content |

This was explicitly enforced by the user on June 8, 2026 — content_type is never optional.

## Single-Request (Preferred) — All 4 Posters at Once

Make.com's Facebook integration accepts up to 4 posters in one request:

```bash
curl -s -X POST "$WEBHOOK_URL" \
  -F "image1=@poster1.png;type=image/png" \
  -F "image2=@poster2.png;type=image/png" \
  -F "image3=@poster3.png;type=image/png" \
  -F "image4=@poster4.png;type=image/png" \
  -F "caption1=🔥 AI Vibe Coder first caption..." \
  -F "caption2=🚀 Second caption..." \
  -F "caption3=🌍 Third caption..." \
  -F "caption4=✨ Fourth caption..." \
  -F "total_posters=4" \
  -F "source=hermes_agent" \
  -F "brand=AI Global" \
  -F "content_type=poster"
```

## Single Poster Request

```bash
curl -s -X POST "$WEBHOOK_URL" \
  -F "image=@poster1.png;type=image/png" \
  -F "caption=🔥 Text caption here..." \
  -F "poster_number=1" \
  -F "total_posters=1" \
  -F "source=hermes_agent" \
  -F "brand=AI Global" \
  -F "content_type=poster"
```

## Reel/Video Request

```bash
curl -s -X POST "$WEBHOOK_URL" \
  -F "video=@reel.mp4;type=video/mp4" \
  -F "caption=🎬 Video caption..." \
  -F "source=hermes_agent" \
  -F "brand=AI Global" \
  -F "content_type=reel"
```

## Caption Format

Captions should be in Mongolian Cyrillic, including:
- Emoji leading (🔥 🚀 🌍 ✨)
- Poster-specific content summary
- CTA (Бүртгүүлэх утас: 89097454)
- Hashtags optional (#AIVibeCoder, #AIGlobal)

## Response

- `"Accepted"` — received successfully
- `"request entity too large"` — switch from JSON/base64 to multipart
- No response / 404 — webhook may be offline
