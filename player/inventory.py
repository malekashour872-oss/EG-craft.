# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Inventory + hotbar.

Spec ref: §8.2 — 36 slots (9 hotbar). Slot = dict(id, count, dur?).
Stack max 64 (tools 1). Survival starts empty. Creative: palette UI
of every block ID + items; click → cursor takes a stack of 64; ∞
shown as "∞". E toggles inventory. Drag: click to pick up, click to
place, RMB places a single item; wheel / keys 1–9 select the hotbar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from world.blocks import (
    ID_AIR, _BLOCKS, ITEM_NAMES_AR, TOOL_BASE,
    TOOL_MATERIALS, TOOL_TYPES, tool_id,
)

STACK_MAX = 64
SLOTS = 36
HOTBAR = 9


@dataclass
class Slot:
    id: int = 0       # 0 = empty
    count: int = 0
    dur: Optional[int] = None  # tool durability

    @property
    def empty(self) -> bool:
        return self.id == 0 or self.count <= 0

    def can_stack(self, other: "Slot") -> bool:
        return (not self.empty and self.id == other.id
                and self.dur is None and other.dur is None)

    def add(self, item_id: int, n: int = 1) -> int:
        """Add n items to this slot; return leftover."""
        if self.empty:
            self.id = item_id
            self.count = 0
        if self.id != item_id:
            return n
        # tools are stack=1
        is_tool = item_id >= TOOL_BASE
        cap = 1 if is_tool else STACK_MAX
        space = cap - self.count
        take = min(n, space)
        self.count += take
        return n - take


class Inventory:
    """36-slot inventory + cursor stack."""

    def __init__(self) -> None:
        self.slots: list[Slot] = [Slot() for _ in range(SLOTS)]
        self.selected: int = 0  # hotbar index 0..8
        self.cursor: Slot = Slot()  # drag-and-drop buffer
        self.creative: bool = False

    # ── Access ──────────────────────────────────────────────
    def hotbar_slot(self) -> Slot:
        return self.slots[self.selected]

    def add_item(self, item_id: int, count: int = 1) -> int:
        """Add an item to the inventory (hotbar first, then main).
        Returns leftover."""
        leftover = count
        # try existing stacks first
        for s in self.slots:
            if s.id == item_id and not s.empty:
                leftover = s.add(item_id, leftover)
                if leftover == 0:
                    return 0
        # then empty slots
        for s in self.slots:
            if s.empty:
                leftover = s.add(item_id, leftover)
                if leftover == 0:
                    return 0
        return leftover

    def remove_selected(self, count: int = 1) -> bool:
        s = self.hotbar_slot()
        if s.empty or s.count < count:
            return False
        s.count -= count
        if s.count <= 0:
            s.id = 0
            s.count = 0
            s.dur = None
        return True

    def select(self, idx: int) -> None:
        if 0 <= idx < HOTBAR:
            self.selected = idx

    def scroll(self, delta: int) -> None:
        self.selected = (self.selected + delta) % HOTBAR

    # ── Drag & drop ────────────────────────────────────────
    def click_pick(self, slot_idx: int, right: bool = False) -> None:
        """Pick up a stack from slot_idx (LMB) or one item (RMB)."""
        s = self.slots[slot_idx]
        if right:
            # take one item from slot to cursor
            if not s.empty and self.cursor.empty:
                self.cursor.id = s.id
                self.cursor.count = 1
                self.cursor.dur = s.dur
                s.count -= 1
                if s.count <= 0:
                    s.id = 0
                    s.dur = None
        else:
            # swap cursor ↔ slot
            self.cursor, self.slots[slot_idx] = s, self.cursor

    def click_place(self, slot_idx: int, right: bool = False) -> None:
        """Place cursor stack into slot_idx."""
        s = self.slots[slot_idx]
        if right:
            # place one item from cursor
            if not self.cursor.empty and (s.empty or s.id == self.cursor.id):
                if s.empty:
                    s.id = self.cursor.id
                    s.dur = self.cursor.dur
                    s.count = 0
                s.count += 1
                self.cursor.count -= 1
                if self.cursor.count <= 0:
                    self.cursor = Slot()
        else:
            self.cursor, self.slots[slot_idx] = s, self.cursor

    # ── Creative palette ──────────────────────────────────
    def creative_palette(self) -> list[int]:
        """Return all block IDs + item IDs for the creative palette."""
        ids = [b.id for b in _BLOCKS.values() if b.id != ID_AIR]
        ids.extend(ITEM_NAMES_AR.keys())
        # tools
        for mat_off, _, _, _, _, _, _ in TOOL_MATERIALS:
            for typ_off, _, _ in TOOL_TYPES:
                ids.append(tool_id(mat_off, typ_off))
        return ids

    # ── Serialisation ──────────────────────────────────────
    def to_dict(self) -> list[dict]:
        return [{"id": s.id, "count": s.count, "dur": s.dur}
                for s in self.slots]

    @classmethod
    def from_dict(cls, data: list[dict]) -> "Inventory":
        inv = cls()
        for i, d in enumerate(data[:SLOTS]):
            inv.slots[i] = Slot(id=d.get("id", 0),
                                count=d.get("count", 0),
                                dur=d.get("dur"))
        return inv
