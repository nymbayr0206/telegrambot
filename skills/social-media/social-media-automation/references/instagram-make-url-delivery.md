# Instagram Delivery via Make.com — Image URLs Required

## The Problem

Make.com webhooks accept `multipart/form-data` with `@file` attachments for carousel posting to Facebook Pages. **But Instagram requires image URLs**, not binary file uploads. When the receiving Make.com scenario bridges to Instagram, it needs publicly accessible image URLs.

## The Solution

Two-step process:

### Step 1: Upload images to a public hosting service

Preferred: **freeimage.host** (no auth required, works when catbox.moe/0x0.st are down):

```bash
# Upload single image and extract URL in one command
curl -s -F "source=@/path/to/image.jpg" \
  -F "type=file" \
  -F "action=upload" \
  https://freeimage.host/json | python3 -c "import sys,json; print(json.load(sys.stdin)['image']['url'])"

# Returns: https://iili.io/XXXXXXX.jpg
```

The `python3 -c` inline pipe is the fastest way to extract the URL. The response shape is:
```json
{
  "image": {
    "url": "https://iili.io/XXXXXXX.jpg",
    "url_viewer": "https://freeimage.host/i/XXXXXXX",
    "filename": "XXXXXXX.jpg",
    ...
  },
  "status_code": 200,
  "success": {"message": "image uploaded", "code": 200}
}
```

**Fallbacks when upload services are down:**
- **catbox.moe** (`https://litterbox.catbox.moe/resources/internals/api.php`): `-F "reqtype=fileupload" -F "time=72h" -F "fileToUpload=@file.jpg"` — 72h expiry, may hit 404/uploader invalid errors
- **0x0.st**: Simple `-F "file=@file.jpg"` — currently disabled for AI botnet spam

### Step 2: Send URLs (not files) in the webhook payload

Use named URL fields instead of file fields. Convention: `image{N}_url` instead of `slide{N}=@file.jpg`:

```bash
curl -s -X POST "https://hook.eu1.make.com/..." \
  -F "content_type=poster" \
  -F "image1_url=https://iili.io/XXXXXXX.jpg" \
  -F "image2_url=https://iili.io/YYYYYYY.jpg" \
  -F "image3_url=https://iili.io/ZZZZZZZ.jpg" \
  -F "image4_url=https://iili.io/WWWWWWW.jpg" \
  -F "caption1=..." \
  -F "caption2=..." \
  -F "caption3=..." \
  -F "caption4=..." \
  -F "total_posters=4" \
  -F "source=hermes_agent" \
  -F "brand=AI Global"
```

The Make.com scenario must be configured to read `image{N}_url` fields (not file fields) and pass them to the Instagram publish module.

## When to Use Which Delivery Mode

| Platform | Webhook Fields | Content Type |
|----------|---------------|--------------|
| **Facebook Page** | `slide{N}=@file.jpg` (multipart binary) | `content_type=poster` |
| **Instagram Business** | `image{N}_url=<URL>` (string fields) | `content_type=poster` |
| **Carousel (both FB+IG)** | `slide{N}=@file.jpg` + Make.com routes to correct platform | `content_type=carousel` |

**Rule of thumb:** If the Make.com scenario ends in an Instagram API call, use URL mode. If it ends in a Facebook Page post, file mode works. When unsure, ask the user which delivery mode Make.com is configured for.

## JSON Array Batch Poster Delivery (Alternative to Multipart)

For sending multiple posters at once with a unified caption, a **JSON POST with an `images` array** works as an alternative to multipart form fields:

### Legacy format (plain URL strings in array)

```bash
WEBHOOK="https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e"

curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "poster",
    "images": [
      "https://tmpfiles.org/dl/wXXXXXX/image1.jpg",
      "https://tmpfiles.org/dl/wXXXXXX/image2.jpg",
      "https://tmpfiles.org/dl/wXXXXXX/image3.jpg",
      "https://tmpfiles.org/dl/wXXXXXX/image4.jpg"
    ],
    "caption": "🔥 Unified caption for all 4 slides..."
  }'
```

**Pros vs multipart:** Cleaner for scripted batch sends, single unified caption, no per-image field naming. **Works when** the Make.com scenario is configured to accept JSON payloads with array fields. Response: `"Accepted"` on success.

### Current format (file_name + data objects + instagram_urls)

As of June 2026, Battushig's Make.com scenario evolved to require **separate fields for Facebook vs Instagram**:

```json
{
  "content_type": "poster",
  "caption": "🔥 Unified caption with #hashtags",
  "images": [
    {"file_name": "news_1.jpg", "data": "https://tmpfiles.org/dl/hash/filename.jpg"},
    {"file_name": "news_2.jpg", "data": "https://tmpfiles.org/dl/hash/filename.jpg"},
    {"file_name": "news_3.jpg", "data": "https://tmpfiles.org/dl/hash/filename.jpg"},
    {"file_name": "news_4.jpg", "data": "https://tmpfiles.org/dl/hash/filename.jpg"}
  ],
  "instagram_urls": [
    "https://tmpfiles.org/dl/hash/img1.jpg",
    "https://tmpfiles.org/dl/hash/img2.jpg",
    "https://tmpfiles.org/dl/hash/img3.jpg",
    "https://tmpfiles.org/dl/hash/img4.jpg"
  ]
}
```

Key differences from legacy:
- `images` is now an **array of objects** — each with `file_name` (used by Facebook) and `data` (the image URL)
- `instagram_urls` is a **separate array of 4 plain URL strings** for Instagram Business
- `content_type` stays the same
- Always verify URLs return `200 image/jpeg` or `200 image/png` before sending

curl command:
```bash
curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "poster",
    "caption": "...",
    "images": [
      {"file_name": "slide1.jpg", "data": "https://tmpfiles.org/dl/hash/img1.jpg"},
      {"file_name": "slide2.jpg", "data": "https://tmpfiles.org/dl/hash/img2.jpg"},
      {"file_name": "slide3.jpg", "data": "https://tmpfiles.org/dl/hash/img3.jpg"},
      {"file_name": "slide4.jpg", "data": "https://tmpfiles.org/dl/hash/img4.jpg"}
    ],
    "instagram_urls": [
      "https://tmpfiles.org/dl/hash/img1.jpg",
      "https://tmpfiles.org/dl/hash/img2.jpg",
      "https://tmpfiles.org/dl/hash/img3.jpg",
      "https://tmpfiles.org/dl/hash/img4.jpg"
    ]
  }'
```

## ⚠️ Pitfall — "send to make" shorthand

When Battushig says "send to make" / "send again to mle" without specifying content type: he means the **most recently discussed content batch**, not the last type I sent. In this session, he said "send again" — I sent the reel, but he corrected: "I meant last 4 slide of news". The posters were what he'd been discussing before.

**Rule:** When "send again" is ambiguous, infer from the last UN-ambiguous content topic the user raised. If the user just reviewed/asked about news posters, "send again" means the news posters — even if the last action you took was a reel.

The Make.com webhook uses `content_type` to route to different scenarios (reel → Instagram Reels, poster → feed/carousel).

## Video/Reel Delivery

Reels need a public video URL (not multipart file upload). The same Make.com webhook handles both reels and posters via the `content_type` field.

### Step 1: Upload video to tmpfiles.org

**tmpfiles.org** is preferred for MP4 videos (handles 1.2MB+ files without size limits; litterbox returns 413 for larger videos):

```bash
# Upload video
curl -s -F "file=@/path/to/video.mp4" https://tmpfiles.org/api/v1/upload
# Returns: {"status":"success","data":{"url":"https://tmpfiles.org/<hash>/<filename>"}}
```

Then extract the **direct download URL** (the returned URL is a page, not the direct media link):

```bash
# Get direct download URL from the page
DIRECT_URL=$(curl -s "https://tmpfiles.org/<hash>/<filename>" | grep -oP 'https://tmpfiles.org/dl/[^"<>]+' | head -1)
# Returns: https://tmpfiles.org/dl/<hash>/<filename>
```

**Verify the direct URL** returns the correct content type:
```bash
curl -s -o /dev/null -w "%{http_code} %{content_type}" "https://tmpfiles.org/dl/<hash>/<filename>"
# Expected: 200 video/mp4
```

### Step 2: Send JSON payload to Make.com

Unlike carousels (multipart) and posters (multipart with image URLs), reels use a **JSON POST** with `content_type=reel`:

```bash
curl -s -X POST "https://hook.eu1.make.com/..." \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "reel",
    "video_url": "https://tmpfiles.org/dl/<hash>/<filename>",
    "caption": "Optional caption text"
  }'
```

Response: `"Accepted"` on success.

The same webhook URL serves both types — `content_type` routes within Make.com:
- `content_type=reel` → Instagram Reel publishing scenario
- `content_type=poster` → Poster/carousel publishing scenario

## Upload Service Comparison

| Service | Command | Pros | Cons |
|---------|---------|------|------|
| **tmpfiles.org** | `-F "file=@file" https://tmpfiles.org/api/v1/upload` | No size limits, works with video | Need to extract direct dl URL from page; temporary |
| **freeimage.host** | `-F "source=@file" -F "type=file" https://freeimage.host/json` | No auth, works, returns JSON | Images only; rate limits? Unknown uptime |
| **catbox.moe** | `-F "reqtype=fileupload" -F "fileToUpload=@file" https://litterbox.catbox.moe/resources/internals/api.php` | Fast, temporary | 72h expiry, may return 404 |
| **0x0.st** | `-F "file=@file" https://0x0.st` | Simple | Currently disabled |
