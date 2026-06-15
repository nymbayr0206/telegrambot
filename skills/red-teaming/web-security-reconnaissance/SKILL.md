---
name: web-security-reconnaissance
description: "Black-box web security audit &amp; reconnaissance using CLI tools only — find vulnerabilities, exposed secrets, misconfigurations, and attack surface without a browser."
version: 1.1.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [security, pentest, reconnaissance, bug-bounty, web-audit, curl, elasticsearch, graphql, cors, clickjacking, xss, wordpress, cloudflare, subdomain-takeover]
    related_skills: []
---

# Web Security Reconnaissance

## Overview

Systematic black-box security auditing of web applications using only CLI tools (curl, grep, python3, dig). No browser required — ideal for environments where the browser toolset is unavailable, or for fast, lightweight reconnaissance before deeper testing.

**What this covers:** hardcoded secrets in JS bundles, CORS misconfigurations, subdomain takeovers, exposed admin/API endpoints, Elasticsearch credential abuse, GraphQL discovery, clickjacking, weak CSP, infrastructure disclosure, missing security headers, CSRF weaknesses, S3 bucket exposure, XSS surface testing (reflected/DOM/stored), cookie security analysis, and protected site detection (Cloudflare challenge, Imunify360, OpenResty anti-bot).

**What this does NOT cover:** authenticated session testing, SQL injection, XSS exploitation, complex fuzzing, or tool-assisted scanning (Burp, ZAP, nuclei).

## Prerequisites

- Terminal access with: `curl`, `grep` (`ripgrep` preferred), `python3`, `dig`
- A target domain (e.g. `example.mn`)

## Workflow

Follow these phases in order. Each phase produces findings that feed the next.

### Phase 1: Surface Reconnaissance

Start broad — understand the infrastructure before diving deep.

**1.1 Initial HTTP probe:**
```bash
curl -sI https://example.mn/ | head -40
```
Check for: `server` (S3, nginx, CloudFront), `x-cache`, `set-cookie`, `x-powered-by`, `x-frame-options`, `strict-transport-security`, `content-security-policy`, `x-content-type-options`, `referrer-policy`.

**1.2 Security headers audit:**
```bash
curl -sI https://example.mn/ | grep -iE 'x-frame|x-content|x-xss|strict-transport|csp|set-cookie|cors|referrer'
```
**Findings to flag:**
- Missing `X-Frame-Options` or `frame-ancestors` → **clickjacking**
- Missing or overly permissive CSP (only `img-src *`) → **weak CSP**
- `Access-Control-Allow-Origin: *` → **CORS misconfiguration**
- Missing HSTS → **SSL stripping risk**

**1.3 DNS & subdomain recon:**
```bash
for sub in www m shop admin api dev test staging app cdn static assets media images uploads; do
  ip=$(dig +short "${sub}.example.mn" 2>/dev/null | head -1)
  [ -z "$ip" ] && echo "${sub}.example.mn → NO DNS (potential takeover)" || echo "${sub}.example.mn → ${ip}"
done
```
**Findings:** Any subdomain with NO DNS record is a **subdomain takeover candidate**.

### Phase 2: Endpoint & Path Discovery

**2.1 Common path brute-force (SPA check):**
```bash
for path in /admin /api /graphql /sitemap.xml /robots.txt /login /register /checkout /.env /config /.git/config /backup /wp-admin /sw.js; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://example.mn${path}")
  echo "${code} -> https://example.mn${path}"
done
```
**Note:** All-200 responses mean a Single Page App (client-side routing). Real API endpoints live on a separate API domain.

**2.2 DNS prefetch & meta analysis:**
```bash
curl -sL https://example.mn/ | grep -oP 'href="[^"]*"|//[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | sort -u
```
Look for `dns-prefetch` links — these reveal the backend services (API, Elasticsearch, CDN, SSO).

### Phase 3: API & Backend Recon

**3.1 Discover API domain:**
```bash
# From dns-prefetch or JS bundles
curl -sI https://api.cody.mn/ -H 'Origin: https://example.mn' | head -20
```

**3.2 Test for CORS misconfiguration:**
```bash
curl -sI 'https://api.example.mn/' -H 'Origin: https://evil.com' | grep -i 'access-control'
```
**Finding:** `Access-Control-Allow-Origin: *` on any endpoint that also sets cookies or returns auth data is **critical CORS misconfiguration**.

**3.3 Enumerate API endpoints:**
```bash
for path in /graphql /api /v1 /v2 /products /users /auth /login /register /orders /cart /search; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://api.example.mn${path}" -H 'Origin: https://example.mn')
  echo "${code} -> https://api.example.mn${path}"
done
```

**3.4 Frame & framework identification:**
Look for framework signatures in body/headers:
- `spree_user[login]` / `spree_user[password]` → **Rails/Spree** e-commerce
- `newrelic` / `NRJS-` → **New Relic** monitoring (license key may be exposed)
- `accessTokenUri` / `refreshToken` → **OAuth2** flow endpoints
- `_next` / `nextjs` → **Next.js**
- `X-Runtime`, `X-Request-Id` → **Ruby on Rails**
- `x-amz-apigw-id` → **API Gateway**

### Phase 4: JS Bundle Analysis

This is the HIGHEST value phase. Download and analyze all JS bundles for hardcoded credentials, API URLs, and feature discovery.

**4.1 Extract JS bundle URLs:**
```bash
curl -sL https://example.mn/ | grep -oP 'src="[^"]+\.js[^"]*"' | sort -u
```

**4.2 Download key bundles:**
```bash
curl -sL "https://example.mn/js/main.xxxxxx.js" > /tmp/main.js
wc -c /tmp/main.js
```

**4.3 Extract everything:**
```bash
# API URLs
grep -oP 'https?://[^"'"'"'` )]+' /tmp/main.js | sort -u

# Internal endpoints
grep -oP '/api[^"'"'"' )]*' /tmp/main.js | sort -u

# GraphQL operations
grep -oP 'gql`[^`]+`' /tmp/main.js | sort -u

# Secrets & credentials (HIGH VALUE)
grep -oP '(api[Kk]ey|secret|password|auth|jwt|bearer|token|basicAuth)[:=]\s*["'"'"']?[a-zA-Z0-9_\-\.@:]{6,80}["'"'"']?' /tmp/main.js

# ES/DB connections (PATTERN: host + username + password in one object)
grep -oP '(username|password|host|index|basicAuth):[^}]+' /tmp/main.js

# OAuth & auth patterns
grep -oP 'accessToken|refreshToken|accessTokenUri|sso|oauth|authorize' /tmp/main.js

# Social/app IDs
grep -oP '(appFacebookId|facebook.*app.*id|fb.*app_id)[:=][^,}]+' /tmp/main.js

# Localhost references in production bundles
grep -oP 'localhost:[0-9]+' /tmp/main.js
```

**What to flag:**
- `basicAuth:"user:pass"` — hardcoded credentials
- `password:"SomePassword"` — plaintext password
- `accessTokenUri` + `clientId` + `clientSecret` — OAuth credentials
- `localhost:PORT` — dev reference leaked to production
- Facebook App IDs, Google API keys, Segment/New Relic write keys

### Phase 5: Credential Verification

When hardcoded credentials are found, **verify them immediately**.

**5.1 Elasticsearch credentials:**
```bash
# Test credentials
curl -s 'https://elastic.example.mn/' -u 'user:password' | head -10

# Count records
curl -s 'https://elastic.example.mn/shoppy/_count' -u 'user:password'

# Search for data
curl -s 'https://elastic.example.mn/shoppy/_search?pretty' -u 'user:password' \
  -H 'Content-Type: application/json' -d '{"size":2}'
```

**ES response interpretation:**
- `security_exception` with role name (e.g. `viewer`, `product_read_only`) → creds WORK but are role-restricted
- `index_not_found_exception` → index name wrong
- Real data → **CRITICAL** finding

**5.2 GraphQL testing:**
```bash
# Try POST with credentials
curl -s 'https://ws.example.mn/graphql' -X POST -u 'user:pass' \
  -H 'Content-Type: application/json' -d '{"query":"{ __typename }"}'

# Check for introspection (if no creds needed)
curl -s 'https://api.example.mn/graphql' -X POST \
  -H 'Content-Type: application/json' -d '{"query":"query { __schema { types { name } } }"}'
```

### Phase 6: Infrastructure Exposure

**6.1 Cloud/Elasticsearch hostname disclosure:**
```bash
# DNS prefetch in HTML can reveal Elastic Cloud hosts
grep -oP 'es\.|elastic\.|cloud\.' /tmp/main.js
# Check for direct cloud provider URLs
curl -sL https://example.mn/ | grep -oP '//[^"'"'"']+\.elastic-cloud\.com'
```

**6.2 S3 bucket exposure:**
```bash
# S3 static hosting (from 'server: AmazonS3' header)
curl -sI 'http://example.mn.s3-website.ap-southeast-1.amazonaws.com/'
curl -sI 'http://example.mn.s3.amazonaws.com/'
```

**6.3 API Gateway exposure:**
```bash
# 'x-amz-apigw-id' header = API Gateway
curl -s 'https://generated.example.mn/' -H 'Authorization: Bearer TEST'
```

### Phase 7: Clickjacking Test

```bash
# On the main domain
curl -sI 'https://example.mn/' | grep -iE 'x-frame-options|content-security-policy|frame-ancestors'
```
**Finding:** No `X-Frame-Options` and no `frame-ancestors` in CSP → **clickjacking**.

### Phase 8: Protected Site Detection (Cloudflare / Imunify360 / OpenResty)

Some targets are heavily protected at the edge. Detect them early to avoid false negatives.

**8.1 Cloudflare challenge page:**
```bash
# Look for these signals in the HTML body
curl -sL 'https://example.mn/' | head -20
```
**Signals:**
- Title: `"One moment, please..."`
- Body contains `setTimeout(function(){ window.location.reload(); }, 5000)`
- `<link rel="icon" href="data:,">` (empty favicon)
- Spinner/loading CSS animations

**8.2 Imunify360 bot protection:**
```bash
# API/REST endpoints return this message
curl -s 'https://example.mn/wp-json/'
```
**Signal:** `"Access denied by Imunify360 bot-protection. IPs used for automation should be whitelisted"`

**8.3 OpenResty 415 anti-bot:**
```bash
# Non-GET requests or non-browser requests return 415
curl -s 'https://example.mn/sitemap.xml'
```
**Signal:** 415 response with `openresty/X.X.X.X` in server header error page.

**8.4 Impact on testing:**
- You CAN still test the main page (homepage usually loads)
- You CANNOT test API endpoints, wp-json, sitemap, or most static assets via curl
- **Bypass strategies:** Use proper browser-like headers (`Accept`, `User-Agent`, `Accept-Language`, `Cache-Control`). Some protections still block even with proper headers — these require a real browser.
- Protected sites are usually well-configured but still have subdomain takeover risks (DNS records are independent of WAF).

### Phase 9: XSS Surface Testing (Methodology)

When no reflected XSS is obvious, systematically test each vector:

**9.1 Reflected XSS in search/URL params:**
```bash
# Test if search terms or params appear in response
curl -s 'https://example.mn/?q=<script>alert(1)</script>' | grep -iE 'script>alert|&lt;script'
curl -s 'https://example.mn/?s=<img src=x onerror=alert(1)>' | grep -iE 'img src|onerror'
curl -s 'https://example.mn/?search=xss-test-12345' | grep 'xss-test-12345'
```

**9.2 Hash-based XSS (SPA hash router):**
```bash
curl -s 'https://example.mn/#/<script>alert(1)</script>' | grep -i 'script>alert'
```

**9.3 Form parameter reflection (Rails/WP/PHP backends):**
```bash
curl -s 'https://api.example.mn/login?email=<img src=x onerror=alert(1)>' | grep -iE 'img src|onerror'
curl -s 'https://api.example.mn/login?return_to=javascript:alert(1)' | grep -i 'javascript'
```

**9.4 DOM-based XSS detection from JS bundles:**
```bash
# Check for dangerous API usage in bundles
grep -oP 'dangerouslySetInnerHTML|innerHTML\s*=|outerHTML|insertAdjacentHTML|eval\(' /tmp/*.js 2>/dev/null
```

**9.5 Stored XSS in Elasticsearch:**
When ES credentials are found, check existing stored data for pre-existing XSS payloads:
```bash
# Search for HTML/script tags in product names
curl -s 'https://elastic.example.mn/shoppy/_search' -u 'user:pass' \
  -H 'Content-Type: application/json' -d '{
    "query": {"bool": {"should": [
      {"wildcard": {"name": "*<script*"}},
      {"wildcard": {"name": "*<iframe*"}},
      {"wildcard": {"name": "*<img*"}},
      {"wildcard": {"name": "*onerror*"}},
      {"wildcard": {"name": "*onload*"}}
    ]}}
  }'
```

**9.6 React-specific considerations:**
- React escapes all JSX expressions by default — XSS in React apps is uncommon without `dangerouslySetInnerHTML`
- `dangerouslySetInnerHTML` found in bundles may be from styled-components (safe CSS-in-JS) — verify context
- `innerHTML` can be used in utility functions that parse HTML-safe strings (Slate editor, etc.) — check if user input reaches these functions
- Weak CSP (no `script-src`) means if any XSS is found, it's immediately exploitable

**9.7 XSS verdict indicators:**
- `<script>` tags in server response body → **Reflected XSS confirmed**
- User-controllable data reaches `innerHTML` or `dangerouslySetInnerHTML` → **DOM XSS confirmed**
- Stored data rendered unsanitized in user-facing pages → **Stored XSS confirmed**
- No reflection, no dangerous API usage, React app → **XSS unlikely but not impossible**

### Phase 10: Cookie Security Analysis

```bash
# Check cookie attributes
curl -sI 'https://example.mn/' | grep -i 'set-cookie'
```
**Check for:**
- `HttpOnly` flag — missing means JS can read the cookie (XSS steals session)
- `Secure` flag — missing means cookie sent over HTTP
- `SameSite` — `None` without Secure is dangerous; `Lax`/`Strict` is good
- `Expires` — Cookies expiring decades in the future (2046+) are a risk
- `Domain` — overly permissive domain scope

## Findings Classification

| Severity | Example |
|----------|---------|
| 🔴 **CRITICAL** | Hardcoded working Elasticsearch credentials in JS; CORS `*` on auth endpoints; Subdomain takeover |
| 🟠 **HIGH** | Clickjacking; Weak CSP; Exposed API keys that work; Cookie without HttpOnly/Secure |
| 🟡 **MEDIUM** | Infrastructure disclosure; New Relic key leak; localhost in production; Framework fingerprinting; Cloudflare/Imunify360/OpenResty version disclosure |
| 🔵 **INFO** | S3 hosting identified; CDN provider; Server version headers; WAF/protection software identified |

## Pitfalls

- **SPA false positives:** All paths returning 200 doesn't mean they exist — it's client-side routing. Use API-based verification.
- **Elasticsearch clusters behind nginx:** The `elastic.cody.mn` endpoint may not be direct ES — check for nginx reverse proxy (HTTP/1.1 vs HTTP/2 headers).
- **WebSocket-only GraphQL:** Some GraphQL endpoints only work over WebSocket protocol (`wss://`), not HTTP POST. Check for `sec-websocket-version` in response headers.
- **Rate limiting:** Fast loops through many paths may trigger WAF/CloudFront blocks (403 errors). Add delays or split into batches.
- **Cookie expiry:** Check expiry dates on set-cookie headers — 20-year cookies are a security concern.
- **WebSocket-only GraphQL:** Some GraphQL endpoints (like `wss://ws.example.mn/graphql`) only respond over WebSocket protocol. HTTP POST returns 400. Check for `sec-websocket-version: 13` in HTTP response headers as a signal.
- **Port scan timeouts:** TCP connection attempts to common ports on Cloudflare-protected hosts will time out (firewalled). Don't rely on port scans for Cloudflare targets.
- **OpenResty 415 responses:** OpenResty returns `415 Unsupported Media Type` for requests it considers non-browser. This is NOT a valid HTTP 415 (content-type) error — it's an anti-bot signal. Detecting this prevents wasted time.
- **Yoast SEO version disclosure:** WordPress sites with Yoast SEO Premium expose the exact version in `<meta name="generator">` or comment tags. Cross-reference with known CVE databases.
- **Social/app IDs in meta tags:** Facebook App IDs from `fb:app_id` or `fb:pages` meta tags can be used for OAuth phishing or API abuse.
- **No browser does not mean no testing:** CLI-only recon finds different things than browser testing (hidden JS bundle secrets, infrastructure analysis, ES credential leaks).

## Verification

After finding credentials, always verify them live — don't report unverified findings.
After finding subdomains with no DNS, confirm by trying to register or checking if cloud services accept the domain.
