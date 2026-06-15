# EspoCRM 9.x REST API — Real Estate CRM Reference

## Connection

```
Host: http://<ip>:<port>/
API Root: /api/v1/  → "EspoCRM REST API"
Auth: X-Api-Key header (not Bearer, not Basic)
```

## Auth — Admin Web Login

```
POST /api/v1/AuthToken
Content-Type: application/json
{"userName": "admin", "password": "<password>"}
→ 200 + token  OR 401 Unauthorized
```

API keys are managed via **Administration > API Keys** in the web UI. An API key that returns 403 on most endpoints has no read access — edit roles in the web UI.

## Key Entities (Dream Team crm — Real Estate)

| Entity | Purpose | Notes |
|--------|---------|-------|
| `RealEstateProperty` | Property listings | type, status, requestType (Sale/Rent), price, bedroomCount |
| `RealEstateRequest` | Client inquiries | type (Sale/Rent), propertyType, fromPrice/toPrice, fromBedroomCount/toBedroomCount |
| `Lead` | Standard CRM lead | firstName, lastName, phoneNumber |
| `Account` | Company/developer | |
| `Contact` | Person contact | |
| `Opportunity` | Deal pipeline | amount (currency), stage, closeDate |
| `Call` | Phone call log | Linked via parentType+parentId |
| `Note` | Internal notes | |
| `User` | System users | |
| `Settings` | System config | Shows active entities, currency list, tabs |

## RealEstateRequest CRUD

### Create
```json
POST /api/v1/RealEstateRequest
X-Api-Key: <key>
Content-Type: application/json
{
  "description": "📞 99112233\n📍 Хан-Уул\n🏠 3 өрөө байр\n📋 Түрээслэх",
  "type": "Sale",          // or "Rent"
  "propertyType": "Apartment",
  "fromBedroomCount": 3,
  "toBedroomCount": 3,
  "fromPrice": 500000000,
  "fromPriceCurrency": "MNT",
  "toPrice": 500000000,
  "toPriceCurrency": "MNT",
  "status": "New"
}
```

**Gotchas:**
- `name` is auto-generated (R 000001, R 000002…) and cannot be overridden via PUT
- IDs are strings (e.g., `6a2c04fb2cc58ef4f`)
- Currency and property/enum fields MUST be set in the **same PUT call** or validation fails

### Update
```json
PUT /api/v1/RealEstateRequest/{id}
{
  "description": "Updated info",
  "status": "In Process"
}
```

### List
```
GET /api/v1/RealEstateRequest?maxSize=20
GET /api/v1/RealEstateRequest?maxSize=1&offset=0
```

## Currency Field Gotcha

EspoCRM 9.x currency fields need **both** value and currency in the **same request**:

```json
// ✅ Works — value + currency together
{"fromPrice": 500000000, "fromPriceCurrency": "USD"}

// ❌ Fails — "validCurrency" validation error
{"fromPrice": 500000000}

// ❌ Also fails — currency alone, then value later
```

The system's currency list is in Settings → `currencyList`. Only configured currencies pass validation.

## Call Entity — Logging Phone Conversations

```json
POST /api/v1/Call
{
  "name": "99112233 - Хан-Уул 3 өрөө",
  "dateStart": "2026-06-12 13:00:00",
  "dateEnd": "2026-06-12 13:10:00",
  "durationMinutes": 10,
  "status": "Held",              // Held | Planned | Not Held
  "direction": "Outbound",       // Outbound | Inbound
  "description": "Ярилцсан дэлгэрэнгүй...",
  "parentType": "RealEstateRequest",
  "parentId": "6a2c07759d4f56cdc",
  "assignedUserId": "6a2bba573119bd70e"  // REQUIRED
}
```

**Required fields:** name, dateStart, dateEnd, assignedUserId
**Linking:** parentType + parentId connects the call to any entity

## Metadata / Discovery

Standard entities are listed in `GET /api/v1/metadata/entityDefs` → aclDefs.
Custom entities (RealEstateProperty, RealEstateRequest) may not appear there but still respond to CRUD.
Settings endpoint: `GET /api/v1/Settings` shows tabList, quickCreateList, globalSearchEntityList, currencyList.

## User Info from Session

- Admin user: `6a2bba573119bd70e` (admin)
- hermes (API key auto-user): `6a2bfde61e6074611`
- Lana (realtor): username `lanaceoclub`, UD: `6a2bbef6a311a0b49`
- All 3 users created 2026-06-12
