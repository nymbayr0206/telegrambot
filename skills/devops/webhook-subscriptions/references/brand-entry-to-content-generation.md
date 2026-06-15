# Brand Entry Website → Hermes → Content Generation Pipeline

Use this pattern when a **client-facing brand entry website** (Vercel/Next.js hosted) collects brand info (logo, colors, fonts, settings) and needs Hermes to automatically generate branded marketing assets — carousel posters, reels/videos, and voiceovers — via KIE.AI.

## Architecture

```
Client submits brand on website
  → POST webhook to Hermes (Vercel → Hermes server)
    → Hermes verifies HMAC signature
      → Hermes loads kie-content-maker skill
        → KIE GPT Image 2 / Nano Banana 2 → carousel posters
        → KIE Veo 3.1 Fast → reels (brand intro)
      → Delivers finished assets via Telegram or back to website
```

**Direction:** Vercel-hosted website → Hermes webhook (this is the reverse of `hermes-cron-to-vercel-ingest.md` where Hermes is the sender).

## Prerequisites

- Hermes gateway running with webhook platform enabled (`hermes webhook list`)
- `KIE_API_KEY` set in Hermes `.env` or environment
- The website can make server-side `POST` requests (Next.js API route or similar)
- Hermes server is reachable from Vercel (public URL or tunnel)

## Webhook Subscription Setup

```bash
hermes webhook subscribe brand-entry \
  --events "brand.entry" \
  --prompt "New brand client {brand.name} submitted their brand info.\n\nLogo URL: {brand.logo_url}\nBrand colors: {brand.colors}\nFont: {brand.font}\nStyle preference: {brand.style}\nContact: {brand.email}\n\nClient details:\n{brand.client_detail}\n\nGenerate a branded carousel poster set (4 slides) and a short reel for this brand using KIE.AI. Use the logo URL as reference. Follow the brand's color scheme (#{brand.colors})." \
  --skills "kie-content-maker" \
  --description "Client brand entry → auto-generate posters and reels" \
  --deliver telegram
```

Returns a webhook URL like `https://your-hermes-server:8644/webhooks/brand-entry`.

## Payload Schema (Website → Hermes)

```json
{
  "event": "brand.entry",
  "source": "brand-entry-website",
  "occurred_at": "2026-05-31T14:00:00+08:00",
  "brand": {
    "name": "Client Brand Name",
    "logo_url": "https://cdn.example.com/uploads/logo.png",
    "colors": "063B4A,4CBFDD,D7AB46",
    "font": "Manrope",
    "style": "modern | minimal | playful",
    "client_detail": "Industry: Retail. Target: Mongolian youth.",
    "email": "client@example.mn",
    "phone": "+976 ..."
  },
  "metadata": {
    "submitted_at": "2026-05-31T14:00:00+08:00",
    "environment": "production"
  }
}
```

## Website Implementation (Next.js API Route)

```typescript
// pages/api/hermes/brand-entry.ts
export async function POST(req: Request) {
  const body = await req.json();
  
  // HMAC sign the body
  const hmac = crypto
    .createHmac('sha256', process.env.HERMES_WEBHOOK_SECRET!)
    .update(JSON.stringify(body))
    .digest('hex');

  const response = await fetch(process.env.HERMES_WEBHOOK_URL!, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Hermes-Event': 'brand.entry',
      'X-Idempotency-Key': `brand_entry:${body.brand.name}_${Date.now()}`,
      'X-Hub-Signature-256': `sha256=${hmac}`,
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(5000), // timeout, don't block signup
  });

  return Response.json({ success: true });
}
```

Set Vercel env vars:
```env
HERMES_WEBHOOK_URL=https://your-hermes-server:8644/webhooks/brand-entry
HERMES_WEBHOOK_SECRET=your-hermes-webhook-secret
```

## Asset Generation (What the Agent Does on Receipt)

When the webhook fires, the agent should:

1. **Download the logo** from `brand.logo_url` to a local cache
2. **Generate a 4-slide carousel** via KIE GPT Image 2:
   - Slide 1: Brand introduction (logo + tagline)
   - Slide 2: Problem/solution comparison
   - Slide 3: Features/benefits
   - Slide 4: Call to action with contact info
3. **(Optional) Generate a reel** via KIE Veo 3.1 Fast:
   - 8-second brand intro video
   - 9:16 aspect ratio (vertical for Reels/TikTok)
4. Deliver assets to Telegram or store for client pickup

## Common Pitfalls

### Vercel API token project scoping

**Problem:** A Vercel API token created from Vercel Dashboard → Settings → Tokens without selecting specific projects returns `{"error": {"code": "not_found", "message": "Project not found."}}` on `GET /v9/projects/:id` even when the project exists and the token authenticates successfully.

**Cause:** Vercel tokens default to no project access. The token's `GET /v2/user` works (returns user info), but project-scoped endpoints fail.

**Fix:** In Vercel Dashboard → Settings → Tokens → click the token → change Scope to either:
- **"All projects (full access)"** — simplest for development
- **"Selected projects"** — add the specific project ID(s)

Then retry the API call without creating a new token.

### Webhook URL reachability

Hermes webhook server on `localhost:8644` is not publicly reachable. For Vercel → Hermes integration:
- **Production:** Deploy Hermes gateway on a public server with proper DNS
- **Development:** Use ngrok, cloudflared, or similar tunnel to expose the webhook URL

### Idempotency

The website should send idempotency keys so duplicate POSTs (from retries) don't generate duplicate content. Hermes doesn't enforce idempotency natively — the agent prompt should check if this brand was already processed in the session.

## Relationship to Other Patterns

- **`clerk-academy-signup-to-hermes.md`** — website signup → lead capture (different: stores lead data, does not generate visual content)
- **`hermes-cron-to-vercel-ingest.md`** — Hermes → Vercel (reverse direction: Hermes posts to the app, not the other way)
- **`kie-content-maker`** skill — the actual generation engine (posters via GPT Image 2, reels via Veo 3.1)
