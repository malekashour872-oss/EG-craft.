# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""In-game UI primitives (Arabic, RTL).

Spec ref: §14.1 — Helpers: draw_panel (dark 90% fill + gold 1 px
border), button (hover = lighter gold border + click sound),
draw_bar (segmented 10-notch bars, top-right; hp red, hunger
orange), Hotbar (bottom-centre; 9 slots of 44 px; selected slot has
a gold frame; item icons come from cached Surface copies of atlas
tiles (texture.py exports tile_surfaces)).
"""
from __future__ import annotations

from typing import Optional

import pygame


GOLD = (255, 200, 60)
DARK_PANEL = (15, 12, 18, 230)
HP_RED = (180, 30, 30)
HUNGER_ORANGE = (200, 120, 30)
HOTBAR_SLOT_SIZE = 44
SEGMENTS = 10


def draw_panel(surface: pygame.Surface, x: int, y: int,
               w: int, h: int) -> pygame.Rect:
    """Dark 90% fill + gold 1 px border."""
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill(DARK_PANEL)
    pygame.draw.rect(panel, GOLD, (0, 0, w, h), 1)
    surface.blit(panel, (x, y))
    return pygame.Rect(x, y, w, h)


def button(surface: pygame.Surface, font: pygame.font.Font,
           label: str, x: int, y: int, w: int, h: int,
           hover: bool = False) -> pygame.Rect:
    """Hover = lighter gold border."""
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill(DARK_PANEL)
    border = (255, 230, 100) if hover else GOLD
    pygame.draw.rect(panel, border, (0, 0, w, h), 2 if hover else 1)
    surface.blit(panel, (x, y))
    # Render Arabic label centered
    from engine.arabic_text import shaped_width, shape
    text_color = (255, 255, 255)
    # Render right-to-left centered
    sw = shaped_width(font, label)
    text_x = x + (w - sw) // 2
    text_y = y + (h - font.get_height()) // 2
    # Use plain font.render for now (the shaper handles Arabic)
    # actually need our shaped render
    from engine.arabic_text import render_text
    # Render at text_x as the LEFT edge; but Arabic is RTL.
    # We render right-aligned at right_x = text_x + sw.
    render_text(surface, font, label, text_color,
                text_x + sw, text_y)
    return pygame.Rect(x, y, w, h)


def draw_bar(surface: pygame.Surface, x: int, y: int,
             val: int, max_val: int, color: tuple[int, int, int],
             bar_w: int = 200, bar_h: int = 18) -> None:
    """Segmented 10-notch bar."""
    # Background
    pygame.draw.rect(surface, (20, 20, 20), (x, y, bar_w, bar_h))
    # Segments
    seg_w = bar_w / SEGMENTS
    filled = int(SEGMENTS * val / max(1, max_val))
    for i in range(SEGMENTS):
        seg_x = int(x + i * seg_w) + 1
        seg_w_int = int(seg_w) - 2
        if i < filled:
            pygame.draw.rect(surface, color,
                              (seg_x, y + 1, seg_w_int, bar_h - 2))
        else:
            pygame.draw.rect(surface, (40, 40, 40),
                              (seg_x, y + 1, seg_w_int, bar_h - 2))


def draw_hotbar(surface: pygame.Surface, font: pygame.font.Font,
                inv, screen_w: int) -> None:
    """9-slot hotbar at bottom-centre."""
    slot_count = 9
    total_w = slot_count * HOTBAR_SLOT_SIZE
    x0 = (screen_w - total_w) // 2
    y = surface.get_height() - HOTBAR_SLOT_SIZE - 8
    from engine.texture import tile_surfaces
    tiles = tile_surfaces()
    for i in range(slot_count):
        sx = x0 + i * HOTBAR_SLOT_SIZE
        rect = pygame.Rect(sx, y, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_SIZE)
        pygame.draw.rect(surface, (20, 20, 20), rect)
        if i == inv.selected:
            pygame.draw.rect(surface, GOLD, rect, 2)
        else:
            pygame.draw.rect(surface, (80, 70, 30), rect, 1)
        # Draw item icon if any
        slot = inv.slots[i]
        if not slot.empty:
            # Look up tile from block def
            from world.blocks import get as get_block
            bdef = get_block(slot.id)
            tile_idx = bdef.tiles[1] if bdef.id != 0 else slot.id - 100
            surf = tiles.get(tile_idx)
            if surf is None and slot.id >= 100:
                # item — pick first tile from item mapping
                surf = tiles.get(2)  # dirt as fallback
            if surf is not None:
                # Scale to 32×32
                scaled = pygame.transform.scale(surf, (32, 32))
                surface.blit(scaled, (sx + 6, y + 6))


def draw_crosshair(surface: pygame.Surface,
                   cx: int, cy: int, color=(255, 255, 255)) -> None:
    """Plus-shaped crosshair at screen centre."""
    pygame.draw.line(surface, color, (cx - 8, cy), (cx + 8, cy), 2)
    pygame.draw.line(surface, color, (cx, cy - 8), (cx, cy + 8), 2)


def draw_vignette(surface: pygame.Surface, alpha: float,
                  color=(255, 0, 0)) -> None:
    """Red damage vignette."""
    if alpha <= 0:
        return
    w, h = surface.get_size()
    vignette = pygame.Surface((w, h), pygame.SRCALPHA)
    a = int(alpha * 100)
    # Gradient — simplified: solid translucent border
    for i in range(8):
        pygame.draw.rect(vignette, (color[0], color[1], color[2], a // (i + 1)),
                          (i * 4, i * 4, w - i * 8, h - i * 8), 4)
    surface.blit(vignette, (0, 0))
