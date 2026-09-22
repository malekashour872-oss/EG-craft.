# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""World manager — chunk dict + load/unload + edit overrides.

Spec ref: §6.5 — Chunk dict keyed (cx, cz). Load radius =
render_distance; unload beyond +2. get_block/set_block in world
space (floor division). Edits are recorded in overrides:
dict[(cx,cz)] → dict[(lx,y,lz)] = id (used by save). Per-chunk
heightmap (topmost solid) maintained for spawning and sky-light.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

from world.chunk import Chunk
from world.worldgen import (
    CHUNK_SIZE_X, CHUNK_SIZE_Y, CHUNK_SIZE_Z, WorldGen,
    heightmap_at,
)


class World:
    """A seeded voxel world."""

    def __init__(self, seed: int = 0, render_distance: int = 4) -> None:
        self.seed = int(seed)
        self.render_distance = max(1, int(render_distance))
        self.chunks: dict[tuple[int, int], Chunk] = {}
        self.overrides: dict[tuple[int, int], dict[tuple[int, int, int], int]] = {}
        self.heightmap_cache: dict[tuple[int, int], int] = {}
        self.worldgen = WorldGen(self.seed)

    # ── Chunk management ────────────────────────────────────
    def _key(self, x: int, z: int) -> tuple[int, int]:
        return (math.floor(x / CHUNK_SIZE_X),
                math.floor(z / CHUNK_SIZE_Z))

    def get_chunk(self, cx: int, cz: int) -> Optional[Chunk]:
        return self.chunks.get((cx, cz))

    def ensure_chunk(self, cx: int, cz: int) -> Chunk:
        key = (cx, cz)
        if key in self.chunks:
            return self.chunks[key]
        c = Chunk(cx, cz, seed=self.seed, worldgen=self.worldgen)
        c.generate(self.worldgen)
        # Apply any overrides for this chunk
        if key in self.overrides:
            for (lx, y, lz), bid in self.overrides[key].items():
                c.set(lx, y, lz, bid)
        # Link neighbours
        for (ox, oz), other in self.chunks.items():
            if abs(ox - cx) <= 1 and abs(oz - cz) <= 1:
                other.neighbours[(cx - ox, cz - oz)] = c
                c.neighbours[(ox - cx, oz - cz)] = other
        self.chunks[key] = c
        return c

    def unload_far(self, center_x: int, center_z: int) -> None:
        ccx, ccz = self._key(center_x, center_z)
        to_remove = []
        for (cx, cz) in self.chunks:
            if (abs(cx - ccx) > self.render_distance + 2
                    or abs(cz - ccz) > self.render_distance + 2):
                to_remove.append((cx, cz))
        for k in to_remove:
            self.chunks.pop(k, None)

    def update_around(self, x: float, z: float) -> None:
        """Load chunks around (x, z) within render_distance."""
        cx, cz = self._key(int(x), int(z))
        for dx in range(-self.render_distance, self.render_distance + 1):
            for dz in range(-self.render_distance, self.render_distance + 1):
                self.ensure_chunk(cx + dx, cz + dz)
        self.unload_far(int(x), int(z))

    # ── Block access (world space) ──────────────────────────
    def get_block(self, x: int, y: int, z: int) -> int:
        if y < 0 or y >= CHUNK_SIZE_Y:
            return 0
        cx, cz = self._key(x, z)
        chunk = self.chunks.get((cx, cz))
        if chunk is None:
            # Column not loaded — generate on demand
            return 0
        lx = x - cx * CHUNK_SIZE_X
        lz = z - cz * CHUNK_SIZE_Z
        return chunk.get(lx, y, lz)

    def set_block(self, x: int, y: int, z: int, bid: int) -> None:
        if y < 0 or y >= CHUNK_SIZE_Y:
            return
        cx, cz = self._key(x, z)
        chunk = self.ensure_chunk(cx, cz)
        lx = x - cx * CHUNK_SIZE_X
        lz = z - cz * CHUNK_SIZE_Z
        chunk.set(lx, y, lz, bid)
        # Record override for save (§15)
        self.overrides.setdefault((cx, cz), {})[(lx, y, lz)] = int(bid)
        # Mark neighbours dirty if on a border
        if lx == 0:
            other = self.chunks.get((cx - 1, cz))
            if other is not None:
                other.dirty = True
        elif lx == CHUNK_SIZE_X - 1:
            other = self.chunks.get((cx + 1, cz))
            if other is not None:
                other.dirty = True
        if lz == 0:
            other = self.chunks.get((cx, cz - 1))
            if other is not None:
                other.dirty = True
        elif lz == CHUNK_SIZE_Z - 1:
            other = self.chunks.get((cx, cz + 1))
            if other is not None:
                other.dirty = True

    # ── Heightmap ─────────────────────────────────────────
    def heightmap_at(self, x: int, z: int) -> int:
        """Topmost solid y in column (x, z)."""
        key = (x, z)
        if key in self.heightmap_cache:
            return self.heightmap_cache[key]
        h = heightmap_at(self.seed, x, z)
        self.heightmap_cache[key] = h
        return h

    # ── Iteration ─────────────────────────────────────────
    def iter_loaded_chunks(self) -> list[Chunk]:
        return list(self.chunks.values())

    def chunk_count(self) -> int:
        return len(self.chunks)

    # ── Debug helpers ──────────────────────────────────────
    def stats(self) -> dict[str, int]:
        return {
            "chunks": len(self.chunks),
            "overrides": sum(len(v) for v in self.overrides.values()),
        }
