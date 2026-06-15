# DOCX Editing with python-docx

Use this when the user sends a Word (.docx) file and asks you to modify it — add/remove paragraphs, edit table content, insert tables, or change formatting.

## Setup

```bash
pip install python-docx
```

## Reading a DOCX

```python
from docx import Document

doc = Document("path/to/file.docx")

# Iterate paragraphs
for i, para in enumerate(doc.paragraphs):
    if para.text.strip():
        print(f"[{i}] ({para.style.name}) {para.text[:200]}")

# Iterate tables
for ti, table in enumerate(doc.tables):
    print(f"Table {ti}: {len(table.rows)} rows x {len(table.columns)} cols")
    for ri, row in enumerate(table.rows):
        cells = [cell.text.strip()[:50] for cell in row.cells]
        print(f"  Row {ri}: {cells}")

# Check sections
print(f"Sections: {len(doc.sections)}")
```

## Editing a Paragraph

### Clear and rewrite
```python
para = doc.paragraphs[5]
para.clear()
run = para.add_run("New text here")
run.font.size = Pt(11)
run.font.name = 'Times New Roman'
```

### Add a run with formatting
```python
run = para.add_run("Bold text")
run.bold = True
run.font.size = Pt(12)
```

## Editing Tables

### Read cell text
```python
cell_text = table.rows[ri].cells[ci].text.strip()
```

### Write cell text
```python
table.rows[ri].cells[ci].text = "New cell content"
```

### Remove a row
```python
target_text = "Row text to find and remove"
for ri, row in enumerate(table.rows):
    if target_text in row.cells[0].text:
        tbl = table._tbl
        tbl.remove(row._tr)
        break
```

## Adding Content

### Add a new table
```python
new_table = doc.add_table(rows=4, cols=3)
new_table.style = 'Table Grid'

# Header row
new_table.rows[0].cells[0].text = "Header 1"
new_table.rows[0].cells[1].text = "Header 2"
new_table.rows[0].cells[2].text = "Header 3"

# Data rows
new_table.rows[1].cells[0].text = "Row 1 data"
```

### Add a new paragraph (appends at end)
```python
para = doc.add_paragraph()
run = para.add_run("New paragraph text")
run.font.size = Pt(12)
```

## Inserting Content Before a Specific Paragraph

python-docx doesn't natively support inserting paragraphs at arbitrary positions. Workaround:

1. Find the target paragraph index.
2. Clear an empty paragraph near that index and rewrite it.
3. For tables added after document read, they appear after the last paragraph. To place a table before a specific section, clear the empty paragraph just before that section's heading.

## Saving
```python
doc.save("path/to/output.docx")
```

## Common Patterns for Mongolian Government/Business Reports

### Report metadata table (2 columns)
```python
table = doc.tables[0]  # First table is usually metadata
# Row cells: [('Гүйцэтгэгч', 'Company Name'), ('Тайланг бичсэн', 'Position Name'), ...]
```

### Role/permission tables
Roles are typically stored in a table with columns: `[Роль, Хийх үндсэн үйлдэл / функциональ эрх]`.
When correcting role lists, first cross-reference against Odoo HR data (`hr.job`, `hr.employee`) to verify each position actually exists.

### Signature tables
Typically 3 columns: `[№, Хэлтэс, Хэлтсийн дарга (гарын үсэг)]`.
Departments should match actual Odoo `hr.department` records.

## Contract Amendment / Deliverable Report Editing

When the user asks you to amend a deliverable report (handover document) to explain why a contract deadline was postponed:

### What to Add

1. **Revised deadline line** — find the original delivery date in the report, update it to the newly agreed date
2. **Delay rationale paragraph** — insert a paragraph explaining what caused the postponement. Pattern:
   > "Захиалагчийн Ерөнхий менежерийн нэмэлт шаардлагын дагуу [шинэ модуль/системийн нэр]-ийг ERP системд нэмэх шаардлага гарсан. Энэхүү нэмэлт ажлын улмаас хүлээлгэн өгөх хугацааг [шинэ огноо] болгон сунгасан."
3. **List of new modules** — bullet list of additional scope items delivered (e.g., хогны машины жингийн тайлан, шатахуун зарцуулалтын тайлан)

### Finding the Right Paragraph

```python
# Find paragraphs containing date references
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if any(kw in text for kw in ['хугацаа', 'хүргэх', 'хүлээлгэн', 'дуусах', '04 сарын', '04 дүгээр']):
        print(f"[{i}] {text[:150]}")
```

### Inserting Content Before a Section

To insert content before a specific section heading (without `python-docx` native insert):
1. Find the paragraph index of the target heading
2. Clear an empty paragraph near that point and rewrite it with your content
3. The document body is a flat list — the index determines position

### Checking for Existing Delay/Rationale Sections

Search for paragraphs containing words like `шалтгаан`, `хойшилсон`, `нэмэлт шаардлага` — if found, edit in place rather than adding duplicate content.

## Pitfalls

- `doc.paragraphs` indices include ALL paragraphs (empty headings, table-of-contents entries, etc.). Verify the text content before editing.
- Table rows removed with `tbl.remove()` change indices of subsequent rows. Process top-to-bottom or re-read the table after removal.
- Font names like 'Times New Roman' may not render in Mongolian on all systems; prefer common system fonts.
- `doc.add_table()` adds the table at the END of the document, not at an insertion point. For inserting within the document body, clear an existing empty paragraph near the desired location.
