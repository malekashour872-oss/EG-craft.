# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Deterministic world generation per column.

Spec ref: §6.3 — Biome noise, height, biome classification, column
layers, water, caves, trees, desert, ore distribution, tree density.
All randomness seeded per §1.7 with a stable hash (A-11).
"""
from __future__ import annotations

import math
import zlib

import numpy as np

from world.blocks import (
    ID_AIR, ID_BEDROCK, ID_DIRT, ID_GRASS, ID_LEAVES, ID_LOG,
    ID_SAND, ID_STONE, ID_WATER, ID_COAL_ORE, ID_IRON_ORE,
    ID_GOLD_ORE, ID_DIAMOND_ORE, ID_SNOW, ID_DEEPSLATE,
)
from world.noise import Perlin

WATER_LEVEL = 18
CHUNK_SIZE_X = 16
CHUNK_SIZE_Y = 64
CHUNK_SIZE_Z = 16


def _stable_hash(*args) -> int:
    """Stable hash per A-11 — zlib.crc32 of UTF-8 bytes."""
    s = "|".join(str(a) for a in args).encode("utf-8")
    return zlib.crc32(s)


class WorldGen:
    """Per-column world generator. Stateless except for the noise
    object (which is seed-bound)."""

    def __init__(self, seed: int = 0) -> None:
        self.seed = int(seed)
        self.biome_noise = Perlin(seed)
        self.height_noise = Perlin(seed + 1)
        self.detail_noise = Perlin(seed + 2)
        self.cave_noise = Perlin(seed + 3)

    def biome_n(self, x: int, z: int) -> float:
        return self.biome_noise.fbm2(x * 0.004, z * 0.004, 3)

    def height_at(self, x: int, z: int) -> int:
        h = int(20 + self.height_noise.fbm2(x * 0.012, z * 0.012, 4) * 10
                + self.detail_noise.perlin2(x * 0.06, z * 0.06) * 2)
        return max(1, min(40, h))

    def biome_at(self, biome_n: float) -> str:
        """Return biome name for a noise value.

        Commercial expansion: extends the §6.3 spec (desert/forest/
        plains) with jungle, savanna, taiga, swamp, mountains,
        mushroom, ocean variants. Documented in DECISIONS.md → L-2.
        """
        if biome_n < -0.85:
            return "deep_ocean"
        if biome_n < -0.55:
            return "ocean"
        if biome_n < -0.35:
            return "desert"
        if biome_n < -0.15:
            return "savanna"
        if biome_n < 0.05:
            return "plains"
        if biome_n < 0.20:
            return "swamp"
        if biome_n > 0.85:
            return "mountains"
        if biome_n > 0.55:
            return "taiga"
        if biome_n > 0.35:
            return "jungle"
        return "forest"

    def tree_density(self, biome: str) -> float:
        densities = {
            "forest":      0.020,
            "plains":       0.004,
            "jungle":       0.030,
            "taiga":        0.025,
            "swamp":        0.010,
            "savanna":      0.001,
            "mountains":    0.002,
            "mushroom":     0.0,
            "ocean":        0.0,
            "deep_ocean":   0.0,
            "desert":       0.0,
        }
        return densities.get(biome, 0.004)

    def ore_at(self, x: int, y: int, z: int) -> int | None:
        """Return ore block id if a stone block here should be an ore."""
        h = _stable_hash(self.seed, x, y, z)
        r = (h % 10000) / 10000.0
        if r < 0.0025 and y < 14:
            return ID_DIAMOND_ORE
        if r < 0.004 and y < 20:
            return ID_GOLD_ORE
        if r < 0.008 and y < 34:
            return ID_IRON_ORE
        if r < 0.010 and y < 44:
            return ID_COAL_ORE
        return None

    def generate_column(self, x: int, z: int) -> tuple[list[int], str, int]:
        """Generate a column of blocks.

        Returns ``(blocks, biome, height)`` where ``blocks`` is a list
        indexed by y (0..63). Length = CHUNK_SIZE_Y.
        """
        biome_n = self.biome_n(x, z)
        biome = self.biome_at(biome_n)
        h = self.height_at(x, z)

        # Beach: low heights → sand surface
        is_beach = h < 18
        is_desert = biome == "desert"
        is_ocean = biome in ("ocean", "deep_ocean")

        blocks: list[int] = [ID_AIR] * CHUNK_SIZE_Y

        # Surface block per biome
        def surface_block(b: str) -> int:
            if is_desert or is_beach:
                return ID_SAND
            if is_ocean:
                return ID_SAND
            if b == "savanna":
                return ID_GRASS
            if b == "jungle":
                return ID_GRASS
            if b == "taiga":
                return ID_SNOW  # snowy surface
            if b == "swamp":
                return ID_GRASS
            if b == "mountains":
                return ID_STONE  # rocky peaks
            if b == "mushroom":
                return ID_DIRT  # mycelium-like stub
            return ID_GRASS

        # Layers
        for y in range(CHUNK_SIZE_Y):
            if y == 0:
                blocks[y] = ID_BEDROCK
            elif y < h - 3:
                blocks[y] = ID_STONE
                # Deepslate layer at y < 8 (commercial expansion)
                from world.blocks import ID_DEEPSLATE
                if y < 8:
                    blocks[y] = ID_DEEPSLATE
            elif h - 3 <= y < h - 1:
                if is_desert or is_beach or is_ocean:
                    blocks[y] = ID_SAND
                else:
                    blocks[y] = ID_DIRT
            elif y == h - 1:
                blocks[y] = surface_block(biome)
            elif h <= y <= WATER_LEVEL:
                if y > h:
                    blocks[y] = ID_WATER
            else:
                blocks[y] = ID_AIR

            # Ore replacement inside stone layers
            if blocks[y] == ID_STONE:
                ore = self.ore_at(x, y, z)
                if ore is not None:
                    blocks[y] = ore

            # Carve caves per §6.3 (skip under water column)
            if 4 <= y <= h - 4 and blocks[y] == ID_STONE:
                if self.cave_noise.perlin3(
                        x * 0.08, y * 0.08, z * 0.08) > 0.62:
                    if not (h <= WATER_LEVEL and y >= h):
                        blocks[y] = ID_AIR

        # Trees: skip desert, skip underwater, surface must be grass
        rng = np.random.default_rng(_stable_hash(self.seed, x, z))
        if (not is_desert and not is_beach and not is_ocean
                and blocks[h - 1] == ID_GRASS):
            p_tree = self.tree_density(biome)
            if rng.random() < p_tree:
                self._place_tree(blocks, h, rng)

        return blocks, biome, h

    def _place_tree(self, blocks: list[int], surface_y: int,
                    rng: np.random.Generator) -> None:
        trunk_h = 4 + int(rng.integers(0, 3))
        # Trunk
        for i in range(trunk_h):
            y = surface_y + i
            if 0 <= y < len(blocks):
                blocks[y] = ID_LOG
        # Leaves: cube 5×5×4 around the top of the trunk
        # corners trimmed per §6.3 (|dx|+|dz| < 5; upper layers < 3)
        # Within the chunk-only worldgen we ignore neighbours; the
        # cross-chunk leaves will be added by the chunk mesher when
        # adjacent chunks are present.
        top = surface_y + trunk_h
        for dy in (-2, -1, 0, 1):
            y = top + dy
            if not (0 <= y < len(blocks)):
                continue
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if dx == 0 and dz == 0 and dy < 1:
                        # trunk cell — skip
                        continue
                    manhattan = abs(dx) + abs(dz)
                    upper_trim = manhattan >= 3 and dy >= 0
                    if manhattan >= 5 or upper_trim:
                        continue
                    # only place on air
                    if blocks[y] == ID_AIR:
                        blocks[y] = ID_LEAVES


# ── Convenience: per-column heightmap for smoke test ──
def heightmap_at(seed: int, x: int, z: int) -> int:
    """Return the surface height (topmost solid) for column (x,z)."""
    wg = WorldGen(seed)
    blocks, _, h = wg.generate_column(x, z)
    # heightmap = h - 1 per A-8
    return max(0, h - 1)


def generate_column(seed: int, x: int, z: int) -> int:
    """Single-column convenience: returns heightmap (h-1)."""
    return heightmap_at(seed, x, z)
