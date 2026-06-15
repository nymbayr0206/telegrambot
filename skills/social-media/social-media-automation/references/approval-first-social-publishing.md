# Approval-first social publishing notes

Use this reference for brand workflows that generate assets automatically but must not publish without the user's explicit approval.

## Core rule

For scheduled or automated content generation, separate creation from publishing:

1. Generate the assets.
2. Deliver previews to Telegram or the agreed review channel.
3. Save a pending approval record with asset paths, caption, campaign, model, and webhook/config pointer.
4. Wait for explicit user approval.
5. Only then send to Make.com/Facebook/Instagram/webhook and advance campaign state.

## Supernova daily carousel case

Supernova's 18-carousel series should use approval-first:

- Generate 4 separate 1:1 slides with KIE GPT Image 2.
- Send the 4 images to Telegram for review.
- Do not call Make.com automatically.
- Store pending approval at the brand automation path.
- After user says `approve Supernova carousel`, send the pending slides to Make.com and then advance `next_carousel`.

Reason: Mongolian text rendered inside images needs human spelling/typography review, and the user explicitly confirmed Make.com should be approval-first.

## Postly/social client rule

For Postly client work, default to approval-first unless the user explicitly gives autopost permission for a particular brand/workflow. This applies to carousels, reels, captions, and video ads.
