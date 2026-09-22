# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Species catalogue (45 base species per §9.1).

A-6: rows are authoritative — id is the English name, class =
passive/hostile by group. A-7: drop cells resolved (slime none;
shadow bone 0–1; witch string 0–2; blaze coal 0–1; vindicator
iron_ingot 0–1; pillager arrow 0–2; ravager leather 0–2; phantom
leather 0–1).

A-15: archetype standing height h (recorded here):
  quadruped 1.4, biped 1.8, bird 0.6, fish 0.6, blob 0.8,
  arachnid 0.6, floating 1.0 (ghast 2.5 — overridden in builder).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

ARCHETYPE_HEIGHTS = {
    "quadruped": 1.4,
    "biped":     1.8,
    "bird":      0.6,
    "fish":      0.6,
    "blob":      0.8,
    "arachnid":  0.6,
    "floating":  1.0,
}


@dataclass
class Species:
    id: str               # English id (e.g. "cow")
    ar: str                # Arabic name
    archetype: str         # quadruped | biped | bird | fish | blob | arachnid | floating
    hp: int
    speed: float
    dmg: object           # 0, int (melee), "ranged3", "explode"
    scale: float
    body: tuple[int, int, int]
    accent: tuple[int, int, int]
    drops: list[tuple[int, tuple[int, int]]]  # [(item_id, (min, max)), ...]
    hostile: bool = False
    # Computed at runtime
    height: float = 0.0

    def __post_init__(self) -> None:
        self.height = ARCHETYPE_HEIGHTS.get(self.archetype, 1.0)


# ── Helper to parse drop strings like "raw_meat 1–2" ──
from world.blocks import (
    ITEM_RAW_MEAT, ITEM_LEATHER, ITEM_FEATHER, ITEM_BONE, ITEM_STRING,
    ITEM_GUNPOWDER, ITEM_ARROW, ITEM_COAL, ITEM_IRON_INGOT,
)


def _drop(item_id: int, lo: int, hi: int) -> tuple[int, tuple[int, int]]:
    return (item_id, (lo, hi))


# ─────────────────────────────────────────────────────────────
# Passive (20)
# ─────────────────────────────────────────────────────────────
PASSIVE: list[Species] = [
    Species("cow", "بقرة", "quadruped", 10, 2.0, 0, 1.0, (92,58,42), (230,230,225),
            [_drop(ITEM_RAW_MEAT, 1, 2), _drop(ITEM_LEATHER, 0, 1)]),
    Species("sheep", "خروف", "quadruped", 8, 2.0, 0, 0.9, (230,230,230), (250,235,205),
            [_drop(ITEM_RAW_MEAT, 1, 1)]),
    Species("pig", "خنزير", "quadruped", 10, 2.2, 0, 0.9, (240,150,150), (255,200,200),
            [_drop(ITEM_RAW_MEAT, 1, 2)]),
    Species("chicken", "دجاجة", "bird", 4, 1.8, 0, 0.6, (240,240,240), (255,60,60),
            [_drop(ITEM_FEATHER, 0, 2), _drop(ITEM_RAW_MEAT, 1, 1)]),
    Species("rabbit", "أرنب", "quadruped", 3, 3.0, 0, 0.5, (180,140,100), (255,255,255),
            [_drop(ITEM_RAW_MEAT, 0, 1)]),
    Species("horse", "حصان", "quadruped", 22, 4.0, 0, 1.3, (120,80,50), (40,30,25),
            [_drop(ITEM_LEATHER, 0, 2)]),
    Species("donkey", "حمار", "quadruped", 20, 3.5, 0, 1.2, (90,70,55), (30,25,20),
            [_drop(ITEM_LEATHER, 0, 1)]),
    Species("camel", "جمل", "quadruped", 25, 3.5, 0, 1.5, (200,170,120), (150,110,70),
            [_drop(ITEM_LEATHER, 0, 2)]),
    Species("goat", "ماعز", "quadruped", 10, 2.6, 0, 0.8, (200,200,190), (90,80,70),
            [_drop(ITEM_RAW_MEAT, 0, 1)]),
    Species("duck", "بطة", "bird", 4, 1.8, 0, 0.6, (220,220,230), (90,150,220),
            [_drop(ITEM_FEATHER, 0, 2)]),
    Species("fish", "سمكة", "fish", 3, 1.5, 0, 0.5, (80,160,220), (220,220,220),
            [_drop(ITEM_RAW_MEAT, 0, 1)]),
    Species("butterfly", "فراشة", "bird", 1, 1.2, 0, 0.3, (255,180,60), (60,60,60), []),
    Species("bee", "نحلة", "bird", 10, 2.5, 0, 0.35, (250,200,50), (50,40,30), []),
    Species("fox", "ثعلب", "quadruped", 10, 3.2, 0, 0.7, (220,120,50), (255,255,255),
            [_drop(ITEM_RAW_MEAT, 0, 1)]),
    Species("wolf", "ذئب", "quadruped", 8, 3.5, 3, 0.8, (180,180,180), (50,50,50),
            [], hostile=False),  # neutral
    Species("turtle", "سلحفاة", "quadruped", 15, 1.0, 0, 0.6, (70,140,90), (220,200,140),
            [_drop(ITEM_RAW_MEAT, 0, 1)]),
    Species("deer", "غزال", "quadruped", 10, 3.0, 0, 1.1, (150,100,60), (240,230,210),
            [_drop(ITEM_RAW_MEAT, 0, 2)]),
    Species("llama", "لامة", "quadruped", 20, 2.5, 0, 1.2, (230,220,200), (120,90,60),
            [_drop(ITEM_LEATHER, 0, 1)]),
    Species("parrot", "ببغاء", "bird", 6, 2.5, 0, 0.5, (50,200,80), (220,50,50),
            [_drop(ITEM_FEATHER, 1, 2)]),
    Species("cat", "قطة", "quadruped", 10, 3.0, 0, 0.6, (200,160,100), (255,255,255), []),
]


# ─────────────────────────────────────────────────────────────
# Hostile (25)
# ─────────────────────────────────────────────────────────────
HOSTILE: list[Species] = [
    Species("zombie", "زومبي", "biped", 20, 2.3, 3, 1.0, (80,140,90), (60,90,170),
            [_drop(ITEM_IRON_INGOT, 0, 1)], hostile=True),  # 10% iron_ingot
    Species("skeleton", "هيكل عظمي", "biped", 20, 2.2, "ranged3", 0.9,
            (220,220,210), (150,150,140),
            [_drop(ITEM_BONE, 0, 2)], hostile=True),
    Species("spider", "عنكبوت", "arachnid", 16, 3.0, 2, 1.0, (50,40,40), (180,30,30),
            [_drop(ITEM_STRING, 0, 2)], hostile=True),
    Species("creeper", "كريبر", "biped", 20, 2.0, "explode", 1.0,
            (80,200,80), (30,90,30),
            [_drop(ITEM_GUNPOWDER, 0, 2)], hostile=True),
    Species("slime", "سلايم", "blob", 8, 1.8, 1, 1.0, (90,200,90), (60,160,60),
            [], hostile=True),  # none per A-7
    Species("shadow", "ظل", "biped", 40, 3.5, 5, 1.1, (20,20,30), (180,60,220),
            [_drop(ITEM_BONE, 0, 1)], hostile=True),
    Species("witch", "ساحرة", "biped", 26, 2.2, "ranged4", 1.0,
            (150,80,160), (60,40,60),
            [_drop(ITEM_STRING, 0, 2)], hostile=True),
    Species("cave_spider", "عنكبوت الكهوف", "arachnid", 12, 3.4, 2, 0.6,
            (30,50,60), (150,30,30),
            [_drop(ITEM_STRING, 0, 1)], hostile=True),
    Species("drowned", "غريق", "biped", 20, 2.0, 3, 1.0, (60,120,130), (90,170,180),
            [_drop(ITEM_IRON_INGOT, 0, 1)], hostile=True),
    Species("husk", "جافة", "biped", 20, 2.1, 3, 1.0, (150,120,80), (110,90,60),
            [_drop(ITEM_IRON_INGOT, 0, 1)], hostile=True),
    Species("stray", "تائة", "biped", 20, 2.2, "ranged3", 0.9,
            (210,220,230), (120,140,160),
            [_drop(ITEM_BONE, 0, 2)], hostile=True),
    Species("silverfish", "سمكة فضية", "arachnid", 8, 3.5, 1, 0.35,
            (150,150,160), (100,100,110), [], hostile=True),
    Species("blaze", "لهيب", "floating", 20, 2.5, "ranged3", 0.9,
            (250,180,40), (255,240,150),
            [_drop(ITEM_COAL, 0, 1)], hostile=True),
    Species("ghast", "شبح", "floating", 10, 1.5, "ranged3", 2.5,
            (240,240,240), (200,200,210),
            [_drop(ITEM_GUNPOWDER, 0, 1)], hostile=True),
    Species("magma_cube", "مكعب ملتهب", "blob", 16, 2.4, 3, 1.0,
            (200,60,20), (120,30,10), [], hostile=True),
    Species("zombie_villager", "زومبي قروي", "biped", 20, 2.2, 3, 1.0,
            (80,140,90), (150,110,70),
            [_drop(ITEM_IRON_INGOT, 0, 1)], hostile=True),
    Species("vindicator", "منتقم", "biped", 24, 2.8, 6, 1.05,
            (90,110,160), (120,120,140),
            [_drop(ITEM_IRON_INGOT, 0, 1)], hostile=True),
    Species("evoker", "استدعائي", "biped", 20, 2.0, 5, 1.0,
            (180,190,200), (60,60,90), [], hostile=True),
    Species("pillager", "لص", "biped", 24, 2.5, "ranged4", 1.0,
            (90,110,150), (70,80,90),
            [_drop(ITEM_ARROW, 0, 2)], hostile=True),
    Species("ravager", "مدمرة", "quadruped", 100, 2.5, 9, 1.8,
            (80,70,70), (50,40,40),
            [_drop(ITEM_LEATHER, 0, 2)], hostile=True),
    Species("guardian", "حارس", "fish", 30, 2.2, 4, 1.0,
            (80,160,140), (200,120,180), [], hostile=True),
    Species("wither_skeleton", "هيكل نار", "biped", 20, 2.6, 7, 1.2,
            (40,35,35), (20,15,15),
            [_drop(ITEM_COAL, 0, 1)], hostile=True),
    Species("piglin", "خنزيري", "biped", 16, 2.6, 4, 1.0,
            (230,150,150), (120,80,50), [], hostile=True),
    Species("phantom", "طيف", "bird", 20, 2.8, 4, 1.2,
            (60,80,140), (30,40,80),
            [_drop(ITEM_LEATHER, 0, 1)], hostile=True),
    Species("endermite", "عثة الظل", "arachnid", 8, 3.2, 1, 0.35,
            (30,25,40), (150,60,180), [], hostile=True),
]


# Index all 45 species
SPECIES: dict[str, Species] = {s.id: s for s in (PASSIVE + HOSTILE)}
BASE_INDEX: list[str] = [s.id for s in (PASSIVE + HOSTILE)]


# ─────────────────────────────────────────────────────────────
# Commercial expansion — new species (extended catalogue).
# Extends the §9.1 45-species table; the registry assertion is
# ``len(REGISTRY) >= 1035`` so adding more is permitted. Documented
# in DECISIONS.md → L-2.
# ─────────────────────────────────────────────────────────────
# Villagers (passive, humanoid) — 6 professions
VILLAGERS: list[Species] = [
    Species("villager_farmer", "قروي فلاح", "biped", 20, 0.3, 0, 1.0,
            (140, 110, 70), (90, 60, 30), []),
    Species("villager_librarian", "قروي أمين مكتبة", "biped", 20, 0.3, 0, 1.0,
            (180, 140, 100), (60, 50, 30), []),
    Species("villager_blacksmith", "قروي حداد", "biped", 20, 0.3, 0, 1.0,
            (100, 80, 60), (40, 30, 20), []),
    Species("villager_butcher", "قروي جزّار", "biped", 20, 0.3, 0, 1.0,
            (160, 90, 90), (90, 50, 50), []),
    Species("villager_priest", "قروي كاهن", "biped", 20, 0.3, 0, 1.0,
            (220, 220, 220), (160, 60, 220), []),
    Species("villager_nitwit", "قروي غبي", "biped", 20, 0.3, 0, 1.0,
            (70, 70, 70), (40, 40, 40), []),
]

# More passive
EXTRA_PASSIVE: list[Species] = [
    Species("panda", "باندا", "quadruped", 20, 0.3, 0, 1.1,
            (220, 220, 220), (40, 40, 40),
            [_drop(ITEM_BONE, 0, 1)]),
    Species("axolotl", "أكسولوتل", "quadruped", 14, 1.0, 0, 0.4,
            (240, 170, 200), (240, 220, 230), []),
    Species("allay", "آلاي", "bird", 6, 0.8, 0, 0.4,
            (160, 230, 230), (255, 255, 255), []),
    Species("frog", "ضفدع", "quadruped", 4, 0.5, 0, 0.3,
            (90, 180, 90), (50, 100, 50), []),
    Species("tadpole", "شرغوف", "fish", 2, 0.5, 0, 0.2,
            (40, 80, 40), (20, 40, 20), []),
    Species("goat_screaming", "ماعز صارخ", "quadruped", 10, 2.6, 0, 0.8,
            (200, 200, 190), (90, 80, 70),
            [_drop(ITEM_RAW_MEAT, 0, 1)]),
    Species("strider", "ممشٍ", "quadruped", 20, 0.3, 0, 0.9,
            (220, 100, 80), (80, 30, 20), []),
    Species("hoglin", "خنزير الجحيم", "quadruped", 40, 1.4, 4, 1.4,
            (160, 100, 80), (90, 50, 40),
            [_drop(ITEM_RAW_MEAT, 0, 2)], hostile=True),
    Species("piglin_brute", "خنزير وحشي", "biped", 50, 0.3, 8, 1.0,
            (200, 140, 140), (120, 80, 50),
            [_drop(ITEM_IRON_INGOT, 0, 1)], hostile=True),
    Species("warden", "السجّان", "biped", 250, 0.3, 12, 1.2,
            (30, 30, 50), (60, 60, 220), [], hostile=True),
    Species("allay_dup", "آلاي شبحي", "bird", 4, 0.8, 0, 0.3,
            (255, 255, 200), (180, 180, 100), []),
]

# Golems (neutral / friendly)
GOLEMS: list[Species] = [
    Species("iron_golem", "غولم الحديد", "biped", 100, 0.3, 12, 1.8,
            (200, 200, 200), (140, 140, 140),
            [_drop(ITEM_IRON_INGOT, 2, 4), _drop(ITEM_LEATHER, 0, 1)]),
    Species("snow_golem", "غولم الثلج", "biped", 4, 0.3, 0, 0.8,
            (240, 240, 240), (200, 80, 40), []),
    Species("shulker", "شولكر", "blob", 30, 0.3, 0, 0.5,
            (160, 100, 160), (80, 40, 80), []),
]

# Bosses (huge HP, hostile)
BOSSES: list[Species] = [
    Species("ender_dragon", "تنين النهاية", "floating", 200, 1.5, 10, 4.0,
            (40, 40, 40), (20, 20, 20), [], hostile=True),
    Species("wither", "الذبول", "floating", 300, 0.5, 12, 3.0,
            (40, 30, 30), (60, 30, 30), [], hostile=True),
    Species("elder_guardian", "الحارس الأكبر", "fish", 120, 0.5, 6, 2.0,
            (90, 140, 130), (60, 90, 80), [], hostile=True),
]

# Extra ambient
EXTRA_AMBIENT: list[Species] = [
    Species("cod_fish", "سمك القد", "fish", 4, 1.0, 0, 0.4,
            (140, 140, 130), (90, 90, 80),
            [_drop(ITEM_RAW_MEAT, 0, 1)]),
    Species("salmon_fish", "سمك السلمون", "fish", 4, 1.0, 0, 0.4,
            (200, 100, 80), (140, 70, 50),
            [_drop(ITEM_RAW_MEAT, 0, 1)]),
    Species("tropical_fish", "سمك استوائي", "fish", 3, 1.0, 0, 0.3,
            (240, 200, 80), (240, 80, 80), []),
    Species("pufferfish", "سمكة المنتفخة", "fish", 3, 0.5, 0, 0.3,
            (220, 200, 80), (200, 100, 60), []),
]


# Extended species catalogue (45 base + ~25 new = 70+ base)
ALL_BASE = (PASSIVE + HOSTILE + VILLAGERS + EXTRA_PASSIVE
            + GOLEMS + BOSSES + EXTRA_AMBIENT)
EXTENDED_SPECIES: dict[str, Species] = {s.id: s for s in ALL_BASE}
EXTENDED_INDEX: list[str] = [s.id for s in ALL_BASE]


def get_species(id: str) -> Optional[Species]:
    """Look up a species by id; falls back to EXTENDED_SPECIES."""
    return EXTENDED_SPECIES.get(id) or SPECIES.get(id)
