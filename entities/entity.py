# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Entity base + body builders (local coordinates).

Spec ref: §9.2 — Archetype parts + animations.
A-15: h = archetype standing height before scale
(quadruped 1.4, biped 1.8, bird 0.6, fish 0.6, blob 0.8,
arachnid 0.6, floating 1.0; ghast 2.5 — overridden in builder).

Walk animation: walkPhase += horizontal_speed × dt × 3.0 / scale;
legs alternate rot.x = sin(phase) × 0.7. Hurt flash 0.15 s:
lerp(palette → (255, 60, 60)). Mesh: one VAO per entity type +
palette, cached; per frame only u_model is set.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class Entity:
    id: str                 # species id (or hybrid id)
    ar_name: str            # Arabic name
    archetype: str          # quadruped | biped | bird | fish | blob | arachnid | floating
    hp: int
    speed: float
    dmg: object             # 0 | int | "rangedN" | "explode"
    scale: float
    body: tuple[int, int, int]
    accent: tuple[int, int, int]
    hostile: bool = False
    drops: list = field(default_factory=list)
    pos: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    vel: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    yaw: float = 0.0
    walk_phase: float = 0.0
    state: str = "idle"     # idle | wander | flee | chase | attack | fuse | explode
    state_timer: float = 0.0
    attack_cooldown: float = 0.0
    is_hybrid: bool = False
    parents: Optional[tuple] = None
    hurt_flash: float = 0.0
    dead: bool = False

    @property
    def height(self) -> float:
        """Standing height (archetype h × scale)."""
        from entities.species import ARCHETYPE_HEIGHTS
        h = ARCHETYPE_HEIGHTS.get(self.archetype, 1.0)
        if self.archetype == "floating" and self.id == "ghast":
            h = 2.5
        return h * self.scale


def make_entity_from_species(species, pos: np.ndarray | None = None) -> Entity:
    """Build an Entity from a Species or HybridSpecies."""
    pos_arr = (np.array(pos, dtype=np.float32) if pos is not None
               else np.zeros(3, dtype=np.float32))
    is_hybrid = getattr(species, "is_hybrid", False)
    parents = None
    if is_hybrid:
        parents = (species.parent_a, species.parent_b)
    return Entity(
        id=species.id,
        ar_name=species.name if is_hybrid else species.ar,
        archetype=species.archetype,
        hp=int(species.hp),
        speed=float(species.speed),
        dmg=species.dmg,
        scale=float(species.scale),
        body=tuple(species.body),
        accent=tuple(species.accent),
        hostile=bool(species.hostile),
        drops=list(species.drops),
        pos=pos_arr,
        is_hybrid=is_hybrid,
        parents=parents,
    )


# ── Body builders (local coordinates, unit = blocks) ─────
# Each builder returns a list of (box_dims, offset, accent_bool) tuples
# where box_dims is (w, h, d) and offset is (x, y, z).

def build_quadruped(scale: float) -> list:
    h = 1.4 * scale
    return [
        ((0.9, 0.6, 1.4), (0, 0.55 * h, 0), False),    # body
        ((0.5, 0.5, 0.5), (0, 0.7 * h, 0.6), False),  # head
        # 4 legs at corners
        ((0.2, 0.5 * h, 0.2), (-0.3, 0.25 * h, 0.5), False),
        ((0.2, 0.5 * h, 0.2), (0.3, 0.25 * h, 0.5), False),
        ((0.2, 0.5 * h, 0.2), (-0.3, 0.25 * h, -0.5), False),
        ((0.2, 0.5 * h, 0.2), (0.3, 0.25 * h, -0.5), False),
    ]


def build_biped(scale: float) -> list:
    h = 1.8 * scale
    return [
        ((0.25, 0.5 * h, 0.25), (-0.15, 0.25 * h, 0), False),  # left leg
        ((0.25, 0.5 * h, 0.25), (0.15, 0.25 * h, 0), False),   # right leg
        ((0.6, 0.45 * h, 0.32), (0, 0.95 * h, 0), False),       # body
        ((0.2, 0.5 * h, 0.2), (-0.4, 0.95 * h, 0), False),     # left arm
        ((0.2, 0.5 * h, 0.2), (0.4, 0.95 * h, 0), False),      # right arm
        ((0.5, 0.5, 0.5), (0, 1.5 * h, 0), False),             # head
    ]


def build_bird(scale: float) -> list:
    h = 0.6 * scale
    return [
        ((0.4, 0.4, 0.6), (0, 0.5 * h, 0), False),    # body
        ((0.3, 0.3, 0.3), (0, 0.85 * h, 0.25), False),  # head
        ((0.1, 0.1, 0.15), (0, 0.85 * h, 0.4), True),  # beak accent
        ((0.06, 0.35, 0.5), (-0.3, 0.5 * h, 0), True),  # left wing
        ((0.06, 0.35, 0.5), (0.3, 0.5 * h, 0), True),   # right wing
    ]


def build_fish(scale: float) -> list:
    return [
        ((0.3, 0.4, 0.8), (0, 0.2, 0), False),
        ((0.08, 0.3, 0.3), (0, 0.2, -0.5), True),  # tail accent
    ]


def build_blob(scale: float) -> list:
    return [
        ((0.8, 0.8, 0.8), (0, 0.4, 0), False),
    ]


def build_arachnid(scale: float) -> list:
    h = 0.6 * scale
    parts = [
        ((0.8, 0.4, 0.9), (0, 0.5 * h, 0), False),    # body
        ((0.4, 0.4, 0.4), (0, 0.5 * h, 0.6), False),  # head
    ]
    # 8 legs angled ±35°
    for i in range(4):
        x_off = 0.4 if i % 2 == 0 else -0.4
        z_off = 0.3 - 0.2 * i
        parts.append(((0.08, 0.5 * h, 0.08),
                       (x_off, 0.4 * h, z_off), False))
        parts.append(((0.08, 0.5 * h, 0.08),
                       (-x_off, 0.4 * h, z_off), False))
    return parts


def build_floating(scale: float, is_ghast: bool = False) -> list:
    s = 2.0 if is_ghast else 0.9
    return [
        ((s, s, s), (0, 0.5 * s, 0), False),  # body
    ] + [((0.08, 0.6, 0.08),
           (-0.3 + 0.2 * i, -0.3, 0), True) for i in range(4)]  # rods


BUILDERS = {
    "quadruped": build_quadruped,
    "biped":     build_biped,
    "bird":      build_bird,
    "fish":      build_fish,
    "blob":      build_blob,
    "arachnid":  build_arachnid,
    "floating":  build_floating,
}


def build_body(archetype: str, scale: float,
               species_id: str = "") -> list:
    if archetype == "floating" and species_id == "ghast":
        return build_floating(scale, is_ghast=True)
    return BUILDERS.get(archetype, build_biped)(scale)
