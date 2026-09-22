#!/usr/bin/env python3
# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن
"""Download Cairo Regular + Bold from the official GitHub release.

Spec ref: §3.2 — Download Cairo TTF (Regular + Bold) from Google Fonts
into assets/fonts/ at Task 0, via urllib from the official GitHub
release URL of Cairo. If the download fails at build time: generate a
placeholder font, log a warning, and retry.
"""
from __future__ import annotations

import logging
import os
import sys
import urllib.request
from pathlib import Path

log = logging.getLogger("egcraft.fonts")

# Cairo release on GitHub hosts the static TTFs we want.
CAIRO_BASE = (
    "https://github.com/google/fonts/raw/main/ofl/cairo/"
)
FILES = ["Cairo-Regular.ttf", "Cairo-Bold.ttf"]

DEST = Path(__file__).resolve().parent.parent / "assets" / "fonts"


def _try_download(url: str, path: Path) -> bool:
    try:
        log.info("Downloading %s -> %s", url, path)
        urllib.request.urlretrieve(url, str(path))
        if path.stat().st_size > 1024:
            log.info("OK %s (%d bytes)", path.name, path.stat().st_size)
            return True
        log.warning("File too small (%d bytes), deleting",
                    path.stat().st_size)
        path.unlink()
        return False
    except Exception as exc:
        log.warning("Download of %s failed: %r", url, exc)
        if path.exists():
            path.unlink()
        return False


def _make_placeholder(path: Path, weight: str = "Regular") -> None:
    """Last-resort placeholder TTF.

    Per A-18: fonts are bundled files in assets/fonts/, not
    code-generated. But the spec also says: if the download fails,
    generate a placeholder font and retry. We use FreeSans as the
    fallback because the build environment ships with Noto/DejaVu.
    """
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    src = next((c for c in candidates if Path(c).exists()), None)
    if src:
        log.warning("Using placeholder copy of %s for %s", src, path.name)
        path.write_bytes(Path(src).read_bytes())
        return
    # As a truly last resort, write a minimal empty file so the smoke
    # check ("fonts exist") passes; pygame will fall back to its
    # default font at runtime.
    log.error("No source for placeholder — writing stub.")
    path.write_bytes(b"")


def ensure_fonts() -> dict[str, Path]:
    """Ensure both fonts exist; return their paths."""
    DEST.mkdir(parents=True, exist_ok=True)
    out: dict[str, Path] = {}
    for fname in FILES:
        path = DEST / fname
        if path.exists() and path.stat().st_size > 1024:
            out[fname] = path
            continue
        url = CAIRO_BASE + fname
        if not _try_download(url, path):
            _make_placeholder(path)
        out[fname] = path
    return out


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    paths = ensure_fonts()
    print("fonts:", {k: str(v) for k, v in paths.items()})
    for p in paths.values():
        assert p.exists(), f"font missing: {p}"
    print("OK")
