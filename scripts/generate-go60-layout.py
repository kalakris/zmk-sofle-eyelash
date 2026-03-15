#!/usr/bin/env python3
"""
Generate a Go60 MoErgo Layout Editor JSON from the Eyelash Sofle ZMK keymap.

This script converts the Sofle keymap into a Go60-compatible layout that can be
imported into the MoErgo Layout Editor at https://my.moergo.com/go60/

Usage:
    python3 scripts/generate-go60-layout.py

Output:
    sofle-eyelash-go60-layout.json (in repo root)

Import via: Go60 Layout Editor → Settings → Local Backup and Restore → Import

Key differences between Sofle and Go60:
- Sofle has 64 keys (including 4 encoder-column keys), Go60 has 60
- Encoder keys at Sofle positions 6, 19, 32, 45 are dropped
- Sofle bottom row has 6 keys/side (including encoder press);
  Go60 has 6 keys/side split into 3 bottom-row + 3 thumb-cluster
- Go60 doesn't include <dt-bindings/zmk/pointing.h>, so &mkp bindings
  can't be used as plain &kp entries — use the editor's built-in &mkp type
  or put them in the Mouse layer which the editor handles specially

Position mapping (Sofle → Go60):
- Rows 0-3: drop encoder column, shift right-side positions accordingly
- Row 4 (bottom/thumb): outer 3 keys → bottom row (48-53),
  inner 3 keys → thumb cluster (54-59), with innermost thumb keys
  (L_T3=56, R_T3=57) as the "extra" keys not present on Sofle

Go60 bottom row physical layout (outer → inner per side):
  Left:  48(L_C4R5) 49(L_C3R5) 50(L_C2R5) 54(L_T1) 55(L_T2) 56(L_T3)
  Right: 57(R_T3) 58(R_T2) 59(R_T1) 51(R_C2R5) 52(R_C3R5) 53(R_C4R5)

Hold-trigger-key-positions in all behaviors (hml, hmr, z_tmux, v_vim, lth)
are automatically converted from Sofle positions to Go60 positions.
Combo key-positions are also converted.
"""

import json
import uuid
import time

# =============================================================================
# Sofle position -> Go60 position mapping
# =============================================================================
# Sofle has 64 keys (13+13+13+13+12), Go60 has 60 keys
# Encoder positions 6, 19, 32, 45 are dropped

SOFLE_TO_GO60 = {}
for s in range(0, 6):    SOFLE_TO_GO60[s] = s         # row0 left 0-5 -> 0-5
for s in range(7, 13):   SOFLE_TO_GO60[s] = s - 1     # row0 right 7-12 -> 6-11
for s in range(13, 19):  SOFLE_TO_GO60[s] = s - 1     # row1 left 13-18 -> 12-17
for s in range(20, 26):  SOFLE_TO_GO60[s] = s - 2     # row1 right 20-25 -> 18-23
for s in range(26, 32):  SOFLE_TO_GO60[s] = s - 2     # row2 left 26-31 -> 24-29
for s in range(33, 39):  SOFLE_TO_GO60[s] = s - 3     # row2 right 33-38 -> 30-35
for s in range(39, 45):  SOFLE_TO_GO60[s] = s - 3     # row3 left 39-44 -> 36-41
for s in range(46, 52):  SOFLE_TO_GO60[s] = s - 4     # row3 right 46-51 -> 42-47
# Row 4: split into bottom row (48-53) and thumb cluster (54-59)
# Go60 layout:
#   48-50: left bottom row  (L_C4R5, L_C3R5, L_C2R5) — outer left keys
#   51-53: right bottom row (R_C2R5, R_C3R5, R_C4R5) — outer right keys
#   54-56: left thumb cluster  (L_T1, L_T2, L_T3)
#   57-59: right thumb cluster (R_T3, R_T2, R_T1)
# Sofle row 4: 52-57 (left), 58-63 (right)
#   Left outer 3 (MUTE, LCTRL, LALT) -> dropped MUTE, shift outward
#   Left inner 3 (LGUI, Space/Nav, Enter/Num) -> left thumbs 54-56
#   Right inner 3 (Enter, sk_RSHFT, Space/Sys) -> dropped Enter, shift outward
#   Right outer 3 (BSPC, VOL_DN, VOL_UP) -> right bottom 51-53
# Sofle 52 (MUTE) -> not mapped (encoder)
SOFLE_TO_GO60[53] = 48  # LCTRL -> L_C4R5 (outermost left)
SOFLE_TO_GO60[54] = 49  # LALT -> L_C3R5
SOFLE_TO_GO60[55] = 50  # LGUI -> L_C2R5
SOFLE_TO_GO60[56] = 54  # Space/Nav -> L_T1
SOFLE_TO_GO60[57] = 55  # Enter/Num -> L_T2
# position 56 (L_T3) = extra innermost key
# Sofle 58 (Enter) -> not mapped (dropped, already on left thumb)
# position 57 (R_T3) = extra innermost key
SOFLE_TO_GO60[59] = 58  # sk_RSHFT -> R_T2
SOFLE_TO_GO60[60] = 59  # Space/Sys -> R_T1
SOFLE_TO_GO60[61] = 51  # BSPC -> R_C2R5
SOFLE_TO_GO60[62] = 52  # VOL_DN -> R_C3R5
SOFLE_TO_GO60[63] = 53  # VOL_UP -> R_C4R5 (outermost right)
# Sofle 63 (VOL_UP) -> not mapped (dropped)


def convert_positions(sofle_positions):
    """Convert a list of Sofle key positions to Go60 positions."""
    result = []
    for p in sofle_positions:
        if p in SOFLE_TO_GO60:
            result.append(SOFLE_TO_GO60[p])
    return sorted(set(result))


# =============================================================================
# Converted hold-trigger-key-positions for Go60
# =============================================================================

HML_POSITIONS = convert_positions([33,34,35,36,37,38,46,47,48,49,50,51,55,56,57,59,60,53,54,52,7,8,9,10,11,12,25,24,23,22,21,20,61,62,63])
HMR_POSITIONS = convert_positions([1,2,3,4,5,13,14,15,16,17,18,26,27,28,29,30,0,31,39,40,41,42,43,44,52,53,54,55,56,57,59,60,61,62,63])
Z_TMUX_POSITIONS = convert_positions([21,22,23,34,35,36,47,48,49])
LTH_POSITIONS = list(range(60))  # all positions


# =============================================================================
# Helper functions
# =============================================================================

def kp(key):
    return {"value": "&kp", "params": [{"value": key}]}

def trans():
    return {"value": "&trans"}

def none_key():
    return {"value": "&none"}

def custom(binding, label=None, desc=None, bg=None):
    entry = {"value": "Custom", "params": [{"value": binding}]}
    decoration = {}
    if label: decoration["label"] = label
    if desc: decoration["description"] = desc
    if bg: decoration["background"] = bg
    if decoration:
        entry["decoration"] = decoration
    return entry

def ls(key):
    """Key with LS() modifier (editor-normalized format)."""
    return {"value": "&kp", "params": [{"value": "LS", "params": [{"value": key}]}]}

def mkp(button):
    return {"value": "&mkp", "params": [{"value": button}]}


# =============================================================================
# Layer definitions
# =============================================================================
# Layer indices:
# 0: Base       5: Step5      10: System
# 1: Step1      6: Step5a     11: Numpad
# 2: Step2      7: Step6      12: Tmux
# 3: Step3      8: Graphite   13: Vim
# 4: Step4      9: Nav        14: Mouse

# ============ LAYER 0: Base ============
base = [
    # Row 0 left (6 keys)
    custom("&esc_grave_tilde", "Esc/`/~", "Tap: Esc, Shift: ~, Mod: `"),
    kp("N1"), kp("N2"), kp("N3"), kp("N4"), kp("N5"),
    # Row 0 right (6 keys)
    kp("N6"), kp("N7"), kp("N8"), kp("N9"), kp("N0"), kp("BSPC"),
    # Row 1 left
    kp("TAB"), kp("Q"), kp("W"), kp("E"), kp("R"), kp("T"),
    # Row 1 right
    kp("Y"), kp("U"), kp("I"), kp("O"), kp("P"), kp("BSLH"),
    # Row 2 left (home row with HRMs)
    kp("GLOBE"),
    custom("&hml LCTRL A", "A", "Hold: Ctrl, Tap: A"),
    custom("&hml LALT S", "S", "Hold: Alt, Tap: S"),
    custom("&hml LGUI D", "D", "Hold: Cmd, Tap: D"),
    custom("&hml LSHFT F", "F", "Hold: Shift, Tap: F"),
    kp("G"),
    # Row 2 right (home row with HRMs)
    kp("H"),
    custom("&hmr RSHFT J", "J", "Hold: Shift, Tap: J"),
    custom("&hmr RGUI K", "K", "Hold: Cmd, Tap: K"),
    custom("&hmr RALT L", "L", "Hold: Alt, Tap: L"),
    custom("&hmr RCTRL SEMI", ";", "Hold: Ctrl, Tap: ;"),
    kp("SQT"),
    # Row 3 left
    kp("LSHFT"),
    custom("&z_tmux 12 Z", "Z/Tmux", "Hold: Tmux layer, Tap: Z"),
    kp("X"), kp("C"),
    custom("&v_vim 13 V", "V/Vim", "Hold: Vim layer, Tap: V"),
    kp("B"),
    # Row 3 right
    kp("N"), kp("M"), kp("COMMA"), kp("DOT"), kp("FSLH"), kp("RSHFT"),
    # Row 4 bottom row (positions 48-53): outermost keys
    # Shifted outward: dropped MUTE (encoder) from left, Enter from right
    kp("LCTRL"),  # L_C4R5 (48)
    kp("LALT"),   # L_C3R5 (49)
    kp("LGUI"),   # L_C2R5 (50)
    kp("BSPC"),   # R_C2R5 (51)
    kp("C_VOL_DN"),  # R_C3R5 (52)
    kp("C_VOL_UP"),  # R_C4R5 (53)
    # Row 4 thumb cluster (positions 54-59)
    custom("&lth 9 SPACE", "Space/Nav", "Hold: Nav layer, Tap: Space"),  # L_T1 (54)
    custom("&lth 11 RET", "Enter/Num", "Hold: Numpad layer, Tap: Enter"),  # L_T2 (55)
    kp("RET"),    # L_T3 (56) — innermost left thumb
    mkp("LCLK"),  # R_T3 (57) — innermost right thumb
    {"value": "&mkp", "params": [{"value": "RCLK"}], "decoration": {"label": "Sticky Shift", "description": "Sticky shift (one-shot)"}},  # R_T2 (58)
    custom("&lth 10 SPACE", "Space/Sys", "Hold: System layer, Tap: Space"),  # R_T1 (59)
]

# ============ LAYER 1: Step1 ============
step1 = [trans()] * 60
step1[25] = custom("&hml LCTRL N", "N", "Hold: Ctrl, Tap: N")
step1[33] = custom("&hmr RGUI A", "A", "Hold: Cmd, Tap: A")
step1[42] = kp("K")

# ============ LAYER 2: Step2 ============
step2 = [trans()] * 60
step2[15] = kp("D")
step2[17] = kp("L")
step2[25] = custom("&hml LCTRL N", "N", "Hold: Ctrl, Tap: N")
step2[27] = custom("&hml LGUI T", "T", "Hold: Cmd, Tap: T")
step2[33] = custom("&hmr RGUI A", "A", "Hold: Cmd, Tap: A")
step2[34] = custom("&hmr RALT E", "E", "Hold: Alt, Tap: E")
step2[42] = kp("K")

# ============ LAYER 3: Step3 ============
step3 = [trans()] * 60
step3[14] = kp("L")
step3[15] = kp("D")
step3[16] = kp("W")
step3[17] = kp("F")
step3[25] = custom("&hml LCTRL N", "N", "Hold: Ctrl, Tap: N")
step3[26] = custom("&hml LALT R", "R", "Hold: Alt, Tap: R")
step3[27] = custom("&hml LGUI T", "T", "Hold: Cmd, Tap: T")
step3[28] = custom("&hml LSHFT S", "S", "Hold: Shift, Tap: S")
step3[33] = custom("&hmr RGUI A", "A", "Hold: Cmd, Tap: A")
step3[34] = custom("&hmr RALT E", "E", "Hold: Alt, Tap: E")
step3[42] = kp("K")

# ============ LAYER 4: Step4 ============
step4 = [trans()] * 60
step4[14] = kp("L")
step4[15] = kp("D")
step4[16] = kp("W")
step4[17] = kp("F")
step4[18] = kp("SEMI")
step4[20] = kp("M")
step4[22] = kp("J")
step4[25] = custom("&hml LCTRL N", "N", "Hold: Ctrl, Tap: N")
step4[26] = custom("&hml LALT R", "R", "Hold: Alt, Tap: R")
step4[27] = custom("&hml LGUI T", "T", "Hold: Cmd, Tap: T")
step4[28] = custom("&hml LSHFT S", "S", "Hold: Shift, Tap: S")
step4[30] = kp("Y")
step4[31] = custom("&hmr RSHFT H", "H", "Hold: Shift, Tap: H")
step4[32] = custom("&hmr RGUI A", "A", "Hold: Cmd, Tap: A")
step4[33] = custom("&hmr RALT E", "E", "Hold: Alt, Tap: E")
step4[34] = custom("&hmr RCTRL I", "I", "Hold: Ctrl, Tap: I")
step4[42] = kp("K")
step4[43] = kp("P")

# ============ LAYER 5: Step5 ============
step5 = [trans()] * 60
step5[13] = kp("B")
step5[14] = kp("L")
step5[15] = kp("D")
step5[16] = kp("W")
step5[17] = kp("Z")
step5[18] = kp("SQT")
step5[19] = kp("F")
step5[20] = kp("O")
step5[21] = kp("U")
step5[22] = kp("J")
step5[25] = custom("&hml LCTRL N", "N", "Hold: Ctrl, Tap: N")
step5[26] = custom("&hml LALT R", "R", "Hold: Alt, Tap: R")
step5[27] = custom("&hml LGUI T", "T", "Hold: Cmd, Tap: T")
step5[28] = custom("&hml LSHFT S", "S", "Hold: Shift, Tap: S")
step5[30] = kp("Y")
step5[31] = custom("&hmr RSHFT H", "H", "Hold: Shift, Tap: H")
step5[32] = custom("&hmr RGUI A", "A", "Hold: Cmd, Tap: A")
step5[33] = custom("&hmr RALT E", "E", "Hold: Alt, Tap: E")
step5[34] = custom("&hmr RCTRL I", "I", "Hold: Ctrl, Tap: I")
step5[37] = custom("&z_tmux 12 Q", "Q/Tmux", "Hold: Tmux layer, Tap: Q")
step5[39] = kp("M")
step5[40] = custom("&v_vim 13 C", "C/Vim", "Hold: Vim layer, Tap: C")
step5[41] = kp("V")
step5[42] = kp("K")
step5[43] = kp("P")

# ============ LAYER 6: Step5a ============
step5a = [trans()] * 60
step5a[13] = kp("B")
step5a[14] = kp("L")
step5a[15] = kp("D")
step5a[16] = kp("W")
step5a[17] = kp("Z")
step5a[18] = kp("SEMI")
step5a[20] = kp("M")
step5a[22] = kp("J")
step5a[25] = custom("&hml LCTRL N", "N", "Hold: Ctrl, Tap: N")
step5a[26] = custom("&hml LALT R", "R", "Hold: Alt, Tap: R")
step5a[27] = custom("&hml LGUI T", "T", "Hold: Cmd, Tap: T")
step5a[28] = custom("&hml LSHFT S", "S", "Hold: Shift, Tap: S")
step5a[30] = kp("Y")
step5a[31] = custom("&hmr RSHFT H", "H", "Hold: Shift, Tap: H")
step5a[32] = custom("&hmr RGUI A", "A", "Hold: Cmd, Tap: A")
step5a[33] = custom("&hmr RALT E", "E", "Hold: Alt, Tap: E")
step5a[34] = custom("&hmr RCTRL I", "I", "Hold: Ctrl, Tap: I")
step5a[37] = custom("&z_tmux 12 Q", "Q/Tmux", "Hold: Tmux layer, Tap: Q")
step5a[41] = kp("F")
step5a[42] = kp("K")
step5a[43] = kp("P")

# ============ LAYER 7: Step6 ============
step6 = [trans()] * 60
step6[13] = kp("B")
step6[14] = kp("L")
step6[15] = kp("D")
step6[16] = kp("W")
step6[17] = kp("Z")
step6[18] = kp("SQT")
step6[19] = kp("F")
step6[20] = kp("O")
step6[21] = kp("U")
step6[22] = kp("J")
step6[25] = custom("&hml LCTRL N", "N", "Hold: Ctrl, Tap: N")
step6[26] = custom("&hml LALT R", "R", "Hold: Alt, Tap: R")
step6[27] = custom("&hml LGUI T", "T", "Hold: Cmd, Tap: T")
step6[28] = custom("&hml LSHFT S", "S", "Hold: Shift, Tap: S")
step6[30] = kp("Y")
step6[31] = custom("&hmr RSHFT H", "H", "Hold: Shift, Tap: H")
step6[32] = custom("&hmr RGUI A", "A", "Hold: Cmd, Tap: A")
step6[33] = custom("&hmr RALT E", "E", "Hold: Alt, Tap: E")
step6[34] = custom("&hmr RCTRL I", "I", "Hold: Ctrl, Tap: I")
step6[35] = kp("COMMA")
step6[37] = custom("&z_tmux 12 Q", "Q/Tmux", "Hold: Tmux layer, Tap: Q")
step6[39] = kp("M")
step6[40] = custom("&v_vim 13 C", "C/Vim", "Hold: Vim layer, Tap: C")
step6[41] = kp("V")
step6[42] = kp("K")
step6[43] = kp("P")
step6[44] = kp("DOT")
step6[45] = kp("MINUS")

# ============ LAYER 8: Graphite ============
graphite = [trans()] * 60
graphite[13] = kp("B")
graphite[14] = kp("L")
graphite[15] = kp("D")
graphite[16] = kp("W")
graphite[17] = kp("Z")
graphite[18] = custom("&graphite_apos", "'/_", "Tap: ', Shift: _")
graphite[19] = kp("F")
graphite[20] = kp("O")
graphite[21] = kp("U")
graphite[22] = kp("J")
graphite[25] = custom("&hml LCTRL N", "N", "Hold: Ctrl, Tap: N")
graphite[26] = custom("&hml LALT R", "R", "Hold: Alt, Tap: R")
graphite[27] = custom("&hml LGUI T", "T", "Hold: Cmd, Tap: T")
graphite[28] = custom("&hml LSHFT S", "S", "Hold: Shift, Tap: S")
graphite[30] = kp("Y")
graphite[31] = custom("&hmr RSHFT H", "H", "Hold: Shift, Tap: H")
graphite[32] = custom("&hmr RGUI A", "A", "Hold: Cmd, Tap: A")
graphite[33] = custom("&hmr RALT E", "E", "Hold: Alt, Tap: E")
graphite[34] = custom("&hmr RCTRL I", "I", "Hold: Ctrl, Tap: I")
graphite[35] = custom("&graphite_comma", ",/?", "Tap: comma, Shift: ?")
graphite[37] = custom("&z_tmux 12 Q", "Q/Tmux", "Hold: Tmux layer, Tap: Q")
graphite[39] = kp("M")
graphite[40] = custom("&v_vim 13 C", "C/Vim", "Hold: Vim layer, Tap: C")
graphite[41] = kp("V")
graphite[42] = kp("K")
graphite[43] = kp("P")
graphite[44] = kp("DOT")
graphite[45] = custom("&graphite_minus", "-/\"", "Tap: -, Shift: \"")
graphite[46] = custom("&graphite_slash", "/ /<", "Tap: /, Shift: <")

# ============ LAYER 9: Nav ============
nav = [
    # Row 0 left
    kp("GRAVE"), kp("F1"), kp("F2"), kp("F3"), kp("F4"), kp("F5"),
    # Row 0 right
    kp("F6"), kp("F7"), kp("F8"), kp("F9"), kp("F10"), trans(),
    # Row 1 left (mkp removed — Go60 doesn't include pointing.h)
    trans(), kp("GRAVE"),
    trans(),
    trans(),
    custom("&kp LG(R)", "Cmd+R", "Command+R"),
    trans(),
    # Row 1 right
    kp("PG_UP"), kp("HOME"), kp("UP"), kp("END"), kp("MINUS"), kp("EQUAL"),
    # Row 2 left
    trans(), ls("GRAVE"), trans(), trans(), trans(),
    trans(),
    # Row 2 right
    kp("PG_DN"), kp("LEFT"), kp("DOWN"), kp("RIGHT"), kp("LBKT"), kp("RBKT"),
    # Row 3 left
    trans(),
    custom("&kp LG(Z)", "Cmd+Z", "Undo"),
    custom("&kp LG(X)", "Cmd+X", "Cut"),
    custom("&kp LG(C)", "Cmd+C", "Copy"),
    custom("&kp LG(V)", "Cmd+V", "Paste"),
    trans(),
    # Row 3 right
    trans(), trans(), kp("INS"), kp("F11"), kp("F12"), trans(),
    # Row 4 bottom row (48-53)
    trans(), trans(), trans(),  # left bottom
    trans(), trans(), trans(),  # right bottom
    # Row 4 thumb cluster (54-59)
    trans(),  # L_T1
    trans(),  # L_T2
    trans(),  # L_T3
    trans(),  # R_T3
    trans(),  # R_T2
    kp("RET"),  # R_T1
]

# ============ LAYER 10: System ============
system = [
    # Row 0 left
    ls("GRAVE"),
    custom("&bt BT_SEL 0", "BT 0", "Bluetooth profile 0"),
    custom("&bt BT_SEL 1", "BT 1", "Bluetooth profile 1"),
    custom("&bt BT_SEL 2", "BT 2", "Bluetooth profile 2"),
    custom("&bt BT_SEL 3", "BT 3", "Bluetooth profile 3"),
    custom("&bt BT_SEL 4", "BT 4", "Bluetooth profile 4"),
    # Row 0 right
    kp("F6"), kp("F7"), kp("F8"), kp("F9"), kp("F10"), trans(),
    # Row 1 left
    trans(),
    custom("&to 0", "Base", "Switch to Base layer"),
    custom("&to 1", "Step1", "Switch to Step 1"),
    custom("&to 2", "Step2", "Switch to Step 2"),
    custom("&to 3", "Step3", "Switch to Step 3"),
    custom("&to 4", "Step4", "Switch to Step 4"),
    # Row 1 right
    custom("&to 5", "Step5", "Switch to Step 5"),
    custom("&to 6", "Step5a", "Switch to Step 5a"),
    custom("&to 7", "Step6", "Switch to Step 6"),
    custom("&to 8", "Graphite", "Switch to Graphite"),
    trans(), trans(),
    # Row 2 left
    trans(),
    custom("&out OUT_USB", "USB", "Output: USB"),
    custom("&out OUT_BLE", "BLE", "Output: Bluetooth"),
    custom("&bt BT_CLR", "BT Clr", "Clear current BT profile"),
    custom("&bt BT_CLR_ALL", "BT ClrAll", "Clear all BT profiles"),
    trans(),
    # Row 2 right
    trans(), trans(), trans(), trans(),
    ls("LBKT"),
    ls("RBKT"),
    # Row 3 left
    trans(),
    custom("&sys_reset", "Reset", "System reset"),
    trans(),
    custom("&bootloader", "Boot", "Enter bootloader"),
    trans(), trans(),
    # Row 3 right
    trans(), trans(),
    custom("&sys_reset", "Reset", "System reset"),
    custom("&soft_off", "Off", "Soft power off"),
    custom("&bootloader", "Boot", "Enter bootloader"),
    trans(),
    # Row 4 bottom row (48-53)
    trans(), trans(), trans(),  # left bottom
    trans(), trans(), trans(),  # right bottom
    # Row 4 thumb cluster (54-59)
    trans(),  # L_T1
    trans(),  # L_T2
    trans(),  # L_T3
    trans(),  # R_T3
    trans(),  # R_T2
    trans(),  # R_T1
]

# ============ LAYER 11: Numpad ============
numpad = [
    # Row 0
    trans(), trans(), trans(), trans(), trans(), trans(),
    trans(), trans(), trans(), trans(), trans(), trans(),
    # Row 1
    trans(), kp("N1"), kp("N2"), kp("N3"), kp("N4"), kp("N5"),
    kp("N6"), kp("N7"), kp("N8"), kp("N9"), kp("N0"), trans(),
    # Row 2
    trans(),
    custom("&rgb_ug RGB_BRI", "RGB+", "RGB brightness up"),
    custom("&rgb_ug RGB_BRD", "RGB-", "RGB brightness down"),
    trans(), trans(), trans(),
    trans(), kp("N4"), kp("N5"), kp("N6"), kp("MINUS"), trans(),
    # Row 3
    trans(),
    custom("&rgb_ug RGB_OFF", "RGB Off", "Turn off RGB"),
    custom("&rgb_ug RGB_ON", "RGB On", "Turn on RGB"),
    custom("&rgb_ug RGB_EFF", "Eff+", "RGB effect forward"),
    custom("&rgb_ug RGB_EFR", "Eff-", "RGB effect reverse"),
    custom("&rgb_ug RGB_SPI", "Spd+", "RGB speed increase"),
    trans(), kp("N1"), kp("N2"), kp("N3"), custom("&kp LS(EQUAL)", "+", "Plus"), trans(),
    # Row 4 bottom row (48-53)
    trans(), trans(), trans(),  # left bottom
    trans(), trans(), trans(),  # right bottom
    # Row 4 thumb cluster (54-59)
    trans(),  # L_T1
    trans(),  # L_T2
    trans(),  # L_T3
    trans(),  # R_T3
    kp("N0"),  # R_T2
    kp("N0"),  # R_T1
]

# ============ LAYER 12: Tmux ============
tmux = [trans()] * 60
tmux[19] = custom("&tmux_tab N7", "Tmux 7", "Tmux tab 7")
tmux[20] = custom("&tmux_tab N8", "Tmux 8", "Tmux tab 8")
tmux[21] = custom("&tmux_tab N9", "Tmux 9", "Tmux tab 9")
tmux[31] = custom("&tmux_tab N4", "Tmux 4", "Tmux tab 4")
tmux[32] = custom("&tmux_tab N5", "Tmux 5", "Tmux tab 5")
tmux[33] = custom("&tmux_tab N6", "Tmux 6", "Tmux tab 6")
tmux[43] = custom("&tmux_tab N1", "Tmux 1", "Tmux tab 1")
tmux[44] = custom("&tmux_tab N2", "Tmux 2", "Tmux tab 2")
tmux[45] = custom("&tmux_tab N3", "Tmux 3", "Tmux tab 3")
tmux[52] = custom("&tmux_tab N0", "Tmux 0", "Tmux tab 0")

# ============ LAYER 13: Vim ============
vim = [trans()] * 60
vim[20] = custom("&vim_split K", "Split Up", "Vim split up (Ctrl+W K)")
vim[31] = custom("&vim_split H", "Split Left", "Vim split left (Ctrl+W H)")
vim[32] = custom("&vim_split J", "Split Down", "Vim split down (Ctrl+W J)")
vim[33] = custom("&vim_split L", "Split Right", "Vim split right (Ctrl+W L)")

# ============ LAYER 14: Mouse ============
mouse = [trans()] * 60
mouse[57] = mkp("LCLK")
mouse[58] = mkp("RCLK")


# =============================================================================
# Custom behavior definitions (raw ZMK devicetree)
# =============================================================================

hml_pos_str = " ".join(str(p) for p in HML_POSITIONS)
hmr_pos_str = " ".join(str(p) for p in HMR_POSITIONS)
z_tmux_pos_str = " ".join(str(p) for p in Z_TMUX_POSITIONS)
lth_pos_str = " ".join(str(p) for p in LTH_POSITIONS)

custom_behaviors = f"""\
combos {{
    compatible = "zmk,combos";

    Backslash {{
        bindings = <&kp BACKSLASH>;
        key-positions = <22 21>;
    }};

    Quote {{
        bindings = <&kp SINGLE_QUOTE>;
        key-positions = <33 34>;
    }};

    Tab {{
        bindings = <&kp TAB>;
        key-positions = <13 14>;
    }};

    Minus {{
        bindings = <&kp MINUS>;
        key-positions = <20 19>;
    }};

    Equals {{
        bindings = <&kp EQUAL>;
        key-positions = <21 20>;
    }};

    LeftParen {{
        bindings = <&kp LPAR>;
        key-positions = <16 17>;
    }};

    RightParen {{
        bindings = <&kp RPAR>;
        key-positions = <18 19>;
    }};

    LBracket {{
        bindings = <&kp LEFT_BRACKET>;
        key-positions = <28 29>;
    }};

    RBracket {{
        bindings = <&kp RIGHT_BRACKET>;
        key-positions = <30 31>;
    }};

    LBrace {{
        bindings = <&kp LEFT_BRACE>;
        key-positions = <41 40>;
    }};

    RBrace {{
        bindings = <&kp RIGHT_BRACE>;
        key-positions = <42 43>;
    }};

    Underscore {{
        bindings = <&kp UNDER>;
        key-positions = <43 44>;
    }};
}};

macros {{
    tmux_tab: tmux_tab {{
        compatible = "zmk,behavior-macro-one-param";
        #binding-cells = <1>;
        wait-ms = <30>;
        tap-ms = <30>;
        bindings =
            <&macro_tap &kp LC(A)>
            , <&macro_param_1to1>
            , <&macro_tap &kp MACRO_PLACEHOLDER>;
    }};

    vim_split: vim_split {{
        compatible = "zmk,behavior-macro-one-param";
        #binding-cells = <1>;
        wait-ms = <30>;
        tap-ms = <30>;
        bindings =
            <&macro_tap &kp LC(W)>
            , <&macro_param_1to1>
            , <&macro_tap &kp MACRO_PLACEHOLDER>;
    }};
}};

behaviors {{
    inner_esc_grave: inner_esc_grave {{
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&kp ESC>, <&kp GRAVE>;
        mods = <(MOD_LCTL|MOD_RCTL|MOD_LALT|MOD_RALT|MOD_LGUI|MOD_RGUI)>;
    }};

    esc_grave_tilde: esc_grave_tilde {{
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&inner_esc_grave>, <&kp TILDE>;
        mods = <(MOD_LSFT|MOD_RSFT)>;
    }};

    graphite_apos: graphite_apos {{
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&kp SQT>, <&kp UNDER>;
        mods = <(MOD_LSFT|MOD_RSFT)>;
    }};

    graphite_minus: graphite_minus {{
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&kp MINUS>, <&kp DQT>;
        mods = <(MOD_LSFT|MOD_RSFT)>;
    }};

    graphite_comma: graphite_comma {{
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&kp COMMA>, <&kp QMARK>;
        mods = <(MOD_LSFT|MOD_RSFT)>;
    }};

    graphite_slash: graphite_slash {{
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&kp SLASH>, <&kp LESS_THAN>;
        mods = <(MOD_LSFT|MOD_RSFT)>;
    }};

    hml: hml {{
        compatible = "zmk,behavior-hold-tap";
        #binding-cells = <2>;
        flavor = "balanced";
        tapping-term-ms = <280>;
        quick-tap-ms = <175>;
        require-prior-idle-ms = <150>;
        bindings = <&kp>, <&kp>;
        hold-trigger-key-positions = <{hml_pos_str}>;
        hold-trigger-on-release;
    }};

    hmr: hmr {{
        compatible = "zmk,behavior-hold-tap";
        #binding-cells = <2>;
        flavor = "balanced";
        tapping-term-ms = <280>;
        quick-tap-ms = <175>;
        require-prior-idle-ms = <150>;
        bindings = <&kp>, <&kp>;
        hold-trigger-key-positions = <{hmr_pos_str}>;
        hold-trigger-on-release;
    }};

    z_tmux: z_tmux {{
        compatible = "zmk,behavior-hold-tap";
        #binding-cells = <2>;
        flavor = "balanced";
        tapping-term-ms = <280>;
        quick-tap-ms = <175>;
        require-prior-idle-ms = <150>;
        bindings = <&mo>, <&kp>;
        hold-trigger-key-positions = <{z_tmux_pos_str}>;
        hold-trigger-on-release;
    }};

    v_vim: v_vim {{
        compatible = "zmk,behavior-hold-tap";
        #binding-cells = <2>;
        flavor = "balanced";
        tapping-term-ms = <280>;
        quick-tap-ms = <175>;
        require-prior-idle-ms = <150>;
        bindings = <&mo>, <&kp>;
        hold-trigger-key-positions = <{z_tmux_pos_str}>;
        hold-trigger-on-release;
    }};

    lth: lth {{
        compatible = "zmk,behavior-hold-tap";
        #binding-cells = <2>;
        flavor = "balanced";
        tapping-term-ms = <280>;
        quick-tap-ms = <175>;
        bindings = <&mo>, <&kp>;
        hold-trigger-key-positions = <{lth_pos_str}>;
        hold-trigger-on-release;
    }};
}};
"""

custom_devicetree = ""


# =============================================================================
# Assemble the full layout
# =============================================================================

layout = {
    "keyboard": "go60",
    "firmware_api_version": "1",
    "locale": "en-US",
    "uuid": str(uuid.uuid4()),
    "parent_uuid": str(uuid.uuid4()),
    "unlisted": False,
    "date": int(time.time()),
    "creator": "kalakris",
    "title": "Sofle Eyelash Export",
    "notes": (
        "Exported from Eyelash Sofle ZMK keymap.\n\n"
        "Features:\n"
        "- Urob timerless home-row mods (hml/hmr with positional hold-tap)\n"
        "- Layer-tap thumb keys (lth) for Nav, Numpad, System layers\n"
        "- Esc/Grave/Tilde mod-morph\n"
        "- Tmux layer (Ctrl+A + number) via hold on Z\n"
        "- Vim split navigation via hold on V\n"
        "- Graphite layout with transition steps (layers 1-8)\n\n"
        "Layers:\n"
        "- 0: Base (QWERTY)\n"
        "- 1-7: Graphite transition steps\n"
        "- 8: Graphite (final)\n"
        "- 9: Nav (navigation, function keys)\n"
        "- 10: System (Bluetooth, bootloader, layer switching)\n"
        "- 11: Numpad\n"
        "- 12: Tmux (tab switching)\n"
        "- 13: Vim (split navigation)\n"
        "- 14: Mouse (trackpad click layer)"
    ),
    "tags": ["qwerty", "graphite", "home-row-mods", "mac"],
    "custom_defined_behaviors": custom_behaviors,
    "custom_devicetree": custom_devicetree,
    "config_parameters": [],
    "layout_parameters": {"cirque_touch_sensitivity": ""},
    "layer_names": [
        "Base", "Step1", "Step2", "Step3", "Step4",
        "Step5", "Step5a", "Step6", "Graphite",
        "Nav", "System", "Numpad", "Tmux", "Vim", "Mouse"
    ],
    "layers": [
        base, step1, step2, step3, step4, step5, step5a, step6, graphite,
        nav, system, numpad, tmux, vim, mouse
    ],
    "macros": [],
    "inputListeners": [
        {
            "code": "&cirque_lh_listener",
            "inputProcessors": [
                {"code": "&zip_xy_scaler", "params": [1, 16]},
                {"code": "&zip_xy_transform", "params": [["INPUT_TRANSFORM_Y_INVERT"]]},
                {"code": "&zip_xy_to_scroll_mapper", "params": []},
                {"code": "&zip_button_behaviors", "params": [{"value": "&none"}]}
            ]
        },
        {
            "code": "&cirque_rh_listener",
            "inputProcessors": [
                {"code": "&zip_xy_scaler", "params": [3, 1]},
                {"code": "&zip_button_behaviors", "params": [{"value": "&none"}]},
                {"code": "&zip_temp_layer", "params": [14, 200]}
            ]
        }
    ],
    "holdTaps": [],
    "combos": []
}

# Validate layer sizes
for i, layer in enumerate(layout["layers"]):
    assert len(layer) == 60, f"Layer {i} ({layout['layer_names'][i]}) has {len(layer)} keys, expected 60"

output_path = "/Users/kalakris/zmk-sofle-eyelash/sofle-eyelash-go60-layout.json"
with open(output_path, "w") as f:
    json.dump(layout, f, indent=2)

print(f"Generated Go60 layout: {output_path}")
print(f"  {len(layout['layers'])} layers, {len(layout['layers'][0])} keys per layer")
print(f"  UUID: {layout['uuid']}")
