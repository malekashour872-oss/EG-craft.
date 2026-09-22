# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Crafting recipes.

Spec ref: §8.3 — exact 3×3 grid patterns (`. = empty, P = planks,
L = log, S = stick, C = cobble, M = material ∈ {P, C, iron, gold,
diamond}`). Recipes: planks_from_log, sticks, crafting_table,
furnace, chest, torch ×4, pickaxe/axe/shovel/sword (per material).
Matching: normalise the pattern (trim empty rows/columns), then
require an exact pattern match.
"""
from __future__ import annotations

from typing import Optional

from world.blocks import (
    ID_LOG, ID_PLANKS, ID_COBBLE, ID_CRAFTING_TABLE,
    ID_FURNACE, ID_CHEST, ID_TORCH,
    ITEM_STICK, ITEM_COAL, ITEM_IRON_INGOT, ITEM_GOLD_INGOT, ITEM_DIAMOND,
    TOOL_BASE, TOOL_MATERIALS, TOOL_TYPES, tool_id,
)

# local alias for clarity (stick is item 101, not a block)
ID_STICK = ITEM_STICK

# Symbol → block/item id mapping (the "M" family).
MATERIAL_MAP = {
    "P":       ID_PLANKS,
    "C":       ID_COBBLE,
    "iron":    ITEM_IRON_INGOT,
    "gold":    ITEM_GOLD_INGOT,
    "diamond": ITEM_DIAMOND,
}


def _make_recipe(name: str, pattern: list[list[str]],
                 result_id: int, count: int = 1,
                 material_keys: Optional[list[tuple[int, int]]] = None
                 ) -> dict:
    """Build a recipe entry.

    ``pattern`` is a 3×3 grid of cells, each a string id or ``"."``
    for empty. ``material_keys`` is a list of (row, col) positions
    that hold a "M" material placeholder; the material is taken from
    the inventory input."""
    return {
        "name": name,
        "pattern": pattern,
        "result_id": result_id,
        "count": count,
        "material_cells": material_keys or [],
    }


# Recipes (per §8.3) — exact patterns
RECIPES: list[dict] = []

# planks_from_log: L anywhere in the grid → 4 planks
RECIPES.append(_make_recipe(
    "planks_from_log",
    [["L", ".", "."], [".", ".", "."], [".", ".", "."]],
    ID_PLANKS, count=4,
))

# sticks: P over P (vertical)
RECIPES.append(_make_recipe(
    "sticks",
    [[".", "P", "."], [".", "P", "."], [".", ".", "."]],
    ID_STICK, count=4,
))

# crafting_table: PP / PP
RECIPES.append(_make_recipe(
    "crafting_table",
    [["P", "P", "."], ["P", "P", "."], [".", ".", "."]],
    ID_CRAFTING_TABLE, count=1,
))

# furnace: 8 × C in a ring, centre empty
RECIPES.append(_make_recipe(
    "furnace",
    [["C", "C", "C"], ["C", ".", "C"], ["C", "C", "C"]],
    ID_FURNACE, count=1,
))

# chest: 8 × P in a ring
RECIPES.append(_make_recipe(
    "chest",
    [["P", "P", "P"], ["P", ".", "P"], ["P", "P", "P"]],
    ID_CHEST, count=1,
))

# torch ×4: coal over stick (vertical)
RECIPES.append(_make_recipe(
    "torch",
    [[".", "coal", "."], [".", "stick", "."], [".", ".", "."]],
    ID_TORCH, count=4,
))

# Pickaxe (material M): MMM / .S. / .S.
RECIPES.append(_make_recipe(
    "pickaxe_wooden",
    [["P", "P", "P"], [".", "S", "."], [".", "S", "."]],
    tool_id(0, 0), count=1,
    material_keys=[(0, 0), (0, 1), (0, 2)],
))
RECIPES.append(_make_recipe(
    "pickaxe_stone",
    [["C", "C", "C"], [".", "S", "."], [".", "S", "."]],
    tool_id(4, 0), count=1,
    material_keys=[(0, 0), (0, 1), (0, 2)],
))
RECIPES.append(_make_recipe(
    "pickaxe_iron",
    [["iron", "iron", "iron"], [".", "S", "."], [".", "S", "."]],
    tool_id(8, 0), count=1,
    material_keys=[(0, 0), (0, 1), (0, 2)],
))
RECIPES.append(_make_recipe(
    "pickaxe_gold",
    [["gold", "gold", "gold"], [".", "S", "."], [".", "S", "."]],
    tool_id(12, 0), count=1,
    material_keys=[(0, 0), (0, 1), (0, 2)],
))
RECIPES.append(_make_recipe(
    "pickaxe_diamond",
    [["diamond", "diamond", "diamond"], [".", "S", "."], [".", "S", "."]],
    tool_id(16, 0), count=1,
    material_keys=[(0, 0), (0, 1), (0, 2)],
))

# Axe (material M): MM. / MS. / .S. (+ mirrored)
RECIPES.append(_make_recipe(
    "axe_wooden",
    [["P", "P", "."], ["P", "S", "."], [".", "S", "."]],
    tool_id(0, 1), count=1,
    material_keys=[(0, 0), (0, 1), (1, 0)],
))
RECIPES.append(_make_recipe(
    "axe_iron",
    [["iron", "iron", "."], ["iron", "S", "."], [".", "S", "."]],
    tool_id(8, 1), count=1,
    material_keys=[(0, 0), (0, 1), (1, 0)],
))
RECIPES.append(_make_recipe(
    "axe_stone",
    [["C", "C", "."], ["C", "S", "."], [".", "S", "."]],
    tool_id(4, 1), count=1,
    material_keys=[(0, 0), (0, 1), (1, 0)],
))
RECIPES.append(_make_recipe(
    "axe_gold",
    [["gold", "gold", "."], ["gold", "S", "."], [".", "S", "."]],
    tool_id(12, 1), count=1,
    material_keys=[(0, 0), (0, 1), (1, 0)],
))
RECIPES.append(_make_recipe(
    "axe_diamond",
    [["diamond", "diamond", "."], ["diamond", "S", "."], [".", "S", "."]],
    tool_id(16, 1), count=1,
    material_keys=[(0, 0), (0, 1), (1, 0)],
))

# Shovel (material M): .M. / .S. / .S.
RECIPES.append(_make_recipe(
    "shovel_wooden",
    [[".", "P", "."], [".", "S", "."], [".", "S", "."]],
    tool_id(0, 2), count=1,
    material_keys=[(0, 1)],
))
RECIPES.append(_make_recipe(
    "shovel_iron",
    [[".", "iron", "."], [".", "S", "."], [".", "S", "."]],
    tool_id(8, 2), count=1,
    material_keys=[(0, 1)],
))
RECIPES.append(_make_recipe(
    "shovel_stone",
    [[".", "C", "."], [".", "S", "."], [".", "S", "."]],
    tool_id(4, 2), count=1,
    material_keys=[(0, 1)],
))
RECIPES.append(_make_recipe(
    "shovel_gold",
    [[".", "gold", "."], [".", "S", "."], [".", "S", "."]],
    tool_id(12, 2), count=1,
    material_keys=[(0, 1)],
))
RECIPES.append(_make_recipe(
    "shovel_diamond",
    [[".", "diamond", "."], [".", "S", "."], [".", "S", "."]],
    tool_id(16, 2), count=1,
    material_keys=[(0, 1)],
))

# Sword (material M): .M. / .M. / .S.
RECIPES.append(_make_recipe(
    "sword_wooden",
    [[".", "P", "."], [".", "P", "."], [".", "S", "."]],
    tool_id(0, 3), count=1,
    material_keys=[(0, 1), (1, 1)],
))
RECIPES.append(_make_recipe(
    "sword_iron",
    [[".", "iron", "."], [".", "iron", "."], [".", "S", "."]],
    tool_id(8, 3), count=1,
    material_keys=[(0, 1), (1, 1)],
))
RECIPES.append(_make_recipe(
    "sword_stone",
    [[".", "C", "."], [".", "C", "."], [".", "S", "."]],
    tool_id(4, 3), count=1,
    material_keys=[(0, 1), (1, 1)],
))
RECIPES.append(_make_recipe(
    "sword_gold",
    [[".", "gold", "."], [".", "gold", "."], [".", "S", "."]],
    tool_id(12, 3), count=1,
    material_keys=[(0, 1), (1, 1)],
))
RECIPES.append(_make_recipe(
    "sword_diamond",
    [[".", "diamond", "."], [".", "diamond", "."], [".", "S", "."]],
    tool_id(16, 3), count=1,
    material_keys=[(0, 1), (1, 1)],
))

# Symbol → item id map (for grid matching)
SYMBOL_MAP = {
    "L": ID_LOG,
    "P": ID_PLANKS,
    "S": ID_STICK,
    "C": ID_COBBLE,
    "coal": ITEM_COAL,
    "stick": ID_STICK,
    "iron": ITEM_IRON_INGOT,
    "gold": ITEM_GOLD_INGOT,
    "diamond": ITEM_DIAMOND,
    ".": None,
}


def _normalise(pattern: list[list[str]]) -> tuple[list[list[str]], list[tuple[int, int]]]:
    """Trim empty rows/columns; return the trimmed pattern + the
    (row, col) offsets relative to the original 3×3 grid."""
    rows = len(pattern)
    cols = len(pattern[0]) if rows else 0
    # find non-empty row range
    non_empty_rows = [r for r in range(rows)
                       if any(pattern[r][c] != "." for c in range(cols))]
    if not non_empty_rows:
        return [], []
    r0, r1 = non_empty_rows[0], non_empty_rows[-1] + 1
    non_empty_cols = [c for c in range(cols)
                       if any(pattern[r][c] != "." for r in range(r0, r1))]
    if not non_empty_cols:
        return [], []
    c0, c1 = non_empty_cols[0], non_empty_cols[-1] + 1
    out = [[pattern[r][c] for c in range(c0, c1)] for r in range(r0, r1)]
    # offsets
    offsets = [(r, c) for r in range(r0, r1) for c in range(c0, c1)]
    return out, offsets


def match_recipe(grid: list[list[int]]) -> tuple[Optional[str],
                                                    Optional[int], int]:
    """Match a 3×3 grid of block/item ids against the recipes.

    Returns ``(recipe_name, result_id, count)`` or
    ``(None, None, 0)`` on no match.
    """
    # Convert grid to symbol-or-id form for comparison
    # We compare directly on item ids.
    for recipe in RECIPES:
        pat = recipe["pattern"]
        mat_offsets = recipe["material_cells"]
        # Normalise both the grid (treating 0 as ".") and the pattern
        grid_syms = [[("." if (grid[r][c] in (0, None)) else grid[r][c])
                      for c in range(3)] for r in range(3)]
        # Try material variants: for recipes with material_cells, the
        # actual material id must be the SAME across all material cells
        material_ids = set()
        for (mr, mc) in mat_offsets:
            val = grid[mr][mc]
            if val not in (0, None):
                material_ids.add(val)
        if len(material_ids) > 1:
            continue  # mixed materials don't match
        mat_id = next(iter(material_ids), None) if material_ids else None
        # Build a comparison grid using "." for empty cells
        compare = [["." for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                sym = pat[r][c]
                if sym == ".":
                    compare[r][c] = "."
                elif sym == "M":
                    compare[r][c] = mat_id if mat_id else "."
                else:
                    compare[r][c] = SYMBOL_MAP.get(sym, ".")
        # Now normalise both
        norm_grid, _ = _normalise(grid_syms)
        norm_pat, _ = _normalise(compare)
        if norm_grid == norm_pat:
            return recipe["name"], recipe["result_id"], recipe["count"]
    return None, None, 0
