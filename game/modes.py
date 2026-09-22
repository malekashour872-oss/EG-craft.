# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Game modes + survival systems.

Spec ref: §11 — Survival: hp = 20, hunger = 20; fall / drown / void
damage ON; finite items; mining times ON. Creative: fly; infinite
stacks; instant break; zero damage; all-blocks palette.
§11.2 survival: Hunger: -1 per 45 s (walking) / 20 s (sprinting).
Regeneration: hunger ≥ 18 → +1 hp per 4 s. Starvation: hunger == 0
→ -1 hp per 4 s, floored at 1 (no hunger death). Eating: RMB with
food selected (raw_meat +3, cooked_meat +8, carrot +3); 1.2 s eat
animation + sound. Damage feedback: red vignette alpha 0.35 for 0.3 s
+ heart shake. Death: death screen (§14); the entire inventory
drops as item entities at the death point; respawn at world spawn
(0, heightmap + 2, 0) with hp and hunger = 20.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from world.blocks import ITEM_RAW_MEAT, ITEM_COOKED_MEAT, ITEM_CARROT

MAX_HP = 20
MAX_HUNGER = 20

# Hunger drain intervals
WALK_HUNGER_INTERVAL = 45.0
SPRINT_HUNGER_INTERVAL = 20.0

# Regen / starvation
REGEN_INTERVAL = 4.0
STARVE_INTERVAL = 4.0
STARVE_FLOOR = 1

# Food values
FOOD_HUNGER_RESTORE = {
    ITEM_RAW_MEAT:    3,
    ITEM_COOKED_MEAT: 8,
    ITEM_CARROT:      3,
}

# Death cause keys (per §3.4)
DEATH_FALL = "fall"
DEATH_DROWN = "drown"
DEATH_EXPLOSION = "explosion"
DEATH_MOB = "mob"
DEATH_HUNGER = "hunger"  # per A-14: string kept; no code path produces
DEATH_VOID = "void"

# Damage feedback
DAMAGE_VIGNETTE_ALPHA = 0.35
DAMAGE_VIGNETTE_DURATION = 0.3


@dataclass
class SurvivalStats:
    hp: int = MAX_HP
    hunger: int = MAX_HUNGER
    walk_hunger_timer: float = 0.0
    sprint_hunger_timer: float = 0.0
    regen_timer: float = 0.0
    starve_timer: float = 0.0
    eat_timer: float = 0.0
    damage_vignette: float = 0.0
    dead: bool = False
    death_cause: Optional[str] = None


class Survival:
    """Per-player survival systems."""

    def __init__(self) -> None:
        self.stats = SurvivalStats()

    def reset(self) -> None:
        self.stats = SurvivalStats()

    def take_damage(self, dmg: int, cause: str) -> None:
        if self.stats.dead:
            return
        self.stats.hp -= dmg
        self.stats.damage_vignette = DAMAGE_VIGNETTE_DURATION
        if self.stats.hp <= 0:
            self.stats.hp = 0
            self.stats.dead = True
            self.stats.death_cause = cause

    def heal(self, amount: int) -> None:
        if self.stats.dead:
            return
        self.stats.hp = min(MAX_HP, self.stats.hp + amount)

    def eat(self, item_id: int) -> bool:
        if item_id not in FOOD_HUNGER_RESTORE:
            return False
        amount = FOOD_HUNGER_RESTORE[item_id]
        self.stats.hunger = min(MAX_HUNGER, self.stats.hunger + amount)
        self.stats.eat_timer = 1.2
        return True

    def tick(self, dt: float, sprinting: bool = False) -> None:
        s = self.stats
        if s.dead:
            return
        # Hunger drain
        if sprinting:
            s.sprint_hunger_timer += dt
            if s.sprint_hunger_timer >= SPRINT_HUNGER_INTERVAL:
                s.sprint_hunger_timer -= SPRINT_HUNGER_INTERVAL
                s.hunger = max(0, s.hunger - 1)
        else:
            s.walk_hunger_timer += dt
            if s.walk_hunger_timer >= WALK_HUNGER_INTERVAL:
                s.walk_hunger_timer -= WALK_HUNGER_INTERVAL
                s.hunger = max(0, s.hunger - 1)
        # Regen
        if s.hunger >= 18 and s.hp < MAX_HP:
            s.regen_timer += dt
            if s.regen_timer >= REGEN_INTERVAL:
                s.regen_timer -= REGEN_INTERVAL
                self.heal(1)
        # Starvation (floor 1, no death)
        if s.hunger == 0 and s.hp > STARVE_FLOOR:
            s.starve_timer += dt
            if s.starve_timer >= STARVE_INTERVAL:
                s.starve_timer -= STARVE_INTERVAL
                s.hp = max(STARVE_FLOOR, s.hp - 1)
        # Eat animation timer
        if s.eat_timer > 0:
            s.eat_timer = max(0.0, s.eat_timer - dt)
        # Damage vignette decay
        if s.damage_vignette > 0:
            s.damage_vignette = max(0.0, s.damage_vignette - dt)


# ── Mode definitions ─────────────────────────────────────
class GameMode:
    """Game-mode policy."""

    SURVIVAL = "survival"
    CREATIVE = "creative"

    @staticmethod
    def is_creative(mode: str) -> bool:
        return mode == GameMode.CREATIVE

    @staticmethod
    def takes_damage(mode: str) -> bool:
        return mode == GameMode.SURVIVAL

    @staticmethod
    def has_finite_items(mode: str) -> bool:
        return mode == GameMode.SURVIVAL

    @staticmethod
    def instant_break(mode: str) -> bool:
        return mode == GameMode.CREATIVE

    @staticmethod
    def can_fly(mode: str) -> bool:
        return mode == GameMode.CREATIVE
