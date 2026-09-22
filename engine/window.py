# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Window + input + GL context bootstrap.

Spec ref: §5.1 — pygame.init(); pygame.display.gl_set_attribute for
CONTEXT_MAJOR_VERSION=3, CONTEXT_MINOR_VERSION=3, CONTEXT_PROFILE_CORE,
DOUBLEBUFFER=1, DEPTH_SIZE=24. set_mode((1280,720), OPENGL|DOUBLEBUF);
window caption per §2.3. Event loop handles QUIT, KEYDOWN/KEYUP,
MOUSEWHEEL. Relative mouse via event.set_grab(True) +
mouse.set_visible(False); toggled on ESC. VSync:
SDL_GL_SetSwapInterval(1).
"""
from __future__ import annotations

import logging
from typing import Callable

import pygame
from OpenGL import GL as gl
from pygame import DOUBLEBUF, OPENGL

# Window title per §2.3 (the literal Arabic string is reproduced here
# rather than imported from game.i18n to respect the import layering:
# engine ← world ← player / entities ← game ← main).


log = logging.getLogger("egcraft.window")

WINDOW_TITLE = "EG Craft — ملكية مالك حسن عاشور"


def _set_gl_attributes() -> None:
    """Request a 3.3 Core context."""
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK,
        pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
    try:
        # SDL2 vsync hint (best effort)
        pygame.display.gl_set_attribute(
            pygame.GL_ACCELERATED_VISUAL, 1)
    except Exception:
        pass


class Window:
    """Top-level window + event pump."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        pygame.init()
        pygame.display.init()
        _set_gl_attributes()
        flags = OPENGL | DOUBLEBUF
        if settings.fullscreen:
            flags |= pygame.FULLSCREEN
        self.screen = None
        self.gl_available = False
        try:
            self.screen = pygame.display.set_mode(
                (settings.width, settings.height), flags)
            self.gl_available = True
        except pygame.error as exc:
            log.warning("set_mode OPENGL failed: %r — "
                        "trying plain surface (no GL)", exc)
            try:
                self.screen = pygame.display.set_mode(
                    (settings.width, settings.height))
            except pygame.error as exc2:
                log.warning("plain set_mode failed: %r", exc2)
                # Last resort: 1×1 surface for event purposes
                try:
                    self.screen = pygame.display.set_mode((1, 1))
                except pygame.error:
                    self.screen = None
        pygame.display.set_caption(WINDOW_TITLE)

        # vsync (best-effort, requires SDL >= 2.0.18)
        if self.gl_available:
            try:
                import ctypes
                import os as _os
                import sys as _sys
                # In a PyInstaller frozen exe, the SDL2 DLL is bundled
                # inside sys._MEIPASS. ``ctypes.CDLL("SDL2")`` won't find
                # it via the default DLL search path on Windows; we need
                # to load it by its full path.
                _sdl_name = "SDL2"
                _sdl_candidates = []
                if getattr(_sys, "frozen", False):
                    _base = getattr(_sys, "_MEIPASS", None) or _os.path.dirname(_sys.executable)
                    if _os.name == "nt":
                        _sdl_candidates.append(_os.path.join(_base, "SDL2.dll"))
                        _sdl_candidates.append(_os.path.join(_base, "pygame", "SDL2.dll"))
                    else:
                        _sdl_candidates.append(_os.path.join(_base, "libSDL2-2.0.so.0"))
                        _sdl_candidates.append(_os.path.join(_base, "libSDL2.so"))
                sdl = None
                for _c in _sdl_candidates:
                    try:
                        sdl = ctypes.CDLL(_c)
                        break
                    except OSError:
                        continue
                if sdl is None:
                    sdl = ctypes.CDLL(_sdl_name)
                sdl.SDL_GL_SetSwapInterval.restype = ctypes.c_int
                sdl.SDL_GL_SetSwapInterval.argtypes = [ctypes.c_int]
                sdl.SDL_GL_SetSwapInterval(1)
                log.info("VSync requested via SDL_GL_SetSwapInterval(1)")
            except Exception as exc:  # noqa: BLE001
                log.warning("VSync set failed: %r", exc)

        # Input state
        self.keys: dict[int, bool] = {}
        self.mouse_buttons: dict[int, bool] = {}
        self.mouse_rel: tuple[int, int] = (0, 0)
        self.mouse_wheel: int = 0
        self.grabbed: bool = False
        self.running: bool = True
        self.paused: bool = False

        # GL state for the renderer to query
        if self.gl_available:
            try:
                gl.glEnable(gl.GL_DEPTH_TEST)
                gl.glDepthFunc(gl.GL_LEQUAL)
                gl.glEnable(gl.GL_CULL_FACE)
                gl.glCullFace(gl.GL_BACK)
                gl.glFrontFace(gl.GL_CCW)
                gl.glEnable(gl.GL_BLEND)
                gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            except Exception as exc:  # noqa: BLE001
                log.warning("Initial GL state failed: %r", exc)

        # Log the actual GL version string for the smoke test acceptance.
        if self.gl_available:
            try:
                self.gl_version = gl.glGetString(
                    gl.GL_VERSION).decode("utf-8", "replace")
            except Exception as exc:  # noqa: BLE001
                self.gl_version = "(unknown)"
                log.warning("glGetString(GL_VERSION) failed: %r", exc)
        else:
            self.gl_version = "(no GL — headless fallback)"
        log.info("GL_VERSION = %s", self.gl_version)

    # ── Input ──────────────────────────────────────────────
    def grab_mouse(self, grab: bool) -> None:
        self.grabbed = grab
        pygame.event.set_grab(grab)
        pygame.mouse.set_visible(not grab)
        if grab:
            pygame.mouse.set_pos(self.settings.width // 2,
                                 self.settings.height // 2)

    def toggle_pause(self) -> None:
        self.paused = not self.paused
        self.grab_mouse(not self.paused)

    # ── Event pump ─────────────────────────────────────────
    def pump(self) -> list[pygame.event.Event]:
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN:
                self.keys[ev.key] = True
                if ev.key == pygame.K_ESCAPE:
                    self.toggle_pause()
            elif ev.type == pygame.KEYUP:
                self.keys[ev.key] = False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons[ev.button] = True
            elif ev.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons[ev.button] = False
            elif ev.type == pygame.MOUSEWHEEL:
                self.mouse_wheel = ev.y
        # mouse motion: only meaningful if grabbed
        if self.grabbed:
            self.mouse_rel = pygame.mouse.get_rel()
        else:
            self.mouse_rel = (0, 0)
        return events

    def consume_wheel(self) -> int:
        w = self.mouse_wheel
        self.mouse_wheel = 0
        return w

    def is_key_down(self, key: int) -> bool:
        return self.keys.get(key, False)

    def is_mouse_down(self, btn: int) -> bool:
        return self.mouse_buttons.get(btn, False)

    # ── Lifecycle ─────────────────────────────────────────
    def swap(self) -> None:
        pygame.display.flip()

    def close(self) -> None:
        try:
            pygame.display.quit()
            pygame.quit()
        except Exception as exc:  # noqa: BLE001
            log.warning("Window.close: %r", exc)

    @property
    def aspect(self) -> float:
        return self.settings.width / max(1, self.settings.height)

    @property
    def size(self) -> tuple[int, int]:
        return (self.settings.width, self.settings.height)
