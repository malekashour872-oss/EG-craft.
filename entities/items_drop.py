# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Item entities (drops).

Spec ref: §9.6 — Item entity = mini cube 0.25 using the item's tile;
spins; gravity + collision; pickup distance 1.5 after a 0.5 s delay;
merges into inventory stacks; despawns after 300 s.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

PICKUP_DELAY = 0.5
PICKUP_DIST = 1.5
DESPAWN_TIME = 300.0


@dataclass
class ItemEntity:
    item_id: int
    count: int
    pos: np.ndarray
    vel: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    age: float = 0.0
    spin_phase: float = 0.0
    dead: bool = False

    def update(self, dt: float, world_get=None,
               player_pos: np.ndarray | None = None) -> bool:
        """Advance one tick. Returns True if the item was picked up
        by the player this tick (caller should add to inventory)."""
        if self.dead:
            return False
        self.age += dt
        self.spin_phase += dt * 3.0
        # gravity
        self.vel[1] -= 24.0 * dt
        self.pos += self.vel * dt
        # floor collision (very crude)
        if world_get is not None:
            x, y, z = (int(math.floor(self.pos[0])),
                        int(math.floor(self.pos[1])),
                        int(math.floor(self.pos[2])))
            if world_get(x, y, z) != 0:
                self.pos[1] = y + 1.0
                self.vel[1] = 0.0
                self.vel[0] *= 0.5
                self.vel[2] *= 0.5
        # Despawn timer
        if self.age >= DESPAWN_TIME:
            self.dead = True
            return False
        # Pickup check
        if player_pos is not None and self.age > PICKUP_DELAY:
            d = float(np.linalg.norm(self.pos - player_pos))
            if d < PICKUP_DIST:
                return True
        return False


class ItemEntityManager:
    """Pool of item entities."""

    def __init__(self) -> None:
        self.items: list[ItemEntity] = []

    def spawn(self, item_id: int, count: int, pos: np.ndarray,
              vel=None) -> None:
        if vel is None:
            rng = np.random.default_rng()
            theta = float(rng.uniform(0, 2 * math.pi))
            vel = np.array(
                [math.cos(theta) * 2.5, 4.0,
                 math.sin(theta) * 2.5], dtype=np.float32)
        self.items.append(ItemEntity(
            item_id=item_id, count=count,
            pos=np.array(pos, dtype=np.float32).copy(),
            vel=vel.astype(np.float32).copy(),
        ))

    def tick(self, dt: float, world_get=None,
             player_pos=None, inventory=None) -> list:
        """Advance; return list of (item_id, count) picked up this
        tick for the caller to merge into the inventory."""
        picked = []
        survivors = []
        for ie in self.items:
            if ie.dead:
                continue
            picked_up = ie.update(dt, world_get=world_get,
                                    player_pos=player_pos)
            if picked_up and inventory is not None:
                leftover = inventory.add_item(ie.item_id, ie.count)
                if leftover == 0:
                    ie.dead = True
                    picked.append((ie.item_id, ie.count))
                else:
                    ie.count = leftover
                    survivors.append(ie)
            else:
                survivors.append(ie)
        self.items = survivors
        return picked

    def to_dict(self) -> list:
        return [{"id": ie.item_id, "count": ie.count,
                 "pos": list(ie.pos), "age": ie.age}
                for ie in self.items]
