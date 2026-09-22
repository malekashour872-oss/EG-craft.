# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""DDA raycast (Amanatides–Woo) for block selection.

Spec ref: §7.4 — reach = 5.0, max 128 steps. Step directions = sign
(dir). tMax_k = ((int bound) − pos_k) / dir_k with correct ±
handling; tDelta_k = |1 / dir_k|. Loop: advance the axis with the
smallest tMax, tracking the entered-face normal; stop at a solid
block or at reach. Water and air are skipped.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

REACH = 5.0
MAX_STEPS = 128


def raycast_voxel(origin: tuple[float, float, float] | np.ndarray,
                  direction: tuple[float, float, float] | np.ndarray,
                  world_get=None,
                  reach: float = REACH,
                  max_steps: int = MAX_STEPS
                  ) -> Optional[tuple[tuple[int, int, int],
                                       tuple[int, int, int], float]]:
    """Amanatides–Woo voxel traversal.

    Returns ``(block_pos, face_normal, hit_dist)`` or ``None`` if
    no solid block is hit within reach.
    """
    # Normalise direction
    dx, dy, dz = float(direction[0]), float(direction[1]), float(direction[2])
    norm = math.sqrt(dx * dx + dy * dy + dz * dz)
    if norm < 1e-9:
        return None
    dx /= norm
    dy /= norm
    dz /= norm

    px, py, pz = float(origin[0]), float(origin[1]), float(origin[2])
    x = int(math.floor(px))
    y = int(math.floor(py))
    z = int(math.floor(pz))

    step_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
    step_y = 1 if dy > 0 else (-1 if dy < 0 else 0)
    step_z = 1 if dz > 0 else (-1 if dz < 0 else 0)

    def _t_max(p: float, step: int, d: float) -> float:
        if step > 0:
            boundary = math.floor(p) + 1
        elif step < 0:
            boundary = math.floor(p)
        else:
            return float("inf")
        if abs(d) < 1e-9:
            return float("inf")
        return (boundary - p) / d

    tMaxX = _t_max(px, step_x, dx)
    tMaxY = _t_max(py, step_y, dy)
    tMaxZ = _t_max(pz, step_z, dz)

    tDeltaX = abs(1.0 / dx) if abs(dx) > 1e-9 else float("inf")
    tDeltaY = abs(1.0 / dy) if abs(dy) > 1e-9 else float("inf")
    tDeltaZ = abs(1.0 / dz) if abs(dz) > 1e-9 else float("inf")

    normal = (0, 0, 0)
    t = 0.0

    for _ in range(max_steps):
        if t > reach:
            break
        # Check current cell
        if world_get is None:
            # Smoke test: hit at first cell with y ≤ heightmap
            return ((x, y, z), normal, t)
        bid = world_get(x, y, z)
        from world.blocks import is_solid
        if is_solid(bid):
            return ((x, y, z), normal, t)

        # Advance
        if tMaxX < tMaxY and tMaxX < tMaxZ:
            x += step_x
            t = tMaxX
            tMaxX += tDeltaX
            normal = (-step_x, 0, 0)
        elif tMaxY < tMaxZ:
            y += step_y
            t = tMaxY
            tMaxY += tDeltaY
            normal = (0, -step_y, 0)
        else:
            z += step_z
            t = tMaxZ
            tMaxZ += tDeltaZ
            normal = (0, 0, -step_z)

    return None


def pick_block(origin, direction, world_get, reach: float = REACH
               ) -> Optional[tuple[int, int, int]]:
    """Convenience: return the (x, y, z) of the hit block or None."""
    hit = raycast_voxel(origin, direction, world_get, reach=reach)
    if hit is None:
        return None
    return hit[0]
