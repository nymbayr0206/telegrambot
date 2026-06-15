# Public Contact Enrichment for Zangia Leads

Use this reference when a user asks to enrich Zangia leads with email addresses, Facebook pages, websites, or other public contact details.

## Principles

- Use public, business-relevant sources only.
- Do not bypass login, CAPTCHA, paywalls, or private profile restrictions.
- Keep source attribution separate from the value: `Email` and `Email Source`, `Facebook Page`, `Website`.
- Do not say an email came from Facebook if Facebook only helped identify the company and the email came from the official website.
- Confirm before writing enrichment data back to Google Sheets or Odoo.

## Recommended enrichment columns

Add these to the `Zangia Leads` sheet when needed:

- `Email`
- `Email Source`
- `Facebook Page`
- `Website`
- `Enrichment Notes`

## Workflow

1. Select one lead row.
2. Use company identifiers from Zangia: Mongolian name, English name, company alias, company URL, phone, and job URL.
3. Locate likely public company channels:
   - Zangia company/job page
   - official website contact page
   - public Facebook business page
   - public LinkedIn company page
4. Extract emails only when visibly public and relevant to business contact.
5. Prefer the official website contact page when available.
6. Record where each value came from.
7. Update the sheet only after user confirmation.
8. Verify by reading the updated row.

## Session example

For `Тоёота Сэйлс Монголиа ХХК / Toyota Sales Mongolia LLC`:

- Facebook page found: `https://www.facebook.com/toyota.mongolia/`
- No email was visibly exposed on the public Facebook page.
- Official contact page found: `https://toyota-mongolia.mn/contact`
- Public email found on official site: `customer_service@toyota-mongolia.mn`
- Phone confirmed: `75109999`

The Google Sheet was updated with:

- `Email`: `customer_service@toyota-mongolia.mn`
- `Email Source`: `https://toyota-mongolia.mn/contact`
- `Facebook Page`: `https://www.facebook.com/toyota.mongolia/`
