# python-pptx + Google Slides Upload

Alternative to pptxgenjs for creating presentations from scratch using Python.

## When to Use

- Node.js/npm is not available but python-pptx is (e.g., Hermes venv at `/opt/hermes/.venv/bin/python`)
- You need complex multi-slide generation with programmatic logic, loops, conditional slides
- You need to upload the result to Google Drive as a native Google Slides presentation
- You need brand-specific color schemes, complex layouts, or Mongolian/other non-Latin text

## Dependencies

```bash
# Use Hermes venv (python-pptx pre-installed):
/opt/hermes/.venv/bin/python script.py

# Or install standalone:
pip install python-pptx
```

## Basic Structure

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)   # LAYOUT_WIDE
prs.slide_height = Inches(7.5)

# Add blank slide
slide = prs.slides.add_slide(prs.slide_layouts[6])

# Background
bg = slide.background.fill
bg.solid()
bg.fore_color.rgb = RGBColor(0x0A, 0x0E, 0x27)

# Colored rectangle shape
shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(1), Inches(5), Inches(3))
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x25, 0x63, 0xEB)
shape.line.fill.background()

# Text box
txBox = slide.shapes.add_textbox(Inches(1), Inches(0.5), Inches(11), Inches(1))
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Slide Title"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
p.font.name = 'Calibri'

# Save
prs.save('/path/to/output.pptx')
```

## Multi-line / Multi-paragraph Text Box

```python
def add_multi_text(slide, left, top, width, height, lines, default_size=16):
    """lines: list of (text, size, color, bold) tuples"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    
    for i, line in enumerate(lines):
        if isinstance(line, str):
            text, size, color, bold = line, default_size, WHITE, False
        else:
            text, size, color, bold = line[0], line[1], line[2], line[3]
        
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = text
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.bold = bold
        p.font.name = 'Calibri'
    
    return tf
```

## Brand Colors (hex to RGB)

```python
DARK_BG = RGBColor(0x0A, 0x0E, 0x27)      # deep navy
PRIMARY = RGBColor(0x25, 0x63, 0xEB)       # blue
TEAL = RGBColor(0x5E, 0xD4, 0xC0)          # teal accent
GOLD = RGBColor(0xD4, 0xAF, 0x37)          # gold accent
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xCC, 0xCC, 0xCC)
MID_BLUE = RGBColor(0x1E, 0x3A, 0x8A)      # medium blue (card bg)
ACCENT_RED = RGBColor(0xE0, 0x4F, 0x5F)    # red accent
```

## Uploading to Google Slides (via Drive)

After creating the .pptx file, upload it to Google Drive with the Google Slides MIME type. Drive auto-converts.

```python
import json, sys
sys.path.insert(0, '/path/to/google-workspace/scripts')
from google_api import build_service
from googleapiclient.http import MediaFileUpload

drive = build_service('drive', 'v3')

file_metadata = {
    'name': 'Presentation Title',
    'mimeType': 'application/vnd.google-apps.presentation'
}

media = MediaFileUpload(
    '/path/to/file.pptx',
    mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation',
    resumable=True
)

file = drive.files().create(
    body=file_metadata,
    media_body=media,
    fields='id,name,mimeType,webViewLink'
).execute()

url = file.get('webViewLink')
print(f'🔗 {url}')
```

### Share (anyone with link can view)

```python
drive.permissions().create(
    fileId=file_id,
    body={'type': 'anyone', 'role': 'reader'},
    fields='id,type,role'
).execute()
```

## Key Differences from pptxgenjs

| Aspect | python-pptx | pptxgenjs |
|--------|-------------|-----------|
| Language | Python | JavaScript/Node.js |
| Coordinates | Inches(), Emu() | Raw inches (float) |
| Colors | RGBColor(r,g,b) | Hex string without # |
| Text boxes | shapes.add_textbox() | slide.addText() |
| Shapes | MSO_SHAPE.RECTANGLE | pres.shapes.RECTANGLE |
| Slide size | prs.slide_width/height | Layout constant |
| Background | slide.background.fill | slide.background = {} |
| Runtime | /opt/hermes/.venv/bin/python | node + pptxgenjs npm global |

## Pitfalls

1. **`python` vs `python3`**: Hermes environments may not have `python` as a command. Use `python3` or the full venv path `/opt/hermes/.venv/bin/python`.
2. **`setup.py --check`**: If `python` not found, retry with `python3` before treating auth as broken. Or use `cd /tmp && HERMES_HOME=/opt/data /opt/hermes/.venv/bin/python .../setup.py --check`.
3. **Google API dependencies**: When running from inside a project checkout (e.g., `/opt/hermes`), `uv run` may try to build the current project. Use a neutral `workdir=/tmp` and set `HERMES_HOME=/opt/data` explicitly.
4. **Text overflow**: python-pptx text boxes have no auto-shrink. Make boxes tall enough or limit text length.
5. **No inline images**: Unlike pptxgenjs, python-pptx images must be added via `slide.shapes.add_picture()`, not embedded in text.
