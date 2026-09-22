# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Logging setup for EG Craft.

Spec ref: §17.4 — logging_setup.py → logs/egcraft.log with timestamps
and tracebacks.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path


_INITIALISED = False


def _resolve_log_path() -> Path:
    """Pick a writable directory for the log file.

    Tries (in order):
    1. ``<user_data_dir>/logs/egcraft.log`` — survives EXE upgrades,
       works inside a read-only PyInstaller ``--onefile`` bundle.
    2. ``./logs/egcraft.log`` (relative to CWD) — legacy/dev fallback.
    Both are created on demand; failures fall back to no file handler.
    """
    try:
        from settings import user_data_dir
        p = user_data_dir() / "logs" / "egcraft.log"
        p.parent.mkdir(parents=True, exist_ok=True)
        # Touch the file to make sure we can actually write to it.
        p.open("a", encoding="utf-8").close()
        return p
    except Exception:
        pass
    # Legacy fallback — only works when CWD is writable (dev mode).
    return Path("logs") / "egcraft.log"


def get_logger(name: str = "egcraft") -> logging.Logger:
    """Return the configured logger; idempotent."""
    global _INITIALISED
    logger = logging.getLogger(name)
    if _INITIALISED:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Stream handler — INFO to stdout (always works)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    sh.setLevel(logging.INFO)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(sh)

    # File handler — best-effort; skip if no writable location
    try:
        log_path = _resolve_log_path()
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    except Exception:
        # Read-only environment (e.g. frozen --onefile launched from
        # C:\Program Files) — keep the stdout handler only.
        pass

    logger.propagate = False
    _INITIALISED = True
    return logger


def log_exception(logger: logging.Logger, exc: BaseException,
                  context: str = "") -> None:
    """Log an exception with full traceback."""
    import traceback
    msg = f"EXCEPTION during {context}: {exc!r}" if context else f"EXCEPTION: {exc!r}"
    logger.error(msg)
    tb = traceback.format_exc()
    for line in tb.splitlines():
        logger.debug(line)
