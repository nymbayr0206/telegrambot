---
name: personal-expense-tracking
description: "OCR Mongolian receipts, categorize purchases, save to organized expense folders, and track eBarimt lottery numbers for government VAT lottery."
version: 1.1.0
author: Hermes Agent
metadata:
  hermes:
    tags: [finance, expense, receipt, ocr, ebarimt, mongolia, tracking]
    related_skills: [ocr-and-documents]
---

# Personal Expense Tracking

## When to Use

- User sends a receipt/bill image (paper or screenshot) and asks to save it
- User asks to track, categorize, or log daily/weekly/monthly expenses
- User asks about eBarimt VAT lottery registration for Mongolian receipts
- User asks "what did I spend on X category" or "show my expenses"

## Workflow

### 1. Receive the receipt image

The user typically sends a photo of a paper receipt or a screenshot of an e-receipt. Save it immediately to the image cache if not already there.

### 2. OCR the receipt

Use the **OCR.space free API** (zero-dependency, works without tesseract):

```python
import base64, json, urllib.request, urllib.parse, ssl

with open('receipt.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

data = urllib.parse.urlencode({
    'base64Image': f'data:image/jpeg;base64,{img_b64}',
    'language': 'eng',  # 'mongolian' NOT supported by OCR.space; use 'eng' for Cyrillic
    'OCREngine': '2',    # Best accuracy engine
}).encode()

ctx = ssl._create_unverified_context()
req = urllib.request.Request(
    'https://api.ocr.space/parse/image',
    data=data,
    headers={'apikey': 'helloworld', 'Content-Type': 'application/x-www-form-urlencoded'}
)
resp = urllib.request.urlopen(req, context=ctx, timeout=30)
result = json.loads(resp.read())
text = result['ParsedResults'][0]['ParsedText']
```

**Pitfall:** OCR.space does NOT support `language=mongolian`. Use `eng` — it handles Mongolian Cyrillic printed text reasonably well. The free key `helloworld` is rate-limited (~10 req/10s, 500/month).

### 3. Extract structured data from OCR output

Parse the raw text to extract:
- **Store name** (e.g. "ОНТАЙМ ТЕХНОЛОГИ ХХК", "НОМин супермаркет", etc.)
- **Date and time** (Mongolian receipts use format: `Огноо: 2026-05-31 22:34:37`)
- **Receipt number** (`Баримтын дугаар:`)
- **Items** (numbered lines with item name and price)
- **Subtotal, VAT, Total** (ММДТ, ДДТД, Нийт дүн / Телех дүн)
- **Payment method** (Бэлэн / Бэлэн бус / Карт / QPay)
- **eBarimt lottery number** (`Сугалааны дугаар:` followed by code like `AZ 11098968`)
- **Merchant VAT/TIN** (`ДДТД:` / регистрийн дугаар)

Mongolian receipt item format is typically:
```
1 барааны_нэр 10000
2 барааны_нэр 2500
```

Price lines may be scattered — group items by proximity and price values to reconstruct line items.

### 4. Categorize the expense

| Category | Examples |
|----------|----------|
| `food/grocery` | Хүнс, зайрмаг, мах, хүнсний ногоо, талх, сүү, чихэр, ундаа |
| `food/restaurant` | Ресторан, гуанз, кафе, хоолны газар, захиалга |
| `transport` | Такси, автобус, шатах тослоо, бензин, замын хураамж |
| `shopping` | Хувцас, гутал, цахилгаан бараа, гэр ахуйн бараа |
| `health` | Эм, эмнэлэг, оношилгоо, аптек |
| `bills/utilities` | Цахилгаан, ус, дулаан, интернет, утас |
| `education` | Сургалт, ном, сурах бичиг |
| `entertainment` | Кино, тоглоом, спорт, зугаа цэнгэл |
| `other` | Бусад |

When category is ambiguous, use the store name + item names to decide. A receipt from "Онтайм Технологи" with chicken rice, kimchi, and cabbage is `food/grocery`.

### 5. Save to folder structure

```
/opt/data/finance/
  expenses/
    YYYY/
      MM/
        receipt-YYYY-MM-DD-storename.jpg     (original image)
        receipt-YYYY-MM-DD-storename.json    (structured metadata)
        README.md                             (monthly summary)
  ebarimt-lottery.md                          (lottery number tracker)
```

### 6. Create JSON metadata

```json
{
  "date": "2026-05-31",
  "time": "22:34:37",
  "store": "Store Name",
  "items": [
    {"name": "Item name", "price": 10000, "category": "food/grocery"},
    {"name": "Item name", "price": 2500, "category": "food/grocery"}
  ],
  "subtotal": 12500,
  "vat": 1250,
  "total": 13750,
  "payment_method": "Бэлэн бус",
  "category": "food/grocery",
  "ebarimt": {
    "lottery_number": "AZ 11098968",
    "merchant_tin": "65200658700"
  },
  "raw_image": "receipt-YYYY-MM-DD-storename.jpg"
}
```

### 7. Update eBarimt lottery tracker

Append to `/opt/data/finance/ebarimt-lottery.md`:

```markdown
## YYYY-MM-DD
| Сугалааны дугаар | Дэлгүүр | Дүн | Огноо | Бүртгүүлсэн? |
|-------------------|---------|-----|-------|--------------|
| AZ XXXXXXXX | Store | X,XXX₮ | YYYY-MM-DD | ❌ Бүртгээгүй |
```

### 8. Update monthly README

Append entry to `/opt/data/finance/expenses/YYYY/MM/README.md`.

### 9. Tell the user

Present a clean summary: store, date, items with prices, total, category, and lottery number. Remind them to register the lottery number in the eBarimt app.

## eBarimt Lottery

Mongolia's VAT lottery (ebarimt.mn) lets consumers win prizes by registering receipt lottery numbers.

**How the user registers (manual):**
1. Open eBarimt mobile app
2. Select "Сугалааны дугаар бүртгүүлэх"
3. Enter the lottery number (e.g. `AZ 11098968`)
4. Submit

### Automated registration via API (partial)

The ebarimt consumer system does have a REST API — it's the same backend the mobile app uses — but authentication requires the user's **ebarimt account credentials** (typically their регистрийн дугаар/register number + password, NOT their email/password).

**Known API details (for future automation attempts):**
- **Auth:** Keycloak OpenID Connect at `https://auth.itc.gov.mn/auth/realms/ITC/protocol/openid-connect/token`
- **Client ID:** `vatps` (accepts `grant_type=password`)
- **Consumer API server:** `https://service.itc.gov.mn/api/easy-register/`
- **Consumer info:** `GET /api/info/consumer/{regNo}`
- **Get profile:** `POST /rest/v1/getProfile`
- **Approve QR:** `POST /rest/v1/approveQr`
- **Login redirects through:** `https://auth.itc.gov.mn/auth/realms/ITC/login-actions/authenticate`

**Limitations:**
- The user must have an active ebarimt account (registered at ebarimt.mn)
- The account username is their **регистрийн дугаар** (citizen register number), NOT their email
- The site (`ebarimt.mn`) and API servers (`api.ebarimt.mn`) may be geo-blocked outside Mongolia
- If the user provides their register number + password, a future session can attempt the full OAuth2 flow + receipt registration
- For now, the agent's safe fallback is to **track** lottery numbers and instruct the user to register via the mobile app

**When to attempt automation:** Only if the user explicitly provides their ebarimt register number and password. Do NOT attempt with email-based credentials — the Keycloak realm rejects them with `invalid_grant`.

## File Naming Convention

```
receipt-YYYY-MM-DD-storename.jpg
receipt-YYYY-MM-DD-storename.json
```

- Date from the receipt itself (not the upload date)
- Store name: lowercase, hyphens for spaces, transliterate Cyrillic to Latin (e.g. `ontime`, `nomin`, `emart`)
- Keep it short but identifiable

## Pitfalls

1. **OCR.space doesn't support Mongolian language param** — use `eng` instead. Cyrillic printed text reads fine with engine 2.
2. **Mongolian receipt text is fragmented** — prices and items may be on separate lines. Reconstruct by proximity.
3. **No tesseract available** — Don't attempt to install tesseract (requires root). OCR.space API is the reliable fallback.
4. **Image format** — JPEG works best. Very large images (>1MB) may be rejected by OCR.space free tier.
5. **eBarimt lottery numbers** — Always extract and save. The user WILL forget to register them if we don't track.
6. **Unclear category** — Default to `other` rather than guessing. The user can recategorize later.
7. **OCR quality varies** — Some receipts may have poor OCR output. Do your best to reconstruct, and note uncertain values in JSON `notes` field.
