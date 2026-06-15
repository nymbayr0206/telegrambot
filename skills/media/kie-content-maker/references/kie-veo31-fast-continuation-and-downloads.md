# KIE Veo 3.1 Fast continuation + download notes

Use when generating multi-part Veo 3.1 Fast social videos, especially Postly-style spokesperson ads.

## Sequential generation pattern

For a 3-part continuation video:

1. Generate scene 1 with `POST /api/v1/veo/generate` using `model: "veo3_fast"`, `aspectRatio: "9:16"`, and an explicit 6–8 second scene prompt.
2. Poll `GET /api/v1/veo/record-info?taskId=<taskId>` until `data.successFlag == 1`.
3. Save:
   - `data.taskId`
   - `data.response.resultUrls[0]`
   - `data.response.seeds[0]`
   - `data.response.hasAudioList[0]`
4. Use the prior scene’s task id / seed / result URL as continuity context for the next generation when the endpoint/model supports it.
5. Repeat for scene 2 and scene 3, writing a manifest with scene number, task id, seed, URL, local file, narration, and audio flag.

## Important response shape

Successful Veo record responses can look like:

```json
{
  "data": {
    "taskId": "...",
    "successFlag": 1,
    "response": {
      "resultUrls": ["https://...mp4"],
      "hasAudioList": [true],
      "seeds": [67144]
    }
  }
}
```

Do not rely on a generic recursive URL extractor if the original prompt used `imageUrls`: it may pick the input/reference image URL instead of the final MP4. Prefer `data.response.resultUrls[0]` for the final video.

## Download pitfall

If `resultUrls[0]` is already an MP4 URL, download it directly with a normal HTTP GET first. Only fall back to `/api/v1/common/download-url` if direct download fails.

A bad downloader can accidentally save the concept/reference PNG under an `.mp4` filename if it extracts the first URL from the whole record. Verify local videos after download:

- first bytes should look like MP4/ISO BMFF (`ftyp` near the beginning), not PNG (`\x89PNG`).
- `ffprobe` should show 9:16 dimensions, duration, and audio/video streams.

## Audio note

Veo can return `hasAudioList: [true]`, but Mongolian pronunciation may still need human QA. If speech is weak, keep the visuals and add a clean Mongolian female TTS voiceover plus exact subtitles in editing.
