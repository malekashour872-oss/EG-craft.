# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Day/Night cycle + sky.

Spec ref: §12 — DAY_LENGTH = 600.0 s; t ∈ [0, 1).
raw = sin(2π · t); daylight = clamp((raw + 0.2) × 1.4, 0.08, 1.0).
Sky colours: sky_day = (0.47, 0.65, 1.0); sky_night = (0.02, 0.02, 0.08);
sky = lerp(night, day, daylight).
Sunset tint: when |raw| < 0.15: mix sky toward (1.0, 0.45, 0.2) by
(1 − |raw| / 0.15) × 0.6.
Start time: t = 0.25 (noon).
Sun/moon: quads on a circle of radius 90 around the player; angle
2πt (sun) and +π (moon). Textured with atlas tiles 25 (sun) and
26 (moon) (generated in T5).
Stars: 300 GL_POINTS on a sphere of radius 95, alpha = 1 − daylight,
drawn at night. Fog per §5.4.
"""
from __future__ import annotations

import math

import numpy as np

DAY_LENGTH = 600.0
SKY_DAY = np.array([0.47, 0.65, 1.0], dtype=np.float32)
SKY_NIGHT = np.array([0.02, 0.02, 0.08], dtype=np.float32)
SUNSET_TINT = np.array([1.0, 0.45, 0.2], dtype=np.float32)

SUN_RADIUS = 90.0
STAR_RADIUS = 95.0
STAR_COUNT = 300

DEFAULT_START_T = 0.25  # noon


class DayNight:
    """Day/Night cycle state."""

    def __init__(self, t: float = DEFAULT_START_T) -> None:
        self.t = float(t) % 1.0
        # Star field (pre-generated for determinism)
        rng = np.random.default_rng(0x5DA9)
        # Evenly distributed on a sphere via random unit vectors
        v = rng.normal(size=(STAR_COUNT, 3))
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        self.star_positions = (v * STAR_RADIUS).astype(np.float32)

    def tick(self, dt: float) -> None:
        self.t = (self.t + dt / DAY_LENGTH) % 1.0

    @property
    def raw(self) -> float:
        return math.sin(2 * math.pi * self.t)

    @property
    def daylight(self) -> float:
        r = self.raw
        d = (r + 0.2) * 1.4
        return max(0.08, min(1.0, d))

    @property
    def sky_color(self) -> np.ndarray:
        d = self.daylight
        sky = SKY_NIGHT + (SKY_DAY - SKY_NIGHT) * d
        # sunset tint
        r = self.raw
        if abs(r) < 0.15:
            factor = (1.0 - abs(r) / 0.15) * 0.6
            sky = sky + (SUNSET_TINT - sky) * factor
        return sky.astype(np.float32)

    @property
    def sun_dir(self) -> np.ndarray:
        """Sun direction from player position."""
        angle = 2 * math.pi * self.t
        # Sun rotates around the X axis (rises east, sets west)
        return np.array([0.0, math.sin(angle), math.cos(angle)],
                        dtype=np.float32)

    @property
    def moon_dir(self) -> np.ndarray:
        """Moon direction = sun + π."""
        angle = 2 * math.pi * self.t + math.pi
        return np.array([0.0, math.sin(angle), math.cos(angle)],
                        dtype=np.float32)

    @property
    def sun_pos(self, player_pos=(0, 0, 0)) -> np.ndarray:
        return np.array(player_pos, dtype=np.float32) + self.sun_dir * SUN_RADIUS

    @property
    def moon_pos(self, player_pos=(0, 0, 0)) -> np.ndarray:
        return np.array(player_pos, dtype=np.float32) + self.moon_dir * SUN_RADIUS

    @property
    def star_alpha(self) -> float:
        return 1.0 - self.daylight

    def is_day(self) -> bool:
        return self.daylight > 0.6

    def is_night(self) -> bool:
        return self.daylight < 0.3
