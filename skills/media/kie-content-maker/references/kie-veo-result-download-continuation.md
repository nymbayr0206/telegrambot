# KIE Veo 3.1 Fast result URL and continuation notes

Use this when generating Veo videos through KIE and downloading outputs.

## Submit

Typical request:

```json
{
  "model": "veo3_fast",
  "aspectRatio": "9:16",
  "prompt": "..."
}
```

For continuation/consistency, persist every response's:

- `taskId`
- `response.seeds[0]`
- `response.resultUrls[0]`
- local downloaded file path

Then pass the prior task/seed/reference information into the next generation when supported by the endpoint. Even when the API accepts continuation hints, verify the actual output visually because continuity can still drift.

## Poll

Poll:

```text
GET /api/v1/veo/record-info?taskId=<taskId>
```

Success shape observed:

```json
{
  "data": {
    "successFlag": 1,
    "response": {
      "resultUrls": ["https://...mp4"],
      "hasAudioList": [true],
      "seeds": [67144]
    }
  }
}
```

## Download pitfall

Do **not** recursively grab the first URL from the record payload. The record often includes `imageUrls` or reference image URLs in `paramJson`; a naive recursive URL extractor may download the reference PNG and save it as `.mp4`.

Preferred extraction order:

1. `data.response.resultUrls[0]`
2. then other explicit video fields only
3. verify the downloaded file magic bytes start with an MP4 header such as `ftyp`, not PNG bytes.

Verification commands/pattern:

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of json output.mp4
```

Expected for a standard Veo Fast vertical clip:

- video stream present
- audio stream present if speech requested
- 720×1280 for 9:16
- around 8 seconds unless a different duration was requested

## Voice note

KIE/Veo may include an audio track (`hasAudioList: [true]`), but Mongolian pronunciation still needs human review. If weak, use the video as visuals and add a clean Mongolian female voiceover/subtitles in editing.