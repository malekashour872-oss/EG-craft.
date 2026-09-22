# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Hand-written Arabic text shaping (no arabic_reshaper, no python-bidi).

Spec ref: §3.3 — Implement FROM SCRATCH. arabic_reshaper and
python-bidi are forbidden (they break under pygbag).

Steps:
1. ARABIC_FORMS table: for each of the 36 letters, store the Unicode
   presentation-form codepoints for the 4 forms: isolated, initial,
   medial, final.
2. Joining rules: a letter connects to the NEXT letter unless it is
   in NON_JOINERS = {ء, آ, أ, إ, ا, د, ذ, ر, ز, و, ؤ, ى, ة}.
   Connects to previous and next ⇒ medial; previous only ⇒ final;
   next only ⇒ initial; neither ⇒ isolated. Lam + Alef ⇒ single
   ligature codepoint (ﻷ ﻹ ﻺ ﻻ).
3. Shaping output: list of presentation-form glyphs in logical order.
   For rendering: reverse the glyph list (pygame renders LTR), then
   call pygame.font.Font.render(...). Numbers/Latin inside Arabic
   strings keep their order — isolate them as LTR runs during
   reversal.
4. API: shape(text: str) -> str and render_text(surface, font, text,
   color, right_x: int, y: int), which blits right-aligned at right_x.
   All UI is right-aligned (RTL layout).

Per A-1: add ا (alef, U+0627) and ؤ (waw-hamza, U+0624) to
ARABIC_FORMS (36 letters). Treat tatweel as a pass-through joiner.
Per A-2: Harakat U+064B–U+0652 are transparent to joining.
"""
from __future__ import annotations

from typing import Optional

import pygame


# ─────────────────────────────────────────────────────────────
# Presentation-form codepoints for the 36 Arabic letters.
# Source: Unicode Standard, "Arabic Presentation Forms-B" block.
#
# Format: base_letter → (isolated, initial, medial, final)
# ─────────────────────────────────────────────────────────────
ARABIC_FORMS: dict[int, tuple[int, int, int, int]] = {
    # أ همزة
    0x0621: (0xFE80, 0xFE80, 0xFE80, 0xFE80),  # ء — only connects in some
    # آ أ إ ا (alef family — NON_JOINERS)
    0x0622: (0xFE81, 0xFE81, 0xFE82, 0xFE82),  # آ
    0x0623: (0xFE83, 0xFE83, 0xFE84, 0xFE84),  # أ
    0x0625: (0xFE87, 0xFE87, 0xFE88, 0xFE88),  # إ
    0x0627: (0xFE8D, 0xFE8D, 0xFE8E, 0xFE8E),  # ا
    # ب
    0x0628: (0xFE8F, 0xFE91, 0xFE92, 0xFE90),  # ب
    # ة ة
    0x0629: (0xFE93, 0xFE93, 0xFE94, 0xFE94),  # ة — only final form
    # ت ث
    0x062A: (0xFE95, 0xFE97, 0xFE98, 0xFE96),  # ت
    0x062B: (0xFE99, 0xFE9B, 0xFE9C, 0xFE9A),  # ث
    # ج ح خ
    0x062C: (0xFE9D, 0xFE9F, 0xFEA0, 0xFE9E),  # ج
    0x062D: (0xFEA1, 0xFEA3, 0xFEA4, 0xFEA2),  # ح
    0x062E: (0xFEA5, 0xFEA7, 0xFEA8, 0xFEA6),  # خ
    # د ذ (NON_JOINERS)
    0x062F: (0xFEA9, 0xFEA9, 0xFEAA, 0xFEAA),  # د
    0x0630: (0xFEAB, 0xFEAB, 0xFEAC, 0xFEAC),  # ذ
    # ر ز (NON_JOINERS)
    0x0631: (0xFEAD, 0xFEAD, 0xFEAE, 0xFEAE),  # ر
    0x0632: (0xFEAF, 0xFEAF, 0xFEB0, 0xFEB0),  # ز
    # س ش ص ض ط ظ ع غ
    0x0633: (0xFEB1, 0xFEB3, 0xFEB4, 0xFEB2),  # س
    0x0634: (0xFEB5, 0xFEB7, 0xFEB8, 0xFEB6),  # ش
    0x0635: (0xFEB9, 0xFEBB, 0xFEBC, 0xFEBA),  # ص
    0x0636: (0xFEBD, 0xFEBF, 0xFEC0, 0xFEBE),  # ض
    0x0637: (0xFEC1, 0xFEC3, 0xFEC4, 0xFEC2),  # ط
    0x0638: (0xFEC5, 0xFEC7, 0xFEC8, 0xFEC6),  # ظ
    0x0639: (0xFEC9, 0xFECB, 0xFECC, 0xFECA),  # ع
    0x063A: (0xFECD, 0xFECF, 0xFED0, 0xFECE),  # غ
    # ٱ ڡ ڡ
    0x0671: (0xFB50, 0xFB50, 0xFB51, 0xFB51),  # ٱ alef-wasla (rare)
    # ف ق
    0x0641: (0xFED1, 0xFED3, 0xFED4, 0xFED2),  # ف
    0x0642: (0xFED5, 0xFED7, 0xFED8, 0xFED6),  # ق
    # ك ل
    0x0643: (0xFED9, 0xFEDB, 0xFEDC, 0xFEDA),  # ك
    0x0644: (0xFEDD, 0xFEDF, 0xFEE0, 0xFEDE),  # ل
    # م ن
    0x0645: (0xFEE1, 0xFEE3, 0xFEE4, 0xFEE2),  # م
    0x0646: (0xFEE5, 0xFEE7, 0xFEE8, 0xFEE6),  # ن
    # ه و
    0x0647: (0xFEE9, 0xFEEB, 0xFEEC, 0xFEEA),  # ه
    0x0648: (0xFEED, 0xFEED, 0xFEEE, 0xFEEE),  # و — NON_JOINER
    # ى
    0x0649: (0xFEEF, 0xFEEF, 0xFEF0, 0xFEF0),  # ى — NON_JOINER
    # ي
    0x064A: (0xFEF1, 0xFEF3, 0xFEF4, 0xFEF2),  # ي
    # ؤ (waw-hamza, NON_JOINER per A-1)
    0x0624: (0xFE85, 0xFE85, 0xFE86, 0xFE86),  # ؤ
    # إ (already covered) — silence duplicates
}

# Letters that don't connect to the NEXT letter (per §3.3)
NON_JOINERS = {
    0x0621, 0x0622, 0x0623, 0x0625, 0x0627,  # ء آ أ إ ا
    0x062F, 0x0630,                          # د ذ
    0x0631, 0x0632,                          # ر ز
    0x0648,                                  # و
    0x0624,                                  # ؤ
    0x0649,                                  # ى
    0x0629,                                  # ة
}

# Harakat (diacritics) — transparent to joining (A-2)
HARAKAT = set(range(0x064B, 0x0653)) | {0x0670}

# Tatweel — pass-through joiner (A-1)
TATWEEL = 0x0640

# Lam-alef ligatures (per A-4)
# madda FEF5/FEF6, hamza-above FEF7/FEF8, hamza-below FEF9/FEFA,
# plain FEFB/FEFC (isolated/final)
LAM_ALEF_LIGATURES = {
    # (lam_form, alef_char) → ligature_codepoint
    # Plain alef combinations
    (0xFEDE, 0x0622): 0xFEF5,  # isolated madda
    (0xFEDF, 0x0622): 0xFEF6,  # final madda
    (0xFEDE, 0x0623): 0xFEF7,  # isolated hamza-above
    (0xFEDF, 0x0623): 0xFEF8,  # final hamza-above
    (0xFEDE, 0x0625): 0xFEF9,  # isolated hamza-below
    (0xFEDF, 0x0625): 0xFEFA,  # final hamza-below
    (0xFEDE, 0x0627): 0xFEFB,  # isolated plain
    (0xFEDF, 0x0627): 0xFEFC,  # final plain
}


def _is_arabic_letter(cp: int) -> bool:
    return cp in ARABIC_FORMS


def _is_non_joiner(cp: int) -> bool:
    return cp in NON_JOINERS


def _is_harakat(cp: int) -> bool:
    return cp in HARAKAT


def _next_letter(codepoints: list[int], i: int) -> Optional[int]:
    """Return the next arabic letter codepoint after index i, or None."""
    j = i + 1
    while j < len(codepoints):
        cp = codepoints[j]
        if _is_harakat(cp) or cp == TATWEEL:
            j += 1
            continue
        return cp
    return None


def _prev_letter(codepoints: list[int], i: int) -> Optional[int]:
    """Return the previous arabic letter codepoint before index i, or None."""
    j = i - 1
    while j >= 0:
        cp = codepoints[j]
        if _is_harakat(cp) or cp == TATWEEL:
            j -= 1
            continue
        return cp
    return None


def shape(text: str) -> str:
    """Shape Arabic text into presentation-form codepoints.

    Returns a string of presentation-form glyphs in logical order.
    """
    if not text:
        return ""

    cps = [ord(c) for c in text]
    out: list[int] = []
    i = 0
    while i < len(cps):
        cp = cps[i]
        if _is_harakat(cp) or cp == TATWEEL:
            # Pass through (harakat attached to base letter)
            out.append(cp)
            i += 1
            continue
        if not _is_arabic_letter(cp):
            # Latin / digit / punctuation — keep as-is
            out.append(cp)
            i += 1
            continue
        # Arabic letter — determine form
        prev_cp = _prev_letter(cps, i)
        next_cp = _next_letter(cps, i)

        prev_can_join = (prev_cp is not None
                          and _is_arabic_letter(prev_cp)
                          and not _is_non_joiner(prev_cp))
        # Special: lam + alef ligature
        if cp == 0x0644 and next_cp in (0x0622, 0x0623, 0x0625, 0x0627):
            # Lam followed by alef-family → ligature
            # Determine if the ligature is isolated or final
            if prev_can_join:
                # final form
                lam_form = 0xFEDF  # lam-final
            else:
                # isolated
                lam_form = 0xFEDE
            lig = LAM_ALEF_LIGATURES.get((lam_form, next_cp))
            if lig is not None:
                out.append(lig)
                # Skip the alef
                i += 2
                continue

        # Standard 4-form shaping
        isolated, initial, medial, final = ARABIC_FORMS[cp]
        connects_prev = prev_can_join
        connects_next = (next_cp is not None
                         and _is_arabic_letter(next_cp)
                         and not _is_non_joiner(cp))
        if connects_prev and connects_next:
            out.append(medial)
        elif connects_prev and not connects_next:
            out.append(final)
        elif not connects_prev and connects_next:
            out.append(initial)
        else:
            out.append(isolated)
        i += 1

    return "".join(chr(cp) for cp in out)


def _split_runs(text: str) -> list[tuple[str, bool]]:
    """Split text into runs, marking each as Arabic (RTL) or LTR
    (digits/Latin). Returns list of (substring, is_rtl)."""
    runs: list[tuple[str, bool]] = []
    if not text:
        return runs
    current = ""
    current_rtl = (ord(text[0]) in ARABIC_FORMS
                   or _is_harakat(ord(text[0]))
                   or ord(text[0]) == TATWEEL)
    for ch in text:
        cp = ord(ch)
        is_rtl = (cp in ARABIC_FORMS or _is_harakat(cp) or cp == TATWEEL)
        if is_rtl != current_rtl:
            runs.append((current, current_rtl))
            current = ""
            current_rtl = is_rtl
        current += ch
    if current:
        runs.append((current, current_rtl))
    return runs


def render_text(surface: pygame.Surface, font: pygame.font.Font,
                text: str, color: tuple[int, int, int],
                right_x: int, y: int) -> pygame.Rect:
    """Render Arabic text right-aligned at (right_x, y).

    Returns the blit rect.
    """
    runs = _split_runs(text)
    # Shape Arabic runs and reverse their order so pygame renders LTR.
    # The runs are in logical order; for an RTL string we display them
    # right-to-left. The simplest approach: render each run separately,
    # accumulate widths, and blit right-to-left starting at right_x.
    rendered: list[tuple[pygame.Surface, int]] = []
    total_width = 0
    for substring, is_rtl in runs:
        if is_rtl:
            shaped = shape(substring)
            # Reverse for LTR rendering in pygame
            display = shaped[::-1]
        else:
            display = substring
        surf = font.render(display, True, color)
        rendered.append((surf, total_width))
        total_width += surf.get_width()

    # Blit right-to-left starting at right_x
    x = right_x
    for surf, _ in reversed(rendered):
        x -= surf.get_width()
        surface.blit(surf, (x, y))
    return pygame.Rect(right_x - total_width, y, total_width,
                        font.get_height())


def shaped_width(font: pygame.font.Font, text: str) -> int:
    """Return the rendered width of shaped text."""
    runs = _split_runs(text)
    total = 0
    for substring, is_rtl in runs:
        if is_rtl:
            display = shape(substring)[::-1]
        else:
            display = substring
        total += font.size(display)[0]
    return total
