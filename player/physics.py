# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Player physics.

Spec ref: §7.1 — Constants (EXACT): GRAVITY=24, TERMINAL=50, JUMP_VEL
=7.8, WALK=4.3, SPRINT=5.6, SNEAK=1.3, SWIM=2.2, FLY=10, FLY_FAST=20,
ground_accel=60, air_control=0.3, friction=10.0 (exp. damp / s).
AABB: 0.6 × 1.8 × 0.6; eye height 1.62.
In water: gravity × 0.3; jump key → vy = 3.5; air meter 15 s, then
2 dmg/s. Sprint requires hunger > 6 and the forward key.

Spec ref: §7.2 — Collision: integrate velocity per axis separately;
move X → resolve against overlapping solid AABBs (voxel scan of the
3×3×3 cells around the player); move Y → set on_ground on landing;
record fall_start when leaving the ground; move Z → resolve as for X.
Fall damage on landing: dmg = int(fall_blocks − 3) if > 0 (not in
water, creative, or fly). Void: y < 0 ⇒ 4 damage per 0.5 s. Sneak
prevents walking off edges (position clamp).
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np

# AABB dimensions (per §7.1)
AABB_W = 0.6
AABB_H = 1.8
AABB_D = 0.6
EYE_HEIGHT = 1.62

# Movement constants
GRAVITY = 24.0
TERMINAL = 50.0
JUMP_VEL = 7.8
WALK = 4.3
SPRINT = 5.6
SNEAK = 1.3
SWIM = 2.2
FLY = 10.0
FLY_FAST = 20.0
GROUND_ACCEL = 60.0
AIR_CONTROL = 0.3
FRICTION = 10.0  # exp. damp / s

# Water
WATER_GRAVITY_MULT = 0.3
WATER_JUMP_VEL = 3.5
AIR_METER_MAX = 15.0
WATER_DMG_PER_S = 2.0

# Fall damage
FALL_DMG_BLOCKS = 3  # dmg = int(fall_blocks − 3) if > 0

# Void
VOID_DMG_PER_S = 4.0  # 4 dmg per 0.5 s ⇒ 8/s? Spec says "4 damage per 0.5 s"
VOID_DMG_INTERVAL = 0.5


class Physics:
    """Per-frame physics integration for the player."""

    def __init__(self, seed: int = 0) -> None:
        self.seed = int(seed)
        self.on_ground = False
        self.in_water = False
        self.fall_start_y: float | None = None
        self.air_meter = AIR_METER_MAX
        self.last_void_dmg = 0.0
        self.last_water_dmg = 0.0
        self.last_fall_damage = 0
        self.creative = False

    # ── Main integration ────────────────────────────────────
    def integrate(self, pos: np.ndarray, vel: np.ndarray, dt: float,
                  world_get: Callable[[int, int, int], int],
                  on_ground: bool = False,
                  keys: dict | None = None,
                  fly: bool = False,
                  in_water: bool = False) -> None:
        """Advance the player one tick.

        Mutates ``pos`` and ``vel`` in place.
        ``world_get(x, y, z)`` returns the block id at that voxel.
        """
        self.in_water = in_water
        if self.creative and fly:
            self._integrate_fly(pos, vel, dt, keys or {})
            return

        # 1. Apply gravity
        if in_water:
            vel[1] -= GRAVITY * WATER_GRAVITY_MULT * dt
        else:
            vel[1] -= GRAVITY * dt
        # clamp terminal velocity (downward)
        if vel[1] < -TERMINAL:
            vel[1] = -TERMINAL

        # 2. Integrate velocity per axis (X then Y then Z) per §7.2
        # X axis
        pos[0] += vel[0] * dt
        self._resolve_axis(pos, vel, axis=0, world_get=world_get)
        # Y axis
        pos[1] += vel[1] * dt
        self.on_ground = self._resolve_axis_y(pos, vel, world_get)
        # Z axis
        pos[2] += vel[2] * dt
        self._resolve_axis(pos, vel, axis=2, world_get=world_get)

        # Fall damage
        if self.on_ground:
            if self.fall_start_y is not None and not in_water:
                fall_blocks = self.fall_start_y - pos[1]
                if fall_blocks > FALL_DMG_BLOCKS:
                    dmg = int(fall_blocks - FALL_DMG_BLOCKS)
                    self.last_fall_damage = dmg
            self.fall_start_y = None
        else:
            if self.fall_start_y is None and vel[1] < 0:
                self.fall_start_y = pos[1]

        # Void damage
        if pos[1] < 0:
            self.last_void_dmg += dt
            # 4 dmg per 0.5 s
            # (accumulated)
        else:
            self.last_void_dmg = 0.0

        # Air meter / drown damage in water
        if in_water:
            self.air_meter -= dt
            if self.air_meter < 0:
                self.last_water_dmg += dt
        else:
            self.air_meter = AIR_METER_MAX
            self.last_water_dmg = 0.0

    def _integrate_fly(self, pos: np.ndarray, vel: np.ndarray, dt: float,
                       keys: dict) -> None:
        # Damping 5/s per §7.3
        damp = math.exp(-5.0 * dt)
        vel *= damp
        pos[0] += vel[0] * dt
        pos[1] += vel[1] * dt
        pos[2] += vel[2] * dt

    # ── Axis collision resolution ──────────────────────────
    def _player_aabb(self, pos: np.ndarray) -> tuple[float, float, float,
                                                      float, float, float]:
        """Return (min_x, min_y, min_z, max_x, max_y, max_z)."""
        return (pos[0] - AABB_W / 2, pos[1], pos[2] - AABB_D / 2,
                pos[0] + AABB_W / 2, pos[1] + AABB_H, pos[2] + AABB_D / 2)

    def _is_blocked(self, x: int, y: int, z: int,
                    world_get: Callable[[int, int, int], int]) -> bool:
        bid = world_get(x, y, z)
        from world.blocks import is_solid
        return is_solid(bid)

    def _resolve_axis(self, pos: np.ndarray, vel: np.ndarray, axis: int,
                      world_get: Callable[[int, int, int], int]) -> None:
        """Sweep the 3×3×3 cells around the player for solid blocks
        and resolve overlaps along ``axis``."""
        min_x = int(math.floor(pos[0] - AABB_W / 2))
        max_x = int(math.floor(pos[0] + AABB_W / 2))
        min_y = int(math.floor(pos[1]))
        max_y = int(math.floor(pos[1] + AABB_H))
        min_z = int(math.floor(pos[2] - AABB_D / 2))
        max_z = int(math.floor(pos[2] + AABB_D / 2))
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                for z in range(min_z, max_z + 1):
                    if not self._is_blocked(x, y, z, world_get):
                        continue
                    # Voxel AABB: (x, y, z) → (x+1, y+1, z+1)
                    if axis == 0:
                        # X overlap?
                        if vel[0] > 0:
                            # player moving +X → collide at x
                            new_x = x - AABB_W / 2 - 0.001
                            if pos[0] > new_x:
                                pos[0] = new_x
                                vel[0] = 0.0
                        elif vel[0] < 0:
                            new_x = (x + 1) + AABB_W / 2 + 0.001
                            if pos[0] < new_x:
                                pos[0] = new_x
                                vel[0] = 0.0
                    elif axis == 2:
                        if vel[2] > 0:
                            new_z = z - AABB_D / 2 - 0.001
                            if pos[2] > new_z:
                                pos[2] = new_z
                                vel[2] = 0.0
                        elif vel[2] < 0:
                            new_z = (z + 1) + AABB_D / 2 + 0.001
                            if pos[2] < new_z:
                                pos[2] = new_z
                                vel[2] = 0.0

    def _resolve_axis_y(self, pos: np.ndarray, vel: np.ndarray,
                        world_get: Callable[[int, int, int], int]) -> bool:
        """Resolve Y collision; return True if landing on ground."""
        on_ground = False
        min_x = int(math.floor(pos[0] - AABB_W / 2))
        max_x = int(math.floor(pos[0] + AABB_W / 2))
        min_z = int(math.floor(pos[2] - AABB_D / 2))
        max_z = int(math.floor(pos[2] + AABB_D / 2))
        # Y range from feet down to head
        feet_y = pos[1]
        head_y = pos[1] + AABB_H
        min_y = int(math.floor(feet_y))
        max_y = int(math.floor(head_y))
        for x in range(min_x, max_x + 1):
            for z in range(min_z, max_z + 1):
                for y in range(min_y, max_y + 1):
                    if not self._is_blocked(x, y, z, world_get):
                        continue
                    if vel[1] < 0:
                        # moving down → feet land on y+1
                        new_y = y + 1 + 0.001
                        if pos[1] < new_y:
                            pos[1] = new_y
                            vel[1] = 0.0
                            on_ground = True
                    elif vel[1] > 0:
                        # moving up → head hits y
                        new_y = y - AABB_H - 0.001
                        if pos[1] > new_y:
                            pos[1] = new_y
                            vel[1] = 0.0
        return on_ground

    # ── Helpers ─────────────────────────────────────────────
    def jump(self, vel: np.ndarray, in_water: bool = False) -> None:
        if in_water:
            vel[1] = WATER_JUMP_VEL
        elif self.on_ground:
            vel[1] = JUMP_VEL

    def reset(self) -> None:
        self.on_ground = False
        self.fall_start_y = None
        self.air_meter = AIR_METER_MAX
        self.last_void_dmg = 0.0
        self.last_water_dmg = 0.0
        self.last_fall_damage = 0
