# Worked Examples — Ireeduimed Brand Content (June 5, 2026)

## First Run: edutemp1 Slide 1 "Жирэмсэн гэдгээ мэдсэн үү?"

### KIE Task Details
- **Model:** gpt-image-2-image-to-image
- **Template ref:** https://litter.catbox.moe/i9vrtx.jpg
- **Task ID:** 68098a6562f658768022bbff588fea8c
- **Generated:** ~65s
- **Credits:** 6
- **Output file:** edutemp1_slide1_v2.png (1229 KB)
- **Output path:** /opt/data/social-content/brands/ireeduimed/output/edutemp1_slide1_v2.png

### What Changed Between v1 and v2
**v1 (rejected):** Only changed the headline, no body content. User said "need more content."
**v2 (approved):** Added 5 real pregnancy tips with ✅ checkmarks + small illustration.

### Working Prompt (approved)
```
HEADLINE: "Жирэмсэн гэдгээ мэдсэн үү?"
BODY:
  ✅ Фолийн хүчил, Д витамин уух
  ✅ Эмчид хандаж үзлэгт хамрагдах
  ✅ Тамхи, архинаас татгалзах
  ✅ Эрүүл хооллолт, хангалттай ус
  ✅ Стрессгүй, тайван байх
ILLUSTRATION: pregnant woman silhouette or baby ultrasound (small, tasteful)
```

## Slides 2-4: Remaining 3 Slides

### Batch Generation Details
All 3 submitted in parallel, all completed within ~100s.

**Slide 2 — Nutrition**
- Task: 7fa937d972ea77f8e28f57eb08a62cb2
- HEADLINE: "Жирэмсний үеийн зөв хооллолт"
- Tips: Шинэ ногоо/жимс/уураг, Фолийн хүчил/төмөр/кальци, 8-10 аяга ус, түүхий хоолноос зайлсхийх, кофеин багасгах
- Illustration: Healthy pregnancy foods

**Slide 3 — Exercise & Rest**
- Task: 913a312f520e45d083ef24b0f9eb8e94
- HEADLINE: "Дасгал хөдөлгөөн ба амралт"
- Tips: Хөнгөн алхах/сунгалт, жирэмсний його, 8-9 цаг унтах, стрессээс хол, биеийн дохиог сонсох
- Illustration: Pregnant woman stretching/walking

**Slide 4 — Medical Checkups**
- Task: 0d570f8030c7bb27690840f785c7dcf5
- HEADLINE: "Эмнэлгийн хяналт ба дараагийн алхамууд"
- Tips: Сарын үзлэгт хамрагдах, хэт авиан шинжилгээ, цус/шижингийн шинжилгээ, төрөх төлөвлөгөө
- Illustration: Doctor with pregnant patient / stethoscope

## Second Run: mindtemp1 Slide 1 "Жирэмсэн үеийн сэтгэл зүй"

- **Model:** gpt-image-2-image-to-image
- **Template ref:** https://litter.catbox.moe/bpk0hu.jpg
- **Task ID:** 89e192d5ba942b928f42bfe6b841c1c1
- **Generated:** ~120s
- **Credits:** 6
- **Output file:** mindtemp1_slide1.png (1274 KB)

### Working Content
```
HEADLINE: "Жирэмсэн үеийн сэтгэл зүй"
BODY:
  🧠 4 жирэмсэн эх тутмын 1 нь сэтгэл гутралд өртдөг
  💡 Дааврын өөрчлөлтөөс сэтгэл хөдлөл тогтворгүй болох нь хэвийн
  💖 Гэр бүлийн дэмжлэг, ойлголцол маш чухал
  🌿 Амралт, тайвшрал, өөртөө цаг гаргах
  🩺 Сэтгэл зүйн тусламж авахаас бүү ай
```

## Key Lessons
1. Always include REAL BODY CONTENT (tips), not just a headline
2. ✅ checkmark format with short tips works well
3. Small illustration alongside text is required
4. One-slide approval before generating remaining 3
5. Template preservation instructions must be very explicit — list FIXED elements first, then what CHANGES
6. KIE gpt-image-2-image-to-image: ~65-120s per slide, 6 credits each
7. catbox.moe URLs expire in 72h — re-upload from local files before each generation session
