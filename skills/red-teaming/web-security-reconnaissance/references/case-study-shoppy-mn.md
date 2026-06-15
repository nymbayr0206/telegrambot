# Case Study: shoppy.mn — Full Reconnaissance

## Target Profile

- **Main:** `https://shoppy.mn/` — React SPA (Ant Design, Apollo GraphQL)
- **Hosting:** Amazon S3 → CloudFront
- **API:** `https://api.cody.mn/` — Ruby on Rails / Spree e-commerce (nginx 1.18.0)
- **API3:** `https://api3.cody.mn/` — nginx 1.30.0
- **ES:** `https://elastic.cody.mn/` — Elasticsearch behind nginx
- **ES Cloud:** `https://shoppy.es.asia-southeast1.gcp.elastic-cloud.com/`
- **WS/GraphQL:** `wss://ws.cody.mn/graphql`
- **PickPack:** `https://pickpack.mn/` — Next.js
- **PickPack Gen:** `https://generated.pickpack.mn/` — Amazon API Gateway
- **SSO:** `https://sso.toki.mn/oauth2/authorize`
- **Stack:** React + Spree (Ruby on Rails) + Elasticsearch + CloudFront + S3

## Security Headers

**shoppy.mn (frontend/S3):** NO security headers (no X-Frame-Options, no HSTS, no proper CSP)
**api.cody.mn:** X-Frame-Options: SAMEORIGIN, HSTS: max-age=15768000, X-Content-Type-Options: nosniff

### Finding: Clickjacking
Frontend lacks both `X-Frame-Options` and `frame-ancestors` CSP directive.

### Finding: Weak CSP
Only `img-src * blob: http: https: data:` — no `script-src`, no `frame-ancestors`, no `base-uri`.

## Subdomains

**ALL tested subdomains (www, m, shop, admin, api, dev, test, staging, app, cdn, static, assets, media, images, uploads) have NO DNS records → subdomain takeover risk.**

Only real subdomains found: the cody.mn wildcard (api.cody.mn, api3.cody.mn, elastic.cody.mn, ws.cody.mn).

## CORS Misconfiguration (CRITICAL)

`api.cody.mn` and `api3.cody.mn` return:
```
access-control-allow-origin: *
access-control-allow-methods: GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS
```

This applies to ALL endpoints including `/login` which sets auth cookies. An attacker's website can make authenticated cross-origin requests.

## Hardcoded Elasticsearch Credentials (CRITICAL)

Found in `/js/main.4406b096.js`:
```
basicAuth:"guest:ShoppyGuest"
```

**Verified working.** `guest` role = `product_read_only`:

| Index | Records | Data |
|-------|---------|------|
| `shoppy` | 108,173 | Mongolian market products |
| `1688` | 623,876 | 1688.com imported products |

Data includes: product names, vendor names/IDs, prices (MNT), descriptions, impressions, reviews, fulfillment durations.

### How to verify ES credentials:
```bash
# Check role (error message reveals it)
curl -s 'https://elastic.cody.mn/' -u 'guest:ShoppyGuest'

# Count accessible indices
curl -s 'https://elastic.cody.mn/shoppy/_count' -u 'guest:ShoppyGuest'

# Read data
curl -s 'https://elastic.cody.mn/shoppy/_search?pretty' -u 'guest:ShoppyGuest' \
  -H 'Content-Type: application/json' -d '{"size":2}'
```

## GraphQL Endpoint

Not exposed via HTTP POST (returns CloudFront 403). Only accessible via WebSocket:
`wss://ws.cody.mn/graphql`

The WebSocket endpoint returns `sec-websocket-version: 13` header but rejects plain HTTP requests (400 Bad Request).

## JavaScript Bundle Analysis

**Bundles (31 .js files split by npm package):** `main.4406b096.js` (111KB), plus vendor chunks (antd, apollo, graphql, react-router, etc.)

### Secrets found in JS:
- `password:"ShoppyGuest"` — plaintext in main.js
- `basicAuth:"guest:ShoppyGuest"` — used for ES
- `es:"https://elastic.cody.mn"` — ES host
- `appFacebookId:"1400896387121048"` — in-app FB app ID
- Facebook App ID (main): `660742257292404` — from meta tag
- `localhost:3005` — dev reference in production

### API discovery from JS:
- `https://api.cody.mn/download/ticket/${id}/${number}`
- `https://api3.cody.mn` (using instead of api.cody.mn for some calls)
- `https://elastic.cody.mn` (ES endpoint)
- `https://generated.pickpack.mn` (API Gateway)
- `https://sso.toki.mn/oauth2/authorize` (SSO)
- `wss://ws.cody.mn/graphql` (GraphQL over WebSocket)

### Service discovery:
- `index:"shoppy"` — ES index name
- OneSignal: `https://cdn.onesignal.com/sdks/OneSignalSDK.js`
- Segment: `ViMnwFrRkdqY8dUVtoZ4NYMaU5ggiI1e` write key
- New Relic: `NRJS-6e7c0738a1daca34ca3` license key
- `accessToken` / `refreshToken` — OAuth2 token management (Stored in localStorage)

## Infrastructure Details

- **Server IP:** 18.153.48.32 (api.cody.mn, AWS Singapore)
- **Certificate:** *.cody.mn, Sectigo DV, expires Feb 2027
- **New Relic:** bam.eu01.nr-data.net (EU endpoint)
- **OneSignal:** Push notification SDK
- **Segment analytics:** Page tracking, identify, group APIs
- **Cookie expiry:** 2046 (20 years) — set-cookie: token

## Rails/Spree Login Page

`https://api.cody.mn/login` — Rails/Spree login form with:
- `spree_user[login]` email field
- `spree_user[password]` password field  
- CSRF token (`authenticity_token`)
- `remember_me` checkbox
- New Relic RUM monitoring injected

## Related Endpoints

- `https://pickpack.mn/` — Next.js app (X-Powered-By: Next.js, s-maxage=31536000)
- `https://generated.pickpack.mn/` — API Gateway (403 MissingAuthenticationTokenException without valid IAM auth)
