---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

```bash
pip install youtube-transcript-api
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Error Handling

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `uv pip install --system youtube-transcript-api` (or `uv run --with youtube-transcript-api python3` if system `pip` is unavailable).

## Known Environment Constraints

This environment runs on a cloud IP that YouTube often blocks:

- `youtube-transcript-api` raises `RequestBlocked` — YouTube blocks cloud provider IPs
- `yt-dlp` fails with "Sign in to confirm you're not a bot" — needs cookies or JS runtime (deno/Node)
- `deno` cannot be installed here (requires `unzip` which is unavailable)

### Fallback Workflow When Cloud IP Is Blocked

1. **Try the `youtubetranscript.com` API** first (less aggressive blocking):
   ```bash
   curl -s "https://youtubetranscript.com/?v=VIDEO_ID&format=json"
   ```
2. **Try alternative transcript APIs** (workers-based proxies that may not be blocked):
   ```bash
   curl -s "https://youtube-transcript-api.louis616.workers.dev/api?video_id=VIDEO_ID"
   ```
3. **Ask the user to copy-paste the transcript** from YouTube (click "Show transcript" under the video).
4. **Ask the user for a different source** — or offer to create content from the topic itself if the video title gives enough context.
5. **Use `yt-dlp` with cookies** if the user can export a cookies.txt from their browser:
   ```bash
   yt-dlp --cookies cookies.txt --write-auto-subs --sub-langs en --skip-download -o "/tmp/%(id)s" "URL"
   ```
   Fallback when `pip` is unavailable:
   ```bash
   uv run --with yt-dlp -- yt-dlp --write-auto-subs --sub-langs en --skip-download "URL"
   ```
   NOTE: `yt-dlp` also needs a JS runtime (deno/Node) for full extraction; without it, metadata is incomplete and some formats may be missing.
