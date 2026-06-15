# Lawyer Review of Work Delivery Reports — Session Reference

Based on real sessions involving Mongolian municipal ERP delivery reports (хөгжүүлэлтийн ажлын тайлан) where a company lawyer (хуульч) reviewed the report and gave correction instructions.

## Typical Lawyer Feedback Categories

When a lawyer reviews a **хөгжүүлэлтийн ажлын тайлан** / хүлээлгэн өгөх баримт (work delivery/completion report), the most common corrections fall into **5 categories**:

### 1️⃣ Delay Reasons & Actual Dates (Хоцролтын шалтгаан ба огноо)
- Must state **why** the delivery was delayed (client-requested scope changes, additional modules, etc.)
- Must state the **actual delay number** — how many days, from which date to which date
- The original deadline vs. the amended deadline must be clear
- If the client (захиалагч) caused the delay via additional requirements, this should be explicitly stated

### 2️⃣ Section 5 — Role/User Names (5-р хэсэг — Хэрэглэгчийн роль)
- The "Roles of the users of this app" / "Хэрэглэгчийн роль ба хийх үйлдэл" section
- Common issue: **wrong or outdated role names** — the names listed don't match the client organization's actual structure
- **Fix**: Query the client's HR system (e.g., Odoo HR `hr.job` model) to get real position names, then match roles to departments

### 3️⃣ Remove Non-Existent Positions
- If the report lists a position that **doesn't exist** in the client organization (e.g., "Худалдан авалтын менежер" / Purchasing Manager)
- It must be removed or replaced with the actual role
- Verify against the client's organizational structure (Odoo HR, org chart)

### 4️⃣ Correct Legal Entity Naming (Хуулийн этгээд)
- The report must use **"Legal person" (Хуулийн этгээд)** — NOT "Person manager" or any other mangled form
- This is a specific legal term under Mongolian law
- In role/approval matrices, the legal entity/CEO approval role should be labeled correctly

### 5️⃣ Department Head Signatures (Тасгийн дарга нарын гарын үсэг)
- Each department that received / accepted the delivered work must have their **department head's signature** on the report
- The signature confirms: "work done and received by this department"
- This is a legal requirement for acceptance (хүлээн авсан) — not just a formality

## Workflow: Fixing a Docx Work Delivery Report Per Lawyer Feedback

1. **User uploads the DOCX** — the report file (e.g., `hugjuuleltiin-ajliin-tailan-final.docx`)
2. **Read with python-docx** — extract all paragraphs, tables, headings to understand the structure
3. **Identify what the lawyer flagged** — map each feedback item to a specific paragraph, table cell, or section
4. **For role names**: query Odoo 19 HR (`hr.job` model via XML-RPC) to get real position titles from the client organization, or ask user for the correct names
5. **Edit the DOCX** — modify paragraphs, tables, and structure using python-docx
6. **Add signature block** — add a section or table for department head signatures
7. **Export** — save as a new DOCX or convert to PDF

## Odoo HR Role Validation

When role names need verification:

```python
# Odoo 19 — Query hr.job for position/job titles
# Via xmlrpc.client
import xmlrpc.client
common = xmlrpc.client.ServerProxy('{url}/xmlrpc/2/common')
uid = common.authenticate(db, login, password, {})
models = xmlrpc.client.ServerProxy('{url}/xmlrpc/2/object')
jobs = models.execute_kw(db, uid, password, 'hr.job', 'search_read', [[]], {
    'fields': ['name', 'department_id'],
    'limit': 50
})
```

This returns all registered job positions. Cross-reference these with the roles listed in the report's Section 5 (Хэрэглэгчийн роль).

## Example Session Context

- **Client (Захиалагч)**: Хан-Уул дүүргийн Тохижилт Үйлчилгээний Төв
- **Contractor (Гүйцэтгэгч)**: "Шуурхай түгээлт" ХХК
- **Project**: Municipal ERP system — garbage collection, vehicle base, HR, procurement web system
- **Report title**: "Хөгжүүлэлтийн ажлын тайлан"
- **Lawyer firm**: Money-ciple company's lawyer

## Pitfalls

- **DOCX files don't persist across Telegram sessions** — when user says "I gave you the DOCX," ask them to re-upload rather than searching the filesystem
- **Scanned PDF is NOT the report** — the scanned contract PDF and the editable work delivery DOCX are two different documents. Don't confuse them
- **Job positions are organization-specific** — don't guess role names; always verify against the actual client's HR data or ask the user
- **Signature blocks are substantive, not cosmetic** — in Mongolian contract law, the receiving party's signature is evidence of acceptance. Don't omit it or treat it as formatting
