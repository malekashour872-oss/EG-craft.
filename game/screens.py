# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""UI screens.

Spec ref: §14.2 — Screen flow & contents.
- Splash (3 s, skippable by click) per §2.7
- Main menu: large gold "EG Craft"; buttons top→bottom: ابدأ اللعب →
  mode submenu (الإبداعي · البقاء) → سجل الكائنات → الإعدادات →
  حقوق الملكية → خروج; footer per §2.7; version in the corner.
- Settings: sliders for render_distance 2–8, fov 60–100, volumes,
  sensitivity; fullscreen toggle; back.
- Pause (ESC): استئناف · حفظ العالم · الإعدادات · القائمة
  الرئيسية · خروج.
- Death: !لقد مت in red + cause string + إحياء · القائمة
  الرئيسية.
- Inventory / Crafting / Furnace / Chest / Species Log per Sections
  8–10.
- HUD: bars, hotbar, crosshair +, F3 debug, interaction hints
  bottom-right.
- Rights: centred gold; owner name at 36 pt; rights paragraph;
  version / year.
"""
from __future__ import annotations

import logging
import math
import time
from typing import Callable, Optional

import pygame

import game.i18n as i18n
from game.ui import (draw_panel, button, draw_bar, draw_hotbar,
                       draw_crosshair, draw_vignette,
                       GOLD, HP_RED, HUNGER_ORANGE)
from engine.arabic_text import render_text, shaped_width

log = logging.getLogger("egcraft.screens")

SPLASH_DURATION = 3.0


class Screens:
    """Screen-rendering manager. Stateless except for cached fonts."""

    def __init__(self, settings) -> None:
        self.settings = settings
        self.state = "splash"
        self.state_t = 0.0
        self.menu_index = 0
        self.species_log_page = 0
        # Fonts — resolve via settings.resource_path so the path works
        # both in dev (./assets/fonts/...) and in a PyInstaller frozen
        # exe (sys._MEIPASS/assets/fonts/...).
        try:
            from settings import resource_path
            font_path = str(resource_path("assets", "fonts",
                                          "Cairo-Regular.ttf"))
            font_path_bold = str(resource_path("assets", "fonts",
                                                "Cairo-Bold.ttf"))
            self.font_h1 = pygame.font.Font(font_path_bold, 48)
            self.font_h2 = pygame.font.Font(font_path_bold, 28)
            self.font_body = pygame.font.Font(font_path, 20)
            self.font_small = pygame.font.Font(font_path, 14)
        except Exception as exc:  # noqa: BLE001
            log.warning("Font load failed: %r — using default", exc)
            self.font_h1 = pygame.font.Font(None, 56)
            self.font_h2 = pygame.font.Font(None, 32)
            self.font_body = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 16)

    # ── Splash ─────────────────────────────────────────────
    def draw_splash(self, surface: pygame.Surface, dt: float) -> bool:
        """Draw splash screen. Returns True when finished (3 s)."""
        self.state_t += dt
        w, h = surface.get_size()
        surface.fill((10, 8, 14))
        # Title
        title = i18n.get("splash_line1")
        tw = shaped_width(self.font_h1, title)
        tx = (w - tw) // 2
        ty = h // 2 - 60
        render_text(surface, self.font_h1, title, GOLD, tx + tw, ty)
        # Subtitle
        sub = i18n.get("splash_line2")
        sw = shaped_width(self.font_h2, sub)
        sx = (w - sw) // 2
        sy = h // 2 + 20
        render_text(surface, self.font_h2, sub, (240, 220, 200),
                    sx + sw, sy)
        # ™ mark
        tm = i18n.get("splash_tm")
        render_text(surface, self.font_body, tm, (200, 180, 80),
                    w - 30, h - 40)
        return self.state_t >= SPLASH_DURATION

    # ── Main menu ──────────────────────────────────────────
    def draw_main_menu(self, surface: pygame.Surface,
                       mouse_pos: tuple[int, int]) -> list[tuple[str, pygame.Rect]]:
        """Draw main menu. Returns [(label, rect)] for hit-test."""
        w, h = surface.get_size()
        surface.fill((10, 8, 14))
        items = []
        # Title
        title = "EG Craft"
        tw = shaped_width(self.font_h1, title)
        tx = (w - tw) // 2
        ty = 60
        render_text(surface, self.font_h1, title, GOLD, tx + tw, ty)
        # Buttons
        labels = [
            i18n.get("play"),
            i18n.get("creative"),
            i18n.get("survival"),
            i18n.get("species_log"),
            i18n.get("settings"),
            i18n.get("rights"),
            i18n.get("quit"),
        ]
        bx = w // 2 - 150
        by = 160
        for i, label in enumerate(labels):
            hover = pygame.Rect(bx, by + i * 56, 300, 48).collidepoint(mouse_pos)
            rect = button(surface, self.font_h2, label,
                          bx, by + i * 56, 300, 48, hover=hover)
            items.append((label, rect))
        # Footer
        footer = i18n.get("footer_copyright")
        fw = shaped_width(self.font_small, footer)
        render_text(surface, self.font_small, footer, GOLD,
                    w - 12, h - 24)
        return items

    # ── Settings ───────────────────────────────────────────
    def draw_settings(self, surface: pygame.Surface,
                     settings) -> list[tuple[str, pygame.Rect]]:
        """Draw settings sliders."""
        w, h = surface.get_size()
        surface.fill((10, 8, 14))
        # Title
        title = i18n.get("settings")
        tw = shaped_width(self.font_h1, title)
        render_text(surface, self.font_h1, title, GOLD,
                    (w - tw) // 2 + tw, 40)
        items = []
        labels = [
            f"render_distance: {settings.render_distance}",
            f"fov: {settings.fov}",
            f"sfx: {settings.sfx:.2f}",
            f"music: {settings.music:.2f}",
            f"sensitivity: {settings.sensitivity}",
            f"fullscreen: {settings.fullscreen}",
            i18n.get("main_menu"),
        ]
        for i, label in enumerate(labels):
            rect = button(surface, self.font_body, label,
                          w // 2 - 200, 120 + i * 50, 400, 40,
                          hover=False)
            items.append((label, rect))
        return items

    # ── Pause ───────────────────────────────────────────────
    def draw_pause(self, surface: pygame.Surface,
                   mouse_pos: tuple[int, int]) -> list[tuple[str, pygame.Rect]]:
        w, h = surface.get_size()
        surface.fill((10, 8, 14, 200), special_flags=pygame.BLEND_RGBA_MULT)
        items = []
        labels = [
            i18n.get("resume"),
            i18n.get("save"),
            i18n.get("settings"),
            i18n.get("main_menu"),
            i18n.get("quit"),
        ]
        for i, label in enumerate(labels):
            rect = button(surface, self.font_h2, label,
                          w // 2 - 150, 150 + i * 56, 300, 48,
                          hover=pygame.Rect(w // 2 - 150, 150 + i * 56,
                                              300, 48).collidepoint(mouse_pos))
            items.append((label, rect))
        return items

    # ── Death ───────────────────────────────────────────────
    def draw_death(self, surface: pygame.Surface, cause: str,
                   mouse_pos: tuple[int, int]) -> list[tuple[str, pygame.Rect]]:
        w, h = surface.get_size()
        surface.fill((30, 0, 0))
        title = i18n.get("dead")
        tw = shaped_width(self.font_h1, title)
        render_text(surface, self.font_h1, title, (220, 40, 40),
                    (w - tw) // 2 + tw, h // 2 - 80)
        cause_str = i18n.get_death_cause(cause)
        cw = shaped_width(self.font_h2, cause_str)
        render_text(surface, self.font_h2, cause_str, (240, 200, 200),
                    (w - cw) // 2 + cw, h // 2 - 20)
        items = []
        labels = [i18n.get("respawn"), i18n.get("main_menu")]
        for i, label in enumerate(labels):
            rect = button(surface, self.font_h2, label,
                          w // 2 - 150, h // 2 + 60 + i * 56,
                          300, 48,
                          hover=pygame.Rect(w // 2 - 150,
                                              h // 2 + 60 + i * 56,
                                              300, 48).collidepoint(mouse_pos))
            items.append((label, rect))
        return items

    # ── Rights ──────────────────────────────────────────────
    def draw_rights(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()
        # Dark royal background
        surface.fill((10, 8, 30))
        # Gold ornamental border
        pygame.draw.rect(surface, GOLD, (16, 16, w - 32, h - 32), 2)
        # Owner name at 36 pt (using font_h1 since 48 is close)
        owner = i18n.get("rights_paragraph")
        # Simplified — just centre the paragraph
        # Title "حقوق الملكية"
        title = i18n.get("rights")
        tw = shaped_width(self.font_h1, title)
        render_text(surface, self.font_h1, title, GOLD,
                    (w - tw) // 2 + tw, 60)
        # Paragraph (multiline — wrap)
        para = i18n.get("rights_paragraph")
        # Just render as single line; UI is RTL.
        pw = shaped_width(self.font_body, para)
        render_text(surface, self.font_body, para, (240, 230, 200),
                    (w - pw) // 2 + pw if pw < w - 80 else w - 40,
                    h // 2)
        # Version / year
        version = "EG Craft v1.0 · © 2025"
        vw = shaped_width(self.font_small, version)
        render_text(surface, self.font_small, version, (180, 160, 100),
                    (w - vw) // 2 + vw, h - 60)

    # ── Species log (key B) ─────────────────────────────────
    def draw_species_log(self, surface: pygame.Surface,
                          registry, page: int = 0,
                          per_page: int = 50) -> None:
        w, h = surface.get_size()
        surface.fill((10, 8, 14))
        # Gold header
        header = i18n.get("species_log_header")
        hw = shaped_width(self.font_h2, header)
        render_text(surface, self.font_h2, header, GOLD,
                    w - 20, 20)
        # Rows
        all_ids = registry.all_ids()
        total_pages = max(1, (len(all_ids) + per_page - 1) // per_page)
        page = max(0, min(page, total_pages - 1))
        start = page * per_page
        for i, sid in enumerate(all_ids[start:start + per_page]):
            sp = registry.get(sid)
            if sp is None:
                continue
            y = 80 + i * 18
            # Index
            idx_str = f"{start + i + 1}."
            iw = shaped_width(self.font_small, idx_str)
            render_text(surface, self.font_small, idx_str,
                        (200, 200, 200), w - 20, y)
            # Name (hybrids highlighted in gold)
            color = GOLD if getattr(sp, "is_hybrid", False) else (240, 240, 240)
            name = getattr(sp, "name", sp.ar) if getattr(sp, "is_hybrid", False) else sp.ar
            render_text(surface, self.font_small, name, color,
                        w - 80, y)
            # Type
            type_str = (i18n.get("species_hostile") if getattr(sp, "hostile", False)
                         else i18n.get("species_passive"))
            render_text(surface, self.font_small, type_str,
                        (180, 180, 180), w - 300, y)
            # HP/SPD
            stats = f"{sp.hp}/{sp.speed}"
            render_text(surface, self.font_small, stats,
                        (200, 200, 200), w - 500, y)
        # Page indicator
        page_str = f"{i18n.get('page')} {page + 1}/{total_pages}"
        render_text(surface, self.font_small, page_str,
                    (200, 200, 200), w - 20, h - 30)

    # ── HUD ───────────────────────────────────────────────
    def draw_hud(self, surface: pygame.Surface, inv, survival,
                 fps: float, pos, daylight: float,
                 chunks: int, entities: int) -> None:
        w, h = surface.get_size()
        # HP / hunger bars (top-right)
        bar_w = 200
        bar_h = 18
        draw_bar(surface, w - bar_w - 12, 12,
                 survival.stats.hp, 20, HP_RED,
                 bar_w=bar_w, bar_h=bar_h)
        draw_bar(surface, w - bar_w - 12, 12 + bar_h + 4,
                 survival.stats.hunger, 20, HUNGER_ORANGE,
                 bar_w=bar_w, bar_h=bar_h)
        # Hotbar
        draw_hotbar(surface, self.font_small, inv, w)
        # Crosshair
        draw_crosshair(surface, w // 2, h // 2)
        # F3 debug
        debug = (f"FPS: {fps:.0f}  pos: {pos}  "
                  f"chunks: {chunks}  entities: {entities}  "
                  f"daylight: {daylight:.3f}")
        dw = shaped_width(self.font_small, debug)
        render_text(surface, self.font_small, debug,
                    (200, 200, 200), w - 12, h - 50)
        # Damage vignette
        draw_vignette(surface, survival.stats.damage_vignette)
