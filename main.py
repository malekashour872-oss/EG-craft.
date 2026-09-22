# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""EG Craft — async entry point.

Spec ref: §16.4 — pygbag-safe async loop pattern:
``asyncio … while running: tick(); await asyncio.sleep(0)``.
No blocking sleeps or loops.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from typing import Optional

from settings import Settings

log = logging.getLogger("egcraft.main")


class Game:
    """Game orchestrator. Holds subsystem references."""

    def __init__(self, settings: Settings, headless: bool = False) -> None:
        self.settings = settings
        self.headless = headless
        self.window = None  # type: Optional[object]
        # Each subsystem gets attached in its corresponding task.
        self.world = None
        self.player = None
        self.entities_manager = None
        self.ui = None
        self.screens = None
        self.sounds = None
        self.music = None
        self.daynight = None
        self.survival = None
        self.mode = "survival"  # survival | creative
        self.state = "splash"   # splash | menu | playing | paused | dead | rights
        self.frame_count = 0
        self.max_frames: Optional[int] = None  # if set, loop exits
        # Commercial extension
        self.touch = None  # TouchBridge (engine/touch.py)
        self.save_slots: list[str] = []
        self.stats = {"play_time": 0.0, "blocks_broken": 0,
                      "blocks_placed": 0, "mobs_killed": 0,
                      "deaths": 0, "distance_walked": 0.0}
        self.version = "2.0.0-commercial"

    def init_window(self) -> None:
        """Create the window + GL context. Called by run()."""
        if self.window is not None:
            return
        if self.headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        from engine.window import Window
        self.window = Window(self.settings)
        # Commercial: also init the touch bridge (no-op on desktop)
        try:
            from engine.touch import TouchBridge
            self.touch = TouchBridge()
            if self.touch.is_mobile:
                log.info("Running under pygbag/mobile — "
                          "touch controls will be applied per-frame.")
        except Exception as exc:  # noqa: BLE001
            log.warning("TouchBridge init failed: %r", exc)
            self.touch = None

    async def run(self) -> None:
        self.init_window()
        # Try to clear the GL back buffer once with a non-black colour
        # so the window isn't pitch black on startup. The real render
        # path (world/camera/UI) is wired in by separate subsystems.
        self._initial_clear()
        # ~60 FPS cap. ``asyncio.sleep(0)`` would spin the CPU at 100%
        # and make the window feel unresponsive on Windows desktop.
        import time
        while True:
            t0 = time.perf_counter()
            self._tick_one()
            if self.window is not None and not self.window.running:
                break
            if self.max_frames is not None and self.frame_count >= self.max_frames:
                break
            # Yield to the asyncio loop + cap the frame rate.
            dt = time.perf_counter() - t0
            sleep_for = max(0.0, 1.0 / 60.0 - dt)
            await asyncio.sleep(sleep_for)

    def _initial_clear(self) -> None:
        """Clear the GL back buffer to a sky-ish colour so the window
        isn't pitch black while the real renderer subsystems boot."""
        if self.window is None or not getattr(self.window, "gl_available", False):
            return
        try:
            from OpenGL import GL as gl
            gl.glClearColor(0.05, 0.08, 0.14, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        except Exception as exc:  # noqa: BLE001
            log.debug("initial GL clear failed: %r", exc)

    def _tick_one(self) -> None:
        self.frame_count += 1
        # Subsystem tick stubs — wired in their respective tasks.
        if self.window is not None:
            self.window.pump()
            # Commercial: apply touch input every frame (pygbag builds)
            if self.touch is not None and self.touch.is_mobile:
                try:
                    self.touch.apply_to_window(self.window)
                    self.touch.reset()
                except Exception as exc:  # noqa: BLE001
                    log.debug("Touch apply failed: %r", exc)
            self.window.swap()


def make_settings() -> Settings:
    return Settings.load()


def setup_environment(headless: bool) -> None:
    if headless:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        os.environ.setdefault("SDL_OPENGL_FORWARD_COMPAT", "1")


async def _async_main() -> int:
    settings = make_settings()
    headless = os.environ.get("EGCRAFT_HEADLESS") == "1"
    setup_environment(headless)
    game = Game(settings, headless=headless)
    await game.run()
    return 0


def main() -> int:
    """Synchronous wrapper that drives the async loop."""
    from game.logging_setup import get_logger
    get_logger()
    try:
        return asyncio.run(_async_main())
    except KeyboardInterrupt:
        log.info("Interrupted by user")
        return 0


# pygbag entry point: aioapp requires an `async def main()` at module
# scope (pygbag picks it up automatically when run with `pygbag`).
async def aio_main() -> int:  # pragma: no cover
    return await _async_main()


# ─────────────────────────────────────────────────────────────────────────────
# Vercel compatibility stub
# ─────────────────────────────────────────────────────────────────────────────
# EG Craft is deployed as a STATIC pygbag bundle (Python → WebAssembly),
# NOT as a Python serverless function. However, when Vercel detects
# `main.py` + `requirements.txt` at the project root, its Python runtime
# auto-imports `main` and looks for a top-level ASGI/WSGI `app` object.
# If that object is missing, the build fails with:
#     "Error: Found main.py but it does not export a top-level [app]"
#
# To satisfy Vercel's build-time check we expose a minimal ASGI v3.0
# callable named `app`. It is NEVER invoked at runtime — the actual
# deployment is the static `build/web/` directory produced by pygbag.
# If a request ever reaches it (e.g. misconfigured routing), it returns
# a 200 OK pointing the user at the game.
# ─────────────────────────────────────────────────────────────────────────────
async def _vercel_asgi_app(scope, receive, send):  # type: ignore[no-untyped-def]
    """Minimal ASGI v3.0 stub for Vercel build-time auto-detection.

    EG Craft runs as a pygbag WebAssembly bundle, not as a serverless
    function. This callable exists only so Vercel's Python runtime
    finds a valid top-level `app` object during the build. It is never
    reached at runtime.
    """
    if scope["type"] != "http":
        return
    await receive()  # consume the request
    body = (
        b"<!doctype html><html lang='ar' dir='rtl'><head>"
        b"<meta charset='utf-8'><title>EG Craft</title></head>"
        b"<body style='font-family:sans-serif;text-align:center;padding:2rem'>"
        b"<h1>EG Craft</h1>"
        b"<p>EG Craft \xd9\x8a\xd8\xb9\xd9\x85\xd9\x84 \xd9\x83\xd8\xaa\xd8\xb7"
        b"\xd8\xa8\xd9\x8a\xd9\x82 WebAssembly \xd8\xb9\xd8\xa8\xd8\xb1 pygbag"
        b"\xd8\x8c \xd9\x88\xd9\x84\xd9\x8a\xd8\xb3 \xd9\x83\xd8\xaf\xd8\xa7"
        b"\xd8\xa9 Python serverless.</p>"
        b"<p><a href='/'>\xd8\xa7\xd9\x84\xd8\xb9\xd9\x88\xd8\xaf\xd8\xa9 "
        b"\xd9\x84\xd9\x84\xd8\xb9\xd8\xa8\xd8\xa9</a></p>"
        b"</body></html>"
    )
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [
            [b"content-type", b"text/html; charset=utf-8"],
            [b"content-length", str(len(body)).encode("ascii")],
        ],
    })
    await send({"type": "http.response.body", "body": body})


# Top-level `app` object — satisfies Vercel's auto-detection check.
app = _vercel_asgi_app


if __name__ == "__main__":
    sys.exit(main())
