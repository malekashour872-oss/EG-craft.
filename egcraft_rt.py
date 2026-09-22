# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Runtime hook for the PyInstaller frozen build.

Runs BEFORE the user's entry point (main.py). Three goals:

1. Switch the working directory to ``sys._MEIPASS`` so that any legacy
   relative paths in the codebase (e.g. ``"assets/fonts/..."``) still
   resolve to the bundled copies inside the EXE.

2. Pre-create the per-user writable directory (``%APPDATA%/EGCraft``
   on Windows, ``~/.egcraft`` elsewhere) so the logger and save module
   can write there without re-checking on every call.

3. Make sure ``stdout``/``stderr`` exist even under ``--noconsole``
   builds — Windows's ``pythonw``-style launcher sets them to ``None``
   in some builds, which crashes anything that tries to ``print()``
   (e.g. uncaught tracebacks in the bootloader).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_stdio() -> None:
    """Under --noconsole on Windows, sys.stdout/stderr can be None.
    Replace them with a null sink so writes don't crash.
    """
    if sys.stdout is None:
        try:
            sys.stdout = open(os.devnull, "w", encoding="utf-8")
        except Exception:
            sys.stdout = type("_Null", (), {"write": lambda *a, **kw: None,
                                            "flush": lambda *a, **kw: None})()
    if sys.stderr is None:
        try:
            sys.stderr = open(os.devnull, "w", encoding="utf-8")
        except Exception:
            sys.stderr = type("_Null", (), {"write": lambda *a, **kw: None,
                                            "flush": lambda *a, **kw: None})()


def _chdir_to_bundle() -> None:
    """Chdir to sys._MEIPASS so legacy relative paths resolve.

    Frozen builds extract bundled files (assets/, fonts, etc.) into
    a temp dir which is exposed as ``sys._MEIPASS``. The user's CWD
    may be anywhere — typically the desktop or the EXE's directory.
    Setting CWD to _MEIPASS makes ``open("assets/fonts/...")`` work.
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if not meipass:
        return
    try:
        os.chdir(meipass)
    except OSError:
        pass  # don't crash the boot for a CWD change


def _ensure_user_data_dir() -> None:
    """Pre-create the per-user writable directory."""
    try:
        appdata = os.environ.get("APPDATA")
        if appdata:
            p = Path(appdata) / "EGCraft"
        else:
            p = Path.home() / ".egcraft"
        p.mkdir(parents=True, exist_ok=True)
        (p / "logs").mkdir(exist_ok=True)
        (p / "saves").mkdir(exist_ok=True)
    except Exception:
        pass  # don't crash the boot


_ensure_stdio()
_chdir_to_bundle()
_ensure_user_data_dir()
