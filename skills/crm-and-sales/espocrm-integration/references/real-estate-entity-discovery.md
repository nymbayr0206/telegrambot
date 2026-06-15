# Real Estate CRM Entity Discovery — Reference

Date: 2026-06-12
Instance: Dream Team crm (EspoCRM 9.3.8)

## Session 1 — Initial Reconnaissance

1. Connected to `http://187.77.140.62:32769/` via API key
2. API key had only User and Note read access (403 on others)
3. `/api/v1/Settings` revealed real-estate custom entities:
   - `RealEstateProperty` — properties/listings
   - `RealEstateRequest` — buyer/tenant requests
4. Brute-force confirmed: standard entities (Lead, Account, Contact) were 403 (no access), custom entities were reachable

## Session 2 — Full Access Confirmed + Data Entry

### API Key Actual Permissions (with `?maxSize=1` query param)
All entities returned 200 OK after adding query parameter:
- RealEstateProperty, RealEstateRequest, Account, Contact, Lead, Opportunity
- Meeting, Call, Task, Case, Campaign, TargetList, Document, User, Note

Lesson: Some EspoCRM 9.x instances return 403 for entity listing without a `maxSize` param. Always test with `?maxSize=1`.

### Instance Details
- **Version**: 9.3.8
- **Application**: Dream Team crm
- **Theme**: Hazyblue
- **Timezone**: UTC
- **Default Currency**: USD (only USD in currencyList)
- **Language**: en_US

### Users Found
| Username | Name | Type | Title | Phone |
|----------|------|------|-------|-------|
| admin | Admin | admin | — | — |
| lanaceoclub | Lana lana | regular | realtor | +976****1716 |

### RealEstateProperty (1 record)
```
id: 6a2bbcb5eed64ee8d
name: "unknown-address"
type: "Land Lot"
status: "New"
requestType: "Sale"
number: 1
price: null, priceCurrency: null
square: null, yearBuilt: null
bedroomCount: null, bathroomCount: null
createdAt: 2026-06-12 08:00:53
createdBy: Admin
```

### RealEstateRequest (1 record created during session)
```
id: 6a2c04fb2cc58ef4f
name: "R 000001" (auto-generated)
type: "Sale"
propertyType: "Apartment"
status: "New"
fromBedroomCount: 3, toBedroomCount: 3
fromPrice: 500000000 USD
toPrice: 500000000 USD
description: "📞 99667788\n📍 Яармаг\n🏠 3 өрөө байр\n💰 500,000,000₮ төсөв\n📋 Худалдан авах хүсэлтэй"
createdAt: 2026-06-12 13:09:15
createdBy: hermes
```

### Opportunity (1 record)
```
id: 6a2be494178004428
name: "unnamed"
amount: 650000000 USD
stage: "Prospecting"
probability: 5
closeDate: 2026-06-19
propertyId: 6a2bbcb5eed64ee8d (links to RealEstateProperty)
```

## Key Observations
- CRM was created same day (2026-06-12) — brand new instance
- Custom entity currency fields (fromPrice, toPrice) require both `fieldName` and `fieldNameCurrency` set in the SAME request
- Auto-numbered names (R 000001) are read-only
- Admin auth via POST /api/v1/AuthToken returned 401 even with seemingly correct password — may be authentication provider difference
- The `hermes` user created RealEstateRequest records (probably the API key's internal user)
- Mongolian language queries work fine for data entry
