# Case Study: intermed.mn — Protected WordPress Audit

## Target Profile

- **URL:** `https://www.intermed.mn/`
- **Type:** WordPress site (Mongolian hospital/emneleg)
- **CMS:** WordPress with Yoast SEO Premium v27.2 + MonsterInsights v10.2.2
- **Protection Layers:**
  - **Cloudflare** (CDN + WAF + challenge page)
  - **Imunify360** (anti-bot module — blocks automated requests)
  - **OpenResty 1.29.2.3** (nginx + Lua) — returns 415 for non-browser traffic

## Protection Detection

### Cloudflare Challenge Page
When curl hits the homepage, Cloudflare returns a waiting room instead of the real site:
```html
<title>One moment, please...</title>
<script>
  setTimeout(function(){
    window.location.reload();
  }, 5000);
</script>
<link rel="icon" href="data:,">
```
This means the actual WordPress content is NOT accessible to automated scanners.

### Imunify360 Block
Any wp-json, REST API, or dynamic path returns:
```json
{"message": "Access denied by Imunify360 bot-protection. IPs used for automation should be whitelisted"}
```

### OpenResty 415 Responses
Most non-homepage URLs return 415 with the OpenResty error page:
```
server: openresty/1.29.2.3
```

All tested subdirectories (store, shop, appointment, booking, doctor, doctors, service, services, search, news, blog, gallery, contact, about) return 415.

### What Loads Successfully
- **Homepage** (`/`) — loads the Cloudflare waiting page
- **robots.txt** — loads (Cloudflare managed, shows Content-Signal directives)
- **Static assets** (CSS/JS from wp-content) — blocked by Imunify360
- **wp-json** — blocked by Imunify360

## Security Headers (Good)

| Header | Value |
|--------|-------|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains` (2 years) ✅ |
| `X-Frame-Options` | `SAMEORIGIN` ✅ |
| `CSP frame-ancestors` | `'self' https://www.intermed.mn` ✅ |
| `X-Content-Type-Options` | `nosniff` ✅ |
| `Referrer-Policy` | `strict-origin-when-cross-origin` ✅ |
| `X-XSS-Protection` | `0` (modern standard — disables legacy XSS filter) ✅ |

## Subdomain Takeover (CRITICAL)

ALL 19 tested subdomains return NO DNS records:

| Subdomain | Status |
|-----------|--------|
| `www.intermed.mn` | ✅ configured |
| `m`, `mail`, `admin`, `api`, `dev`, `test`, `staging` | ❌ NO DNS |
| `cdn`, `static`, `media`, `images`, `uploads` | ❌ NO DNS |
| `app`, `portal`, `doctor`, `doctors`, `booking`, `appointment`, `lab` | ❌ NO DNS |

**Impact:** An attacker could register these on CloudFront, GitHub Pages, Vercel, or Netlify and serve fake login pages, phishing forms, or malware — all under a legitimate `intermed.mn` domain.

## Version Disclosure

From the first (unblocked) request's HTML, Yoast SEO Premium v27.2 was identified via meta tags:
```html
<!-- This site is optimized with the Yoast SEO Premium plugin v27.2 -->
```

## Infrastructure

- **Cloudflare:** Edge CDN + WAF (cf-ray headers, NEL reporting, alt-svc: h3)
- **Backend Server:** OpenResty 1.29.2.3
- **OpenGraph:** Facebook app integration (article:publisher → Facebook page)
- **Analytics:** Google Analytics via MonsterInsights (G-F7E28HXR1B)
- **Sitemap:** Wordpress Yoast SEO sitemap (blocked by OpenResty)
- **REST API:** wp-json/v2 endpoints protected (401 unauthorized)

## Likely Attack Surface (not testable via CLI)

Since the site is behind Cloudflare challenge + Imunify360, these require real browser testing:

1. **Login page** — `wp-login.php` returns 404 to bots, but likely exists for real browsers
2. **Contact forms** — CF7, Formidable, or other WordPress form plugins
3. **File uploads** — `/wp-content/uploads/` blocked
4. **Plugin vulnerabilities** — Yoast SEO Premium 27.2 — check CVE database
5. **Comment XSS** — if comments are enabled and unauthenticated
6. **Appointment/booking system** — likely custom functionality

## Key Takeaways for Protected Sites

1. **Subdomain takeover is always testable** — DNS records are independent of WAF
2. **robots.txt often bypasses WAF** — Cloudflare managed robots.txt reveals Allowed paths
3. **Request fingerprinting:** Imunify360 blocks based on missing browser headers (Accept-Language, cache headers, realistic Accept order)
4. **Version info leaks from cached pages** — The initial HTML (before Cloudflare challenge clears) may still include Yoast/WP generator tags
5. **Email-based IP discovery** — MX records may reveal the origin server IP behind Cloudflare
6. **OpenResty + Imunify360 + Cloudflare** is a strong but not impenetrable stack — XSS, SQLi, and auth bypass still need manual/browser testing
