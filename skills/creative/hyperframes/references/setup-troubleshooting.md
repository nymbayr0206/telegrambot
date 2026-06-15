# HyperFrames Setup Troubleshooting

## Environment: HerMes Agent on Debian (VPS/Docker)

### 1. Node.js version

**Problem:** System Node is v20.19.2 (Debian stable). HyperFrames requires >= v22.

**Fix — nvm:**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 22
nvm use v22.22.3
```

If `~/.npmrc` has a `prefix` setting (from user-level npm config), nvm will complain. Silence with:
```bash
nvm use --delete-prefix v22.22.3
```

### 2. npm global install fails with EACCES

**Problem:** `npm install -g hyperframes` tries to write to `/usr/local/lib/node_modules/` and fails.

**Fix — set user-level prefix:**
```bash
mkdir -p ~/.npm-global
echo "prefix=$HOME/.npm-global" >> ~/.npmrc
export PATH="$HOME/.npm-global/bin:$PATH"
npm install -g hyperframes@latest
```

### 3. npm cache corrupted (root-owned files)

**Problem:** Previous npm runs created root-owned files in `~/.npm/_cacache/`. `npm install` fails with `ENOENT` on rename.

**Fix — bypass with separate cache dir:**
```bash
export NPM_CONFIG_CACHE=/tmp/hf-cache
mkdir -p /tmp/hf-cache
# Then run all npm/npx commands with this env var set
```

### 4. Chrome-headless-shell not found

**Problem:** System has no Chrome. `npx puppeteer browsers install chrome-headless-shell` fails because `unzip` is not installed (no sudo).

**Fix — manual download via Python:**
```bash
python3 -c "
import zipfile, os, shutil, urllib.request
url = 'https://storage.googleapis.com/chrome-for-testing-public/130.0.6723.91/linux64/chrome-headless-shell-linux64.zip'
urllib.request.urlretrieve(url, '/tmp/chrome.zip')
with zipfile.ZipFile('/tmp/chrome.zip', 'r') as z:
    z.extractall('/tmp/chrome-extract')
for root, dirs, files in os.walk('/tmp/chrome-extract'):
    for f in files:
        if 'chrome-headless-shell' in f:
            os.makedirs(os.path.expanduser('~/.local/bin'), exist_ok=True)
            shutil.copy2(os.path.join(root, f), os.path.expanduser('~/.local/bin/chrome-headless-shell'))
            os.chmod(os.path.expanduser('~/.local/bin/chrome-headless-shell'), 0o755)
            print('Installed chrome-headless-shell at ~/.local/bin/')
"
export PATH="$HOME/.local/bin:$PATH"
```

### 5. /dev/shm too small (64 MB)

**Problem:** Container has only 64 MB of shared memory. Chrome needs ≥256 MB for clean `HeadlessExperimental.beginFrame` capture.

**Fix — force screenshot fallback mode:**
```bash
export PRODUCER_FORCE_SCREENSHOT=true
# HyperFrames auto-detects and falls back to screenshot-based frame capture
# Works fine, just slightly slower. No Chrome crash.
```

### 6. Audio not included in rendered output

**Problem:** `<audio data-audio-id="bgm" data-start="0" data-duration="15" src="assets/bg_music.mp3">` is correctly set up in the HTML but the rendered MP4 has `hasAudio: false`.

**Likely root cause:** Screenshot fallback mode (`PRODUCER_FORCE_SCREENSHOT`) doesn't capture audio. Or the audio element is not detected by the capture pipeline in screenshot mode.

**Fix — add audio via FFmpeg post-processing:**
```bash
ffmpeg -y -i rendered_video.mp4 \
  -i assets/audio_file.mp3 \
  -t 15 \
  -c:v copy \
  -c:a aac -b:a 128k \
  -map 0:v:0 -map 1:a:0 \
  -shortest \
  final_with_audio.mp4
```

This is a reliable workaround regardless of the root cause.

### 7. Google Fonts fail in sandboxed render

**Problem:** `@import url('...fonts.googleapis.com...')` requires network access which may be blocked during render.

**Fix — use system fonts instead:**
- DejaVu Sans (good Cyrillic/Mongolian support): `font-family: 'DejaVu Sans', sans-serif;`
- DejaVu Serif: `font-family: 'DejaVu Serif', serif;`
- No @font-face declaration needed — system fonts are always available.

### 8. Lint: unscoped GSAP selectors

**Problem:** `hyperframes lint` warns about `unscoped_gsap_selector` when GSAP uses class names like `.divider` or `.logo-text` that could conflict across compositions.

**Fix — scope selectors to composition:**
```js
const R = "[data-composition-id=\"main\"]";
tl.from(R + " .logo-ai", { ... });
tl.to(R + " .divider", { ... });
```

### Full render command (this system)
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use --delete-prefix v22.22.3 --silent
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
export NPM_CONFIG_CACHE=/tmp/hf-cache
export PRODUCER_FORCE_SCREENSHOT=true

cd /path/to/project
hyperframes render --quality draft --output draft.mp4

# Add audio (if needed)
ffmpeg -y -i draft.mp4 -i assets/audio.mp3 -t 15 -c:v copy -c:a aac -shortest final.mp4
```
