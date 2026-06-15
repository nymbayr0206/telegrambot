# eBarimt / МТА API Research Notes

## Overview

API research for Mongolia's official e-receipt system (ebarimt.mn), run by the Tax Authority (Татварын Ерөнхий Газар / ITC). Two separate API surfaces exist:

1. **POS API 3.0** — for merchants to issue receipts (well-documented on developer.itc.gov.mn)
2. **Consumer / Mobile App API** — for citizens to register receipts, check lottery, etc.

This file documents the **consumer-side** API discovered via mobile app traffic analysis.

## Key Discovery: Authentication Server

| Component | URL |
|-----------|-----|
| Keycloak realm | `https://auth.itc.gov.mn/auth/realms/ITC` |
| Token endpoint | `https://auth.itc.gov.mn/auth/realms/ITC/protocol/openid-connect/token` |
| Consumer API server | `https://service.itc.gov.mn` |
| POS API (production) | `https://ebarimt.techpartners.asia` |
| POS API (staging) | `https://st-api.ebarimt.mn` |
| POS API (dev) | `https://ebarimt.techpartners.asia` |
| Web app | `https://ebarimt.mn` |
| Lottery site | `https://lottery.ebarimt.mn` |

## Keycloak Auth Flow

The consumer mobile app authenticates via Keycloak OpenID Connect with:

- **Realm:** `ITC`
- **Client ID:** `vatps` (confirmed working — accepts password grant)
- **Grant type:** `password` (resource owner password credentials)

```bash
curl -X POST "https://auth.itc.gov.mn/auth/realms/ITC/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=vatps&username=<REGNO>&password=<PASSWORD>"
```

**Note:** The username is the user's **регистрийн дугаар** (register number), NOT their email. The email/password combo used for other Google accounts will NOT work — the user must be registered on ebarimt.mn first.

**Observed errors:**
- `invalid_client` — wrong client_id
- `invalid_grant` — wrong username/password (client exists but credentials don't match)
- `unauthorized_client` — client exists but not allowed for password grant

## Consumer API Endpoints

Base: `https://service.itc.gov.mn/api/easy-register/`

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/info/consumer/{regNo}` | GET | Bearer | Get consumer info by reg number |
| `/rest/v1/getProfile` | POST | Bearer | Get user profile |
| `/rest/v1/approveQr` | POST | Bearer | Approve QR receipt registration |
| `/sso/login` | GET | No | SSO login page (redirects to Keycloak) |

## Known Pitfalls

1. **ebarimt.mn blocks curl/bots.** The main website (`ebarimt.mn`) and subdomains (`api.ebarimt.mn`, `st-api.ebarimt.mn`) all return HTTP 000 (connection timeout) from this server — likely geo-blocking or Cloudflare. The Keycloak auth server (`auth.itc.gov.mn`) and consumer API server (`service.itc.gov.mn`) ARE reachable, so the API flow works even when the website doesn't.

2. **Consumer registration for lottery.** The ebarimt mobile app (currently `com.itc.vatps.mobile.app` on Google Play) allows citizens to register receipts by:
   - QR code scan
   - Entering ДДТД (document number)
   - Entering сугалааны дугаар (lottery number) directly
   
   There is no known public consumer API for automated lottery registration. The mobile app communicates with `service.itc.gov.mn` internally.

3. **No public consumer API.** The POS API 3.0 (documented at `developer.itc.gov.mn`) is for merchants to issue receipts. Consumer-facing features (lottery registration, receipt lookup) are only available through the mobile app or the ebarimt.mn website.

4. **LOTTERY NUMBERS CAN BE SAVED LOCALLY.** Since there's no programmatic API for lottery registration, save lottery numbers to the local tracker at `/opt/data/finance/ebarimt-lottery.md` and remind the user to register via the mobile app.

## Service Accessibility

| Service | Reachable? | Notes |
|---------|-----------|-------|
| `auth.itc.gov.mn:443` | ✅ Yes | Keycloak SSO |
| `service.itc.gov.mn:443` | ✅ Yes | Consumer API |
| `ebarimt.techpartners.asia:443` | ✅ Yes | POS/proxy API |
| `ebarimt.mn:443` | ❌ No | Geo-blocked / bot protection |
| `api.ebarimt.mn:443` | ❌ No | Same as above |
| `lottery.ebarimt.mn:443` | ❌ No | Same as above |
| `share.itc.gov.mn:443` | ❌ No | Auth CSR |

## Reference

- GitHub: `github.com/techpartners-asia/ebarimt-pos3-go` — Go POS API 3.0 SDK (shows all consumer endpoints)
- GitHub: `github.com/lambda-platform/ebarimt-rest-api` — REST API wrapper
- Docs: `https://developer.itc.gov.mn/docs/ebarimt-api/8mw1byololjkv-cz-ahim-t-lb-rijn-barimtyn-sistem-pos-api-3-0`
