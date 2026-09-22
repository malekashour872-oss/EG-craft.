# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Entity spawner.

Spec ref: §9.4 — Tick every 2.0 s. Caps: passive 12, hostile 15.
daylight > 0.6 → spawn passive; daylight < 0.3 → spawn hostile;
otherwise none. Position: random loaded chunk, random column, y =
heightmap + 1; must be air × 2 above solid; distance to player 20..40.
Weights uniform over the class. Despawn: distance > 56 (instant).
Dawn burn: hostile with sky access (no solid above) when daylight >
0.7 → 1 dmg/s.
"""
from __future__ import annotations

import logging
import random
from typing import Callable

import numpy as np

from entities.species import PASSIVE, HOSTILE, SPECIES
from entities.entity import Entity, make_entity_from_species

log = logging.getLogger("egcraft.spawner")

SPAWN_TICK_INTERVAL = 2.0
PASSIVE_CAP = 12
HOSTILE_CAP = 15
SPAWN_MIN_DIST = 20
SPAWN_MAX_DIST = 40
DESPAWN_DIST = 56


class Spawner:
    """Entity spawning + despawning manager."""

    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)
        self.timer = 0.0

    def tick(self, dt: float, daylight: float,
             entities: list[Entity], player_pos: np.ndarray,
             world, registry=None) -> None:
        """Advance spawner; mutate ``entities`` in-place."""
        self.timer += dt
        if self.timer < SPAWN_TICK_INTERVAL:
            self.timer -= SPAWN_TICK_INTERVAL if self.timer >= SPAWN_TICK_INTERVAL else 0
            return
        self.timer = 0.0
        # Despawn far entities
        to_remove = []
        for e in entities:
            if e.dead:
                continue
            d = float(np.linalg.norm(e.pos - player_pos))
            if d > DESPAWN_DIST:
                to_remove.append(e)
        for e in to_remove:
            entities.remove(e)

        # Dawn burn
        if daylight > 0.7:
            for e in entities:
                if e.hostile and not e.dead:
                    # check sky access
                    x, y, z = int(e.pos[0]), int(e.pos[1]) + 2, int(e.pos[2])
                    if world.get_block(x, y, z) == 0:
                        e.hp -= 1
                        if e.hp <= 0:
                            e.dead = True

        # Spawn caps
        passive_n = sum(1 for e in entities
                         if not e.hostile and not e.dead)
        hostile_n = sum(1 for e in entities
                         if e.hostile and not e.dead)

        # Decide what to spawn
        if daylight > 0.6 and passive_n < PASSIVE_CAP:
            self._spawn_one(entities, player_pos, world,
                            passive=True, registry=registry)
        elif daylight < 0.3 and hostile_n < HOSTILE_CAP:
            self._spawn_one(entities, player_pos, world,
                            passive=False, registry=registry)

    def _spawn_one(self, entities: list[Entity], player_pos,
                   world, passive: bool, registry=None) -> None:
        # Pick a random loaded chunk
        chunks = list(world.chunks.values())
        if not chunks:
            return
        chunk = self.rng.choice(chunks)
        # Random column in the chunk
        lx = self.rng.randint(0, 15)
        lz = self.rng.randint(0, 15)
        wx = chunk.cx * 16 + lx
        wz = chunk.cz * 16 + lz
        h = world.heightmap_at(wx, wz)
        y = h + 1
        # Distance check
        d = float(np.linalg.norm(
            np.array([wx, y, wz], dtype=np.float32) - player_pos))
        if not (SPAWN_MIN_DIST <= d <= SPAWN_MAX_DIST):
            return
        # Air × 2 above solid
        if world.get_block(wx, y, wz) != 0:
            return
        if world.get_block(wx, y + 1, wz) != 0:
            return
        # Choose species
        pool = PASSIVE if passive else HOSTILE
        if not pool:
            return
        sp = self.rng.choice(pool)
        pos = np.array([wx + 0.5, y, wz + 0.5], dtype=np.float32)
        ent = make_entity_from_species(sp, pos)
        entities.append(ent)
