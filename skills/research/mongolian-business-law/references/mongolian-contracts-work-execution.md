# Work Execution Contracts (Ажил гүйцэтгэх гэрээ) — Session Reference

Concrete patterns and lessons from real sessions involving Mongolian work execution contract analysis, penalty calculations, and amendments.

## Contract Structure (Typical)

Based on a Хан-Уул дүүргийн Тохижилт Үйлчилгээний Төв × "Шуурхай түгээлт" ХХК contract (2026):

| Section | Content |
|---------|---------|
| **1. Гэрээний зүйл** | Subject — ERP system development for garbage collection management |
| **2. Талуудын эрх үүрэг** | Rights & obligations of both parties |
| **3. Гүйцэтгэх хугацаа** | Performance period (with start/end dates, extensions) |
| **4. Үнэ ба төлбөр тооцоо** | Price and payment terms |
| **5. Хариуцлага** | Liability — including penalty (алданги) clauses |
| **6. Давагдашгүй хүчин зүйл** | Force majeure |
| **7. Маргаан шийдвэрлэх** | Dispute resolution |
| **8. Эцсийн заалт** | Final provisions including amendment clause (9.1 — all amendments must be in writing, signed by both parties) |

## Penalty Calculation Pattern

### Scenario: ERP Delivery Delay
- **Contract value**: 19,000,000 ₮ (19 сая)
- **Remaining balance**: 9,500,000 ₮ (9.5 сая)
- **Penalty rate**: 0.5% per day (from contract clause)
- **Daily penalty on full amount**: 19M × 0.5% = 95,000 ₮/day
- **Daily penalty on remaining**: 9.5M × 0.5% = 47,500 ₮/day

### Key Issue: Which Base Amount?
Mongolian contracts often specify penalty as percentage of either:
- **Full contract amount (нийт дүн)** — even if partial payment made
- **Remaining unpaid balance (үлдэгдэл)** — only on what's still owed

Always verify the exact clause wording. Ambiguity here is common and can be negotiated.

### Date Negotiation Leverage
When the **client (захиалагч)** causes the delay by requesting additional features:
- The penalty start date can be reset to the new agreed deadline
- The penalty can be argued away entirely under clause 4.1 (захиалагчийн мэдээлэх үүрэг — client's obligation to provide information)
- A formal supplementary agreement (нэмэлт гэрээ) should document the scope change, new deadline, and whether penalties apply

### Amendment Documentation
Required elements in a Mongolian contract amendment (нэмэлт гэрээ):
1. **Reference to original contract** — date, number, parties
2. **Reason for amendment** — specific circumstances (e.g., client requested additional modules)
3. **New terms** — changed deadlines, scope items, or payment terms
4. **Signature block** — both parties sign
5. **Date of amendment**

## Workflow: User Submits Scanned Contract

1. **OCR** — Use EasyOCR with Mongolian (`mn`) language support
2. **Page-by-page extraction** — Render each page as image, OCR, concatenate
3. **Structured summary** — Parties → Subject → Price → Deadlines → Penalties → Amendment clause
4. **No direct PDF editing** — Scanned PDFs are image-based. Always draft a separate amendment document (нэмэлт гэрээ) as a new file
5. **Delivery report modification** — If user has a DOCX delivery report that needs editing, have them re-upload it (Telegram doesn't preserve uploaded DOCX files across sessions in the system)
