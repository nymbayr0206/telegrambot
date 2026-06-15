# GPT Image 1.5 Notes

## Model Names Tested

| Model Name | Result |
|---|---|
| `gpt-image-1.5-image-to-image` | 422 - model not supported |
| `gpt-image-1-5-image-to-image` | 422 - model not supported |
| `gpt-image/1.5-image-to-image` | Model accepted, but returns 500 Internal Error consistently |

## GPT Image /1.5-image-to-image

The model `gpt-image/1.5-image-to-image` is recognized by the API (does NOT return "model not supported") but consistently fails with "Internal Error, Please try again later" (code 500) on every attempt regardless of prompt content or input format.

### Input Schema (from OpenAPI spec)

```json
{
  "model": "gpt-image/1.5-image-to-image",
  "input": {
    "input_urls": ["https://..."],  // Array of uploaded file URLs
    "prompt": "Edit the image...",
    "aspect_ratio": "1:1",
    "quality": "high"
  }
}
```

### Required field: `input_urls`

The `input_urls` field accepts an array of file URLs from KIE file storage. It does NOT accept:
- data: URIs (returns "File type not supported")
- Arbitrary public URLs (untested but likely works since it only says "File URL after upload")

### File Upload Unavailability

To use `input_urls`, you must first upload images to KIE file storage via:
- `POST /api/file-base64-upload` — returns 403 "error code: 1010"
- `POST /api/file-stream-upload` — returns 404 Not Found

Neither endpoint is accessible from this server with the current API key. The file upload API may require a different auth scope or a paid plan.

### Alternative: GPT Image 2 Text-to-Image

Since image-to-image is broken, use `gpt-image-2-text-to-image` with detailed prompts describing the reference image's visual style (colors, layout zones, card elements, shadows, typography feel). This approach produced working posters for AI Global's temp1.jpg (1254x1254 dark tech background with gold accents).
