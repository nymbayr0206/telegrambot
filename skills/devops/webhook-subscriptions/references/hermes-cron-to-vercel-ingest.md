# Hermes cron to Vercel ingest webhook pattern

Use this reference when the user wants Hermes to push scheduled content/data into a Vercel/Next.js app, especially from a cron job.

## Pattern

1. Vercel app exposes an API route such as:
   - `POST /api/hermes/daily-industry-news`
2. Vercel stores a shared secret in an environment variable, for example:
   - `HERMES_NEWS_WEBHOOK_SECRET`
3. Hermes cron job produces a JSON payload.
4. Hermes signs the raw JSON and sends headers:
   - `x-hermes-source: hermes-daily-industry-news`
   - `x-hermes-timestamp: <current Unix timestamp seconds>`
   - `x-hermes-signature: sha256=<hmac_hex>`
5. App verifies timestamp freshness and HMAC before saving data.

## HMAC signing

Canonical signing payload:

```text
timestamp + "." + rawJsonBody
```

Signature:

```text
sha256=<hex HMAC-SHA256 using shared secret>
```

Important: sign the exact raw JSON string sent in the HTTP body, not a re-parsed/reformatted object.

## Test payload

For first connectivity test, send the smallest valid payload:

```json
{
  "source": "hermes-daily-industry-news",
  "date": "YYYY-MM-DD",
  "timezone": "Asia/Ulaanbaatar",
  "industries": []
}
```

## Vercel/Next.js route requirements

- Use Node runtime if using `crypto` HMAC:
  - `export const runtime = "nodejs";`
- Read the body as raw text first:
  - `const rawBody = await req.text();`
- Verify headers before parsing/saving.
- Reject stale timestamps, e.g. older than 5 minutes.
- Use `crypto.timingSafeEqual` for signature comparison.
- Parse JSON only after signature succeeds.
- Return structured response:

```json
{
  "ok": true,
  "receivedIndustries": 0,
  "receivedArticles": 0,
  "created": 0,
  "updated": 0,
  "errors": []
}
```

## Daily industry news payload shape

For a top-10 industries news pipeline, each run usually sends:

- 10 industries
- 3 articles per industry
- bilingual English/Mongolian fields
- one `imageUrl` per article for the slider
- `sourceName`, `sourceUrl`, and `publishedAt` for grounding

Recommended article fields:

```json
{
  "id": "YYYY-MM-DD-industry-slug-01",
  "rank": 1,
  "title": { "en": "...", "mn": "..." },
  "summary": { "en": "...", "mn": "..." },
  "body": { "en": "...", "mn": "..." },
  "imageUrl": "https://...",
  "imageAlt": { "en": "...", "mn": "..." },
  "sourceName": "...",
  "sourceUrl": "https://...",
  "publishedAt": "...",
  "tags": ["..."],
  "importanceScore": 0
}
```

## Pitfalls

- Do not create the Hermes cron job until the real webhook URL and shared secret are available.
- Placeholder domains like `https://your-domain.com/...` are not actionable.
- If the user says the secret is “same as env var”, ask for the value or the server-side path/variable from which Hermes can read it.
- Upsert by `sourceUrl` or deterministic `id` so retries do not duplicate articles.
- Start with `draft` mode for editorial QA unless the user explicitly chooses auto-publish.
