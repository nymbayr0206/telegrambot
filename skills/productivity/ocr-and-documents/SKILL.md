---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, easyocr, marker-pdf)."
version: 2.4.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | easyocr (~500MB + models) | marker-pdf (~3-5GB) |
|---------|-----------------|----------------------------|---------------------|
| **Text-based PDF** | ✅ | ❌ (skip — use pymupdf) | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (80+ languages) | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ❌ | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ❌ | ✅ |
| **Code blocks** | ❌ | ❌ | ✅ |
| **Forms** | ❌ | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ❌ | ✅ |
| **Reading order detection** | ❌ | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (from any image) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ (core purpose) | ✅ |
| **EPUB** | ✅ | ❌ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ❌ (raw text only) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~500MB + model downloads (~200MB more) | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~5-30s/page (CPU) | ~1-14s/page (CPU), ~0.2s/page (GPU) |
| **No root / no tesseract** | ✅ | ✅ (pure Python) | ✅ (pure Python) |
| **Multilingual on CPU** | ❌ | ✅ (incl. Mongolian mn) | ✅ |

**Decision**: Use pymupdf for text-based PDFs. Use **easyocr** when you need OCR but system lacks space for marker-pdf, tesseract binary is missing, or the document has non-Latin scripts (Mongolian, Cyrillic, CJK). Use **marker-pdf** for complex layout, equations, forms, or when high-quality markdown output is essential.

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

If the system Python has no `pip` or is externally managed, use a throwaway `uv` virtualenv rather than forcing system installs:

```bash
uv venv /tmp/pdfvenv
uv pip install --python /tmp/pdfvenv/bin/python pymupdf pymupdf4llm
/tmp/pdfvenv/bin/python scripts/extract_pymupdf.py document.pdf --markdown
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## easyocr (Python-native OCR, good for multilingual)

Best for: scanned PDFs on systems without tesseract, limited disk (~700MB total), or documents in Mongolian/Cyrillic/CJK scripts.

```bash
pip install easyocr
```

**Pipeline: pymupdf → render pages → easyocr**

For scanned/image-based PDFs, render pages with pymupdf first, then OCR:

```python
import easyocr
import fitz  # pymupdf
from PIL import Image

# 1. Initialize reader with target languages
reader = easyocr.Reader(['en', 'mn'], gpu=False)  # Mongolian + English

# 2. Open PDF and render each page
doc = fitz.open('document.pdf')
for i in range(doc.page_count):
    page = doc[i]
    # Render at 300 DPI — high enough for OCR, manageable file size
    pix = page.get_pixmap(dpi=300)
    # PIL DecompressionBombWarning trigger at >89M pixels — resize if needed
    img_path = f'/tmp/page_{i}.png'
    pix.save(img_path)

    # 3. Downscale for OCR speed (1200px on longest side)
    img = Image.open(img_path)
    ratio = min(1200/img.width, 1200/img.height)
    new_size = (int(img.width*ratio), int(img.height*ratio))
    img_resized = img.resize(new_size, Image.LANCZOS)
    img_resized.save(f'/tmp/page_{i}_ocr.png', 'PNG')

    # 4. OCR
    results = reader.readtext(f'/tmp/page_{i}_ocr.png')
    for (bbox, text, confidence) in results:
        print(text)
```

**Key pitfalls:**
- **Huge renders**: 300 DPI on A4 → ~9400×13300 px (~125M pixels), triggers PIL DecompressionBombWarning. Always resize before passing to PIL/OCR.
- **Background process**: running easyocr in `terminal(background=true)` can fail if the process doesn't inherit the correct virtualenv. Run in foreground with generous timeout.
- **Language codes**: `easyocr.Reader(['mn', 'en'])` for Mongolian + English. Available: ['en', 'mn', 'zh', 'ja', 'ko', 'ru', 'de', 'fr', 'es', ...] — 80+ supported.
- **First run downloads**: model files (~200MB) are downloaded on first `Reader()` call. Expect 1-2 minutes on the first run, even on fast connections.
- **No markdown output**: easyocr returns raw text lines only. Layout, tables, and formatting are lost. For structured output, use marker-pdf.
- **GPU vs CPU**: GPU is much faster (0.5-2s/page vs 5-30s/page) but not available on all systems. Set gpu=True if CUDA is available.

PIL preprocessing (contrast boost, section cropping) from `references/pil-ocr-preprocessing.md` applies before the `reader.readtext()` call for improved accuracy on poor-quality scans.

---

## marker-pdf (high-quality OCR)

If marker-pdf is too heavy for the system, use **easyocr** above as a lighter alternative.

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## PDF → Coaching / Knowledge Base Workflow

When the user asks to "read this book" or "create a knowledge base" from a PDF, do not only summarize it in chat. Build a durable, navigable markdown knowledge base:

When the PDF is being used for social/carousel content, inspect the table of contents and estimate content volume from structure: major sections before appendix/index are a good default count for high-quality 4-slide carousel posts; detailed subsections are an expanded daily-campaign count. Store the source PDF under the relevant brand workspace when applicable, and save a concise carousel plan with total posts and total images.

1. Extract full text and metadata with PyMuPDF or marker as appropriate.
2. Save the raw extracted text beside the source PDF for later line/page lookup.
3. Inspect the table of contents and several high-value sections before synthesizing.
4. Create a directory such as `/opt/data/knowledge_bases/<slug>/` with:
   - `README.md` describing purpose, source PDF, extracted text path, and how to use it.
   - Numbered module notes for the major concepts/workflows.
   - A `source-index.md` or equivalent mapping important topics back to PDF pages/sections.
5. Translate old/domain-specific language into modern, ethical, reusable operating principles when appropriate.
6. If the user wants future coaching or recurring use, save a compact memory pointing to the KB path and its modules.

Prefer concise module notes over mirroring the entire PDF. Preserve enough source pointers to return to the original text later.

## DOCX (Word) Editing

For editing existing DOCX files — modifying paragraphs, tables, adding/removing rows, inserting signature tables — see `references/docx-editing.md`. This covers the python-docx patterns used for Mongolian government reports, handover documents, and business documents.

## XLSX (Excel) — stdlib-only parsing

When `openpyxl`/`pandas`/`xlrd` are unavailable (no pip, no root, no apt), parse `.xlsx` files using only Python stdlib (`zipfile` + `xml.etree.ElementTree`). An xlsx file is a ZIP of XML files.

See `references/xlsx-stdlib-parsing.md` for the full technique: shared strings, multi-sheet access, number formatting, date serial conversion, and pitfalls.

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)
- **OCR.space free API fallback** — when no local tools are available (no pip, no tesseract), use the zero-dependency OCR.space API. See `references/ocr-space-free-api.md`. Requires only Python stdlib (`urllib`, `base64`). Good for one-off image-to-text extraction.
- **PIL preprocessing for OCR** — when OCR results are poor, use PIL to preprocess: enlarge 2× (LANCZOS), grayscale, contrast enhancement (2-3×), sharpen. Crop image into horizontal sections and OCR each separately for better coverage of wide images or dense text. See `references/pil-ocr-preprocessing.md`.
- **Receipt → expense tracking workflow** — when the user sends a receipt image, OCR it, parse items/costs, categorize (food/transport/business), save to `/opt/data/finance/expenses/YYYY/MM/`, and track ebarimt lottery numbers. See `references/receipt-expense-workflow.md`.
- **eBarimt e-government API research** — Keycloak auth (client_id `vatps`), consumer/service endpoints, public info APIs, and known server addresses for Mongolia's digital receipt system. See `references/ebarimt-api-research.md`.
- **Contract terms analysis** — OCR a scanned contract → extract party registration numbers → extract penalty terms → calculate overdue penalties. Covers Mongolian contract terminology (алданги, торгууль, хугацаа), party identification (регистрийн дугаар), date math, common delay reasons for deliverable reports. See `references/contract-terms-analysis.md`.
- **PDF → Mongolian audiobook** — Extract English text, translate to Mongolian, format as multi-voice dialogue (male+female), and generate chapter-by-chapter MP3 via KIE ElevenLabs `elevenlabs/text-to-dialogue-v3`. Uses `scripts/kie_multi_voice_tts.py` at `/opt/data/scripts/`. Supported voices: Lily (♀), Callum/Daniel/Liam (♂). Pricing: ~$0.07/1K chars via KIE. See `references/pdf-to-mongolian-audiobook.md`.
