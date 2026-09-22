# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Procedural Minecraft-style texture atlas.

Spec ref: §5.5 — Atlas 256×256 = 16×16 tiles of 16 px, built with
numpy uint8 RGBA. A global pixel-noise helper applies per-pixel
value jitter of the base colour by uniform ±V (V per tile).

24 tiles (0–23): grass_top, grass_side, dirt, stone, cobble, sand,
gravel, log_side, log_top, planks, leaves, water, glass, coal_ore,
iron_ore, gold_ore, diamond_ore, bedrock, crafting_top,
crafting_side, furnace_front, furnace_side, chest_side, torch.

Tile 25 = sun, tile 26 = moon (per A-9). Tiles 24, 27–31 reserved
blank.
"""
from __future__ import annotations

import math

import numpy as np

ATLAS_SIZE = 256
TILE_SIZE = 16
TILES_PER_ROW = ATLAS_SIZE // TILE_SIZE  # 16


def _rng_for_tile(tile: int) -> np.random.Generator:
    """Deterministic RNG per tile (so the atlas is reproducible)."""
    return np.random.default_rng(seed=0xC1A5 + tile)


def _jitter(arr: np.ndarray, base: tuple[int, int, int], V: int,
            rng: np.random.Generator) -> np.ndarray:
    """Apply per-pixel value jitter of ±V to a (h, w, 3) uint8 array
    whose base colour is ``base``."""
    h, w, _ = arr.shape
    noise = rng.integers(-V, V + 1, size=(h, w, 1), dtype=np.int16)
    out = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return out


def _blank_tile(rng=None) -> np.ndarray:
    return np.zeros((TILE_SIZE, TILE_SIZE, 4), dtype=np.uint8)


def _solid_tile(base: tuple[int, int, int], V: int = 8,
                rng: np.random.Generator | None = None) -> np.ndarray:
    """16×16 RGBA with base colour and per-pixel jitter ±V."""
    if rng is None:
        rng = np.random.default_rng()
    arr = np.tile(np.array(base, dtype=np.uint8),
                  (TILE_SIZE, TILE_SIZE, 1))
    arr = _jitter(arr, base, V, rng)
    alpha = np.full((TILE_SIZE, TILE_SIZE, 1), 255, dtype=np.uint8)
    return np.concatenate([arr, alpha], axis=-1)


def _draw_speckles(arr: np.ndarray, color: tuple[int, int, int],
                   p: float, rng: np.random.Generator) -> None:
    h, w, _ = arr.shape
    mask = rng.random((h, w)) < p
    arr[mask, :3] = np.array(color, dtype=np.uint8)


def _draw_polyline(arr: np.ndarray, color: tuple[int, int, int],
                   rng: np.random.Generator,
                   length: int = 8) -> None:
    """Draw a darker polyline."""
    h, w, _ = arr.shape
    x = rng.integers(0, w)
    y = rng.integers(0, h)
    dx = rng.choice([-1, 0, 1])
    dy = rng.choice([-1, 0, 1])
    for _ in range(length):
        if 0 <= x < w and 0 <= y < h:
            arr[y, x, :3] = np.array(color, dtype=np.uint8)
        x = int(np.clip(x + dx, 0, w - 1))
        y = int(np.clip(y + dy, 0, h - 1))


# ─────────────────────────────────────────────────────────────
# Tile builders
# ─────────────────────────────────────────────────────────────

def _grass_top(rng):
    arr = _solid_tile((106, 170, 64), V=18, rng=rng)
    _draw_speckles(arr, (90, 150, 50), p=0.08, rng=rng)
    return arr


def _grass_side(rng):
    arr = _solid_tile((134, 96, 67), V=14, rng=rng)
    arr[:4, :, :3] = np.tile(np.array((106, 170, 64), dtype=np.uint8),
                             (4, TILE_SIZE, 1))
    return arr


def _dirt(rng):
    return _solid_tile((134, 96, 67), V=16, rng=rng)


def _stone(rng):
    arr = _solid_tile((125, 125, 125), V=12, rng=rng)
    for _ in range(3):
        _draw_polyline(arr, (95, 95, 95), rng, length=6)
    return arr


def _cobble(rng):
    arr = _solid_tile((125, 125, 125), V=12, rng=rng)
    for _ in range(5):
        cx, cy = int(rng.integers(2, 14)), int(rng.integers(2, 14))
        r = int(rng.integers(2, 4))
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    arr[y, x, :3] = (160, 160, 160)
    return arr


def _sand(rng):
    return _solid_tile((219, 207, 163), V=10, rng=rng)


def _gravel(rng):
    arr = _solid_tile((136, 126, 126), V=25, rng=rng)
    # big blotches
    for _ in range(4):
        cx, cy = int(rng.integers(0, 16)), int(rng.integers(0, 16))
        r = int(rng.integers(2, 4))
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    arr[y, x, :3] = (110, 100, 100)
    return arr


def _log_side(rng):
    arr = _solid_tile((102, 81, 50), V=8, rng=rng)
    # vertical dark grain lines at x ∈ {2, 7, 12}
    for x in (2, 7, 12):
        arr[:, x, :3] = (70, 55, 35)
    return arr


def _log_top(rng):
    arr = _solid_tile((151, 122, 73), V=0, rng=rng)
    # concentric rings (distance mod 4 < 1 → dark)
    cx, cy = 7.5, 7.5
    for y in range(TILE_SIZE):
        for x in range(TILE_SIZE):
            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if int(d) % 4 == 0:
                arr[y, x, :3] = (110, 90, 55)
    return arr


def _planks(rng):
    arr = _solid_tile((162, 130, 78), V=8, rng=rng)
    # horizontal seams at y ∈ {0, 5, 10, 15}
    for y in (0, 5, 10, 15):
        arr[y, :, :3] = (120, 95, 55)
    return arr


def _leaves(rng):
    arr = _solid_tile((58, 95, 32), V=30, rng=rng)
    # alpha: p=0.12 of pixels fully transparent
    mask = rng.random((TILE_SIZE, TILE_SIZE)) < 0.12
    arr[mask, 3] = 0
    return arr


def _water(rng):
    arr = _solid_tile((47, 93, 201), V=10, rng=rng)
    arr[:, :, 3] = 170  # alpha=170
    return arr


def _glass(rng):
    arr = np.zeros((TILE_SIZE, TILE_SIZE, 4), dtype=np.uint8)
    # border 1 px (200,220,230,255)
    arr[0, :, :] = (200, 220, 230, 255)
    arr[-1, :, :] = (200, 220, 230, 255)
    arr[:, 0, :] = (200, 220, 230, 255)
    arr[:, -1, :] = (200, 220, 230, 255)
    # inner alpha=28
    arr[1:-1, 1:-1, 3] = 28
    arr[1:-1, 1:-1, :3] = (200, 220, 230)
    return arr


def _ore(base_color, rng):
    arr = _solid_tile((125, 125, 125), V=12, rng=rng)
    n = int(rng.integers(4, 7))
    for _ in range(n):
        cx, cy = int(rng.integers(0, 16)), int(rng.integers(0, 16))
        r = int(rng.integers(1, 3))
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    arr[y, x, :3] = base_color
    return arr


def _bedrock(rng):
    return _solid_tile((60, 60, 60), V=35, rng=rng)


def _crafting_top(rng):
    arr = _planks(rng)
    # dark grid border 1 px + centre 2 px square
    arr[0, :, :3] = (90, 70, 40)
    arr[-1, :, :3] = (90, 70, 40)
    arr[:, 0, :3] = (90, 70, 40)
    arr[:, -1, :3] = (90, 70, 40)
    arr[7:9, 7:9, :3] = (90, 70, 40)
    return arr


def _crafting_side(rng):
    arr = _planks(rng)
    # simple dark rectangles (tool silhouettes)
    arr[3:6, 3:5, :3] = (60, 45, 25)
    arr[3:6, 10:12, :3] = (60, 45, 25)
    return arr


def _furnace_front(rng):
    arr = _stone(rng)
    # dark opening 6×5 centred at bottom
    arr[8:13, 5:11, :3] = (40, 40, 40)
    return arr


def _furnace_side(rng):
    return _cobble(rng)


def _chest_side(rng):
    arr = _solid_tile((120, 90, 55), V=8, rng=rng)
    # latch 2×3 (255,215,0)
    arr[7:10, 7:9, :3] = (255, 215, 0)
    return arr


def _torch(rng):
    arr = np.zeros((TILE_SIZE, TILE_SIZE, 4), dtype=np.uint8)
    # 2 px-wide stick centred (120,90,50) rows 6..15
    arr[6:16, 7:9, :3] = (120, 90, 50)
    arr[6:16, 7:9, 3] = 255
    # flame 4×4 (255,200,60)/(255,120,20) rows 2..5
    arr[2:6, 6:10, :3] = (255, 200, 60)
    arr[2:6, 6:10, 3] = 255
    arr[4:6, 6:10, :3] = (255, 120, 20)
    return arr


def _sun(rng):
    arr = np.zeros((TILE_SIZE, TILE_SIZE, 4), dtype=np.uint8)
    cx = cy = 7.5
    for y in range(TILE_SIZE):
        for x in range(TILE_SIZE):
            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if d <= 6:
                arr[y, x, :3] = (255, 230, 120)
                arr[y, x, 3] = 255
            elif d <= 7:
                arr[y, x, :3] = (255, 200, 80)
                arr[y, x, 3] = 200
    return arr


def _moon(rng):
    arr = np.zeros((TILE_SIZE, TILE_SIZE, 4), dtype=np.uint8)
    cx = cy = 7.5
    for y in range(TILE_SIZE):
        for x in range(TILE_SIZE):
            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if d <= 6:
                arr[y, x, :3] = (230, 230, 230)
                arr[y, x, 3] = 255
    # 3 craters
    for cx, cy, r in [(5, 5, 1), (10, 9, 1), (8, 12, 1)]:
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    arr[y, x, :3] = (180, 180, 180)
    return arr


# Tile → builder lookup (per §5.5 + A-9)
TILE_BUILDERS = [
    _grass_top,    # 0
    _grass_side,    # 1
    _dirt,          # 2
    _stone,         # 3
    _cobble,        # 4
    _sand,          # 5
    _gravel,        # 6
    _log_side,      # 7
    _log_top,       # 8
    _planks,        # 9
    _leaves,        # 10
    _water,         # 11
    _glass,         # 12
    lambda r: _ore((35, 35, 35), r),   # 13 coal_ore
    lambda r: _ore((216, 175, 147), r), # 14 iron_ore
    lambda r: _ore((252, 222, 112), r), # 15 gold_ore
    lambda r: _ore((93, 236, 245), r),  # 16 diamond_ore
    _bedrock,       # 17
    _crafting_top,  # 18
    _crafting_side, # 19
    _furnace_front, # 20
    _furnace_side,  # 21
    _chest_side,    # 22
    _torch,         # 23
    _blank_tile,    # 24 reserved
    _sun,           # 25 sun
    _moon,          # 26 moon
    _blank_tile, _blank_tile, _blank_tile,
    _blank_tile, _blank_tile,  # 27..31 reserved
]


def build_atlas() -> np.ndarray:
    """Build the 256×256 RGBA atlas and return it."""
    atlas = np.zeros((ATLAS_SIZE, ATLAS_SIZE, 4), dtype=np.uint8)
    for tile in range(32):
        if tile >= len(TILE_BUILDERS):
            break
        rng = _rng_for_tile(tile)
        builder = TILE_BUILDERS[tile]
        pixels = builder(rng)
        tx = (tile % TILES_PER_ROW) * TILE_SIZE
        ty = (tile // TILES_PER_ROW) * TILE_SIZE
        atlas[ty:ty + TILE_SIZE, tx:tx + TILE_SIZE] = pixels
    return atlas


# ── Pygame Surface cache (for UI icons) ──
_tile_surfaces: dict[int, object] = {}
_atlas_surface: object | None = None


def get_atlas_surface():
    """Return the atlas as a pygame.Surface (cached)."""
    global _atlas_surface
    if _atlas_surface is not None:
        return _atlas_surface
    import pygame
    atlas = build_atlas()
    # arr is (H, W, 4); pygame surfarray wants (W, H, 3) for RGB +
    # separate alpha or (W, H) for RGBA via frombuffer
    _atlas_surface = pygame.image.frombuffer(
        atlas.tobytes(), (ATLAS_SIZE, ATLAS_SIZE), "RGBA").convert_alpha()
    return _atlas_surface


def tile_surfaces():
    """Return per-tile pygame.Surface dict (for UI hotbar icons)."""
    global _tile_surfaces
    if _tile_surfaces:
        return _tile_surfaces
    import pygame
    atlas = build_atlas()
    for tile in range(32):
        tx = (tile % TILES_PER_ROW) * TILE_SIZE
        ty = (tile // TILES_PER_ROW) * TILE_SIZE
        sub = atlas[ty:ty + TILE_SIZE, tx:tx + TILE_SIZE]
        surf = pygame.image.frombuffer(
            sub.tobytes(), (TILE_SIZE, TILE_SIZE), "RGBA").convert_alpha()
        _tile_surfaces[tile] = surf
    return _tile_surfaces


def tile_avg_color(tile: int) -> tuple[int, int, int]:
    """Return the average RGB of a tile (for particle tinting)."""
    rng = _rng_for_tile(tile)
    builder = TILE_BUILDERS[tile] if tile < len(TILE_BUILDERS) else _blank_tile
    pixels = builder(rng)
    avg = pixels[..., :3].mean(axis=(0, 1)).astype(int)
    return tuple(int(c) for c in avg)


def dump_atlas_png(path: str) -> None:
    """Save the atlas as a PNG for the §17.3 smoke check."""
    import pygame
    surf = get_atlas_surface()
    pygame.image.save(surf, path)
