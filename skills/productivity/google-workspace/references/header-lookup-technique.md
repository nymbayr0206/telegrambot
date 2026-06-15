# Sheets Column Mapping via Header Lookup

When reading a Google Sheet whose column layout may vary across tabs or enrichment runs, always find column indices by matching header names rather than hardcoding positions.

## Pattern

```python
# Read all data from the sheet
result = service.spreadsheets().values().get(
    spreadsheetId=sheet_id,
    range="'Tab Name'!A1:Z"
).execute()
values = result.get('values', [])
headers = values[0]  # first row is the header

# Find column by name (not by hardcoded index)
email_idx = None
phone_idx = None
for idx, h in enumerate(headers):
    if h == 'Email':
        email_idx = idx
    elif h == 'Phone':
        phone_idx = idx

# Now access data by found index
for row in values[1:]:  # skip header
    email = row[email_idx].strip() if len(row) > email_idx and row[email_idx].strip() else ""
```

## Why

- Different tabs may have different column structures
- Enrichment may add new columns over time
- Hardcoded indices (e.g. `row[14]`) cause off-by-one errors when columns shift
- A one-time header scan at read time eliminates position assumptions
