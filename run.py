# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""EG Craft CLI launcher.

Spec ref: §4 — run.py CLI: --smoke | --debug | --seed N | --res WxH
Spec ref: §17.3 — run.py --smoke runs test_smoke.py.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Optional


def _parse_resolution(s: str) -> tuple[int, int]:
    if "x" in s.lower():
        w, h = s.lower().split("x", 1)
        return int(w), int(h)
    raise argparse.ArgumentTypeError(
        f"invalid --res {s!r}, expected WxH e.g. 1280x720")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="egcraft", description="EG Craft launcher")
    p.add_argument("--smoke", action="store_true",
                   help="run the test_smoke.py assertions")
    p.add_argument("--debug", action="store_true",
                   help="run with extra debug logging + screenshots")
    p.add_argument("--seed", type=int, default=None,
                   help="world seed (default: 12345 from settings.py)")
    p.add_argument("--res", type=_parse_resolution, default=None,
                   help="window resolution, e.g. 1280x720")
    p.add_argument("--headless", action="store_true",
                   help="force headless mode (SDL_VIDEODRIVER=dummy)")
    p.add_argument("--frames", type=int, default=None,
                   help="exit after N frames (smoke mode uses this)")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.headless or args.smoke:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        os.environ.setdefault("EGCRAFT_HEADLESS", "1")

    if args.smoke:
        # Re-export test_smoke.run under run.py --smoke.
        import importlib
        ts = importlib.import_module("test_smoke")
        return ts.run(args.frames or 300)

    # Normal play: settings + main loop
    from settings import Settings
    settings = Settings.load()
    if args.seed is not None:
        settings.seed = args.seed
    if args.res is not None:
        settings.width, settings.height = args.res

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    import main as main_mod
    return main_mod.main()


if __name__ == "__main__":
    sys.exit(main())
