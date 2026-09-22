# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Hybrid genetics: pre-generate all 990 unordered pairs (45 × 44 / 2)
= 1035 registered species.

Spec ref: §9.1 — Pair stats are deterministic: rng =
default_rng(hash(pair_id)) (stable hash, A-11); hybrid.name and stats
are computed with the §10 formulas; hostile = father.hostile. Hybrid
IDs: "H{a}_{b}" with a < b by base index (father = a, mother = b).

§10.2 — Child genetics:
- shape: a.archetype
- scale: (a.scale + b.scale) / 2 × U(0.9, 1.1), clamped to [0.4, 2.5]
- hp: round((a.hp + b.hp) / 2 × U(0.95, 1.05))
- speed: same formula as hp
- dmg: round(avg of NONZERO parent dmgs); 0 if both are 0
- body: per channel round(mix(a.body, b.body, 0.5)) + randint(-12, 12), clamped to [0, 255]
- accent: same as body
- hostile: a.hostile
- drops: a.drops at 50% amounts

§10.3 — Hybrid Arabic name:
name = first_half(a.ar) + second_half(b.ar), with halves split at
ceil(n/2) / floor(n/2) characters, computed on the raw Arabic
string before shaping. If the result is shorter than 2 characters →
"هجين" + a.ar + b.ar.
"""
from __future__ import annotations

import math
import zlib
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from entities.species import Species, SPECIES, BASE_INDEX


def _stable_hash_int(*args) -> int:
    """Stable hash per A-11 — zlib.crc32 of UTF-8 bytes."""
    s = "|".join(str(a) for a in args).encode("utf-8")
    return zlib.crc32(s)


def make_child_name(a_ar: str, b_ar: str) -> str:
    """Per §10.3: first_half(a) + second_half(b).

    Halves split at ceil(n/2) for a, floor(m/2) for b."""
    n = len(a_ar)
    m = len(b_ar)
    first_half = a_ar[:math.ceil(n / 2)]
    second_half = b_ar[max(0, m - math.floor(m / 2)):]
    name = first_half + second_half
    if len(name) < 2:
        name = "هجين" + a_ar + b_ar
    return name


def _avg_nonzero_dmg(a_dmg, b_dmg) -> object:
    """Round average of nonzero parent dmgs; 0 if both are 0."""
    def to_int(d):
        if isinstance(d, (int, float)):
            return int(d) if not isinstance(d, str) else 0
        return 0
    av = to_int(a_dmg)
    bv = to_int(b_dmg)
    if av == 0 and bv == 0:
        return 0
    if av == 0:
        return bv
    if bv == 0:
        return av
    return round((av + bv) / 2)


def _mix_color(a: tuple, b: tuple, rng: np.random.Generator) -> tuple[int, int, int]:
    """Per channel: round(mix(a, b, 0.5)) + randint(-12, 12), clamped [0,255]."""
    out = []
    for i in range(3):
        v = round(a[i] * 0.5 + b[i] * 0.5) + int(rng.integers(-12, 13))
        out.append(max(0, min(255, v)))
    return tuple(out)  # type: ignore


def _scale_drops(drops: list) -> list:
    """a.drops at 50% amounts."""
    out = []
    for item_id, (lo, hi) in drops:
        new_lo = max(0, int(lo * 0.5))
        new_hi = max(0, int(hi * 0.5))
        out.append((item_id, (new_lo, new_hi)))
    return out


@dataclass
class HybridSpecies:
    id: str
    name: str
    parent_a: str
    parent_b: str
    archetype: str
    scale: float
    hp: int
    speed: float
    dmg: object
    body: tuple[int, int, int]
    accent: tuple[int, int, int]
    hostile: bool
    drops: list = field(default_factory=list)
    is_hybrid: bool = True

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name,
                "parent_a": self.parent_a, "parent_b": self.parent_b,
                "archetype": self.archetype,
                "scale": self.scale, "hp": self.hp,
                "speed": self.speed, "dmg": str(self.dmg),
                "body": list(self.body), "accent": list(self.accent),
                "hostile": self.hostile,
                "drops": [(i, list(r)) for i, r in self.drops]}


def hybrid_pair(a: Species, b: Species, seed: int = 0) -> HybridSpecies:
    """Compute the hybrid species for an unordered (a, b) pair.

    Per §9.1: father = a = picked first, mother = b.
    """
    # Order by base index (a < b)
    ai = BASE_INDEX.index(a.id)
    bi = BASE_INDEX.index(b.id)
    if ai > bi:
        a, b = b, a
        ai, bi = bi, ai
    # Deterministic RNG
    pair_seed = _stable_hash_int(seed, ai, bi)
    rng = np.random.default_rng(pair_seed)

    # Scale
    scale = (a.scale + b.scale) / 2 * float(rng.uniform(0.9, 1.1))
    scale = max(0.4, min(2.5, scale))
    # HP
    hp = round((a.hp + b.hp) / 2 * float(rng.uniform(0.95, 1.05)))
    # Speed
    speed = round((a.speed + b.speed) / 2 * float(rng.uniform(0.95, 1.05)), 2)
    # Dmg
    dmg = _avg_nonzero_dmg(a.dmg, b.dmg)
    # Body & accent
    body = _mix_color(a.body, b.body, rng)
    accent = _mix_color(a.accent, b.accent, rng)
    # Name
    name = make_child_name(a.ar, b.ar)
    # Drops
    drops = _scale_drops(a.drops)
    hid = f"H{ai}_{bi}"
    return HybridSpecies(
        id=hid, name=name, parent_a=a.id, parent_b=b.id,
        archetype=a.archetype, scale=float(scale), hp=int(hp),
        speed=float(speed), dmg=dmg, body=body, accent=accent,
        hostile=a.hostile, drops=drops,
    )


def generate_all_hybrids(seed: int = 0) -> dict[str, HybridSpecies]:
    """Generate all 990 unordered pairs (45 × 44 / 2)."""
    out: dict[str, HybridSpecies] = {}
    for i in range(45):
        for j in range(i + 1, 45):
            a = SPECIES[BASE_INDEX[i]]
            b = SPECIES[BASE_INDEX[j]]
            h = hybrid_pair(a, b, seed=seed)
            out[h.id] = h
    return out
