# Make.com Webhook Pattern for Facebook Posting

## Webhook URL

```
https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e
```

## Field Format

Make.com scenario expects **numbered multipart form fields**:

```
image1=@poster1.png  (file)
image2=@poster2.png  (file)
...
caption1=...  (text)
caption2=...  (text)
...
total_posters=4
source=kie_gpt_image_2
brand=AI Global
```

## Sending Pattern (Session-Proven)

### Pattern A: Single Combined Request (Primary)

Send all N posters in ONE multipart POST:

```bash
curl -s -X POST "https://hook.eu1.make.com/..." \
  -F "image1=@poster1.png;type=image/png" \
  -F "image2=@poster2.png;type=image/png" \
  -F "image3=@poster3.png;type=image/png" \
  -F "image4=@poster4.png;type=image/png" \
  -F "caption1=First caption..." \
  -F "caption2=Second caption..." \
  -F "total_posters=4" \
  -F "source=kie_gpt_image_2" \
  -F "brand=AI Global"
```

### Pattern B: Individual Backup

After the combined request, send each poster individually (2s delay between each) as a safety net:

```bash
for i in 1 2 3 4; do
  sleep 2
  curl -s -X POST "https://hook.eu1.make.com/..." \
    -F "image=@poster${i}.png;type=image/png" \
    -F "caption=..." \
    -F "poster_number=${i}" \
    -F "total_posters=4" \
    -F "brand=AI Global"
done
```

## Failure Modes

| Approach | Result |
|---|---|
| Base64-in-JSON single payload | Request entity too large (400) |
| Separate individual POSTs (no combined) | Only 1 poster arrives on Facebook |
| Combined + individual backup | All 4 arrive on Facebook ✅ |

## Adding New Posters

When 3 posters are already on Facebook and you only need to add a 4th:
- Send only poster 4 via individual POST
- Do NOT resend the existing 3 posters
- Always use `total_posters=4` so Make.com expects 4 total
