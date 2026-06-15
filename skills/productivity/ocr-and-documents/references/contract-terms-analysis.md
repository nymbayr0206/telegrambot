# Contract Terms Analysis (OCR → Financial Calculation)

Use when the user sends a scanned contract PDF and asks you to analyze terms, calculate penalties, or extract key financial data.

## Typical Flow

1. **OCR the contract** using EasyOCR workflow (see SKILL.md — easyocr section)
2. **Extract key terms** from the raw OCR text
3. **Calculate financials** based on those terms
4. **Amend deliverable report** with findings (see `references/docx-editing.md`)

## Key Terms to Extract from Mongolian Contracts

| Mongolian | English | Example |
|-----------|---------|---------|
| Гэрээний үнэ / дүн | Contract value | 19,000,000 ₮ |
| Урьдчилгаа (50%) | Prepayment | 9,500,000 ₮ |
| Үлдэгдэл төлбөр | Remaining balance | 9,500,000 ₮ |
| Хугацаа (эхлэх/дуусах) | Period (start/end) | 2026.04.09 → 2026.04.28 |
| Алданги (хувь/хоног) | Penalty (%/day) | 0.5% per day |
| Хоцорсон хоног | Days overdue | 11 days |
| Данс | Bank account | Хаан банк 5131367678 |

## Party Registration Numbers (Регистрийн дугаар)

Mongolian contracts always list the **улсын бүртгэлийн дугаар** (state registration number) of each party in the introductory paragraph — typically in the format:

```
Нэг талаас [XXXXXXX] тоот регистрийн дугаартай [Байгууллагын нэр]...
нөгөө талаас [XXXXXXX] тоот регистрийн дугаартай [Компанийн нэр]...
```

### Where to find them in the OCR output

The registration numbers are always in **Page 1** of the contract, near the top, in the party identification section. The OCR output places them adjacent to the organization names. This pattern is universal across Mongolian work execution contracts (ажил гүйцэтгэх гэрээ), supply contracts, and service agreements.

### Example from a real contract

```
OCR text:
  Нэг талаас 5673461 тоот регистрийн дугаартай Хан-Уул дүүргийн
  Тохижилт Үйлчилгээний Төв ОНӨААТҮГ-ын үйл
  ажиллагаа хариуцсан менежер Г Анхбаяр
  (цаашид Захиалагч гэх)
  нөгөө талаас 6655513 тоот регистрийн дугаартай
  Шуурхай түгээлт ХХК-ын захирал Э Цог-Эрдэнэ
  (цаашид гүйцэтгэгч гэх)

Extraction:
  → Захиалагч (Customer):  5673461  — Хан-Уул дүүргийн Тохижилт Үйлчилгээний Төв ОНӨААТҮГ
  → Гүйцэтгэгч (Contractor):  6655513  — "Шуурхай түгээлт" ХХК
```

### Pattern for the user asking "захиалагчийн регистрийн дугаар хэд вэ?"

When the user asks for a party's registration number from a contract they previously sent:

1. **Search past sessions** for the contract PDF (typically named `*Doc_Extract*` or `*гэрээ*.pdf`)
2. **Locate the OCR output** in the session data — the raw OCR text is in the terminal tool output of the session where the PDF was processed
3. **Find the introductory paragraph** of the contract — registration numbers immediately follow the phrase `...тоот регистрийн дугаартай...`
4. **Return the number** for the specified party (захиалагч = customer/orderer, гүйцэтгэгч = contractor)

### Pitfall: OCR quality on numbers

Mongolian OCR (EasyOCR with `['mn', 'en']`) sometimes misreads digits, especially when the scan is low quality or the font is small. If the registration number looks suspicious (too short, too long, or contains non-numeric characters), verify by:
- Checking the same number appears consistently across multiple OCR runs
- Looking at the original scanned image for that section of the page
- Cross-referencing with Odoo partner records if the company is known

## Penalty Calculation

### Simple formula
```
penalty = contract_value × daily_rate × days_overdue
```

### Example
```python
contract_value = 19_000_000   # 19 million MNT
daily_rate = 0.5 / 100        # 0.5% per day
days_overdue = 11             # May 23 → June 2

total_penalty = contract_value * daily_rate * days_overdue
# Result: 1,045,000 MNT
```

### Variants
- **Full contract value**: penalty on total contract amount (stricter)
- **Remaining balance only**: penalty on unpaid amount (more lenient)
- **Daily × days**: simple multiplication (not compounded — Mongolian practice)

## Date Math Pitfalls

When the user says "May 30th was the last day" and delivery is June 2:

```python
from datetime import date
deadline = date(2026, 5, 30)
delivery = date(2026, 6, 2)
days = (delivery - deadline).days  # = 3 (May 31, Jun 1, Jun 2)
```

- Python's `date arithmetic` gives calendar days between dates
- This matches Mongolian "хоног тутам" (per calendar day) interpretation
- Always double-check with the user whether they count inclusive or exclusive of the deadline day

## Common Delay Reasons (from client-side)

When documenting the reason for a postponed delivery deadline in the handover report, common patterns from this session:

- **New module request**: Client General Manager requested additional reporting modules mid-project
  - Example: Garbage truck weight reporting from 3rd party system
  - Example: Vehicle fuel consumption tracking
- **Data integration**: Connecting to a 3rd party system that was not originally scoped
- **Scope change**: Requirements added after the original deadline was set

## Documenting in the Handover Report

After calculating penalties and identifying delay reasons, the next step is to amend the deliverable/handover report (see `references/docx-editing.md` for the DOCX editing patterns). Typical additions:

1. **Revised deadline**: Change delivery date to the agreed-upon new date
2. **Delay rationale**: Paragraph explaining what caused the postponement
3. **New modules delivered**: List of additional scope items completed
