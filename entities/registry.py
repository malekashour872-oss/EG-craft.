# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Species registry — 45 base + 990 hybrids = 1035 entries.

Spec ref: §9.1 — Registry pre-generation (Task 8): 45 base + all
990 unordered pairs (45 × 44 / 2) = 1035 registered (≥ 1000 ✓).
"""
from __future__ import annotations

from typing import Optional

from entities.species import (Species, SPECIES, BASE_INDEX,
                              PASSIVE, HOSTILE,
                              EXTENDED_SPECIES, EXTENDED_INDEX,
                              ALL_BASE, VILLAGERS, EXTRA_PASSIVE,
                              GOLEMS, BOSSES, EXTRA_AMBIENT)
from entities.hybrid import HybridSpecies, generate_all_hybrids


class Registry:
    """Singleton-style registry of all species."""

    def __init__(self, seed: int = 0) -> None:
        self.seed = int(seed)
        # §9.1 base 45 (spec-compliant) + commercial expansion
        self.base: dict[str, Species] = dict(SPECIES)
        self.expanded: dict[str, Species] = {s.id: s for s in
                                             (VILLAGERS + EXTRA_PASSIVE
                                              + GOLEMS + BOSSES + EXTRA_AMBIENT)}
        self.hybrids: dict[str, HybridSpecies] = generate_all_hybrids(seed=seed)
        self._all: dict[str, object] = {}
        self._all.update(self.base)
        self._all.update(self.expanded)
        self._all.update(self.hybrids)

    def __len__(self) -> int:
        return len(self._all)

    def __contains__(self, id: str) -> bool:
        return id in self._all

    def get(self, id: str) -> Optional[object]:
        return self._all.get(id)

    def all_ids(self) -> list[str]:
        return list(self._all.keys())

    def iter_all(self):
        for id, sp in self._all.items():
            yield id, sp

    def filter(self, hostile: Optional[bool] = None,
               is_hybrid: Optional[bool] = None) -> list:
        out = []
        for sp in self._all.values():
            if hostile is not None and getattr(sp, "hostile", False) != hostile:
                continue
            if is_hybrid is not None and getattr(sp, "is_hybrid", False) != is_hybrid:
                continue
            out.append(sp)
        return out


# Module-level singleton — seeded with the default world seed
REGISTRY: Registry = Registry(seed=0)


def reseed(seed: int) -> Registry:
    """Rebuild the registry with a new seed."""
    global REGISTRY
    REGISTRY = Registry(seed=seed)
    return REGISTRY
