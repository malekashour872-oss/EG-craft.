# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Block entities (furnace, chest).

Spec ref: §8.5 — dict[(x,y,z)] → {type, slots…}. Furnace: input,
fuel, output, progress, burn_left. Chest: 27 slots. Furnaces tick
only while loaded. Block entities are persisted in the save (§15).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from world.blocks import (
    ID_FURNACE, ID_CHEST,
    ITEM_COAL, ID_PLANKS, ID_LOG, ITEM_STICK,
    ITEM_IRON_INGOT, ITEM_GOLD_INGOT, ID_GLASS, ID_SAND,
    ITEM_IRON_ORE, ITEM_GOLD_ORE, ITEM_RAW_MEAT, ITEM_COOKED_MEAT,
)

# local alias (stick is item 101, not a block)
ID_STICK = ITEM_STICK


# Smelting recipes (per §8.4) — 5 s per item
SMELTING_INPUT_TO_OUTPUT = {
    ITEM_IRON_ORE: ITEM_IRON_INGOT,
    ITEM_GOLD_ORE: ITEM_GOLD_INGOT,
    ID_SAND:        ID_GLASS,
    ITEM_RAW_MEAT:  ITEM_COOKED_MEAT,
    ID_LOG:         ITEM_COAL,
}

# Fuel burn times in seconds (per §8.4)
FUEL_BURN_TIME = {
    ITEM_COAL: 40.0,
    ID_PLANKS: 7.5,
    ID_LOG:     7.5,
    ID_STICK:   2.5,
}

SMELT_TIME = 5.0  # 5 s per item


@dataclass
class FurnaceState:
    input_id: int = 0
    input_count: int = 0
    fuel_id: int = 0
    fuel_count: int = 0
    output_id: int = 0
    output_count: int = 0
    progress: float = 0.0
    burn_left: float = 0.0

    def to_dict(self) -> dict:
        return {"input_id": self.input_id, "input_count": self.input_count,
                "fuel_id": self.fuel_id, "fuel_count": self.fuel_count,
                "output_id": self.output_id,
                "output_count": self.output_count,
                "progress": self.progress, "burn_left": self.burn_left}

    @classmethod
    def from_dict(cls, d: dict) -> "FurnaceState":
        return cls(input_id=d.get("input_id", 0),
                   input_count=d.get("input_count", 0),
                   fuel_id=d.get("fuel_id", 0),
                   fuel_count=d.get("fuel_count", 0),
                   output_id=d.get("output_id", 0),
                   output_count=d.get("output_count", 0),
                   progress=d.get("progress", 0.0),
                   burn_left=d.get("burn_left", 0.0))


@dataclass
class ChestState:
    slots: list[int] = field(default_factory=lambda: [0] * 27)
    counts: list[int] = field(default_factory=lambda: [0] * 27)

    def to_dict(self) -> dict:
        return {"slots": self.slots, "counts": self.counts}

    @classmethod
    def from_dict(cls, d: dict) -> "ChestState":
        slots = d.get("slots", [0] * 27)
        counts = d.get("counts", [0] * 27)
        return cls(slots=slots[:27] + [0] * (27 - len(slots)),
                   counts=counts[:27] + [0] * (27 - len(counts)))


class BlockEntityManager:
    """Per-position block-entity store."""

    def __init__(self) -> None:
        self.furnaces: dict[tuple[int, int, int], FurnaceState] = {}
        self.chests: dict[tuple[int, int, int], ChestState] = {}

    def create_for(self, x: int, y: int, z: int, block_id: int) -> None:
        pos = (x, y, z)
        if block_id == ID_FURNACE and pos not in self.furnaces:
            self.furnaces[pos] = FurnaceState()
        elif block_id == ID_CHEST and pos not in self.chests:
            self.chests[pos] = ChestState()

    def remove(self, x: int, y: int, z: int) -> None:
        self.furnaces.pop((x, y, z), None)
        self.chests.pop((x, y, z), None)

    # ── Furnace ticking ─────────────────────────────────────
    def tick_furnaces(self, dt: float) -> None:
        for state in self.furnaces.values():
            self._tick_furnace(state, dt)

    def _tick_furnace(self, s: FurnaceState, dt: float) -> None:
        # If burning, decrement burn_left
        if s.burn_left > 0:
            s.burn_left = max(0.0, s.burn_left - dt)
        # If we have an input + can output, smelt
        if s.input_count > 0 and s.input_id in SMELTING_INPUT_TO_OUTPUT:
            out_id = SMELTING_INPUT_TO_OUTPUT[s.input_id]
            can_output = (s.output_count == 0 or s.output_id == out_id) \
                and s.output_count < 64
            if can_output and s.burn_left > 0:
                s.progress += dt
                if s.progress >= SMELT_TIME:
                    s.progress = 0.0
                    s.input_count -= 1
                    if s.input_count <= 0:
                        s.input_id = 0
                    if s.output_count == 0:
                        s.output_id = out_id
                    s.output_count += 1
            elif can_output and s.burn_left <= 0:
                # try to consume fuel
                if s.fuel_count > 0 and s.fuel_id in FUEL_BURN_TIME:
                    s.burn_left = FUEL_BURN_TIME[s.fuel_id]
                    s.fuel_count -= 1
                    if s.fuel_count <= 0:
                        s.fuel_id = 0

    # ── Serialisation ──────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "furnaces": {f"{x},{y},{z}": s.to_dict()
                          for (x, y, z), s in self.furnaces.items()},
            "chests": {f"{x},{y},{z}": c.to_dict()
                        for (x, y, z), c in self.chests.items()},
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BlockEntityManager":
        mgr = cls()
        for key, sd in d.get("furnaces", {}).items():
            x, y, z = (int(v) for v in key.split(","))
            mgr.furnaces[(x, y, z)] = FurnaceState.from_dict(sd)
        for key, cd in d.get("chests", {}).items():
            x, y, z = (int(v) for v in key.split(","))
            mgr.chests[(x, y, z)] = ChestState.from_dict(cd)
        return mgr
