# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Top-level settings dataclass for EG Craft.

Spec ref: §4 — settings.py defaults.
Loaded/saved as JSON via :func:`load` / :func:`save`.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def resource_path(*parts: str) -> Path:
    """Resolve a path inside the project's bundled assets.

    In a normal dev run: resolves relative to this file's directory.
    In a PyInstaller frozen exe: resolves relative to ``sys._MEIPASS``
    (the temporary extraction directory).
    """
    base = getattr(sys, "_MEIPASS", None)
    if base is not None:
        return Path(base, *parts)
    here = Path(__file__).resolve().parent
    return here.joinpath(*parts)


def user_data_dir() -> Path:
    """Per-user writable directory for settings/saves/logs.

    Uses ``%APPDATA%/EGCraft`` on Windows, ``~/.egcraft`` elsewhere.
    Created on first call.
    """
    appdata = os.environ.get("APPDATA")
    if appdata:
        p = Path(appdata) / "EGCraft"
    else:
        p = Path.home() / ".egcraft"
    p.mkdir(parents=True, exist_ok=True)
    return p


@dataclass
class Settings:
    width: int = 1280
    height: int = 720
    fov: float = 70.0
    render_distance: int = 4
    master_volume: float = 0.8
    sfx: float = 1.0
    music: float = 0.4
    sensitivity: float = 0.0022
    fullscreen: bool = False
    seed: int = 12345
    vsync: bool = True
    mouse_sensitivity: float = 0.0022  # alias for sensitivity

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        clean = {k: v for k, v in data.items() if k in known}
        return cls(**clean)

    # Class-method alias so callers can use either ``Settings.load()``
    # (classmethod syntax used by main.py and run.py) or the module-level
    # ``settings.load()`` function. Both resolve to the same impl.
    @classmethod
    def load(cls, path: Path | str | None = None) -> "Settings":
        return load(path)

    @classmethod
    def save(cls, settings: "Settings",
             path: Path | str | None = None) -> None:
        save(settings, path)


def bundled_path() -> Path:
    """Read-only location of the bundled settings.json.

    In dev: ``<project>/assets/settings.json``.
    In a frozen exe: ``sys._MEIPASS/assets/settings.json``.
    """
    return resource_path("assets", "settings.json")


def default_path() -> Path:
    """Writable location of the user's settings.json.

    Reads come from :func:`bundled_path` (the shipped defaults).
    Writes go to ``user_data_dir()/settings.json`` so the file survives
    EXE upgrades and works inside a read-only ``--onefile`` bundle.
    """
    return user_data_dir() / "settings.json"


def load(path: Path | str | None = None) -> Settings:
    # Read from the bundled defaults first (shipped with the EXE).
    src = Path(path) if path else bundled_path()
    if src.exists():
        try:
            with src.open("r", encoding="utf-8") as fh:
                return Settings.from_dict(json.load(fh))
        except (json.JSONDecodeError, OSError):
            pass
    # Fall back to the user's writable copy (created by a previous save).
    user_p = default_path()
    if user_p.exists():
        try:
            with user_p.open("r", encoding="utf-8") as fh:
                return Settings.from_dict(json.load(fh))
        except (json.JSONDecodeError, OSError):
            pass
    # First run: persist defaults to the user path so future reads work.
    s = Settings()
    try:
        save(s, user_p)
    except OSError:
        pass  # read-only env — keep in-memory defaults
    return s


def save(settings: Settings, path: Path | str | None = None) -> None:
    p = Path(path) if path else default_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            json.dump(settings.to_dict(), fh, indent=2, ensure_ascii=False)
    except OSError:
        # Don't crash the game if the user dir is read-only — settings
        # simply won't persist. The in-memory Settings object is still
        # usable for the rest of the session.
        pass
