# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Chunk storage + mesh builder.

Spec ref: §6.4 — SIZE_X=16, SIZE_Y=64, SIZE_Z=16. Storage:
np.zeros((16, 64, 16), dtype=np.uint8) indexed [x, y, z]. is_solid /
is_transparent helpers. Mesher algorithm: for each solid block, for
each of its 6 faces, if neighbour is transparent → emit the face.
Vertex layout 6 floats (x, y, z, u, v, light). Each face = 4 vertices
+ 6 indices. UVs map to (u0,v0)..(u1,v1). Water: separate translucent
mesh, after opaque pass, no depth-write. Torch: two crossed quads.
"""
from __future__ import annotations

import math

import numpy as np

from world.blocks import (
    ID_AIR, ID_LEAVES, ID_GLASS, ID_WATER, ID_TORCH,
    is_solid, is_transparent,
    get as get_block,
)
from world.worldgen import (
    CHUNK_SIZE_X, CHUNK_SIZE_Y, CHUNK_SIZE_Z, WorldGen,
)

# Baked face-light per §6.4
FACE_LIGHT = (1.00, 0.50, 0.80, 0.80, 0.65, 0.65)

# Face → neighbour offset (Dx, Dy, Dz) and the 4 corner positions
# (CCW seen from outside) per §6.4 table.
FACE_DEFS = (
    # +Y top
    ((0, 1, 0),
     [(0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)]),
    # -Y bottom
    ((0, -1, 0),
     [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
    # +X
    ((1, 0, 0),
     [(1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)]),
    # -X
    ((-1, 0, 0),
     [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
    # +Z
    ((0, 0, 1),
     [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
    # -Z
    ((0, 0, -1),
     [(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)]),
)

# UV corner order matches the face-corner order so the texture maps
# correctly onto each face.
UV_CORNERS = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

HALF_TEXEL = 0.5 / 256.0


def _tile_uv(tile: int) -> tuple[float, float, float, float]:
    """Return (u0, v0, u1, v1) for a tile index, with half-texel
    inset per §5.5."""
    u0 = (tile % 16) / 16.0 + HALF_TEXEL
    v0 = (tile // 16) / 16.0 + HALF_TEXEL
    u1 = (tile % 16 + 1) / 16.0 - HALF_TEXEL
    v1 = (tile // 16 + 1) / 16.0 - HALF_TEXEL
    return u0, v0, u1, v1


class Chunk:
    """A 16×64×16 chunk of voxel blocks."""

    __slots__ = ("cx", "cz", "seed", "blocks", "neighbours", "dirty",
                 "_opaque_v", "_opaque_i", "_water_v", "_water_i",
                 "_cross_v", "_cross_i", "_worldgen")

    def __init__(self, cx: int, cz: int, seed: int = 0,
                 worldgen: WorldGen | None = None) -> None:
        self.cx = cx
        self.cz = cz
        self.seed = int(seed)
        self.blocks = np.zeros((CHUNK_SIZE_X, CHUNK_SIZE_Y, CHUNK_SIZE_Z),
                               dtype=np.uint8)
        self.neighbours: dict[tuple[int, int], "Chunk"] = {}
        self.dirty = True
        self._opaque_v: list[float] = []
        self._opaque_i: list[int] = []
        self._water_v: list[float] = []
        self._water_i: list[int] = []
        self._cross_v: list[float] = []
        self._cross_i: list[int] = []
        self._worldgen = worldgen

    # ── Block access ───────────────────────────────────────
    def get(self, x: int, y: int, z: int) -> int:
        if not (0 <= x < CHUNK_SIZE_X and 0 <= y < CHUNK_SIZE_Y
                and 0 <= z < CHUNK_SIZE_Z):
            return 0
        return int(self.blocks[x, y, z])

    def set(self, x: int, y: int, z: int, block_id: int) -> None:
        if not (0 <= x < CHUNK_SIZE_X and 0 <= y < CHUNK_SIZE_Y
                and 0 <= z < CHUNK_SIZE_Z):
            return
        if int(self.blocks[x, y, z]) == int(block_id):
            return
        self.blocks[x, y, z] = int(block_id)
        self.dirty = True

    def world_block(self, lx: int, ly: int, lz: int) -> int:
        """Get a block in this chunk or its neighbours (for face
        culling at chunk borders)."""
        if 0 <= lx < CHUNK_SIZE_X and 0 <= lz < CHUNK_SIZE_Z:
            return self.get(lx, ly, lz)
        # Off-edge: ask neighbour
        for (ox, oz), chunk in self.neighbours.items():
            nx = lx - ox * CHUNK_SIZE_X
            nz = lz - oz * CHUNK_SIZE_Z
            if 0 <= nx < CHUNK_SIZE_X and 0 <= nz < CHUNK_SIZE_Z:
                return chunk.get(nx, ly, nz)
        return 0

    # ── Generation ─────────────────────────────────────────
    def generate(self, worldgen: WorldGen | None = None) -> None:
        wg = worldgen or self._worldgen or WorldGen(self.seed)
        for lx in range(CHUNK_SIZE_X):
            for lz in range(CHUNK_SIZE_Z):
                wx = self.cx * CHUNK_SIZE_X + lx
                wz = self.cz * CHUNK_SIZE_Z + lz
                blocks, _, _ = wg.generate_column(wx, wz)
                for y in range(CHUNK_SIZE_Y):
                    if y < len(blocks):
                        self.blocks[lx, y, lz] = blocks[y]
        self.dirty = True

    # ── Mesh builder ───────────────────────────────────────
    def build_mesh(self) -> tuple[list[float], list[int]]:
        """Build the opaque + water + cross meshes.

        Returns ``(opaque_vertices, opaque_indices)`` where each
        vertex is 6 floats (x, y, z, u, v, light). Water + cross
        meshes are stored on the chunk in ``_water_v/_water_i`` and
        ``_cross_v/_cross_i``.
        """
        self._opaque_v.clear()
        self._opaque_i.clear()
        self._water_v.clear()
        self._water_i.clear()
        self._cross_v.clear()
        self._cross_i.clear()

        base_index = 0
        water_base = 0
        cross_base = 0

        for x in range(CHUNK_SIZE_X):
            for y in range(CHUNK_SIZE_Y):
                for z in range(CHUNK_SIZE_Z):
                    bid = int(self.blocks[x, y, z])
                    if bid == 0:
                        continue
                    if bid == ID_TORCH:
                        # Cross mesh — two diagonal quads
                        self._emit_cross(x, y, z, bid, cross_base)
                        cross_base += 4
                        continue
                    if bid == ID_WATER:
                        # Water pass
                        self._emit_face(x, y, z, 0, bid,
                                        self._water_v, self._water_i,
                                        water_base, water=True)
                        water_base += 4
                        continue
                    # Opaque + leaves + glass + ores + crafted blocks
                    for face_idx, (offset, corners) in enumerate(FACE_DEFS):
                        nx, ny, nz = x + offset[0], y + offset[1], z + offset[2]
                        neighbour = self.world_block(nx, ny, nz)
                        if is_transparent(neighbour) and neighbour != bid:
                            self._emit_face(x, y, z, face_idx, bid,
                                            self._opaque_v, self._opaque_i,
                                            base_index)
                            base_index += 4

        self.dirty = False
        return self._opaque_v, self._opaque_i

    def _emit_face(self, x: int, y: int, z: int, face_idx: int,
                   bid: int, verts: list[float], inds: list[int],
                   base: int, water: bool = False) -> None:
        offset, corners = FACE_DEFS[face_idx]
        bdef = get_block(bid)
        tile = bdef.tiles[1] if face_idx not in (0, 1) \
            else (bdef.tiles[0] if face_idx == 0 else bdef.tiles[2])
        u0, v0, u1, v1 = _tile_uv(tile)
        light = FACE_LIGHT[face_idx]
        if water:
            light = 1.0
        uv_map = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        for i, (cx, cy, cz) in enumerate(corners):
            uu, vv = uv_map[i]
            verts.extend([x + cx, y + cy, z + cz, uu, vv, light])
        inds.extend([base, base + 1, base + 2,
                     base, base + 2, base + 3])

    def _emit_cross(self, x: int, y: int, z: int, bid: int,
                    base: int) -> None:
        """Two crossed quads for torches."""
        bdef = get_block(bid)
        tile = bdef.tiles[0]
        u0, v0, u1, v1 = _tile_uv(tile)
        light = 1.0
        uv_map = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        # Quad 1: (0,0,0) → (1,0,1) → (1,1,1) → (0,1,0)
        q1 = [(0, 0, 0), (1, 0, 1), (1, 1, 1), (0, 1, 0)]
        # Quad 2: (1,0,0) → (0,0,1) → (0,1,1) → (1,1,0)
        q2 = [(1, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 0)]
        for quad in (q1, q2):
            for i, (cx, cy, cz) in enumerate(quad):
                uu, vv = uv_map[i]
                self._cross_v.extend(
                    [x + cx, y + cy, z + cz, uu, vv, light])
            self._cross_i.extend(
                [base, base + 1, base + 2, base, base + 2, base + 3])
            base += 4

    @property
    def opaque_mesh(self) -> tuple[list[float], list[int]]:
        return self._opaque_v, self._opaque_i

    @property
    def water_mesh(self) -> tuple[list[float], list[int]]:
        return self._water_v, self._water_i

    @property
    def cross_mesh(self) -> tuple[list[float], list[int]]:
        return self._cross_v, self._cross_i
