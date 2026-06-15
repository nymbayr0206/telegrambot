# Vercel Deployment URL Discovery

When a custom domain (e.g., `agenticforce.com`) maps to a different platform (e.g., Hostinger), but the actual API/Vercel app is elsewhere, use this workflow to find the real deployment URL.

## The Problem

A domain like `agenticforce.com` can:
- Point to Hostinger Website Builder (static site)
- Point to Vercel (Next.js app)
- Have DNS proxy rules that route `/api/*` differently

The **custom domain is NOT a reliable indicator** of where your backend is deployed.

## Discovery Workflow

### Step 1: Identify the platform serving the custom domain

```bash
curl -sI "https://agenticforce.com" | grep -i "x-powered-by\|platform\|server"
```

- `x-powered-by: HostingerWebsiteBuilder` / `platform: hostinger` → **Hostinger, not Vercel**
- `server: Vercel` / `x-vercel-id` → **Vercel**
- HTML body contains `"Website Builder 404"` → **Hostinger 404 page**

### Step 2: Find the GitHub repo and check Vercel project name

```bash
cd /path/to/repo
git remote -v
# Usually: origin git@github.com:owner/agenticforceweb.git
```

The Vercel project name is typically the GitHub repo name. The preview URL follows:
- `https://<project-name>.vercel.app` (e.g., `https://agenticforceweb.vercel.app`)

### Step 3: Test the Vercel preview URL

```bash
# Check if it's actually Vercel
curl -sI "https://agenticforceweb.vercel.app" | grep -i "server"

# Test API contract (auth-gated)
curl -s -w "\nHTTP: %{http_code}" \
  "https://agenticforceweb.vercel.app/api/hermes/postly/brands"
# → 401 (Unauthorized) = endpoint EXISTS, needs auth

curl -s -w "\nHTTP: %{http_code}" \
  -H "x-hermes-secret: <SECRET>" \
  "https://agenticforceweb.vercel.app/api/hermes/postly/brands"
# → 200 = endpoint EXISTS and authenticated
```

### Step 4: Verify via existing known-working routes

If the Vercel app has any known working endpoint (e.g., `import-news`), test it on both domains:

```bash
# Test known endpoint on custom domain
curl -s -X POST -H "x-hermes-secret: <SECRET>" \
  -d '{"articles":[]}' \
  "https://agenticforce.com/api/hermes/import-news"
# → 400 "Invalid Hermes payload" = Vercel (code processes the request)
# → Hostinger 404 / XML error = NOT Vercel

# Same test on preview URL
curl -s -X POST -H "x-hermes-secret: <SECRET>" \
  -d '{"articles":[]}' \
  "https://agenticforceweb.vercel.app/api/hermes/import-news"
# → 400 "Invalid Hermes payload" = Vercel ✓
```

### Step 5: Check for DNS proxy rules

Some deployments proxy `/api/*` from the custom domain to Vercel. Verify by sending the same request to both:

```bash
# If custom domain returns Vercel JSON for API routes but Hostinger HTML for /
# → DNS/proxy rules exist that route /api/* to Vercel
```

## Response Body Tell

| Response Body | Platform |
|---|---|
| `"Website Builder 404"` | **Hostinger** |
| HTML with header/footer + `"This page could not be found."` | **Vercel** (Next.js 404 page) |
| `{"error":"Unauthorized"}` | **Vercel** (API endpoint exists, needs auth) |
| XML `<Error><Code>...` | **AWS S3 / Cloud storage** (misconfigured routing) |
| `{"error":"Invalid Hermes payload"}` | **Vercel** (API exists, payload rejected by validation) |

## Domain Table Pattern

Keep a table like this for the project:

| Domain | Platform | Notes |
|---|---|---|
| `agenticforce.com` | Hostinger Website Builder | Static marketing site |
| `www.postly.mn` | Vercel (agenticforceweb) | Same app as preview URL |
| `agenticforceweb.vercel.app` | Vercel | Auto-deployed from GitHub main |

## Pitfalls

- **Never assume a custom domain points to Vercel** — check the response body, not just the domain name
- **Vercel preview URLs work even when custom domains don't** — use `project-name.vercel.app` as the interim base URL
- **The user may configure AGENTICFORCE_BASE_URL to the custom domain** expecting reverse proxy. Verify before using it, and use the preview URL for direct API access
- **After a git push, Vercel takes 1-5 minutes to deploy** — a 404 immediately after push is normal; it's not a failure signal
- **Check feature branches before assuming code doesn't exist** — run `git branch -a | grep <feature>` before creating anything
