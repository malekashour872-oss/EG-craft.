# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Projectiles (arrows, fireballs).

Spec ref: §9.3 — Ranged hostiles: skeleton, stray, witch, pillager,
ghast, blaze keep distance 8; fire a projectile every 2 s. Arrow:
speed 18, gravity 18, dmg per table. Witch: dmg 4. Blaze fireball:
speed 8, no gravity, dmg 3.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class Projectile:
    pos: np.ndarray
    vel: np.ndarray
    dmg: int
    gravity: float
    owner: str          # "skeleton" | "blaze" | "witch" | ...
    lifetime: float = 5.0
    dead: bool = False
    sprite_tile: int = 23

    def update(self, dt: float, world_get=None) -> None:
        if self.dead:
            return
        self.vel[1] -= self.gravity * dt
        self.pos += self.vel * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.dead = True
            return
        if world_get is not None:
            x, y, z = int(math.floor(self.pos[0])), \
                       int(math.floor(self.pos[1])), \
                       int(math.floor(self.pos[2]))
            bid = world_get(x, y, z)
            if bid != 0:  # solid block
                self.dead = True


class ProjectileManager:
    """Pool of projectiles."""

    def __init__(self) -> None:
        self.projectiles: list[Projectile] = []

    def spawn_arrow(self, origin, target, dmg: int) -> None:
        d = np.array(target, dtype=np.float32) - np.array(
            origin, dtype=np.float32)
        n = float(np.linalg.norm(d))
        if n < 1e-6:
            return
        v = (d / n) * 18.0
        self.projectiles.append(Projectile(
            pos=np.array(origin, dtype=np.float32),
            vel=v.astype(np.float32),
            dmg=dmg, gravity=18.0, owner="skeleton",
        ))

    def spawn_fireball(self, origin, target, dmg: int = 3) -> None:
        d = np.array(target, dtype=np.float32) - np.array(
            origin, dtype=np.float32)
        n = float(np.linalg.norm(d))
        if n < 1e-6:
            return
        v = (d / n) * 8.0
        self.projectiles.append(Projectile(
            pos=np.array(origin, dtype=np.float32),
            vel=v.astype(np.float32),
            dmg=dmg, gravity=0.0, owner="blaze",
        ))

    def spawn_witch_potion(self, origin, target, dmg: int = 4) -> None:
        d = np.array(target, dtype=np.float32) - np.array(
            origin, dtype=np.float32)
        n = float(np.linalg.norm(d))
        if n < 1e-6:
            return
        v = (d / n) * 6.0
        self.projectiles.append(Projectile(
            pos=np.array(origin, dtype=np.float32),
            vel=v.astype(np.float32),
            dmg=dmg, gravity=9.0, owner="witch",
        ))

    def tick(self, dt: float, world_get=None) -> None:
        for p in self.projectiles:
            p.update(dt, world_get=world_get)
        self.projectiles = [p for p in self.projectiles if not p.dead]

    def iter_alive(self):
        for p in self.projectiles:
            if not p.dead:
                yield p
