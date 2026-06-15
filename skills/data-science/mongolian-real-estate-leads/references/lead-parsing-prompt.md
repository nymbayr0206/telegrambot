# Mongolian Lead Parsing Prompts

LLM prompts for extracting structured real estate lead data from Mongolian voice transcripts.

## Full Prompt (DeepSeek / Cheap Model)

```
Та Монгол хэл дээрх үл хөдлөх хөрөнгийн үйлчлүүлэгчийн 
дуут бичлэгийн транскриптыг задлан шинжилж, дараах JSON 
форматаар хариулах AI туслах байна.

Транскрипт:
{transcript}

Дараах талбаруудыг гаргаж авна уу:
- client_name: Үйлчлүүлэгчийн нэр (байхгүй бол null)
- phone: Утасны дугаар (байхгүй бол null)
- property_type: "apartment" | "house" | "land" | "commercial" | "office"
- bedrooms: Өрөөний тоо (тоо, байхгүй бол null)
- district: Дүүргийн нэрс (массив)
- budget_min: Хамгийн бага төсөв (төгрөгөөр, байхгүй бол null)
- budget_max: Хамгийн их төсөв (төгрөгөөр, байхгүй бол null)
- buy_or_rent: "buy" | "rent"
- urgency: "low" | "medium" | "high" | "immediate"
- lead_score: 0-100 хүртэлх тоо
- lead_score_reason: Онооны тайлбар (монголоор)
- notes: Бусад мэдээлэл

Зөвхөн JSON хариулна уу. Бусад тайлбар, текст оруулж болохгүй.
```

## Short Prompt (for faster/cheaper inference)

```
Extract from Mongolian real estate voice transcript. Return ONLY JSON:
{transcript}

Fields: client_name, phone, property_type, bedrooms, district[],
budget_min, budget_max, buy_or_rent, urgency, lead_score(0-100),
lead_score_reason, notes
```

## Examples

### Input:
"Сайн байна уу, би Болормаа гэж байна. Надад 200 сая хүртэлх үнэтэй, 
Баянзүрх дүүрэгт 2 өрөө байр хэрэгтэй байна. Энэ сардаа авах гэж 
бодож байна. Утасны дугаар 99123456."

### Expected Output:
```json
{
  "client_name": "Болормаа",
  "phone": "99123456",
  "property_type": "apartment",
  "bedrooms": 2,
  "district": ["Баянзүрх"],
  "budget_min": null,
  "budget_max": 200000000,
  "buy_or_rent": "buy",
  "urgency": "high",
  "lead_score": 85,
  "lead_score_reason": "Тодорхой шаардлагатай, төсөв, дүүрэг, утасны дугаараа өгсөн, энэ сардаа худалдаж авахаар төлөвлөж байна",
  "notes": null
}
```

## Scoring Rules

| Factor | Points | Condition |
|--------|--------|-----------|
| Specific property type | +10 | Explicitly stated |
| Bedroom count | +10 | Explicitly stated |
| District preference | +10 | 1+ districts named |
| Budget specified | +15 | Any budget amount |
| Budget range given | +20 | Both min and max |
| Short timeline | +25 | "энэ сар", "дараа 7 хоног" |
| Medium timeline | +15 | "ойрын үед", "удахгүй" |
| Phone provided | +15 | Phone number in transcript |
| Buyer (vs renter) | +10 | "худалдаж авах" |
| Referred | +15 | "танил зөвлөсөн" |
| Total max | 100 | |
