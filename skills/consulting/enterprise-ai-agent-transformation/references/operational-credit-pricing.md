# Operational AI Service Credit Pricing — Methodology & Data

## Purpose

Design recurring monthly credit packages (100K₮ / 390K₮ / 990K₮) for AI agent services where clients pay for "what they consume" — CRM records processed, images generated, videos created, reports run. No token/API jargon. Pure business-value framing.

**Use this when:** the client asks "how much per month?" instead of "how much to build it?"; when designing a SaaS-style credit/usage model for ongoing AI services; when translating API costs into MNT credit packages.

## Core Pricing Formula

```
Selling Price = (API Unit Cost × USD→MNT Rate) × Markup
```

| Parameter | Value | Notes |
|-----------|-------|-------|
| Markup | **2.8×** | Covers platform, support, margin |
| USD→MNT | **3,400₮** | Approximate rate (verify current) |
| Credit budget | `Selling Price / 2.8 / 3,400` | = USD available for API costs |

### Example
100,000₮ → $29.41 USD → $10.50 API budget (after 2.8× markup)

## API Cost Data (as of June 2026)

### DeepSeek Flash (AI text processing)
| Metric | Official Price |
|--------|---------------|
| Input tokens (cache miss) | **$0.14 / 1M tokens** |
| Output tokens | **$0.28 / 1M tokens** |

**Per-call estimate (real estate call, 3 min):**
- input ~600 tokens, output ~200 tokens → **$0.00014 / call → ~0.48₮**

### KIE.ai GPT Image 2 (image generation via KIE proxy)
| Resolution | Estimated Cost (KIE) |
|-----------|---------------------|
| 1K | ~$0.06 / image |
| **2K (standard)** | **~$0.12 / image** |
| 4K | ~$0.30 / image |

KIE.ai claims 30-70% savings vs OpenAI official pricing. Official GPT Image 2 at 1024×1024 high quality = $0.211/image. The KIE markup makes these viable for mass-market Mongolian business pricing.

### KIE.ai Veo 3 Fast (video generation via KIE proxy)
| Video Type | Cost |
|-----------|------|
| **8 seconds with audio (Fast)** | **$0.40 / video** |
| 8 seconds with audio (Quality) | $2.00 / video |

### Supabase (CRM database storage)
| Plan | Cost | Database | Notes |
|------|------|----------|-------|
| Pro | **$25/month** | 8GB | Covers ~100K+ CRM records |
| Team | $75/month | 16GB | For larger deployments |

**CRM record sizing:** ~500 bytes per record (7 text fields). 100,000 records ≈ 50MB. Database cost is negligible at scale — the $25/month Pro plan is the main cost.

## Per-Operation Cost Matrix

| Operation | API Cost (USD) | Cost (MNT) | After 2.8× Markup (MNT) |
|-----------|---------------|-----------|------------------------|
| 1 CRM record (AI process) | $0.00014 | 0.48₮ | **~1.3₮** |
| 1 matching operation | $0.00020 | 0.67₮ | **~1.9₮** |
| 1 monthly report | $0.00056 | 1.90₮ | **~5.3₮** |
| 1 image (2K, GPT Image 2) | $0.12 | 408₮ | **~1,142₮** |
| 1 video (8s, Veo 3 Fast) | $0.40 | 1,360₮ | **~3,808₮** |

## Real Estate Scenario — Capacity Calculator

**Assumptions:**
- 10 agents, 50 calls/day each, 22 working days = 11,000 calls/month
- Each call → AI processes transcript → CRM entry → classification → match suggestions

### Monthly AI Cost for Full Call Processing
- 11,000 calls × $0.00014 = **$1.54 / month** (before markup)
- After 2.8× markup: **~5,240₮ / month** for full call processing
- → Text processing is effectively free. The real costs are images and videos.

### Capacity per Tier (all-AI-processing scenario)

| Tier | CRM Records | Matches | Reports | Images (2K) | Videos (8s) |
|------|-------------|---------|---------|-------------|-------------|
| **100,000₮** | 75,000 | 53,000 | 18,700 | 87 | 26 |
| **390,000₮** | 292,000 | 209,000 | 73,000 | 341 | 102 |
| **990,000₮** | 742,000 | 530,000 | 185,000 | 866 | 259 |

### Realistic Blended Scenario (50% CRM + 25% images + 20% video + 5% reports)

| Tier | CRM Records | Images | Videos | Reports |
|------|-------------|--------|--------|---------|
| **100,000₮** | 37,500 | 21 | 5 | 937 |
| **390,000₮** | 146,000 | 85 | 20 | 3,657 |
| **990,000₮** | 371,000 | 216 | 51 | 9,284 |

## Business Value Translation

### Hours Saved

| Tier | CRM Volume | Manual Hours | Work Days | Salary Saved (2M₮/mo) |
|------|-----------|-------------|-----------|----------------------|
| 100K | 75,000 | 3,752 hrs | 469 days | **42M₮** |
| 390K | 292,000 | 14,631 hrs | 1,829 days | **166M₮** |
| 990K | 742,000 | 37,140 hrs | 4,642 days | **422M₮** |

*Manual time: 3 minutes per CRM record (listen + type). Salary: 2M₮/month, 176 hrs/month.*

### Cost vs Traditional Agency

| Service | AI Price (per unit) | Traditional Price | Savings |
|---------|-------------------|-------------------|---------|
| 1 social media poster | ~1,100₮ (after markup) | 50,000-150,000₮ | **~99%** |
| 1 marketing video (8s) | ~3,800₮ (after markup) | 200,000-1,000,000₮ | **~99%** |
| CRM data entry (1 record) | ~1.3₮ (after markup) | ~1,000₮ (manual) | **~99%** |

## Designing Credit Tiers — Principles

1. **Lowest tier (100K₮) is an entry point** — shows value without overwhelming budget. Text AI is so cheap that even this tier processes 6 months of calls for a 10-agent team.

2. **Middle tier (390K₮) is the sweet spot** — 3.9× the price, 3.9× the capacity. Clean linear scaling builds trust. Good for a serious monthly commitment.

3. **Top tier (990K₮) is the power user** — 2.5× the middle tier. Meant for agencies or broker offices that need volume image/video generation alongside CRM.

4. **Always show blended scenarios** — pure "all CRM" numbers sound fake because they're so large. Mix in visible deliverables (images, videos) so the client sees a realistic monthly output.

## Output Template for Client-Facing Docs

```
## [TIER NAME — 100,000₮ / сар]

Таны авах боломжууд:

📋 **37,500 CRM бүртгэл** — 10 агентын 3 сарын дуудлага боловсруулна
🖼️ **21 маркетингийн зураг** — сошиал постер, зар
🎬 **5 богино видео** — 8 секундын маркетингийн видео
📊 **937 тайлан** — борлуулалт, үйл ажиллагааны тайлан

⏱️ 3,752 цаг хүний хөдөлмөр хэмнэнэ ≈ 42 сая₮ цалинтай тэнцэнэ
```

## Key Sales Pitch

> "100,000₮ төлөөд та 10 агентынхаа 3 сарын дуудлагын боловсруулалт, 21 сошиал постер, 5 маркетингийн видеог нэг дор хийлгэх боломжтой. Гар аргаар хийвэл 42 сая₮-ийн цалин, 3,752 цаг зарцуулах байсан."

## Data Sources (Verified)

| Service | Source URL |
|---------|-----------|
| DeepSeek Flash pricing | https://api-docs.deepseek.com/quick_start/pricing |
| KIE.ai Veo 3 pricing | https://kie.ai/v3-api-pricing |
| KIE.ai GPT Image 2 | https://kie.ai/gpt-image-2 |
| KIE.ai general pricing | https://kie.ai/pricing |
| Supabase pricing | https://supabase.com/pricing |

*Prices are as of June 2026. API prices can change — re-verify before building final client proposals.*
