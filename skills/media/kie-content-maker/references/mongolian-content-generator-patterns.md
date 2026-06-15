# Mongolian Content Generator Patterns

## Origin

Derived from building the AI Global `aiglobal_success_story_v1` student success story system. These patterns apply to any Mongolian-language content generator that feeds into a template-driven carousel pipeline.

## Student Description Parsing

The Hermes content generator accepts a compact student description string and parses it into structured fields:

```
"Тэмүүлэн, 22, оюутан"           → name=Тэмүүлэн, age=22, occupation=оюутан, gender=male
"Батбаатар, 28, программист"     → name=Батбаатар, age=28, occupation=программист
"Номин, 20, оюутан, эм"          → name=Номин, age=20, occupation=оюутан, gender=female
```

### Pitfall: Mongolian Name Substring Gender Detection

**Problem:** Mongolian male names can contain substrings that match female keywords. The most common case:

| Name | Contains | Matches as | Actual gender |
|------|----------|------------|---------------|
| **Тэмүүлэн** | `эм` (female) | female ❌ | male |
| **Гэрэлтуяа** | `эм` | female ❌ | male |
| **Дэлгэрмөрөн** | `эмэгтэй` (woman) | female ❌ | male |

**Fix:** Use whole-word matching, not substring matching:

```python
# WRONG — "эм" is a substring of "Тэмүүлэн"
if "эм" in name.lower():
    gender = "female"

# RIGHT — check whole word boundaries
FEMALE_WORDS = ["эм", "эмэгтэй", "охин"]
def is_whole_word(text, target):
    text = text.lower().strip()
    words = text.split()
    return target in words

if any(is_whole_word(part, w) for w in FEMALE_WORDS):
    gender = "female"
```

Also note: Mongolian "эм" (woman/female) is a standalone word, not a substring match. Never use `in` for gender detection on Mongolian text.

### Age Detection

Mongolian ages can come in multiple formats:

| Input | Clean age |
|-------|-----------|
| `22` | `22` |
| `22 настай` | `22` |
| `22н` | `22` |

Handle by stripping common suffixes and checking digit content:

```python
age_clean = part.replace(" ", "")
age_clean = age_clean.replace("настай", "").replace("н", "")
if age_clean.isdigit():
    age = age_clean
```

## Content Story Format (Pipe-Delimited)

When generating marker values for a 4-slide success story carousel, use a pipe-delimited string to pass all 12 content fields in a single argument:

```
headline|quote|cta|problem1|problem2|problem3|week1|week2|week3|metric1|metric2|metric3
```

### Minimal (3 fields)

```
"45 хоногт AI апп бүтээж орлого олсон|Би өмнө нь код бичдэггүй байсан|Дараагийн амжилтын түүх та байж болно"
```

### Full (12 fields)

```
"45 хоногт AI апп бүтээж орлого олсон|Би өмнө нь код бичдэггүй байсан|Дараагийн амжилт та байж болно|Код бичдэггүй|Техникийн мэдлэг бага|Санаагаа бүтээдэггүй|AI Agent сурсан|MVP хийсэн|Хэрэглэгч авсан|5,000₮ орлого|120 хэрэглэгч|V2 гаргасан"
```

### Field Mapping

```
Index: 0         1     2    3         4         5         6       7      8        9           10          11
Field: headline | quote | cta | problem1 | problem2 | problem3 | week1 | week2 | week3 | metric1 | metric2 | metric3
```

### Default Values (if field not provided)

Each field has a Mongolian-language default so the carousel is always complete:

- `headline`: `"45 хоногт AI апп бүтээж орлого олсон"` (3-line fallback at script level)
- `quote`: `"Би өмнө нь код бичиж чаддаггүй байсан."`
- `cta`: `"Дараагийн амжилтын түүх та байж болно"`
- `problem_1/2/3`: `"Код бичиж чаддаггүй"` / `"Техникийн мдлэг бага"` / `"Санаагаа бүтээгдэхүүн болгож чаддаггүй"`
- `week_1/2/3`: `"AI Agent сурсан"` / `"MVP бүтээсэн"` / `"Анхны хэрэглэгчээ авсан"`
- `metric_1/2/3`: `"5,000₮ эхний орлого"` / `"120 хэрэглэгч"` / `"V2 хувилбар гаргасан"`

## KIE Image Prompt Templates for Student Slots

Each of the 4 image slots has a fixed prompt template. Only `{age}` and `{gender}` vary. The prompts themselves never change between carousels.

### Slot A — Student Portrait

```
Create a professional portrait photo of a young Mongolian student,
{age} years old, {gender}, in a professional setting.
Friendly smile, professional appearance, modern clothing.
White or cream background with soft yellow/gold accent lighting.
Studio quality photography, realistic, high resolution.
NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS.
One single portrait image.
```

### Slot B — Before/Struggle

```
Create a photo of a young Mongolian student,
{age} years old, {gender}, looking thoughtful and confused.
Sitting at a desk with a laptop, furrowed brow, thinking pose.
Educational setting, warm indoor lighting.
Realistic photography, professional quality.
NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS.
One single portrait image.
```

### Slot C — Success/Happy

```
Create a photo of a young Mongolian student,
{age} years old, {gender}, smiling happily with a laptop.
Celebrating success, looking confident and proud.
Bright lighting, achievement mood, professional look.
Realistic photography, high quality.
NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS.
One single portrait image.
```

### Slot D — Result/Dashboard

```
Create a clean modern mobile app dashboard or data visualization screen.
Colorful charts, achievement badges, progress bars.
Modern UI design, bright colors, clean minimal style.
NO TEXT, NO LETTERS, NO LOGOS, NO WATERMARKS.
One single square image.
```

Note: Slot D has no `{age}`/`{gender}` because it's a dashboard, not a person.

## Concrete Implementation

The full implementation for AI Global lives at:

```
/opt/data/social-content/brands/ai-global/
  scripts/generate_success_story.py    ← content generator (this reference)
  scripts/generate_slot_images.py      ← KIE image generator
  templates/aiglobal_success_story_v1/ ← template + renderer
```
