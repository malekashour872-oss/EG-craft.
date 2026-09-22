# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Save/Load.

Spec ref: §15 — Save path: assets/saves/world_<seed>/. Files:
meta.json (pretty JSON), blocks.gzip.json (gzip-compressed JSON,
per A-19), block_entities.json, entities.json, registry_hybrids.json
(runtime definitions; deterministic catalogue is recomputed).
F5 = save, F9 = load. Auto-save on quit-to-menu. Web build: saving
disabled; show the web_nosave toast.
"""
from __future__ import annotations

import gzip
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

log = logging.getLogger("egcraft.save")


def _saves_dir() -> Path:
    """Writable per-user saves directory.

    In dev: ``./assets/saves`` (legacy, matches spec §15).
    In a frozen PyInstaller exe: ``<user_data_dir>/saves`` — the bundle
    is read-only, so we cannot write next to the EXE.
    """
    if getattr(sys, "frozen", False):
        try:
            from settings import user_data_dir
            d = user_data_dir() / "saves"
            d.mkdir(parents=True, exist_ok=True)
            return d
        except Exception:
            pass
    # Dev / unfrozen — keeps the spec §15 layout.
    d = Path("assets") / "saves"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _world_dir(seed: int) -> Path:
    return _saves_dir() / f"world_{seed}"


def _ensure_dir(seed: int) -> Path:
    p = _world_dir(seed)
    p.mkdir(parents=True, exist_ok=True)
    return p


def is_web_build() -> bool:
    """Detect pygbag environment."""
    try:
        import sys
        return "pygbag" in sys.modules or "emscripten" in sys.platform.lower()
    except Exception:  # noqa: BLE001
        return False


# ── Meta ──────────────────────────────────────────────────
def save_meta(world, label: Optional[str] = None) -> dict:
    """Build the meta.json dict."""
    seed = getattr(world, "seed", 0)
    return {
        "seed": int(seed),
        "label": label,
        "mode": getattr(world, "mode", "survival"),
        "time_t": getattr(world, "time_t", 0.0),
        "player": {
            "pos": list(getattr(world, "player_pos", [0, 0, 0])),
            "yaw": getattr(world, "player_yaw", 0.0),
            "pitch": getattr(world, "player_pitch", 0.0),
            "hp": getattr(world, "player_hp", 20),
            "hunger": getattr(world, "player_hunger", 20),
            "inv": getattr(world, "player_inv", []),
        },
        "settings": getattr(world, "settings_snapshot", {}),
    }


def load_meta(seed: int) -> Optional[dict]:
    p = _world_dir(seed) / "meta.json"
    if not p.exists():
        return None
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# ── Blocks (gzip JSON per A-19) ──────────────────────────
def save_blocks(world) -> bytes:
    """Serialise world overrides as gzip-compressed JSON (A-19)."""
    overrides = getattr(world, "overrides", {})
    data: dict[str, dict[str, int]] = {}
    for (cx, cz), cells in overrides.items():
        key = f"{cx},{cz}"
        data[key] = {f"{x},{y},{z}": int(bid)
                     for (x, y, z), bid in cells.items()}
    raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return gzip.compress(raw)


def load_blocks(world) -> None:
    """Load blocks from disk and apply overrides to the world."""
    p = _world_dir(world.seed) / "blocks.gzip.json"
    if not p.exists():
        return
    with p.open("rb") as fh:
        raw = gzip.decompress(fh.read())
    data = json.loads(raw.decode("utf-8"))
    for chunk_key, cells in data.items():
        cx, cz = (int(v) for v in chunk_key.split(","))
        world.overrides.setdefault((cx, cz), {})
        for cell_key, bid in cells.items():
            x, y, z = (int(v) for v in cell_key.split(","))
            world.overrides[(cx, cz)][(x, y, z)] = int(bid)
            # apply to the loaded chunk if present
            chunk = world.chunks.get((cx, cz))
            if chunk is not None:
                chunk.set(x, y, z, int(bid))


# ── Full save/load ───────────────────────────────────────
def save_world(world, label: Optional[str] = None) -> Path:
    """Save the world. Returns the save dir path."""
    if is_web_build():
        log.info("Web build: saving disabled (web_nosave toast)")
        return _world_dir(world.seed)
    d = _ensure_dir(world.seed)
    # meta
    meta = save_meta(world, label=label)
    with (d / "meta.json").open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
    # blocks (gzip per A-19)
    with (d / "blocks.gzip.json").open("wb") as fh:
        fh.write(save_blocks(world))
    # block entities
    bem = getattr(world, "block_entities", None)
    if bem is not None:
        with (d / "block_entities.json").open("w", encoding="utf-8") as fh:
            json.dump(bem.to_dict(), fh, ensure_ascii=False, indent=2)
    # entities
    em = getattr(world, "entities_manager", None)
    if em is not None and hasattr(em, "to_dict"):
        with (d / "entities.json").open("w", encoding="utf-8") as fh:
            json.dump(em.to_dict(), fh, ensure_ascii=False, indent=2)
    log.info("Saved world (seed=%s) to %s", world.seed, d)
    return d


def load_world(world, label: Optional[str] = None) -> bool:
    """Load the world from disk."""
    if is_web_build():
        log.info("Web build: loading disabled")
        return False
    meta = load_meta(world.seed)
    if meta is None:
        log.warning("No save found for seed=%s", world.seed)
        return False
    load_blocks(world)
    bem = getattr(world, "block_entities", None)
    if bem is not None:
        p = _world_dir(world.seed) / "block_entities.json"
        if p.exists():
            with p.open("r", encoding="utf-8") as fh:
                bem_data = json.load(fh)
            from game.block_entities import BlockEntityManager
            new_bem = BlockEntityManager.from_dict(bem_data)
            world.block_entities = new_bem
    log.info("Loaded world (seed=%s) label=%s", world.seed, label)
    return True
