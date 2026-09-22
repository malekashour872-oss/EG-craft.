# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Touch input bridge for the pygbag web build.

Reads the JS-side ``window.EGC.input`` object (populated by
``web/mobile.js``) and exposes it as a Python-side input state.

Spec ref: extension to §5.1 — when running under pygbag/Emscripten,
the window event pump also consumes the touch-bridge state.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

log = logging.getLogger("egcraft.touch")


@dataclass
class TouchInputState:
    """Mirror of window.EGC.input on the JS side."""

    move_x: float = 0.0       # -1..1 strafe
    move_y: float = 0.0       # -1..1 forward
    look_dx: float = 0.0      # delta since last frame
    look_dy: float = 0.0
    jump: bool = False
    sneak: bool = False
    fly_toggle: bool = False
    break_held: bool = False
    place_held: bool = False
    inv_toggle: bool = False
    hotbar_index: int = 0

    def reset_deltas(self) -> None:
        """Call after each frame to clear per-frame deltas."""
        self.look_dx = 0.0
        self.look_dy = 0.0
        # Edge-triggered flags
        self.fly_toggle = False
        self.inv_toggle = False


class TouchBridge:
    """Bridges JS touch input → Python TouchInputState.

    On desktop (non-pygbag) the bridge is a no-op and reports
    ``is_mobile = False``.
    """

    def __init__(self) -> None:
        self.is_mobile = self._detect_pygbag()
        self.state = TouchInputState()
        self._js_obj = None

    def _detect_pygbag(self) -> bool:
        try:
            import sys
            return ("emscripten" in sys.platform.lower()
                    or "pygbag" in sys.modules)
        except Exception:  # noqa: BLE001
            return False

    def _get_js_input(self) -> TouchInputState:
        """Fetch the window.EGC.input object via JS interop."""
        if not self.is_mobile:
            return self.state
        try:
            # pygbag/pythonjs interop
            import js  # type: ignore
            egc = getattr(js.window, "EGC", None)
            if egc is None:
                return self.state
            inp = getattr(egc, "input", None)
            if inp is None:
                return self.state
            s = self.state
            s.move_x = float(getattr(inp, "moveX", 0.0) or 0.0)
            s.move_y = float(getattr(inp, "moveY", 0.0) or 0.0)
            s.look_dx = float(getattr(inp, "lookDX", 0.0) or 0.0)
            s.look_dy = float(getattr(inp, "lookDY", 0.0) or 0.0)
            s.jump = bool(getattr(inp, "jump", False))
            s.sneak = bool(getattr(inp, "sneak", False))
            s.fly_toggle = bool(getattr(inp, "flyToggle", False))
            s.break_held = bool(getattr(inp, "breakHeld", False))
            s.place_held = bool(getattr(inp, "placeHeld", False))
            s.inv_toggle = bool(getattr(inp, "invToggle", False))
            s.hotbar_index = int(getattr(inp, "hotbarIndex", 0) or 0)
        except Exception as exc:  # noqa: BLE001
            log.debug("TouchBridge poll failed: %r", exc)
        return self.state

    def poll(self) -> TouchInputState:
        """Return the current touch input state."""
        if not self.is_mobile:
            return self.state
        return self._get_js_input()

    def apply_to_window(self, window) -> None:
        """Mutate a Window's input state with touch input.

        Called every frame; the main loop converts this to the same
        keyboard/mouse events that pygame uses.
        """
        if not self.is_mobile:
            return
        s = self._get_js_input()
        # Inject synthetic key states (WASD-equivalent)
        if s.move_y > 0.3:
            window.keys[ord('w')] = True
        else:
            window.keys.pop(ord('w'), None)
        if s.move_y < -0.3:
            window.keys[ord('s')] = True
        else:
            window.keys.pop(ord('s'), None)
        if s.move_x > 0.3:
            window.keys[ord('d')] = True
        else:
            window.keys.pop(ord('d'), None)
        if s.move_x < -0.3:
            window.keys[ord('a')] = True
        else:
            window.keys.pop(ord('a'), None)
        # Jump / sneak
        window.keys[pygame_K_SPACE if False else 32] = s.jump  # K_SPACE = 32
        window.keys[pygame_K_LSHIFT if False else 1073742052] = s.sneak
        # Mouse buttons (1=left, 3=right)
        if s.break_held:
            window.mouse_buttons[1] = True
        else:
            window.mouse_buttons.pop(1, None)
        if s.place_held:
            window.mouse_buttons[3] = True
        else:
            window.mouse_buttons.pop(3, None)
        # Look deltas → window.mouse_rel equivalent
        if abs(s.look_dx) > 0.1 or abs(s.look_dy) > 0.1:
            window.mouse_rel = (int(s.look_dx), int(s.look_dy))
        # Hotbar index
        if 0 <= s.hotbar_index <= 8:
            # Window doesn't track hotbar directly; the game applies it.
            pass

    def reset(self) -> None:
        self.state.reset_deltas()
