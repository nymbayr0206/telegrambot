# Pinnacle Playbook II — Source Map & Closing Secrets Reference

**Title:** Team Pinnacle Playbook, 2nd Edition
**Author:** Eric Olson / Ethereal
**KB location:** `/opt/data/knowledge_bases/team_pinnacle_playbook_ii/`

## ⚠️ Status: PDF Extracted Text Missing

The extracted text file (`team_pinnacle_playbook_ii_extracted.txt`) was cleaned from disk. Only the summarized KB modules remain. To regenerate verbatim content, ask the user to re-upload `Team Pinnacle Playbook II.pdf` and re-run the extraction process.

## Page Map (from source index)

| Page | Content | KB Coverage |
|------|---------|-------------|
| 2 | Mission/vision/intro | `01-core-philosophy-and-principles.md` |
| 9 | 5-minute 1-on-1 overview | Partial |
| 11 | 7 types of people who do well | Not extracted |
| 12 | Prospecting tips | `03-prospecting-and-recruiting.md` |
| 13 | Follow-up interview | `03-prospecting-and-recruiting.md` |
| 14+ | Objection handling | `03-prospecting-and-recruiting.md` |
| 21 | Top 10 things in first 30 days | `04-fast-start-and-first-30-days.md` |
| 22 | Fast start analogy | `04-fast-start-and-first-30-days.md` |
| 23-24 | Promotion guidelines | Not extracted |
| 50 | Follow-up rules | `05-sales-and-client-process.md` |
| 58+ | Field training and sales process | `05-sales-and-client-process.md` |
| 93 | DIMER / saving rules | Not extracted |
| **97** | **35 Secrets of Success** ⭐ | **PARTIALLY — see below** |
| **98** | **10 Steps to Building Leaders** ⭐ | `06-leadership-duplication-and-training.md` |
| **99** | **10 Steps to Speed Duplication** ⭐ | `06-leadership-duplication-and-training.md` |
| 101 | 10 Things to Master | Not extracted |
| 102 | Higher Laws of Business | Not extracted |
| 103 | Laws of Building | Not extracted |
| 104 | 6 Steps to Business Development | `06-leadership-duplication-and-training.md` |
| 105 | Becoming a Field Trainer | Not extracted |
| 108 | STAR Personality Lens | `06-leadership-duplication-and-training.md` |
| 109 | Business Pipeline | `02-business-pipeline.md` |
| 112 | 10 Commitments to Building a Big Baseshop | Not extracted |
| 114 | Profile of Strong Builders/SMD | Not extracted |
| 116 | Training and Meeting System | `06-leadership-duplication-and-training.md` |
| 117 | Meeting-After-Meeting Cornerstones | `06-leadership-duplication-and-training.md` |
| 118 | Recognition System | `06-leadership-duplication-and-training.md` |
| **137** | **10 Best Ways to Close** ⭐ | **PARTIALLY — see below** |
| 138 | People Skills | Not extracted |
| 139-141 | Full-time/Part-time Schedules | Not extracted |
| 147 | Code of Honor | Not extracted |
| 148-149 | Persistency & Net Point Ratio | Not extracted |

## What We Know About the "35 Secrets of Success" (Page 97)

The full verbatim list is lost with the extracted text. However, the playbook's core philosophy extracts known from the KB:

- **Daily activity creates pipeline. Pipeline creates appointments. Appointments create clients.**
- **Mission before commission** — connect every close to client value
- **FOCUS: Follow One Course Until Successful**
- **Follow-up is a business discipline, not an option**
- **Build leaders, not only sales** — income vs scale distinction
- **Lead from the front** — do the activity first before asking others
- **Simplify to multiply** — systems simple enough for a newbie to duplicate

If the user re-uploads the PDF, extract page 97 specifically first.

## What We Know About "10 Best Ways to Close" (Page 137)

The KB summarizes the closing philosophy as a 3-step process:

1. **Collect Information** — discover the client's situation, goals, pain points
2. **Give a Recommendation** — present options with pros/cons, costs, risks, fit
3. **Implement & Follow Up** — paperwork, delivery, review, referrals

Modernized for real estate coaching:
- **Diagnose before prescribe** — understand before pitching
- **Objections = opportunities** — acknowledge, normalize, reframe to value
- **Referrals at happiness stage** — ask immediately after value is delivered
- **Follow-up cadence** — HOT daily, WARM weekly, COLD 1-2x/month

## Leadership Formulas Available in KB

These are fully documented and verified:

- **10 Steps to Building Leaders** → `06-leadership-duplication-and-training.md`
- **10 Steps to Speed Duplication** → `06-leadership-duplication-and-training.md`
- **6 Steps to Business Development** → `06-leadership-duplication-and-training.md`
- **STAR Personality Lens** → `06-leadership-duplication-and-training.md`
- **Objection Handling Framework** → `05-sales-and-client-process.md`

## How to Regenerate Full Extracted Text

If user re-uploads the PDF to the chat:

```python
# Use ocr-and-documents skill, marker-pdf, or PyMuPDF
import pymupdf
doc = pymupdf.open("path/to/Team Pinnacle Playbook II.pdf")
text = ""
for page in doc:
    text += page.get_text()
# Save to /opt/data/knowledge_bases/team_pinnacle_playbook_ii/full_text.txt
# Then parse the key sections by page number references above
```
