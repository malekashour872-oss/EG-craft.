# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Finite-state-machine AI per entity.

Spec ref: §9.3 — Idle/wander, passive flee, wolf chase, hostile chase
+ attack, ranged hostiles keep distance, creeper fuse/explode,
shadow teleport, flying hover, fish flops.
"""
from __future__ import annotations

import math
import random
from typing import Callable

import numpy as np


def _dist2d(a: np.ndarray, b: np.ndarray) -> float:
    dx = float(a[0] - b[0])
    dz = float(a[2] - b[2])
    return math.sqrt(dx * dx + dz * dz)


def _vec_to(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    d = b - a
    n = float(np.linalg.norm(d))
    if n < 1e-6:
        return np.zeros(3, dtype=np.float32)
    return (d / n).astype(np.float32)


class EntityAI:
    """Per-entity AI tick."""

    def __init__(self, rng_seed: int = 0) -> None:
        self.rng = random.Random(rng_seed)

    def tick(self, entity, dt: float, player_pos: np.ndarray,
             world_get: Callable[[int, int, int], int],
             spawn_others: Callable = None) -> None:
        """Advance one AI tick."""
        if entity.dead:
            return
        # Hurt flash decay
        if entity.hurt_flash > 0:
            entity.hurt_flash = max(0.0, entity.hurt_flash - dt)
        # Cooldowns
        if entity.attack_cooldown > 0:
            entity.attack_cooldown -= dt
        if entity.state_timer > 0:
            entity.state_timer -= dt

        # State transitions
        if entity.hostile:
            self._tick_hostile(entity, dt, player_pos, world_get)
        else:
            self._tick_passive(entity, dt, player_pos, world_get)

        # Walk animation phase
        h_speed = math.sqrt(float(entity.vel[0]) ** 2
                              + float(entity.vel[2]) ** 2)
        entity.walk_phase += h_speed * dt * 3.0 / max(0.1, entity.scale)

    def _tick_passive(self, entity, dt, player_pos, world_get) -> None:
        if entity.state == "idle":
            if entity.state_timer <= 0:
                entity.state = "wander"
                entity.state_timer = self.rng.uniform(2, 5)
                target = entity.pos + np.array(
                    [self.rng.uniform(-8, 8), 0,
                     self.rng.uniform(-8, 8)], dtype=np.float32)
                entity._wander_target = target
            return
        if entity.state == "wander":
            if hasattr(entity, "_wander_target"):
                d = _vec_to(entity.pos, entity._wander_target)
                entity.vel[0] = d[0] * entity.speed
                entity.vel[2] = d[2] * entity.speed
                if _dist2d(entity.pos, entity._wander_target) < 0.5 \
                        or entity.state_timer <= 0:
                    entity.state = "idle"
                    entity.state_timer = self.rng.uniform(1, 3)
                    entity.vel[0] = 0
                    entity.vel[2] = 0
            else:
                entity.state = "idle"
        if entity.state == "flee":
            # Flee from player
            d = _vec_to(player_pos, entity.pos)
            entity.vel[0] = d[0] * entity.speed * 1.4
            entity.vel[2] = d[2] * entity.speed * 1.4
            if entity.state_timer <= 0:
                entity.state = "idle"
                entity.state_timer = self.rng.uniform(1, 3)

    def _tick_hostile(self, entity, dt, player_pos, world_get) -> None:
        d = _dist2d(entity.pos, player_pos)
        if entity.id == "creeper":
            self._tick_creeper(entity, dt, player_pos, d)
            return
        if entity.id == "shadow":
            self._tick_shadow(entity, dt, player_pos, d)
            return
        if entity.archetype == "floating":
            self._tick_floating(entity, dt, player_pos, d)
            return
        if entity.archetype == "fish":
            self._tick_fish(entity, dt, world_get)
            return
        # Standard melee / ranged hostile
        if d < 16:
            entity.state = "chase"
            v = _vec_to(entity.pos, player_pos)
            entity.vel[0] = v[0] * entity.speed
            entity.vel[2] = v[2] * entity.speed
            # face the player
            entity.yaw = math.atan2(-v[0], -v[2])
            # attack
            if d < 1.6 and entity.attack_cooldown <= 0:
                entity.state = "attack"
                entity.attack_cooldown = 1.0
                # actual damage is applied by the game loop
        else:
            entity.state = "idle"
            entity.vel[0] = 0
            entity.vel[2] = 0

    def _tick_creeper(self, entity, dt, player_pos, d) -> None:
        if d < 2.5:
            entity.state = "fuse"
            entity.state_timer = 1.5
        if entity.state == "fuse":
            if d > 5:
                entity.state = "chase"
                entity.state_timer = 0
            elif entity.state_timer <= 0:
                entity.state = "explode"
        else:
            v = _vec_to(entity.pos, player_pos)
            entity.vel[0] = v[0] * entity.speed
            entity.vel[2] = v[2] * entity.speed

    def _tick_shadow(self, entity, dt, player_pos, d) -> None:
        if d > 6 and entity.state_timer <= 0:
            # teleport behind player
            angle = self.rng.uniform(0, 2 * math.pi)
            offset = np.array([math.sin(angle) * 2,
                              0, math.cos(angle) * 2],
                             dtype=np.float32)
            target = player_pos - offset
            # Check if target is air above solid
            if (world_get(int(target[0]), int(target[1]) + 1, int(target[2])) == 0
                    and world_get(int(target[0]), int(target[1]), int(target[2])) != 0):
                entity.pos[:] = target
            entity.state_timer = 4.0
        # Always chase
        v = _vec_to(entity.pos, player_pos)
        entity.vel[0] = v[0] * entity.speed
        entity.vel[2] = v[2] * entity.speed

    def _tick_floating(self, entity, dt, player_pos, d) -> None:
        # hover + approach
        target_y = float(player_pos[1]) + 2.0 + math.sin(
            float(entity.walk_phase) * 0.5) * 0.5
        entity.vel[1] = (target_y - float(entity.pos[1])) * 0.5
        if d < 16:
            v = _vec_to(entity.pos, player_pos)
            entity.vel[0] = v[0] * entity.speed
            entity.vel[2] = v[2] * entity.speed

    def _tick_fish(self, entity, dt, world_get) -> None:
        # constrained to water
        bid = world_get(int(entity.pos[0]), int(entity.pos[1]),
                        int(entity.pos[2]))
        if bid != 11:  # not water
            entity.vel[1] -= 24.0 * dt
            entity.hurt_flash = 0.1
        else:
            entity.vel[1] = 0
