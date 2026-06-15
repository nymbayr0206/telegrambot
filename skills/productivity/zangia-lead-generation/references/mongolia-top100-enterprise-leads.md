# Mongolia TOP-100 enterprise lead source

Use this reference when the user asks for Mongolian "top taxpayers", "top 100 companies", or major enterprise lead targets.

## Primary public sources

- MNCCI page: `https://www.mongolchamber.mn/p/558`
- iKon article: `https://ikon.mn/n/3g0z`
- iKon interactive HTML: `https://content.ikon.mn/visuals/2024top100/index.html?v6`
- 2024 CSV found in the interactive script: `https://content.ikon.mn/visuals/2024top100/top100-2024.csv?v=4`

## Interpretation caveat

Do not call the list a pure "tax-paid ranking" unless the source explicitly says so. The MNCCI TOP-100 AAN ranking uses multiple indicators, including:

- sales revenue
- tax paid
- insured employee count
- profit
- assets

Useful public fact from the 2024 announcement: the TOP-100 companies paid about **7.64 trillion MNT** in taxes, about **28%** of total tax revenue, and generated revenue equivalent to about **69% of GDP**.

## Extraction pattern

The iKon interactive page loads `main.js`, which calls D3 CSV. Inspect the script for `d3.csv(...)` and fetch the referenced CSV.

Python pattern:

```python
import csv, io, urllib.request
url = 'https://content.ikon.mn/visuals/2024top100/top100-2024.csv?v=4'
text = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=30).read().decode('utf-8-sig')
rows = list(csv.DictReader(io.StringIO(text)))
ranked = []
for r in rows:
    val = (r.get('2024') or '').strip()
    if val and val not in ['-', '_']:
        ranked.append({'Rank 2024': int(val), 'Company': r['Name'], 'Rank 2023': r.get('2023', '')})
ranked.sort(key=lambda x: x['Rank 2024'])
```

## Lead-sheet columns

For enterprise prospecting, create both a raw list and an enrichment-ready list.

Raw columns:

- `Rank 2024`
- `Company`
- `Rank 2023`
- `Source`

Enrichment-ready columns:

- `Rank 2024`
- `Company`
- `Industry guess`
- `Website`
- `Phone`
- `Email`
- `Decision maker`
- `Source`
- `Lead status`
- `AI use-case idea`
- `Next step`
- `Notes`

## AI-agent offer mapping

- Mining: daily production/safety reports, equipment/maintenance workflows, contractor/vendor document routing.
- Banking/BBSB/finance: customer service, document intake, internal knowledge assistant, compliance summaries.
- Retail/FMCG: sales reports, inventory alerts, customer follow-up, promotion/campaign analytics.
- Telecom/technology: support triage, ticket routing, churn/retention workflows, knowledge base assistant.
- Construction/real estate: project reporting, material requests, site photo/report summaries, CRM follow-up.
- Healthcare/pharma: appointment/follow-up, customer service, inventory, medical/admin document workflows.

## Pitfalls

- Some company names contain non-breaking spaces or variant Mongolian spellings; normalize whitespace before dedupe.
- Some ranks have `_` or `-` for missing years; only include valid integer values for the target year.
- Do not assume public phone/email exists in the TOP-100 source; enrichment requires official websites, public social pages, company profiles, or other public sources.
- Always retain source URLs so the user can verify the lead list.
