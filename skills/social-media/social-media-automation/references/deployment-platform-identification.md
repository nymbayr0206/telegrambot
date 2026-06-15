# Deployment Platform Identification

When diagnosing why an API endpoint doesn't exist, the HTTP status code alone is misleading. Different platforms return different bodies for the same 404 status. Check the **response body and headers** to identify the platform.

## Platform Signatures

| Platform | HTTP 404 Body | Response Headers |
|---|---|---|
| **Vercel (Next.js)** | Full HTML page with navigation, footer, `__NEXT_DATA__` script tags, `_next/static/` chunks. Title: `404: This page could not be found.` | `server: hcdn`, `x-hcdn-request-id:`, `platform: hostinger` (if domain proxied) |
| **Hostinger Website Builder** | HTML with `Website Builder 404` title and `assets.zyrosite.com` / `cdn.zyrosite.com` resource URLs | `x-powered-by: HostingerWebsiteBuilder`, `platform: hostinger`, `content-security-policy: frame-ancestors *.builder-preview.com *.hostinger.com` |
| **Vercel SPA (Vue.js)** | HTML page for the SPA itself, no 404 message — Vue app renders client-side | `server: Vercel`, no `x-hcdn` headers |
| **Vercel edge 404** | Small body with just `"error":"Not Found"` JSON or minimal HTML | `server: Vercel` |

## Diagnostic Commands

```bash
# Quick platform check — inspect headers
curl -sI "https://example.com" | grep -i "server\|platform\|x-powered-by"

# Check body fingerprint
curl -s "https://example.com/api/hermes/postly/brands" | head -c 200

# Look for Next.js specific tags
curl -s "https://example.com/api/hermes/postly/brands" | grep -o "next-data\|__NEXT\|_next/static" | head -3

# Look for Hostinger specific tags
curl -s "https://example.com/api/hermes/postly/brands" | grep -o "zyrosite\|builder-preview\|Hostinger" | head -3
```

## Key Rule

A Vercel 404 for a missing API route returns the full site layout (navigation, footer, Clerk scripts) because Next.js wraps all pages in the root layout. This looks identical to a working page. **The only way to distinguish is to check the `<title>` tag for "404" or look for `_not-found` in the React serialized state.**

## Session Example

In June 2026, `agenticforce.com` was on **Hostinger Website Builder** (not Vercel), while `www.postly.mn` and `agenticforceweb.vercel.app` served the same Next.js app on Vercel. The Hostinger site returned `x-powered-by: HostingerWebsiteBuilder` in production but the Vercel project was served at `www.postly.mn` with `server: hcdn`. Both resolve to the same IP — the edge proxy (hostinger) passed traffic differently per domain.
