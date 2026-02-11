# CLAUDE.md

## Repository Overview

ZMK firmware configuration for the Eyelash Sofle split keyboard. This is a ZMK user config repo — it defines the keymap, board configuration, and build settings. The actual ZMK firmware source is pulled in via West (Zephyr's package manager).

## Key Files

- `config/eyelash_sofle.keymap` — Main keymap file (layers, behaviors, combos, macros)
- `config/eyelash_sofle.conf` — Kconfig settings (RGB, sleep, Bluetooth, mouse, etc.)
- `build.yaml` — Defines which boards/shields to build (left with ZMK Studio, right, settings_reset)
- `config/west.yml` — West manifest pinning ZMK version and additional modules
- `boards/` — Custom board definitions for the Eyelash Sofle

## Building and Downloading Firmware

Firmware is built via GitHub Actions. Every push triggers the `Build and Draw` workflow.

### Build + Download workflow

```bash
# 1. Push changes
git push

# 2. Watch the build (optional — it takes ~2 min)
gh run list --limit 1
gh run watch          # live stream of build progress

# 3. Download firmware artifacts once complete
gh run download --dir firmware

# Firmware files land in firmware/firmware/:
#   eyelash_sofle_studio_left.uf2        — left half (with ZMK Studio enabled)
#   nice_view_adapter nice_view_battery-eyelash_sofle_right-zmk.uf2  — right half
#   settings_reset-eyelash_sofle_left-zmk.uf2  — settings reset
```

The workflow also auto-commits a keymap drawing via keymap-drawer (commit message prefixed with `[Draw]`). This means after pushing, the remote may have one extra commit — use `git pull --rebase` before pushing again.

## Keymap Architecture

### Layers
0. **Base** — QWERTY with home-row mods (urob timerless HRM pattern)
1. **Nav** — Navigation, function keys, mouse keys
2. **Layer 2** — Bluetooth, system controls, bootloader
3. **Numpad** — Number pad layout
4. **Tmux** — Tmux tab switching via `tmux_tab` macro (Ctrl+A then number)

### Behaviors
- `hml` / `hmr` — Left/right home-row mods using positional hold-tap with `require-prior-idle-ms`
- `lth` — Layer-tap for thumb keys. Like HRMs but uses `hold-trigger-key-positions` (all keys) and `hold-trigger-on-release` instead of `require-prior-idle-ms`, so layer-hold works reliably after quick keypresses
- `z_tmux` — Hold Z for Tmux layer, tap for Z
- `esc_grave_tilde` — Tap for Esc, Shift for ~, other mods for `

### Key Constants
- `QUICK_TAP_MS = 175` — Quick-tap window used across behaviors
