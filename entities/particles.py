# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Particle pool.

Spec ref: §9.8 — Pool of 256 coloured mini-cubes (0.08); gravity;
life 0.6 s; one shared white VAO tinted per particle via a u_model
colour variant of PROGRAM_LINES (fill quads via PROGRAM_MAIN white
texture).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

PARTICLE_POOL_SIZE = 256
PARTICLE_SIZE = 0.08
PARTICLE_LIFE = 0.6


@dataclass
class Particle:
    pos: np.ndarray
    vel: np.ndarray
    color: tuple[int, int, int]
    life: float


class ParticleSystem:
    """Fixed-size pool of mini-cube particles."""

    def __init__(self) -> None:
        self.particles: list[Particle] = []
        for _ in range(PARTICLE_POOL_SIZE):
            self.particles.append(Particle(
                pos=np.zeros(3, dtype=np.float32),
                vel=np.zeros(3, dtype=np.float32),
                color=(255, 255, 255),
                life=0.0,
            ))
        self.cursor = 0

    def emit(self, pos, color, count: int = 8,
             speed: float = 3.0) -> None:
        """Emit ``count`` particles from ``pos``."""
        rng = np.random.default_rng()
        for _ in range(count):
            p = self.particles[self.cursor]
            p.pos[:] = pos
            theta = float(rng.uniform(0, 2 * math.pi))
            phi = float(rng.uniform(0, math.pi))
            s = float(rng.uniform(0.3, 1.0)) * speed
            p.vel[0] = s * math.sin(phi) * math.cos(theta)
            p.vel[1] = s * math.cos(phi) + 2.0
            p.vel[2] = s * math.sin(phi) * math.sin(theta)
            p.color = color
            p.life = PARTICLE_LIFE
            self.cursor = (self.cursor + 1) % PARTICLE_POOL_SIZE

    def update(self, dt: float, world_get=None) -> None:
        """Advance all particles one tick."""
        for p in self.particles:
            if p.life <= 0.0:
                continue
            p.life -= dt
            # gravity
            p.vel[1] -= 24.0 * dt
            p.pos += p.vel * dt
            # Floor collision
            if world_get is not None:
                x, y, z = int(math.floor(p.pos[0])), int(math.floor(p.pos[1])), int(math.floor(p.pos[2]))
                if world_get(x, y, z) != 0:
                    p.vel[:] = 0
                    p.life = min(p.life, 0.05)

    def active_count(self) -> int:
        return sum(1 for p in self.particles if p.life > 0)
