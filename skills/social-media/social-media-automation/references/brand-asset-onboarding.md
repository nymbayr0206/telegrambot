# Brand Asset Onboarding — Client Reference Materials

## When the client sends assets

When a client (or the user on behalf of a client) sends image/asset files and says "save these as reference materials," follow this workflow.

### Step 1: Check the brand workspace

```text
/opt/data/social-content/brands/<brand-slug>/
  brand-guide.md
  assets/
    logos/
    backgrounds/
    references/
    fonts/
  ...
```

If the brand workspace doesn't exist, create it per `templates/brand-guide.md` and the multi-brand layout documented in `references/multi-brand-carousel-workspace.md`.

### Step 2: Identify what each file is

If your model supports vision, analyze each image to classify it:

- **Logo** → `assets/logos/` — brand logo, icon, wordmark
- **Background** → `assets/backgrounds/` — brand-appropriate backgrounds, gradients, textures
- **Reference** → `assets/references/` — poster examples, mood boards, competitor ads, style guides
- **Font** → `assets/fonts/` (relative to assets root) — brand font files

**If vision is unavailable** (model doesn't support image input, or API rejects the image), ask the user to describe each image and provide a descriptive filename. Example:

> "I received 3 images. For each one, please tell me:
> 1. What is it? (logo, background, reference poster?)
> 2. What filename should I use?"

### Step 3: Use descriptive filenames

This user explicitly prefers **descriptive filenames** so they can reference assets by name later.

- `logo-ai-global.png` ✓ — can say "put logo on top right"
- `ref-brand-style.jpg` ✓ — can say "use this style reference"
- `background-wave-dark.jpg` ✓ — can say "use dark wave background"

Bad: `img_572764d865a.jpg` ✗ — meaningless hash

**Naming convention:**
- Prefix with asset type: `logo-`, `ref-`, `bg-`, `font-`
- Use the brand slug: `ai-global`, `postly`, `supernova`
- Describe the content: `logo-ai-global.png`, `bg-gradient-dark.jpg`
- Keep extensions the same (don't convert unless needed)

### Step 4: Copy files to correct subdirectory

Use `terminal()` or `exec_code()` to copy:

```bash
cp <source> /opt/data/social-content/brands/<slug>/assets/logos/logo-<slug>-<desc>.<ext>
cp <source> /opt/data/social-content/brands/<slug>/assets/references/ref-<slug>-<desc>.<ext>
cp <source> /opt/data/social-content/brands/<slug>/assets/backgrounds/bg-<slug>-<desc>.<ext>
```

### Step 5: Update brand-guide.md

After saving assets, update `brand-guide.md` to reflect what's now available:

```markdown
## Assets available
- Logo: `assets/logos/logo-ai-global.png`
- Background: `assets/backgrounds/bg-gradient-dark.jpg`
- References:
  - `assets/references/ref-brand-style.jpg`

## Visual identity (updated)
- Colors: (extract from reference or ask user)
- Fonts: (ask user if not provided)
```

Update the Status line from `draft` to include asset status:

```markdown
Status: draft — assets loaded, waiting for brand colors/fonts confirmation
```

### Step 6: Confirm with the user

Send a summary message confirming what was saved and where:

> "Saved your 3 assets to AI Global:
> - `logo-ai-global.png` → assets/logos/
> - `ref-poster-example.jpg` → assets/references/
> - `bg-gradient-dark.jpg` → assets/backgrounds/
>
> Now you can say 'put logo top right' and I'll find it.
> Still needed: brand colors, fonts, tagline — or we can use what's in the references."

## Extended directory structure

Beyond logos, backgrounds, and references, consider adding:

- **`people/`** — founder/CEO/team headshots, intro photos, spokesperson images. These are not logos but are used in different carousel/reel layouts. This session created a `people/` folder for founder + tushig-intro images.
- **`icons/`** — brand icons, social icons, bullet-point graphics (create as needed).

## Duplicate detection

Users occasionally re-upload the same files (e.g. re-sending from a different device or chat). Use **MD5 hashing** to detect duplicates before saving:

```bash
# Compare new uploads against existing assets
md5sum /opt/data/image_cache/new_upload.jpg /opt/data/social-content/brands/<slug>/assets/*/*.jpg
```

Or in Python:

```python
import hashlib
with open(path, 'rb') as f:
    h = hashlib.md5(f.read()).hexdigest()
```

If an uploaded file hashes identically to an existing asset, tell the user: "This matches the file I already have — it's the same as X." This avoids confusion when users re-send the same images with different auto-generated filenames.

## Key pitfalls

- **Don't rename files randomly** — the user's whole point was predictable filenames so they can reference them. Always ask for or derive a meaningful name.
- **Don't assume you can see the image** — if your model lacks vision, just copy the files and ask. Never pretend to have seen something you can't.
- **Don't save everything in one flat directory** — logos, backgrounds, references, and people serve different purposes. Use the subdirectory structure.
- **Don't overwrite existing assets** without asking.
- **Update the brand-registry.json** if this is a new brand being registered.
- **Telegram auto-renames uploaded files.** When a user sends images via Telegram, the Hermes gateway saves them as `img_<random-hash>.jpg` regardless of the original filename. The original name is lost. Do NOT tell the user "you named them X" — explicitly explain: *"Telegram renamed your files to auto-generated names. To organize them properly, tell me what each image is: logo, background, founder photo, etc."* Then derive a descriptive name yourself (e.g. `logo-ai-global.jpg`, `founder-ai-global.jpg`).
- **User frustration signal: "file-name-eer ni oilgoj bolohgui bnuu?"** (Can't you understand from the filename?) — When this happens, the user assumes the original filenames survived. Explain Telegram's auto-renaming calmly, then ask for classification rather than the filename itself.
