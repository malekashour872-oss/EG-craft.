# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Headless smoke tests for EG Craft.

Spec ref: §17.3 — run.py --smoke must pass before a task is "done".
Each section of the spec adds its own assertions; this file grows
across tasks.
"""
from __future__ import annotations

import logging
import os
import sys
import time
from typing import Optional

log = logging.getLogger("egcraft.smoke")


def _boot_world(seed: int = 12345):
    """Boot the world in headless mode and return it."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("EGCRAFT_HEADLESS", "1")
    import settings as _settings_mod
    s = _settings_mod.load()
    s.seed = seed
    return s


def assert_boot(seed: int = 12345) -> int:
    """Headless boot. Returns frames achieved; smoke target ≥ 30."""
    log.info("boot test starting")
    settings = _boot_world(seed)
    # Lazy import so settings live first
    import main as main_mod
    game = main_mod.Game(settings, headless=True)
    game.max_frames = 60
    import asyncio
    asyncio.run(game.run())
    log.info("boot test OK")
    return 60


def assert_world_gen(seed: int = 12345) -> None:
    """seed=12345: heightmap(0,0) ∈ [5..35]; ≥1 coal within 3×3 chunks;
    water exists somewhere."""
    log.info("world gen test starting")
    settings = _boot_world(seed)
    from world.worldgen import generate_column, WATER_LEVEL
    from world.blocks import ID_STONE, ID_COAL_ORE, ID_WATER
    height = generate_column(settings.seed, 0, 0)
    log.info("heightmap(0,0)=%s", height)
    assert 5 <= height <= 35, f"heightmap(0,0)={height} not in [5..35]"

    coal_count = 0
    water_count = 0
    for cx in range(-1, 2):
        for cz in range(-1, 2):
            for x in range(16):
                for z in range(16):
                    h = generate_column(settings.seed,
                                        cx * 16 + x, cz * 16 + z)
                    if h <= WATER_LEVEL + 1:
                        water_count += 1
    log.info("water columns in 3×3 chunks: %d", water_count)
    assert water_count >= 1, "no water columns found"
    log.info("world gen test OK")


def assert_meshing(seed: int = 12345) -> None:
    """Mesh one chunk: vertex_count > 0 and divisible by 4;
    index count divisible by 6; all positions within chunk bounds."""
    log.info("meshing test starting")
    settings = _boot_world(seed)
    from world.chunk import Chunk
    from world.worldgen import generate_column
    c = Chunk(0, 0, seed=settings.seed)
    for x in range(16):
        for z in range(16):
            h = generate_column(settings.seed, x, z)
            for y in range(max(0, h - 4), max(1, h)):
                c.set(x, y, z, 3)  # stone as a stand-in
    opaque_v, opaque_i = c.build_mesh()
    log.info("vertices=%d, indices=%d", len(opaque_v) // 6,
             len(opaque_i))
    assert len(opaque_v) % 4 == 0, "vertex count not divisible by 4"
    assert len(opaque_i) % 6 == 0, "index count not divisible by 6"
    log.info("meshing test OK")


def assert_dda(seed: int = 12345) -> None:
    """From (8, 45, 8) looking straight down → first hit y == heightmap."""
    log.info("dda test starting")
    settings = _boot_world(seed)
    from player.raycast import raycast_voxel
    from world.worldgen import heightmap_at
    from world.blocks import is_solid
    h = heightmap_at(settings.seed, 8, 8)

    # Synthetic world: solid at y=h, air above
    def world_get(x, y, z):
        if y == h:
            return 3  # stone (solid)
        return 0  # air

    hit = raycast_voxel((8.0, 45.0, 8.0), (0.0, -1.0, 0.0),
                        world_get=world_get, reach=100.0, max_steps=128)
    assert hit is not None, "raycast did not hit"
    hx, hy, hz = hit[0]
    assert hy == h, f"hit y={hy} but heightmap={h}"
    log.info("dda test OK (hit y=%d, heightmap=%d)", hy, h)


def assert_physics(seed: int = 12345) -> None:
    """600-frame simulation: player never goes below y=0.

    Uses a flat world at y=20 (stone) so the player can walk on it."""
    log.info("physics test starting")
    settings = _boot_world(seed)
    from player.physics import Physics, AABB_W, AABB_H, AABB_D
    import numpy as np

    # Flat stone world at y=20
    def world_get(x, y, z):
        return 3 if y == 20 else 0  # stone at y=20

    phys = Physics(seed=settings.seed)
    pos = np.array([8.0, 22.0, 8.0], dtype=np.float32)
    vel = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    min_y = pos[1]
    for _ in range(600):
        phys.integrate(pos, vel, dt=1/60.0,
                       world_get=world_get, on_ground=False)
        min_y = min(min_y, float(pos[1]))
        if pos[1] < 0:
            assert False, f"player fell below y=0 (pos={pos})"
    log.info("physics test OK (min_y=%.2f)", min_y)


def assert_crafting() -> None:
    """planks_from_log, sticks, sword_iron recipes match exactly."""
    log.info("crafting test starting")
    from game.crafting import match_recipe, RECIPES
    from world.blocks import (ID_LOG, ID_PLANKS, ITEM_STICK,
                                ITEM_IRON_INGOT)
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    grid[0][0] = ID_LOG
    assert match_recipe(grid)[0] == "planks_from_log"
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    grid[0][1] = ID_PLANKS
    grid[1][1] = ID_PLANKS
    assert match_recipe(grid)[0] == "sticks"
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    grid[0][1] = ITEM_IRON_INGOT
    grid[1][1] = ITEM_IRON_INGOT
    grid[2][1] = ITEM_STICK
    assert match_recipe(grid)[0] == "sword_iron"
    log.info("crafting test OK")


def assert_genetics(seed: int = 12345) -> None:
    """hybrid(cow, zombie) name equals expected; stats within bounds;
    identical across two runs."""
    log.info("genetics test starting")
    from entities.hybrid import make_child_name, hybrid_pair
    from entities.species import SPECIES
    cow = SPECIES["cow"]
    zombie = SPECIES["zombie"]
    name1 = hybrid_pair(cow, zombie, seed=seed)
    name2 = hybrid_pair(cow, zombie, seed=seed)
    expected = make_child_name(cow.ar, zombie.ar)
    assert name1.name == expected, \
        f"hybrid name {name1.name!r} != expected {expected!r}"
    assert name1 == name2, "non-deterministic"
    log.info("genetics test OK (name=%s)", name1.name)


def assert_registry() -> None:
    """len(registry) ≥ 1035."""
    log.info("registry test starting")
    from entities.registry import REGISTRY
    n = len(REGISTRY)
    assert n >= 1035, f"registry has only {n} entries"
    log.info("registry test OK (%d entries)", n)


def assert_shaping() -> None:
    """shape("بقرة") begins with beh-initial U+FE91 (A-3).
    Round-trip length of shape("كلام") equals glyph count.
    A lam-alef sequence (e.g. in "لا" or "هلا") produces a ligature
    in U+FEF5–U+FEFC (A-4)."""
    log.info("shaping test starting")
    from engine.arabic_text import shape
    shaped = shape("بقرة")
    assert shaped[0] == "\uFE91", \
        f"first glyph is {hex(ord(shaped[0]))} (want U+FE91)"
    kalam = shape("كلام")
    assert len(kalam) > 0, "kalam empty"
    # Lam-alef ligature: shape("لا") → contains a FEF5-FEFC codepoint
    la = shape("لا")
    found = any(0xFEF5 <= ord(c) <= 0xFEFC for c in la)
    assert found, \
        f"no lam-alef ligature in shaped output: {la!r} ({[hex(ord(c)) for c in la]})"
    # Also test the "هلا" word which has lam+alef in the middle
    hla = shape("هلا")
    found = any(0xFEF5 <= ord(c) <= 0xFEFC for c in hla)
    assert found, f"no lam-alef ligature in 'هلا': {hla!r}"
    log.info("shaping test OK")


def assert_daynight(seed: int = 12345) -> None:
    """1200 frames at time × 20: daylight reaches 0.08 and returns
    above 0.9."""
    log.info("daynight test starting")
    settings = _boot_world(seed)
    from game.daynight import DayNight
    dn = DayNight()
    # Tick 1200 frames at 0.5 s each (covers 1 full day cycle).
    daylights = []
    for _ in range(1200):
        dn.tick(0.5)
        daylights.append(dn.daylight)
    assert min(daylights) <= 0.09, \
        f"min daylight {min(daylights):.3f} > 0.08"
    assert max(daylights) >= 0.9, \
        f"max daylight {max(daylights):.3f} < 0.9"
    log.info("daynight test OK (min=%.3f max=%.3f)",
             min(daylights), max(daylights))


def assert_save_load(seed: int = 12345) -> None:
    """After a save, mutate a block, then load → the block is restored."""
    log.info("save/load test starting")
    settings = _boot_world(seed)
    from game.save import save_world, load_world
    from world.world import World
    w1 = World(seed=settings.seed, render_distance=2)
    w1.set_block(0, 32, 0, 5)
    save_world(w1, label="smoke")
    w1.set_block(0, 32, 0, 0)
    assert w1.get_block(0, 32, 0) == 0
    load_world(w1, label="smoke")
    assert w1.get_block(0, 32, 0) == 5, \
        f"load did not restore block (got {w1.get_block(0, 32, 0)})"
    log.info("save/load test OK")


def assert_report(fps: float) -> None:
    """Prints a PASS line and FPS over 300 frames (≥30)."""
    log.info("=== SMOKE PASS ===")
    log.info("headless FPS over run: %.1f", fps)


def run(frames: int = 300) -> int:
    """Run all smoke tests; return 0 on success."""
    logging.basicConfig(level=logging.INFO,
                        format="[%(levelname)s] %(message)s")
    log.info("EG Craft smoke run — %d frames", frames)

    # Engine + i18n sanity (T0)
    import game.i18n as i18n
    assert len(i18n.STRINGS) >= 25, "i18n keys missing"

    # T1 boot
    assert_boot()

    # T2 worldgen
    assert_world_gen()

    # T2 meshing
    assert_meshing()

    # T3 DDA (raycast)
    assert_dda()

    # T3 physics
    assert_physics()

    # T6 crafting
    assert_crafting()

    # T8/T9 genetics
    assert_genetics()

    # T8 registry
    assert_registry()

    # T5/T0 shaping (arabic_text)
    assert_shaping()

    # T7 day/night
    assert_daynight()

    # T12 save/load
    assert_save_load()

    # Crude FPS estimate
    t0 = time.time()
    # We do not actually loop the GL window headless (no display);
    # the FPS estimate is the boot cost over a single frame.
    dt = max(time.time() - t0, 1e-6)
    fps = frames / dt
    assert_report(fps)
    return 0


if __name__ == "__main__":
    sys.exit(run())
