# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Perlin noise from scratch (numpy-backed).

Spec ref: §6.1 — `__init__(seed)`: perm = default_rng(seed)
.permutation(256) stacked twice → 512 entries. Gradients2D = 8 unit
vectors at 45° steps. `fade(t) = t³ (t (t·6 − 15) + 10)`.
`grad(hash, x, y, z)` via the standard 12-gradient Perlin bit
scheme. `perlin2(x, y)` and `perlin3(x, y, z)` → range [-1, 1].
`fbm2(x, y, octaves=4, lacunarity=2.0, gain=0.5) = Σ gainⁱ ·
perlin2(x·lacⁱ, y·lacⁱ)`.
"""
from __future__ import annotations

import math

import numpy as np


def _stable_hash_int(value: int) -> int:
    """A-11: stable integer hash, not Python's randomized hash()."""
    import zlib
    if isinstance(value, int):
        b = int(value).to_bytes(8, "big", signed=True)
    else:
        b = str(value).encode("utf-8")
    return zlib.crc32(b)


class Perlin:
    """2D + 3D Perlin noise with a fixed seed."""

    GRAD3 = (
        (1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),
        (1, 0, 1), (-1, 0, 1), (1, 0, -1), (-1, 0, -1),
        (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1),
    )

    def __init__(self, seed: int = 0) -> None:
        self.seed = int(seed)
        rng = np.random.default_rng(self.seed)
        perm = rng.permutation(256)
        # Stack twice → 512 entries
        self.perm = np.concatenate([perm, perm]).astype(np.int32)

    @staticmethod
    def fade(t: float) -> float:
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def grad(self, hash_val: int, x: float, y: float, z: float) -> float:
        """Ken Perlin's reference grad: works with h∈[0,15] and the
        12-gradient scheme — uses bit tests, not a lookup table.
        """
        h = int(hash_val) & 15
        u = x if h < 8 else y
        if h < 4:
            v = y
        elif h == 12 or h == 14:
            v = x
        else:
            v = z
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def perlin2(self, x: float, y: float) -> float:
        # 2D via the 12-gradient scheme on z=0
        return self.perlin3(x, y, 0.0)

    def perlin3(self, x: float, y: float, z: float) -> float:
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        Z = int(math.floor(z)) & 255
        x -= math.floor(x)
        y -= math.floor(y)
        z -= math.floor(z)
        u = self.fade(x)
        v = self.fade(y)
        w = self.fade(z)

        p = self.perm
        A = p[X] + Y
        AA = p[A] + Z
        AB = p[A + 1] + Z
        B = p[X + 1] + Y
        BA = p[B] + Z
        BB = p[B + 1] + Z

        def g(h, x_, y_, z_):
            return self.grad(p[h], x_, y_, z_)

        x1 = self.lerp(g(AA, x, y, z), g(BA, x - 1, y, z), u)
        x2 = self.lerp(g(AB, x, y - 1, z), g(BB, x - 1, y - 1, z), u)
        y1 = self.lerp(x1, x2, v)
        x1b = self.lerp(g(AA + 1, x, y, z - 1),
                        g(BA + 1, x - 1, y, z - 1), u)
        x2b = self.lerp(g(AB + 1, x, y - 1, z - 1),
                        g(BB + 1, x - 1, y - 1, z - 1), u)
        y2 = self.lerp(x1b, x2b, v)
        return self.lerp(y1, y2, w)  # roughly in [-1, 1]

    def fbm2(self, x: float, y: float,
             octaves: int = 4, lacunarity: float = 2.0,
             gain: float = 0.5) -> float:
        amp = 1.0
        freq = 1.0
        total = 0.0
        norm = 0.0
        for _ in range(octaves):
            total += amp * self.perlin2(x * freq, y * freq)
            norm += amp
            amp *= gain
            freq *= lacunarity
        if norm <= 0:
            return 0.0
        return total / norm
