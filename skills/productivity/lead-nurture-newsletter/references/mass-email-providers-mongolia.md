# Mass Email Provider Comparison (Mongolia B2B)

When the user asks for the cheapest/best mass email provider for Mongolian B2B lead outreach, use this comparison.

## Price Comparison

| Provider | Price / 1000 emails | Notes |
|----------|-------------------|-------|
| **Amazon SES** | ~₮40 (350 MNT / 1000) | Cheapest at scale. No free tier for production. |
| **Brevo** | **Free** (300/day) → ₮200/1000 after | Best for small lists (≤300/day free). No Mongolia blocks. |
| **SendGrid** | Free (100/day) → ₮150/1000 | Small free tier, widely known. |
| Mailgun | ₮250/1000 | Good deliverability but pricier. |
| Mailchimp | ₮300-600/1000 | Expensive for CRM use. More for newsletters. |

## Recommendation Logic

### For ≤ 300 leads → Brevo (free tier)
- 300 free emails/day — covers any batch the user has
- Simple API, easy setup
- Can also send SMS from same platform
- Deliverability good for Mongolian recipients

### For 300-5000 leads → Amazon SES
- Cheapest at scale
- Requires domain verification + SPF/DKIM setup
- Best for ongoing campaigns
- AWS integration if user already uses AWS

### For < 100 leads, one-time → Brevo free or Gmail draft approval
- If truly one-off, Gmail drafts through `google-workspace` skill are simplest
- User approves each draft

## When User Already Uses Make.com

Brevo and SendGrid both have native Make.com modules. Amazon SES has AWS Lambda/SQS paths through Make.com but requires more setup.

## Setup Effort

| Provider | Setup Time | Difficulty |
|----------|-----------|------------|
| Brevo | 15 min | Easy — create account, verify domain, get API key |
| Amazon SES | 45-60 min | Medium — AWS account, domain verification, SPF/DKIM, test mode |
| SendGrid | 20 min | Easy — create account, verify sender |

## Deliverability Considerations for Mongolia

- Mongolian email providers (MongolContent, BodiMail, etc.) accept all three providers without issues.
- Gmail / Yahoo recipients: SES and Brevo both have good reputation management.
- Avoid sending from unverified domains — always verify sender domain with SPF + DKIM.
- Small warm-up needed for new domains: start with 10-20/day for the first week.

## Brevo Quick Setup

```bash
# 1. Sign up at https://www.brevo.com
# 2. Verify domain
# 3. Get API key (Settings → API Keys)
# 4. Send via curl:
curl -X POST https://api.brevo.com/v3/smtp/email \
  -H "api-key: $BREVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sender": {"name": "Company Name", "email": "noreply@domain.mn"},
    "to": [{"email": "lead@company.mn"}],
    "subject": "Your Subject",
    "htmlContent": "<h1>Hello</h1><p>Message body</p>"
  }'
```

## Amazon SES Quick Setup

```bash
# 1. AWS Console → SES → Verify domain
# 2. Set up SPF/DKIM DNS records
# 3. Move from sandbox by requesting production access
# 4. Install boto3 and send:
#    If pip/pip3 is available: pip install boto3
#    If only uv is available:   uv pip install boto3

# Python send example:
import boto3
client = boto3.client('ses', region_name='us-east-1')
response = client.send_email(
    Source='noreply@domain.mn',
    Destination={'ToAddresses': ['lead@company.mn']},
    Message={
        'Subject': {'Data': 'Your Subject', 'Charset': 'UTF-8'},
        'Body': {'Html': {'Data': '<h1>Hello</h1><p>Message</p>', 'Charset': 'UTF-8'}}
    }
)
```
