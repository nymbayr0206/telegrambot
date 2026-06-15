# Receipt OCR → Expense Tracking → eBarimt Lottery Workflow

When the user sends a receipt/expense image, follow this end-to-end workflow:

## Step 1: OCR the Receipt

Use `ocr.space` free API (zero-dependency, works without tesseract):

```python
import base64, json, urllib.request, urllib.parse, ssl

with open('receipt.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

data = urllib.parse.urlencode({
    'base64Image': f'data:image/jpeg;base64,{img_b64}',
    'language': 'eng',       # Mongolian not supported — use eng for Cyrillic receipts
    'OCREngine': '2',
}).encode()

ctx = ssl._create_unverified_context()
req = urllib.request.Request(
    'https://api.ocr.space/parse/image',
    data=data,
    headers={
        'apikey': 'helloworld',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
)
resp = urllib.request.urlopen(req, context=ctx, timeout=30)
result = json.loads(resp.read())
text = result['ParsedResults'][0]['ParsedText']
```

**Limitations:** OCR.space doesn't support Mongolian language (returns error). English works for Cyrillic printed text but may have inaccuracies. Free key `helloworld` is rate-limited (~10 req/10s, 500/month).

## Step 2: Parse the Receipt Data

Extract from OCR text:
- **Store name** (e.g., "ОНТАЙМ ТЕХНОЛОГИ ХХК")
- **Date/time** (e.g., "2026-05-31 22:34:37")
- **Receipt number**
- **Line items** with prices — categorize each:
  - `food` (хүнс: тахианы будаа, кимчи, байцаа, etc.)
  - `transport` (тээвэр)
  - `utility` (нийтийн үйлчилгээ)
  - `business` (бизнесийн зардал)
- **Total amount**
- **Payment method** (бэлэн / бэлэн бус / карт)
- **Lottery number** (сугалааны дугаар, e.g., "AZ 11098968")
- **ДДТД** (document ID for VAT lookup)

## Step 3: Save to Finance Folder

```
/opt/data/finance/expenses/
├── ebarimt-lottery.md     # Lottery number tracker
└── YYYY/
    └── MM/
        ├── README.md       # Monthly expense summary
        ├── receipt-YYYY-MM-DD-storename.jpg  # Raw image
        └── receipt-YYYY-MM-DD-storename.json  # Structured metadata
```

### JSON Schema

```json
{
  "date": "2026-05-31",
  "time": "22:34:37",
  "store": "Store Name",
  "address": "Location",
  "receipt_number": "123",
  "items": [
    {"name": "Item description", "price": 10000, "category": "food"}
  ],
  "subtotal": 17700,
  "total": 19345,
  "payment_method": "Бэлэн бус (Card)",
  "category": "food/grocery",
  "ebarimt": {
    "lottery_number": "AZ 11098968",
    "vat_registration": "06520065870000",
    "merchant_tin": "65200658700"
  },
  "raw_image": "receipt-YYYY-MM-DD-storename.jpg",
  "notes": ""
}
```

### Monthly README.md Template

```markdown
# Финансын бүртгэл / Expense Tracker — YYYY-MM

## MM/D — Store Name
- **Төрөл:** 🍽️ Хүнс / 🚗 Тээвэр / 💼 Бизнес
- **Дүн:** XX₮
- **Сугалаа:** AZ XXXXXXXX
```

## Step 4: eBarimt Lottery Tracking

Save lottery numbers to `/opt/data/finance/ebarimt-lottery.md`:

```markdown
# eBarimt Сугалааны Бүртгэл

## YYYY-MM-DD
| Сугалааны дугаар | Дэлгүүр | Дүн | Бүртгүүлсэн? |
|-------------------|---------|-----|--------------|
| AZ 11098968 | Онтайм Технологи ХХК | 19,345₮ | ❌ |
```

The user must register lottery numbers through the ebarimt mobile app. See `references/ebarimt-api-research.md` for automated registration via Keycloak auth (requires user's ebarimt credentials — usually regNo, not email).

## Step 5: Categorize

| Category | Tag | Examples |
|----------|-----|---------|
| 🍽️ Хүнс (Food) | `food` | Chicken rice, kimchi, cabbage, grocery |
| 🚗 Тээвэр (Transport) | `transport` | Gas, taxi, bus |
| 💼 Бизнес (Business) | `business` | Equipment, software, office |
| 🏠 Өрх (Household) | `household` | Bills, utilities, rent |
| 🎮 Бусад (Other) | `other` | Entertainment, shopping |

## Notes

- This server cannot access `ebarimt.mn` (times out) — lottery registration must be done via mobile app or with credentials
- Receipt images saved in monthly subdirectories under `/opt/data/finance/expenses/`
- Memory references the base path for quick future access
