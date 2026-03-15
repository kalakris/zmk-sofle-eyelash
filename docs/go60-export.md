# Go60 Export

The Sofle keymap can be exported to MoErgo Go60 format for use with the Go60 Layout Editor.

## Export workflow

```bash
# Generate the Go60 layout JSON
python3 scripts/generate-go60-layout.py

# Import at https://my.moergo.com/go60/
# Settings → Local Backup and Restore → Import
# Then compile and flash from the editor
```

## Key files
- `scripts/generate-go60-layout.py` — Conversion script (Sofle keymap → Go60 JSON)
- `sofle-eyelash-go60-layout.json` — Generated output (importable by Go60 editor)

## Position mapping

Sofle has 64 keys, Go60 has 60. The 4 encoder-column keys (Sofle positions 6, 19, 32, 45) are dropped.

### Rows 0-3 (main grid)
Encoder column removed, right-side positions shift down accordingly.

### Row 4 (bottom/thumb)
Sofle has 6 keys per side. Go60 has 6 per side split into 3 bottom-row + 3 thumb-cluster.

The Sofle's outer 3 keys per side map to Go60 bottom row, inner 3 to thumb cluster. The innermost thumb keys (L_T3=56, R_T3=57) are "extra" keys not present on the Sofle.

Physical layout (outer → inner per side):
```
Left:  48(L_C4R5) 49(L_C3R5) 50(L_C2R5) 54(L_T1) 55(L_T2) 56(L_T3)
Right: 57(R_T3) 58(R_T2) 59(R_T1) 51(R_C2R5) 52(R_C3R5) 53(R_C4R5)
```

Current mapping:
```
Left:  LCTRL(48) LALT(49) LGUI(50) Space/Nav(54) Enter/Num(55) Enter(56)
Right: mkpLCLK(57) mkpRCLK(58) Space/Sys(59) BSPC(51) VOL_DN(52) VOL_UP(53)
```

Dropped keys: MUTE (encoder press, left), plain Enter (right, already on left thumb).

## Go60 Layout Editor JSON format

The JSON has these key fields:
- `layers` — Array of layers, each an array of 60 key entries
- `layer_names` — Array of layer name strings (must match `[a-zA-Z0-9_]`)
- `custom_defined_behaviors` — Raw ZMK devicetree for custom behaviors, macros, combos
- `custom_devicetree` — Raw devicetree inserted at top level (for `#define`, node overrides)
- `inputListeners` — Trackpad configuration (left/right cirque listeners)
- `layout_parameters` — Hardware params like `cirque_touch_sensitivity`

### Key entry formats
- Simple keypress: `{"value": "&kp", "params": [{"value": "A"}]}`
- Transparent: `{"value": "&trans"}`
- None: `{"value": "&none"}`
- Mouse click: `{"value": "&mkp", "params": [{"value": "LCLK"}]}`
- Custom behavior: `{"value": "Custom", "params": [{"value": "&hml LCTRL A"}], "decoration": {"label": "A", "description": "Hold: Ctrl"}}`
- Shifted key (editor-normalized): `{"value": "&kp", "params": [{"value": "LS", "params": [{"value": "GRAVE"}]}]}`

## Gotchas and lessons learned

### pointing.h not included
The Go60 editor's generated keymap does NOT `#include <dt-bindings/zmk/pointing.h>`. This means `&mkp` bindings must use the editor's built-in `&mkp` JSON type, not `Custom` entries with raw pointing codes. Using `custom("&mkp LCLK", ...)` will fail at compile time with "expected number or parenthesized expression".

### Key code normalization
The editor normalizes some key codes on export:
- `TILDE` → `LS(GRAVE)`
- `LBRC` → `LS(LBKT)`
- `RBRC` → `LS(RBKT)`

Use the normalized forms in the generator to avoid diffs on re-export.

### custom_defined_behaviors structure
- Do NOT wrap in `/ { }` — the editor inserts this content inside an existing root node
- Combos, macros, and behaviors blocks go here as sibling nodes
- `#define` directives should go in `custom_devicetree` instead

### custom_devicetree
- Inserted at top level, suitable for `#define` and node reference overrides (`&sk { ... };`)
- Be careful with Python f-strings: `{` and `}` need to be doubled (`{{`/`}}`) in f-strings but NOT in regular strings

### Layer names
Must contain only `a-zA-Z0-9_`. No spaces (e.g., "Step1" not "Step 1").

### Modifier-wrapped key codes
Key codes like `LG(R)`, `LS(EQUAL)` must use `Custom` entries, not plain `&kp` params. The editor's validation rejects them as plain key codes.

### inputListeners
Controls trackpad behavior. Don't overwrite with `[]` or trackpad settings get reset. The left trackpad is typically configured as scroll, right as mouse.

### Trackpad scroll scaling
`zip_xy_scaler` params are `[multiplier, divisor]` (max value 16). For scroll mode, higher divisor = slower scrolling. The scaler runs before `zip_xy_to_scroll_mapper` which converts continuous movement to discrete scroll ticks.

### Hold-trigger-key-positions
All positional hold-tap behaviors (hml, hmr, z_tmux, v_vim, lth) need their key positions converted from Sofle numbering to Go60 numbering. The generator script handles this automatically via `SOFLE_TO_GO60` mapping and `convert_positions()`.

### Combos
Combo key-positions also need conversion. The generator handles this with hardcoded Go60 positions derived from the Sofle originals.
