# eBarimt API Research — Mongolian Digital Receipt & Lottery System

## Overview

eBarimt is Mongolia's electronic receipt system, operated by ITC (Мэдээлэл, Технологийн Төв). It covers:
- POS receipt registration (merchants issuing VAT receipts)
- Consumer lottery registration (citizens registering receipt lottery numbers)
- VAT cashback and reporting

## Auth Server (Keycloak)

```
Auth endpoint:  https://auth.itc.gov.mn/auth/realms/ITC/protocol/openid-connect/token
Auth realm:     ITC
Client ID:      vatps
Grant types:    password, authorization_code, refresh_token, client_credentials
```

### Keycloak Configuration Discovery

```
Realm well-known:  https://auth.itc.gov.mn/auth/realms/ITC/.well-known/openid-configuration
Supported grant types: authorization_code, implicit, refresh_token, password, client_credentials,
                       urn:openid:params:grant-type:ciba, urn:ietf:params:oauth:grant-type:token-exchange,
                       urn:ietf:params:oauth:grant-type:device_code
```

Note: The client "vatps" accepts password grant. `invalid_grant` means bad credentials (wrong username/password), not a client configuration issue. There is no staging realm — "Staging" returns "Realm does not exist".

## Consumer Login Flow

The consumer login at `service.itc.gov.mn` redirects to Keycloak:

```
https://auth.itc.gov.mn/auth/realms/ITC/login-actions/authenticate?session_code=...&execution=...&client_id=vatps&tab_id=...
```

Form fields: `username` (hidden), `password`, `rememberMe`, `credentialId`, `login` (submit).

**Known limitation:** The Keycloak session_code expires quickly. A fresh session must be obtained for each login attempt.

## API Servers

| Server | Purpose | Accessible? |
|--------|---------|-------------|
| `auth.itc.gov.mn` | Keycloak auth | ✅ Yes |
| `service.itc.gov.mn` | Consumer (easy-register) APIs | ✅ Yes (HTTP 302 → Keycloak) |
| `ebarimt.techpartners.asia` | Production POS + info APIs | ✅ Yes (some endpoints) |
| `api.ebarimt.mn` | Merchant POS API 3.0 (production) | ❌ Timeout |
| `st-api.ebarimt.mn` | Merchant POS API 3.0 (staging) | ❌ Timeout |
| `ebarimt.mn` | Consumer web portal | ❌ Timeout (SPA, JS-heavy) |
| `lottery.ebarimt.mn` | Lottery portal | ❌ Timeout |
| `developer.itc.gov.mn` | API documentation (Stoplight) | ✅ Yes (docs only) |

## Consumer API Endpoints (via service.itc.gov.mn, auth required)

From the POS 3.0 Go SDK (`github.com/techpartners-asia/ebarimt-pos3-go`):

```
# Easy Register (хялбар бүртгэл) — consumer-facing
ConsumerInfo:   GET  https://service.itc.gov.mn/api/easy-register/api/info/consumer/{regNo}
GetProfile:     POST https://service.itc.gov.mn/api/easy-register/rest/v1/getProfile
ApproveQR:      POST https://service.itc.gov.mn/api/easy-register/rest/v1/approveQr

# Foreigner registration
ForiegnerPassportInfo:  GET  https://service.itc.gov.mn/api/easy-register/api/info/foreigner/{passportNo}/{fNumber}
ForiegnerInfoRegister:  PUT  https://service.itc.gov.mn/api/easy-register/api/info/foreigner/{passportNo}
```

## Public (No-Auth) Info Endpoints

```
# TIN/Lookup info (no auth required)
GetTinInfo:   GET https://ebarimt.techpartners.asia/api/info/check/getTinInfo?regNo={regNo}
GetBranchInfo: GET https://ebarimt.techpartners.asia/api/info/check/getBranchInfo
GetInfo:      GET https://ebarimt.techpartners.asia/api/info/check/getInfo?tin={tin}
```

## POS Receipt API (merchant-facing)

Not applicable for consumer lottery registration. Requires merchant credentials (apiKey, merchantTin, posNo).

## Receipt Image OCR → eBarimt Workflow

1. User sends receipt image (photo of paper receipt with QR/DDTD/lottery number)
2. OCR via `ocr.space` API (free key: `helloworld`) or tesseract
3. Parse: store name, date, items, total, ДДТД, lottery number
4. Save to `/opt/data/finance/expenses/YYYY/MM/` as JSON + raw image
5. Log lottery number at `/opt/data/finance/ebarimt-lottery.md`
6. To register: user must either:
   - Use mobile app (Scan QR/enter lottery number manually)
   - Or provide ebarimt credentials (username = usually regNo, not email) for automated login

## Credentials Note

eBarimt consumer accounts are usually registered by **регистрийн дугаар** (register number), not email. Email + password login may fail with `invalid_grant` if the account was created with a register number as the username.

## References

- POS 3.0 Go SDK: https://github.com/techpartners-asia/ebarimt-pos3-go
- POS 3.0 API docs: https://developer.itc.gov.mn/docs/ebarimt-api
- Consumer app (Google Play): `com.itc.vatps.mobile.app`
- Consumer app (old): `mn.mta.vatps`
