# Dream Team CRM Instance

| Property | Value |
|---|---|
| **URL** | http://187.77.140.62:32769/ |
| **API Base** | http://187.77.140.62:32769/api/v1/ |
| **API Key** | `e9a86a254bf03ff29c220e2c63c9b0f1` |
| **Auth Header** | `X-Api-Key` |
| **EspoCRM Version** | 9.3.8 |
| **Name** | Dream Team crm |
| **Type** | Real Estate CRM |

## Users

| ID | Name | Username | Role |
|---|---|---|---|
| `6a2bba573119bd70e` | Admin | admin | admin |
| `6a2bbef6a311a0b49` | Lana lana | lanaceoclub | regular (realtor) |

## Currency

Only **USD** is configured in `currencyList`. MNT is not supported — all amounts are in USD.

## Current Records (as of 2026-06-12)

### RealEstateProperty (3)

| ID | Name | Type | Request | Status | Price | Details |
|---|---|---|---|---|---|---|
| `6a2bbcb5eed64ee8d` | unknown-address | Land Lot | Sale | New | — | — |
| `6a2...4509` | Яармаг | Apartment | **Rent** | New | — | 3 өрөө. Owner: 88998899 |
| `6a2...9709` | 13-р гудамж, УБ | Separate House | Sale | New | 1B | 5 bed |

### RealEstateRequest (2 active)

| # | Phone | Location | Type | Budget | Notes |
|---|---|---|---|---|---|
| **R 000001** | 99667788 | Яармаг | Sale, 3 өрөө | 500M USD | Created 2026-06-12 |
| **R 000003** | 80001059 | Хан-Уул | Rent, 3 өрөө | — | ⏰ Follow-up **2026-06-26** (client in countryside) |

### Accounts (1)

| ID | Name | Phone | Address |
|---|---|---|---|
| `6a2c446a0bba315ff` | RE/MAX 100% | +97672700100 | Romana Residence - 1104, Хан-Уул, 15-р хороо |

### Contacts (1)

| ID | Name | Phone | Account | Title |
|---|---|---|---|---|
| `6a2c446a18f70df5b` | Lkhamsuren Oyun (remax100) | +97688117615 | RE/MAX 100% | Realtor |

### Leads (3)

| ID | Name | Phone | Status | Source |
|---|---|---|---|---|
| `6a2c0a369e113d9b4` | 80001059 Хан-Уул | +97680001059 | New | Call |
| `6a2c0a52aec85f286` | 99667788 Яармаг | +97699667788 | New | Call |
| `6a2c41d966fe63328` | 88998899 Яармаг (түрээслүүлэгч) | +97688998899 | New | Call |

### Tasks (1 active)

| ID | Name | Due | Priority |
|---|---|---|---|
| `6a2c08f0ca03c48f6` | 80001059 руу залгах - Хан-Уул 3 өрөө түрээс | 2026-06-26 09:00 | High |

### Cron Jobs (2)

| Name | Schedule | Purpose |
|---|---|---|
| Өглөөний CRM Task сануулга | Daily 00:00 UTC (08:00 ULAT) | Check EspoCRM tasks due today → Telegram reminder (silent if none) |
| 80001059 руу залгах сануулга | One-shot 2026-06-26 01:00 UTC (09:00 ULAT) | Specific follow-up reminder |

### Opportunity (1)

| ID | Name | Amount | Stage | Close Date |
|---|---|---|---|---|
| `6a2be494178004428` | unnamed | 650M USD | Prospecting | 2026-06-19 |

## Calls Log (3)

| ID | Name | Contact | Duration | Direction | Linked To |
|---|---|---|---|---|---|
| `6a2c085977f53f7c6` | 80001059 - Хан-Уул 3 өрөө түрээс | 80001059 | 10min | Outbound | R 000003 |
| `6a2c08be10e859a76` | 80001059 - Хөдөө явсан, 2 долоо хоногийн дараа залгах | 80001059 | 5min | Outbound | R 000003 |
| `6a2c08f0ca03c48f6` | 88998899 - Яармаг 3 өрөө байр түрээслүүлнэ | 88998899 | 5min | Outbound | Property Яармаг |

## Hosting

- EspoCRM runs in a separate Docker container on the same host
- Only ports **32768** (uvicorn/Hermes gateway) and **32769** (Apache/EspoCRM) are externally accessible
- This agent runs in a different container sharing only `/opt/data` via Docker volume
- No web server is available in this container — files in `/opt/data/www/` are not externally served
- To share files externally: use MEDIA: delivery via Telegram, or upload to EspoCRM as Attachment entities
