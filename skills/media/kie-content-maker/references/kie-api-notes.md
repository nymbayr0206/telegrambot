# KIE.AI API Notes for Content Maker

These notes condense the KIE.AI docs observed during the session. Treat them as a starting point; if a request returns a schema/validation error, inspect the live docs or error response and update the request body.

## Base and Auth

Base URL:

```text
https://api.kie.ai
```

Protected endpoints use bearer auth:

```text
Authorization: Bearer <KIE_API_KEY>
Content-Type: application/json
```

Do not persist literal user API keys in skills, memory, commits, or reusable scripts.

## Common Jobs API

Marketplace models use a unified task endpoint:

```text
POST /api/v1/jobs/createTask
GET  /api/v1/jobs/recordInfo
```

Typical request shape from docs:

```json
{
  "model": "nano-banana-2",
  "callBackUrl": "https://your-domain.com/api/callback",
  "input": {
    "prompt": "..."
  }
}
```

For production, docs recommend `callBackUrl` callbacks instead of only polling.

## Nano Banana 2

Docs page: Google - Nano Banana 2.

Endpoint:

```text
POST /api/v1/jobs/createTask
```

Model:

```text
nano-banana-2
```

Use for image/poster generation. Include the poster brief in `input.prompt`.

## ElevenLabs via KIE

Endpoint:

```text
POST /api/v1/jobs/createTask
```

Observed model names:

```text
elevenlabs/text-to-speech-turbo-2-5
elevenlabs/text-to-speech-multilingual-v2
elevenlabs/text-to-dialogue-v3
```

Docs example shape:

```json
{
  "model": "elevenlabs/text-to-speech-turbo-2-5",
  "callBackUrl": "https://your-domain.com/api/callback",
  "input": {
    "text": "Unlock powerful API with KIE.AI! ..."
  }
}
```

## Veo 3.1

Docs identify KIE's Veo 3.1 generation API as more than a direct wrapper and mention these variants:

- Veo 3.1 Quality — highest fidelity.
- Veo 3.1 Fast — cost-efficient, strong visual results.
- Veo 3.1 Lite — most cost-effective high-volume option.

Task modes described:

- `TEXT_2_VIDEO` — text prompt only.
- `FIRST_AND_LAST_FRAMES_2_VIDEO` — one/two frame transition video.
- `REFERENCE_2_VIDEO` — material/reference image based generation; docs noted Fast model only and support for 16:9 and 9:16.

Endpoints observed:

```text
POST /api/v1/veo/generate
GET  /api/v1/veo/record-info
POST /api/v1/veo/get-1080p-video
POST /api/v1/veo/get-4k-video
POST /api/v1/veo/extend
```

Status values on Veo detail responses:

```text
successFlag = 0  Generating
successFlag = 1  Success
successFlag = 2  Failed before completion
successFlag = 3  Generation failed after task creation / upstream failure
```

Docs state 16:9 and 9:16 are supported. 1080P and 4K upgrade endpoints exist; 4K costs extra credits.

## Common API

Credit check:

```text
GET /api/v1/chat/credit
```

Temporary download URL:

```text
POST /api/v1/common/download-url
```

Docs note download links are temporary (observed note: valid for about 20 minutes), so download or cache generated files immediately.

**Response shape:** `{"code":200, "msg":"success", "data":"https://signed-download-url..."}` — `data` is a **string** (the signed S3/Cloudflare R2 URL), not a dict. Accessing `body["data"]` gives the URL directly. Do NOT call `.get("downloadUrl")` on it.

**Pitfall:** This signed URL is the only way to download the file. The original KIE tempfile URL (e.g. `https://tempfile.aiquickdraw.com/...`) returns HTTP 403 when accessed directly without the signed query parameters.
