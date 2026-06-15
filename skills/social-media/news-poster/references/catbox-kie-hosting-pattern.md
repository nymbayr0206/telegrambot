# catbox.moe Hosting for KIE input_urls

## Why catbox.moe over tmpfiles.org

- catbox.moe litterbox is **100% reliable** for KIE `gpt-image-2-image-to-image` (confirmed June 9, 2026)
- tmpfiles.org is unreliable — returns `"Image fetch failed"` (failCode 400) on some jobs while working on others
- catbox URLs work DIRECTLY in `input_urls` — no conversion needed (unlike tmpfiles.org which needs `/dl/` conversion)

## Upload Command

```bash
url=$(curl -s -F "reqtype=fileupload" -F "time=72h" \
  -F "fileToUpload=@/path/to/image.png" \
  https://litterbox.catbox.moe/resources/internals/api.php)
# Returns raw URL string: https://litter.catbox.moe/xxxxxx.png
```

**Parameters:**
- `reqtype=fileupload` — required
- `time=72h` — expiry (72 hours, 24h is also supported)
- `fileToUpload` — the file (jpg, png, mp4 all work)

## Verification

```bash
curl -s -o /dev/null -w "%{http_code}" "https://litter.catbox.moe/xxxxxx.png"
# Should return 200
```

## Use in KIE input_urls

```json
"input_urls": [
  "https://litter.catbox.moe/abc123.jpg",  // template
  "https://litter.catbox.moe/def456.png",  // article photo
  "https://litter.catbox.moe/ghi789.png"   // logo
]
```

## Fallback: tmpfiles.org (less reliable)

If catbox.moe is down:
```bash
upload=$(curl -s -F "file=@image.png" https://tmpfiles.org/api/v1/upload)
url=$(echo "$upload" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['url'])")
# Convert w/ → dl/ format for KIE reliability
dl_url="${url/tmpfiles.org\/w/tmpfiles.org\/dl\/w}"
```

## 3-Image Approach (Preferred, June 9 2026)

For AI Global news posters (news-post-1 template), always upload THREE images:
1. Template reference
2. Article/news photo
3. AI Global logo (from `/opt/data/social-content/brands/ai-global/assets/logos/logo-ai-global-transparent.png`)

This lets KIE preserve the logo by treating it as a "character reference" rather than a style element to reinterpret. The user explicitly approved this method and rejected Pillow overlay.
