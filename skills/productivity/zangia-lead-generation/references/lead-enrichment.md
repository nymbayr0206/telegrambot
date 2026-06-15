# Zangia Lead Enrichment Notes

Use this when the user asks to enrich Zangia leads with email, Facebook, website, or other public contact data.

## Scope

- Use only public business/contact data from public pages.
- Do not bypass Facebook login walls, CAPTCHA, paywalls, or private profiles.
- Prefer official company websites/contact pages as the source of truth when Facebook does not expose an email publicly.
- Record both the discovered value and the source URL so the user can verify it.
- Ask for confirmation before writing enriched fields back to Google Sheets, Odoo, or another database.

## Practical Workflow

1. Pick one lead or a small batch from the existing Zangia lead list.
2. Start from the Zangia fields already collected: company name, English name, phone/contact, company URL, job URL.
3. Search for a public Facebook page and/or official website using company name variants in English and Mongolian.
4. Try public Facebook pages first if specifically requested, but do not rely on Facebook alone:
   - Facebook often hides contact info or returns minimal/no content without a browser/login.
   - If no email is visible on Facebook, check official website contact pages discovered from search results or the Zangia/company page.
5. Extract emails with source context; ignore obvious bot-challenge/support addresses from search engines.
6. Store enrichment fields separately from original Zangia fields.

## Suggested Google Sheet Enrichment Columns

Add these columns when enriching an existing Zangia Leads sheet:

- `Email`
- `Email Source`
- `Facebook Page`
- optional: `Website`
- optional: `Enrichment Status`
- optional: `Last Enriched At`

## Example: Toyota Sales Mongolia

For `Тоёота Сэйлс Монголиа ХХК / Toyota Sales Mongolia LLC`:

- Public Facebook page found: `https://www.facebook.com/toyota.mongolia/`
- Facebook itself did not expose a public email in the checked content.
- Official contact page exposed: `customer_service@toyota-mongolia.mn`
- Official contact source: `https://toyota-mongolia.mn/contact`
- Phone confirmed: `75109999`

Lesson: when the user asks for email "from Facebook if available," report whether Facebook exposed it; if not, use and label a verified official website email rather than leaving the lead un-enriched.

## Reporting Pattern

Be explicit about source quality:

- `Email from Facebook`: if visible on the public Facebook page.
- `Email from official website`: if Facebook had no email but the official company site did.
- `No public email found`: if neither source exposes one.

Then ask before writing back to the sheet/database unless the user already confirmed the write.