# AgenticForce Workshop Signup Capture

Use this reference when the user wants to collect registrations for AgenticForce workshops/webinars/academy sessions before sending outreach emails.

## Pattern

1. Prepare the destination database first, usually the existing Google Sheet `Zangia Leads` with a dedicated tab named `Workshop Signups`.
2. Confirm or create these headers before any campaign send:
   - Submitted At
   - Workshop Date
   - Full Name
   - Email
   - Phone
   - Company
   - Job Title
   - Industry
   - Company Size
   - Interest / Pain Point
   - Source
   - UTM Source
   - UTM Medium
   - UTM Campaign
   - Referrer
   - Landing Page
   - Lead Score
   - Status
   - Notes
3. Configure or reuse the Hermes website signup webhook so it appends rows to `Workshop Signups` and sends a Telegram notification to the user.
4. The webhook should capture leads only by default. Do **not** send automatic email/SMS follow-ups unless the user explicitly approves an automation sequence.
5. Add/verify the website route before sending outreach. Preferred public links for the AgenticForce website are:
   - Mongolian: `https://agenticforceweb.vercel.app/mn/workshop`
   - English: `https://agenticforceweb.vercel.app/en/workshop`
6. If the site repo is unavailable on the Hermes host, prepare a small patch package rather than claiming deployment. Include:
   - `app/[locale]/workshop/page.tsx`
   - `app/[locale]/workshop/thank-you/page.tsx`
   - `app/api/workshop-signup/route.ts`
   - `README.md` with required environment variables and apply/deploy steps.

## Payload notes

The website API route should forward a normalized JSON payload to Hermes containing form fields, locale, landing page, referrer, UTM fields, source, and an idempotency key where possible. Server-side forwarding should keep the Hermes webhook secret off the client.

## Verification checklist

- [ ] Sheet tab exists with the expected headers.
- [ ] Webhook/subscription is configured to append to the tab and notify Telegram.
- [ ] Test submission writes a row or a controlled test path has been verified.
- [ ] Public signup URL is deployed and reachable before sending bulk outreach.
- [ ] Campaign email body uses the verified signup URL, not a placeholder.
