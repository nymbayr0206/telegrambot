# One-Shot Recon Command Reference

Complete CLI command snippets for each recon phase. Copy, paste, and modify for your target.

## Phase 1: Initial Probe

```bash
# Full headers
curl -sI https://TARGET/ | head -40

# Security headers only
curl -sI https://TARGET/ | grep -iE 'x-frame|x-content|x-xss|strict-transport|csp|set-cookie|cors|referrer'

# URL path scan (SPA vs server-side check)
for path in /admin /api /graphql /sitemap.xml /robots.txt /login /register /checkout /.env /config /.git/config /backup /wp-admin /sw.js; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' "https://TARGET${path}") -> ${path}"
done
```

## Phase 2: Subdomain Recon

```bash
for sub in www m mail shop admin api dev test staging app cdn static assets media images uploads portal doctor doctors booking appointment lab; do
  ip=$(dig +short "${sub}.TARGET" 2>/dev/null | head -1)
  [ -z "$ip" ] && echo "${sub}.TARGET → NO DNS (takeover?)" || echo "${sub}.TARGET → ${ip}"
done
```

## Phase 3: API Discovery & CORS

```bash
# Check main API
curl -sI 'https://api.TARGET/' -H 'Origin: https://TARGET' | head -20

# CORS test
curl -sI 'https://api.TARGET/' -H 'Origin: https://evil.com' | grep -i 'access-control'

# CORS with credentials test
curl -s -D- 'https://api.TARGET/login' -H 'Origin: https://evil.com' -H 'Cookie: session=test' | head -20

# API endpoint brute-force
for path in /graphql /api /v1 /v2 /products /users /auth /login /register /orders /cart /search; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://api.TARGET${path}" -H 'Origin: https://TARGET')
  echo "${code} -> https://api.TARGET${path}"
done
```

## Phase 4: JS Bundle Analysis

```bash
# Download main page and find JS bundles
curl -sL 'https://TARGET/' | grep -oP 'src="[^"]+\.js[^"]*"' | sort -u

# Download each bundle
curl -sL 'https://TARGET/js/main.XXXXX.js' > /tmp/main.js

# === EXTRACTS ===

# API URLs
grep -oP 'https?://[^"'"'"'` )]+' /tmp/main.js | grep -v 'w3.org\|facebook\|cdn.|\google\|onesignal' | sort -u

# API paths
grep -oP '/api[^"'"'"' )]*' /tmp/main.js | sort -u

# GraphQL queries
grep -oP 'gql`[^`]+`' /tmp/main.js | sort -u

# Secrets
grep -oP '(api[Kk]ey|secret|password|auth|jwt|bearer|basicAuth)[:=]\s*["'"'"']?[a-zA-Z0-9_\-\.@:]{6,80}["'"'"']?' /tmp/main.js

# ES/DB connection objects
grep -oP '(username|password|host|index|basicAuth):[^}]+' /tmp/main.js

# OAuth
grep -oP 'accessToken|refreshToken|accessTokenUri|sso|oauth|authorize' /tmp/main.js

# App IDs
grep -oP '(appFacebookId|facebook.*app.*id|fb.*app_id)[:=][^,}]+' /tmp/main.js

# Localhost leak
grep -oP 'localhost:[0-9]+' /tmp/main.js

# Apollo operations count
grep -oP 'useQuery|useMutation|useLazyQuery' /tmp/main.js | sort | uniq -c | sort -rn
```

## Phase 5: Credential Verification (Elasticsearch)

```bash
# Test credentials
curl -s 'https://elastic.TARGET/' -u 'username:password' | head -10

# Count doc per index
for idx in shoppy 1688 products users orders vendors; do
  count=$(curl -s "https://elastic.TARGET/$idx/_count" -u 'username:password' -H 'Content-Type: application/json' 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('count','ERROR'))" 2>/dev/null)
  echo "$idx -> $count"
done

# Read data
curl -s "https://elastic.TARGET/shoppy/_search?pretty" -u 'username:password' -H 'Content-Type: application/json' -d '{"size":2}'

# Check role/permissions via error message
curl -s 'https://elastic.TARGET/' -u 'username:password' -H 'Content-Type: application/json'
```

## Phase 6: GraphQL

```bash
# POST
curl -s 'https://TARGET/graphql' -X POST -H 'Content-Type: application/json' -d '{"query":"query { __typename }"}'

# With auth
curl -s 'https://ws.TARGET/graphql' -X POST -u 'user:pass' -H 'Content-Type: application/json' -d '{"query":"query { __typename }"}'

# Introspection
curl -s 'https://TARGET/graphql' -X POST -H 'Content-Type: application/json' -d '{"query":"query { __schema { types { name fields { name } } } }"}'
```

## Phase 7: Misc Checks

```bash
# Clickjacking
curl -sI 'https://TARGET/' | grep -iE 'x-frame-options|content-security-policy|frame-ancestors'

# S3 bucket
curl -sI 'http://TARGET.s3-website.ap-southeast-1.amazonaws.com/'
curl -sI 'http://TARGET.s3.amazonaws.com/'

# Open redirect
curl -sI "https://TARGET//evil.com"
curl -sI "https://TARGET/?redirect=https://evil.com"

# Path traversal
curl -sI 'https://TARGET/../../../etc/passwd'
```

## Phase 8: Protected Site Detection

```bash
# Cloudflare challenge page
curl -sL 'https://TARGET/' | head -20

# Imunify360 detection
curl -s 'https://TARGET/wp-json/'

# OpenResty 415 detection
curl -sI 'https://TARGET/sitemap.xml'
```

## Phase 9: XSS Testing

```bash
# Reflected via search param
curl -s 'https://TARGET/?q=<script>alert(1)</script>' | grep -iE 'script>alert|&lt;script'

# Hash-based (SPA)
curl -s 'https://TARGET/#/<script>alert(1)</script>' | grep -i 'script>alert'

# Form parameter reflection
curl -s 'https://TARGET/login?email=<img src=x onerror=alert(1)>' | grep -iE 'img src|onerror'

# DOM-based detection
grep -oP 'dangerouslySetInnerHTML|innerHTML\s*=|outerHTML|eval\(' /tmp/*.js 2>/dev/null

# Stored XSS in ES data
curl -s 'https://elastic.TARGET/shoppy/_search' -u 'user:pass' -H 'Content-Type: application/json' \
  -d '{"query":{"bool":{"should":[{"wildcard":{"name":"*<script*"}},{"wildcard":{"name":"*<iframe*"}}]}}}'

# Cookie security check
curl -sI 'https://TARGET/' | grep -i 'set-cookie'
```

## Phase 10: Framework Fingerprinting (Expanded)

```bash
# Rails/Spree login detection
curl -s 'https://TARGET/login' | grep -oP 'spree_user|spree_|authenticity_token'

# WordPress version from Yoast/generator tags
curl -sL 'https://TARGET/' | grep -iP 'yoast|generator|wordpress'

# Cloudflare detection
curl -sI 'https://TARGET/' | grep -i 'cf-ray\|cloudflare'

# OpenResty detection
curl -s 'https://TARGET/robots.txt' 2>/dev/null | head -3 # returns openresty error page
```
