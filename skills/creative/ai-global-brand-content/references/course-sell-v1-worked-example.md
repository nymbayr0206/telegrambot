# Course Sell v1 — Worked Example (June 2026)

**Course:** AI+ Agent™ — Ai Agent Building Course
**Instructor:** А. Мөнх-Учрал
**Brand:** AI Global
**Template:** temp1 (dark background + gold decor)
**Format:** 4-slide carousel, 1:1 image-to-image via KIE GPT Image 2

---

## Pre-Approval Text Content (present to user first)

### Slide 1 — Instructor Intro
```
Headline: "Өөрийн AI Agent-ээ бүтээ. Ажлаа автоматжуул. Цагаа чөлөөл."
Instructor: А. Мөнх-Учрал — AI+ Agent хөтөлбөрийн багш
Bio: IO Institute — Software багш, 10+ жил • Med Koders LLC — Үүсгэн байгуулагч • etaxi ecosystem хөгжүүлэгч
Bottom: "Танд туслах, таны өмнөөс ажиллах AI туслахуудыг өөрөө бүтээж сур. Ямар ч код бичихгүйгээр."
```

### Slide 2 — Time Savings
```
Headline: "Долоо хоногт 20+ цагийг чөлөөл"
Bullets: Автомат хариулт — 5 цаг/долоо хоног
         Дата боловсруулалт — 8 цаг/долоо хоног
         Тайлан шинжилгээ — 7 цаг/долоо хоног
         Хэрэглэгчийн дэмжлэг — 10 цаг/долоо хоног
Total: "Сард 80+ цаг = 2 бүтэн ажлын долоо хоног"
```

### Slide 3 — Workforce Efficiency
```
Headline: "1 хүн = 5 хүний ажил"
Sub: 1 AI Agent Builder + 10+ AI Agent 24/7
Comparison:
  • Уламжлалт баг: 5-6 ажилтан — 60-80 сая ₮/сар
  • AI Agent: 1 хүн + AI — 15-20 сая ₮/сар
  • Зардал 70% хэмнэнэ
```

### Slide 4 — CTA
```
Headline: "AI+ Agent — Таны AI карьерийн эхлэл"
Benefits:
  • AI Agent бүтээж сур
  • Сард 10+ сая ₮ орлого олох чадвар
  • Зөвхөн 20 хүнийг бүртгэнэ
  • Ямар ч код бичих мэдлэг шаардлагагүй
CTA: "Мэдээлэл авах → Коммент бичээрэй"
```

---

## Generation Workflow

### Uploads
```bash
# temp1
curl -s -F "file=@.../backgrounds/temp1.jpg" https://tmpfiles.org/api/v1/upload
# → https://tmpfiles.org/dl/<hash>/temp1.jpg

# Instructor photo
curl -s -F "file=@.../people/trainer-munkhuchral.jpg" https://tmpfiles.org/api/v1/upload
# → https://tmpfiles.org/dl/<hash>/trainer-munkhuchral.jpg
```

### KIE Submit — Slide 1 (with instructor photo)
```bash
curl -s -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -d '{
  "model": "gpt-image-2-image-to-image",
  "input": {
    "prompt": "STRICT RULE — THE TEMPLATE BACKGROUND (first image) MUST BE PRESERVED EXACTLY AS-IS:\n... list each element explicitly (logo, phone, background, decorations) ...\n\nTake the persons face from the second image...\n\nAdd text in CYRILLIC MONGOLIAN...",
    "input_urls": ["https://tmpfiles.org/dl/<hash>/temp1.jpg", "https://tmpfiles.org/dl/<hash>/trainer-munkhuchral.jpg"],
    "aspect_ratio": "1:1",
    "resolution": "1K"
  }
}'
```

### KIE Submit — Slides 2-4 (temp1 text-only, no photo)
Same but only 1 URL in input_urls (temp1 only), no photo second image.

### Polling
```bash
for i in $(seq 1 30); do
  result=$(curl -s "https://api.kie.ai/api/v1/jobs/recordInfo?taskId=<tid>" \
    -H "Authorization: Bearer $KIE_API_KEY")
  state=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('state','unknown'))")
  echo "[$i] State: $state"
  [ "$state" = "success" ] && { echo "$result" | python3 -c "..."; break; }
  [ "$state" = "fail" ] && { echo "$result"; break; }
  sleep 10
done
```

### Download
```bash
curl -s -L "<resultUrl>" -o "/.../outputs/ai-agent-slideN.png"
```

---

## CTA Rules (from user — DO NOT violate)
- ❌ NO "Бүртгүүлэх" (Register)
- ❌ NO start date on poster
- ✅ "Мэдээлэл авах → Коммент бичээрэй"
- ✅ "Зөвхөн X хүнийг бүртгэнэ" (e.g. 20)
- ✅ Slide 1 must feature instructor real photo

## temp1 Immutability
- DO NOT modify temp1 at all — logo, phone, background, decor all stay exactly as-is
- If AI modifies temp1, list each element name explicitly in prompt
- User may replace temp1 file at any time — always overwrite and re-upload
