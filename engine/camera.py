# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""First-person camera (yaw/pitch + sprint FOV bump).

Spec ref: §5.3 — Yaw/pitch; pitch clamped ±89°. FOV interpolated +10
while sprinting. Forward/right vectors recomputed every frame.
eye = pos + (0, 1.62, 0).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from engine.math3d import Vec3, clamp, lerp, vec3


@dataclass
class Camera:
    pos: np.ndarray  # (3,) float32 — feet position
    yaw: float = 0.0   # around +Y, radians
    pitch: float = 0.0  # around local X, radians
    base_fov: float = 70.0
    fov: float = 70.0
    target_fov: float = 70.0
    eye_height: float = 1.62

    @property
    def eye(self) -> np.ndarray:
        return self.pos + vec3(0.0, self.eye_height, 0.0)

    def forward(self) -> np.ndarray:
        cp = math.cos(self.pitch)
        sy = math.sin(self.yaw)
        cy = math.cos(self.yaw)
        sp = math.sin(self.pitch)
        # -Z forward in right-handed (yaw=0 → -Z)
        return vec3(-sy * cp, sp, -cy * cp)

    def right(self) -> np.ndarray:
        sy = math.sin(self.yaw)
        cy = math.cos(self.yaw)
        return vec3(cy, 0.0, -sy)

    def up(self) -> np.ndarray:
        return vec3(0.0, 1.0, 0.0)

    def look_offset(self, dx: float, dy: float,
                    sensitivity: float = 0.0022) -> None:
        """Apply mouse look deltas."""
        self.yaw += dx * sensitivity
        self.pitch = clamp(self.pitch - dy * sensitivity,
                           math.radians(-89.0), math.radians(89.0))

    def set_sprint(self, sprinting: bool, dt: float) -> None:
        self.target_fov = self.base_fov + (10.0 if sprinting else 0.0)
        # interpolate at 8 per second so the bump feels natural
        rate = 1.0 - math.exp(-dt * 8.0)
        self.fov = lerp(self.fov, self.target_fov, rate)

    def reset(self, pos: np.ndarray, yaw: float = 0.0,
              pitch: float = 0.0) -> None:
        self.pos = pos.astype(np.float32).copy()
        self.yaw = yaw
        self.pitch = pitch
        self.fov = self.base_fov
        self.target_fov = self.base_fov

    def get_view_matrix(self) -> np.ndarray:
        from engine.math3d import look_at
        return look_at(self.eye, self.eye + self.forward(), self.up())
