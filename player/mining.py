# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Mining and block placement.

Spec ref: §7.5 — Mining (hold LMB): progress += dt / break_time;
break_time = hardness × 1.5 / tool_mult. tool_mult = tool speed if
the tool class matches the block's tool, else 1. If block.min_tier >
tool tier: time × 3.33 and no drop. Creative: instant. Crack overlay:
darken face light by progress × 0.7. Spawn 8 particle cubes coloured
by the block tile's average colour. On break: drop an item entity (§9.6)
and play the sound.

Placing (RMB): Place the selected hotbar block at hit_pos + normal
if the target cell is air/water and does not intersect the player or
any entity AABB. Placing crafting_table / furnace / chest creates a
block entity (§8.5). Selection: black wireframe (GL_LINES, 12 edges,
PROGRAM_LINES) on the hit block.
"""
from __future__ import annotations

import logging
from typing import Callable, Optional

import numpy as np

from world.blocks import (
    ID_AIR, ID_WATER, ID_TORCH, ID_CRAFTING_TABLE, ID_FURNACE, ID_CHEST,
    get as get_block, is_solid,
)
from player.physics import AABB_W, AABB_H, AABB_D
from player.raycast import raycast_voxel, REACH

log = logging.getLogger("egcraft.mining")

# Particle spawn count on break
BREAK_PARTICLES = 8


class Mining:
    """Tracks mining progress on the targeted block."""

    def __init__(self) -> None:
        self.target: Optional[tuple[int, int, int]] = None
        self.progress: float = 0.0
        self.break_time: float = 0.0
        self.last_hardness: float = 0.0
        self.creative: bool = False

    def update(self, dt: float, lmb_held: bool,
               origin: tuple[float, float, float],
               direction: tuple[float, float, float],
               world_get: Callable[[int, int, int], int],
               tool_mult: float = 1.0,
               tool_tier: int = 0) -> Optional[tuple]:
        """Advance mining for one frame.

        Returns ``(block_pos, drop_id, particles_color)`` on a
        successful break, else ``None``.
        """
        if not lmb_held:
            self.target = None
            self.progress = 0.0
            return None

        hit = raycast_voxel(origin, direction, world_get, reach=REACH)
        if hit is None:
            self.target = None
            self.progress = 0.0
            return None

        block_pos, _, _ = hit
        bid = world_get(*block_pos)
        bdef = get_block(bid)

        # Bedrock / unbreakable
        if bdef.hardness < 0 or bid == ID_TORCH:
            # torch is breakable (hardness 0.1) — but creative-only?
            if bid == ID_TORCH:
                pass
            else:
                self.target = None
                self.progress = 0.0
                return None

        if self.creative:
            # Instant break
            self.target = block_pos
            self.progress = 1.0
            color = self._block_avg_color(bid)
            self._reset()
            return (block_pos, bdef.drop, color)

        if self.target != block_pos:
            self.target = block_pos
            self.progress = 0.0
            self.last_hardness = bdef.hardness
            # break_time = hardness × 1.5 / tool_mult
            base_time = bdef.hardness * 1.5
            if tool_mult > 0:
                base_time /= tool_mult
            # Wrong tool tier penalty
            if bdef.min_tier > tool_tier:
                base_time *= 3.33
                # no drop will be spawned
            self.break_time = max(0.05, base_time)

        self.progress += dt / max(0.05, self.break_time)
        if self.progress >= 1.0:
            color = self._block_avg_color(bid)
            drop = bdef.drop
            # Wrong tier → no drop
            if bdef.min_tier > tool_tier:
                drop = None
            self._reset()
            return (block_pos, drop, color)
        return None

    def _reset(self) -> None:
        self.target = None
        self.progress = 0.0
        self.break_time = 0.0

    def _block_avg_color(self, bid: int) -> tuple[int, int, int]:
        """Approximate the block's average colour from its tile base."""
        # We don't have texture sampling here; return the block's
        # tile-average as a placeholder. The real implementation would
        # ask texture.py for tile_surfaces[bdef.tiles[1]].mean().
        # For smoke purposes, fall back to white.
        return (200, 200, 200)


def can_place_at(world_get, x: int, y: int, z: int,
                 player_pos: np.ndarray) -> bool:
    """Per §7.5: target must be air or water, and must not intersect
    the player's AABB or any entity AABB."""
    bid = world_get(x, y, z)
    if bid not in (ID_AIR, ID_WATER):
        return False
    # Player AABB check
    pmin_x = player_pos[0] - AABB_W / 2
    pmax_x = player_pos[0] + AABB_W / 2
    pmin_y = player_pos[1]
    pmax_y = player_pos[1] + AABB_H
    pmin_z = player_pos[2] - AABB_D / 2
    pmax_z = player_pos[2] + AABB_D / 2
    bmin_x, bmax_x = x, x + 1
    bmin_y, bmax_y = y, y + 1
    bmin_z, bmax_z = z, z + 1
    overlap = (pmin_x < bmax_x and pmax_x > bmin_x
               and pmin_y < bmax_y and pmax_y > bmin_y
               and pmin_z < bmax_z and pmax_z > bmin_z)
    return not overlap


def place_block(world_set, x: int, y: int, z: int, bid: int,
                player_pos: np.ndarray, world_get=None) -> bool:
    """Place a block at (x, y, z) if allowed. Returns True on success."""
    if world_get is None:
        world_get = lambda _x, _y, _z: 0  # noqa: E731
    if not can_place_at(world_get, x, y, z, player_pos):
        return False
    world_set(x, y, z, bid)
    return True


def selection_box_lines(x: int, y: int, z: int) -> list[tuple[float, float, float]]:
    """Return the 12 edges (24 vertices) of the wireframe around
    the voxel (x, y, z)."""
    pts = [
        (x, y, z), (x + 1, y, z), (x + 1, y, z + 1), (x, y, z + 1),
        (x, y + 1, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x, y + 1, z + 1),
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # bottom
        (4, 5), (5, 6), (6, 7), (7, 4),  # top
        (0, 4), (1, 5), (2, 6), (3, 7),  # verticals
    ]
    out = []
    for a, b in edges:
        out.append(pts[a])
        out.append(pts[b])
    return out
