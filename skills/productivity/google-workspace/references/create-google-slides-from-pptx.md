# Creating Google Slides from .pptx

The `google_api.py` script has **no `slides` subcommand** for Google Slides API. Two workarounds:

## Option A: Convert .pptx via Drive upload (recommended)

Create a `.pptx` file locally with `python-pptx`, then upload to Google Drive with the Slides MIME type. Drive auto-converts.

```python
from googleapiclient.http import MediaFileUpload

# Build Drive service (see google_api.py for build_service helper)
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

**Pitfalls:**
- The `google_api.py drive upload --mime` flag does NOT work for conversion; use the raw API call above.
- Google Slides API must be enabled in the Cloud Console projects for the resulting Slides file to be editable via API. If only the Drive API is enabled, the file is created and viewable but Slides API `batchUpdate` calls will fail with 403.
- `python-pptx` must be installed: `pip install python-pptx`
- **Uploaded slides are private by default.** After upload, share them so the recipient can view:

```python
# Make viewable by anyone with link
drive.permissions().create(
    fileId=file_id,
    body={'type': 'anyone', 'role': 'reader'},
    fields='id,type,role'
).execute()

# Or share with a specific user as editor
drive.permissions().create(
    fileId=file_id,
    body={'type': 'user', 'role': 'writer', 'emailAddress': 'user@example.com'},
    fields='id,type,role,emailAddress'
).execute()
```

- For complex multi-slide presentations, use `templates/presentation-builder.py` from this skill — it provides reusable helpers (`add_bg`, `add_textbox`, `add_multi_text`, `add_card`, `add_rect`) for consistent brand-themed slides with minimal boilerplate.

## Option B: Enable Google Slides API + use directly

If the Google Slides API IS enabled (not just Drive), use the Slides API directly:

```python
slides = build_service('slides', 'v1')
pres = slides.presentations().create(body={'title': 'Title'}).execute()
pres_id = pres['presentationId']
# Then use batchUpdate to add slides, text, tables, etc.
```

But if the API isn't enabled, the Drive upload conversion is the only path.

## python-pptx Quick Reference

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.333)   # widescreen
prs.slide_height = Inches(7.5)

# Add blank slide
slide = prs.slides.add_slide(prs.slide_layouts[6])

# Background color
bg = slide.background.fill
bg.solid()
bg.fore_color.rgb = RGBColor(0x0D, 0x1B, 0x3E)  # dark blue

# Colored rectangle
shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0xD4, 0xAF, 0x37)  # gold
shape.line.fill.background()

# Text box
txBox = slide.shapes.add_textbox(left, top, width, height)
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Hello"
p.font.size = Pt(24)
p.font.bold = True
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

# Table
table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
table = table_shape.table
table.cell(0, 0).text = "Header"
table.cell(0, 0).fill.solid()
table.cell(0, 0).fill.fore_color.rgb = MED_BLUE

prs.save('output.pptx')
```
