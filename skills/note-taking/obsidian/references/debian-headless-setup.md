# Obsidian on Headless Debian (no root)

This reference captures the steps to install Obsidian and set up a vault on a Debian 13 (Trixie) server where the `hermes` user has no `sudo` access and no GUI display.

## Constraints encountered
- `sudo` not available
- `dpkg -i` refused for non-root
- `AppImage` requires FUSE (`libfuse.so.2`), which is also unavailable
- No desktop environment (`DISPLAY` unset)

## Working approach: extract AppImage manually

```bash
# 1. Download AppImage (111 MB)
curl -sL -o /tmp/obsidian.AppImage \
  "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.8.9/Obsidian-1.8.9.AppImage"

# 2. Extract without running (no FUSE needed)
cd /opt/data
chmod +x /tmp/obsidian.AppImage
/tmp/obsidian.AppImage --appimage-extract
# Creates squashfs-root/ with the obsidian binary + Electron runtime

# 3. Clean up after extraction (optional - binary not needed for filesystem vault work)
rm /tmp/obsidian.AppImage
rm -rf squashfs-root/
```

The Obsidian GUI cannot launch (no display), but the vault filesystem works perfectly — all note operations go through Hermes file tools (`read_file`, `write_file`, `search_files`, `patch`). The `.obsidian` config files make it a real vault that opens correctly when synced to a machine with a display.

## Installation alternatives (when available)
- Debian 13 Trixie: `apt install obsidian` (may be in repos)
- Snap: `snap install obsidian --classic`
- Flatpak: `flatpak install flathub md.obsidian.Obsidian`

## Vault path convention
On server environments, prefer `/opt/data/home/Obsidian Vault` over `~/Documents/Obsidian Vault` (which does not exist on headless installs).
