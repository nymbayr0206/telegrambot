# XLSX Parsing — Python stdlib only (no openpyxl/pandas)

When `openpyxl`, `xlrd`, or `pandas` are not installed and you cannot install them (no pip, no root), parse `.xlsx` files using only Python stdlib. An `.xlsx` file is a ZIP archive of XML files.

## Quick-start snippet

```python
import zipfile, xml.etree.ElementTree as ET

ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

with zipfile.ZipFile('file.xlsx', 'r') as z:
    # 1. Read shared strings (cell text values)
    ss_xml = z.read('xl/sharedStrings.xml')
    ss_root = ET.fromstring(ss_xml)
    shared_strings = []
    for si in ss_root.iter(ns + 'si'):
        texts = [t.text for t in si.iter(ns + 't') if t.text]
        shared_strings.append(' '.join(texts))

    # 2. List sheets
    wb_xml = z.read('xl/workbook.xml')
    wb_root = ET.fromstring(wb_xml)
    for sheet in wb_root.iter(ns + 'sheet'):
        print(f"Sheet: {sheet.attrib['name']}")

    # 3. Read a sheet
    sheet_xml = z.read('xl/worksheets/sheet1.xml')
    root = ET.fromstring(sheet_xml)
    sheet_data = root.find(f'{ns}sheetData')

    for row in sheet_data:
        vals = []
        for cell in row:
            cell_type = cell.attrib.get('t', '')
            cell_val = cell.find(f'{ns}v')
            val_text = cell_val.text if cell_val is not None else ''

            if cell_type == 's' and val_text:
                idx = int(val_text)
                vals.append(shared_strings[idx])
            else:
                # Format numbers cleanly
                try:
                    f = float(val_text)
                    vals.append(str(int(f)) if f == int(f) else f"{f:,.0f}")
                except:
                    vals.append(val_text)
        print(' | '.join(vals))
```

## Sheet file mapping

| File in ZIP | Content |
|---|---|
| `xl/workbook.xml` | Sheet names and IDs |
| `xl/sharedStrings.xml` | All text values (referenced by index) |
| `xl/worksheets/sheet1.xml` | Sheet 1 data |
| `xl/worksheets/sheet2.xml` | Sheet 2 data |
| ... | Sheet N data |
| `xl/styles.xml` | Number formats, fonts, colors (optional) |

## Common pitfalls

- **Empty cells**: some cell elements contain only `r` (ref) attribute with no `v` child. Handle by checking `cell_val is not None`.
- **Date serial numbers**: Excel stores dates as serial numbers (days since 1900-01-01). Convert: `from datetime import date, timedelta; date(1900, 1, 1) + timedelta(serial - 2)`. The `-2` accounts for Excel's leap-year bug.
- **Number cell type (`t='n'`)**: numeric cells don't use shared strings. The `v` element contains the raw number.
- **Large files**: stdlib parsing loads everything into memory. Not suitable for files >50MB. For those, find a way to install openpyxl.
- **Merged cells**: not handled by this approach; the raw XML only stores the top-left cell value.
- **Sheet relations**: if sheets have drawings or images, check `xl/worksheets/_rels/sheetN.xml.rels`.

## When to use this vs installing a library

| Condition | Approach |
|---|---|
| No pip, no root, no venv | ✅ stdlib parsing |
| Has uv in PATH | `uv pip install openpyxl` into a throwaway venv |
| Has pip/root | `pip install openpyxl` or `apt install python3-openpyxl` |
| File >50MB | Install openpyxl — or read in chunks |
| User needs formatted/pretty output | stdlib parsing + manual formatting (as above) |
| User needs analysis/aggregation | Install pandas via uv venv |
