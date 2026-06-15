# AI Global — Template-Based Poster Generation (Current Workflow)

**Status:** Supersedes the "Italian minimal magazine" style from the original brand guide.
The user now uses dark tech + gold temp1/reeltemp1 templates.

## Templates

| Name | Format | Path | Use |
|------|--------|------|-----|
| `temp1` | 1:1 1254×1254 | `backgrounds/temp1.jpg` | Carousel/posters |
| `reeltemp1` | 9:16 720×1280 | `assets/reeltemp1.jpg` | Reels |

## Generation Model

`gpt-image-2-image-to-image` via KIE AI (NOT `gpt-image/1.5-image-to-image`).

## Workflow

See `creative/kie-image-to-image` skill for the full workflow including:
- Uploading template to tmpfiles.org for public URL
- Submitting to KIE with `input_urls`
- Downloading results
- Sending to Make.com

## Make.com Webhook

```
https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e
```

- Single poster: `-F "image=@file" -F "poster_number=N" -F "total_posters=4"`
- Carousel (4 posters): `-F "image1=@file" -F "image2=@file" -F "image3=@file" -F "image4=@file"`

## Critical Rules

- ❌ NEVER use FFmpeg for posters — only for reel video composition
- ❌ Never regenerate already-approved/on-Facebook posters
- ✅ "Carousel" = 4 posters
- ✅ Always upload the template file first — local paths don't work with KIE
