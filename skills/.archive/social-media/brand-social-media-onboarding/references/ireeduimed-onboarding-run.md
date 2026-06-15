# Ireeduimed Onboarding — Full Session (June 5, 2026)

## Voice Message Received (Phase 1 — Brand Creation)

User said: "Ирээдүймэд" (misheard as "IdeaBeMed" — confirmed correct spelling after).

Actual: **Ирээдүймэд** (Ирээдүй + Мэд = Future + Knowledge/Media)

## Phase 1 — Brand Setup

### Steps Executed

1. **Check existing brands:** `ls /opt/data/social-content/brands/` — found ai-global, agenticforce, postly, supernova, usi-machinery. No match.
2. **Receive logo:** User sent `img_9d039584aa40.jpg` saying "Ene logo shuu save it as logo"
3. **Create brand folder:** `/opt/data/social-content/brands/ireeduimed/`
4. **Save logo:** `cp` to `assets/logos/logo-ireeduimed.jpg` + `logo-ireeduimed.png`
5. **Register in brand-registry.json:** Added entry with slug, name, workspace, created_at
6. **Create subdirs:** assets/logos, templates, source-materials, scripts, references, output

## Phase 2 — Info Collection (voice message)

User provided:
- **Phone:** 7771 0404
- **Address:** 25-р эмийн сан, замын урд, Ялгуун төвийн 3 давхарт
- **Business:** Эх ураг эмэгтэйчүүдийн эмнэлэг (OB/GYN clinic)
- **Audience:** Жирэмсэн эхчүүд / Pregnant women, expecting moms
- **Content type:** Daily educational tips, 4-slide carousels

## Phase 3 — Template Setup (edutemp1)

User sent `img_93b39e7d34e7.jpg` saying: "Save this as edutemp1 and reference all the time... only can change that dynamic field of the news headline... do not change the logo, content purpose, anything else"

### Template created
- **Name:** edutemp1
- **Path:** `templates/edutemp1/edutemp1-reference.jpg`
- **Dimensions:** 1254×1254 (1:1 square social format)
- **Online URL:** https://litter.catbox.moe/i9vrtx.jpg
- **Logo URL:** https://litter.catbox.moe/atdcff.jpg
- **Spec:** `templates/edutemp1/template-spec.md`
- **KB:** `/opt/data/knowledge_bases/ireeduimed-edutemp1/README.md`

### Fixed vs Dynamic
| Status | Elements |
|--------|----------|
| 🔒 FIXED | Logo, background, layout, contact (7771 0404 / address), brand name, content purpose |
| ✅ DYNAMIC | Only headline text |

### KIE Generation Pattern
When generating with edutemp1:
```
model: gpt-image-2-image-to-image
input_urls: [https://litter.catbox.moe/i9vrtx.jpg, https://litter.catbox.moe/atdcff.jpg]
prompt: "Use the FIRST image (edutemp1) as the EXACT template.
Preserve ALL fixed elements. ONLY change the headline text to: [NEW HEADLINE].
Do NOT change the logo, background, layout, contact info, or any other element."
```

## Notes

- User is extremely direct — minimal words, expects immediate execution
- "Save it as logo" → save immediately without asking questions
- Voice mishearing: "IdeaBeMed" → actually "Ирээдүймэд". Always confirm cyrillic.
- Model (deepseek-v4-flash) has NO vision capability — cannot see images. Save on user instruction alone.
- Template preservation is STRICT for edutemp1 — only headline changes. No other flexibility.
