# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Entity nametags (Arabic, camera-facing quads).

Spec ref: §5.6 — Render the Arabic name via arabic_text + a pygame
font to a Surface; upload as a GL texture (cache: name → (tex_id, w,
h)); draw as a camera-facing quad above the entity head. White text
with black outline.
"""
from __future__ import annotations

from typing import Optional


class NametagCache:
    """Cache of (tex_id, w, h) per Arabic name."""

    def __init__(self, font: object | None = None) -> None:
        self.font = font
        self.cache: dict[str, tuple[int, int, int]] = {}

    def get(self, name: str) -> Optional[tuple[int, int, int]]:
        return self.cache.get(name)

    def put(self, name: str, tex_id: int, w: int, h: int) -> None:
        self.cache[name] = (tex_id, w, h)

    def clear(self) -> None:
        # Optional GL cleanup
        self.cache.clear()


def render_nametag_surface(name: str, font) -> object:
    """Render the Arabic name as a pygame Surface (white text + black
    outline)."""
    import pygame
    from engine.arabic_text import render_text
    # Estimate size
    w, h = font.size(name)
    surf = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
    # outline (offsets)
    for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                    (-1, -1), (1, 1), (-1, 1), (1, -1)]:
        render_text(surf, font, name, (0, 0, 0), w + 4, 2 + oy)
    # main text
    render_text(surf, font, name, (255, 255, 255), w + 4, 2)
    return surf


def upload_surface_to_gl(surf) -> tuple[int, int, int]:
    """Upload a pygame Surface to GL as a texture; return (tex_id, w, h)."""
    import pygame
    from OpenGL import GL as gl
    import ctypes
    w = surf.get_width()
    h = surf.get_height()
    data = pygame.image.tostring(surf, "RGBA", True)
    tex = gl.glGenTextures(1)
    tex_id = int(tex) if isinstance(tex, ctypes.c_uint) else tex
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
                        gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                        gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S,
                        gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T,
                        gl.GL_CLAMP_TO_EDGE)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0,
                    gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data)
    return (tex_id, w, h)
