#!/usr/bin/env python3
# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Post-build processor for the pygbag web bundle.

pygbag 0.9.1 has two limitations that this script works around:

1. The ``--app_name`` CLI flag is parsed but IGNORED — the output apk
   is always named ``<folder_name>.apk``. On Vercel the folder name is
   unpredictable, so we rename the apk to a stable ``egcraft.apk`` and
   patch every reference to the old name inside ``index.html``.

2. pygbag ships its own ``index.html`` template (terminal + console +
   progress bar). The project's ``web/index.html`` carries the EG Craft
   mobile-first UI (splash, joystick, action buttons, hotbar). This
   script merges the two: it takes pygbag's index.html as the base
   (because it owns the WASM loader + apk mount logic) and injects the
   mobile UI elements + ``mobile.js`` into it.

Run after ``pygbag --build .``::

    python scripts/post_build.py build/web

The script is idempotent — running it twice produces the same output.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


STABLE_APK_NAME = "egcraft.apk"
STABLE_ARCHIVE = "egcraft"

# Files from web/ that must accompany the bundle
WEB_ASSETS = ("mobile.js", "manifest.webmanifest", "index.html")


def find_apk(build_dir: Path) -> Path | None:
    """Return the first ``*.apk`` file in *build_dir*, or None."""
    apks = sorted(build_dir.glob("*.apk"))
    return apks[0] if apks else None


def rename_apk(build_dir: Path) -> tuple[str, str]:
    """Rename ``<folder>.apk`` to ``egcraft.apk`` and return (old, new) names."""
    apk = find_apk(build_dir)
    if apk is None:
        raise SystemExit(f"post_build: no .apk found in {build_dir}")
    old_stem = apk.stem  # e.g. "fixed" or "eg-craft"
    target = build_dir / STABLE_APK_NAME
    if apk != target:
        if target.exists():
            target.unlink()
        apk.rename(target)
    return old_stem, STABLE_APK_NAME[:-4]  # return stem of new name


def patch_index_refs(build_dir: Path, old_stem: str, new_stem: str) -> None:
    """Replace every occurrence of *old_stem* with *new_stem* in index.html.

    pygbag embeds the archive name in several places inside the generated
    ``index.html`` (the ``apk =`` Python assignment, the ``archive`` JS
    config key, the ``<title>``, the loader print banner, etc.). All of
    them must point at the renamed apk or the WASM loader will 404.
    """
    idx = build_dir / "index.html"
    if not idx.exists():
        raise SystemExit(f"post_build: {idx} not found")
    text = idx.read_text(encoding="utf-8")
    # Replace both the bare stem ("fixed") and the apk filename
    # ("fixed.apk"). Order matters: do the .apk form first so the bare
    # replacement doesn't corrupt it.
    text = text.replace(f"{old_stem}.apk", f"{new_stem}.apk")
    text = text.replace(old_stem, new_stem)
    idx.write_text(text, encoding="utf-8")


def copy_web_assets(project_root: Path, build_dir: Path) -> None:
    """Copy mobile.js and manifest.webmanifest into the build output."""
    web_dir = project_root / "web"
    for name in ("mobile.js", "manifest.webmanifest"):
        src = web_dir / name
        dst = build_dir / name
        if src.exists():
            shutil.copyfile(src, dst)


# ─────────────────────────────────────────────────────────────────────────────
# Mobile UI injection
# ─────────────────────────────────────────────────────────────────────────────
# We inject the EG Craft mobile-first UI (splash, touch controls, hotbar)
# INTO pygbag's generated index.html. pygbag owns the WASM loader, so we
# keep its <head> and <body> structure intact and only ADD our elements.

MOBILE_CSS = """
    <style id="egcraft-mobile-css">
    /* EG Craft mobile UI — injected by scripts/post_build.py */
    #egc-loader {
      position: fixed; inset: 0; display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: 24px; z-index: 9999;
      background: linear-gradient(135deg, #0a080e 0%, #1a1424 100%);
      color: #fff; font-family: 'Cairo', 'Noto Sans Arabic', system-ui, sans-serif;
    }
    #egc-loader .logo { font-size: 48px; font-weight: 800; color: #ffc83c;
      text-shadow: 0 4px 24px rgba(255,200,60,0.4); letter-spacing: 2px; }
    #egc-loader .sub { color: #c8b890; font-size: 14px; }
    #egc-loader .notice { color: #888; font-size: 11px; max-width: 80vw;
      text-align: center; line-height: 1.5; }
    #egc-loader .start-btn { margin-top: 16px; padding: 14px 36px;
      background: linear-gradient(135deg, #ffc83c, #ff8c20); color: #1a0e00;
      font-weight: 700; font-size: 16px; border-radius: 999px; border: none;
      cursor: pointer; box-shadow: 0 6px 24px rgba(255,140,32,0.4); display: none; }
    #egc-loader .start-btn:active { transform: scale(0.96); }
    #egc-touch { position: fixed; inset: 0; pointer-events: none; z-index: 50; display: none; }
    #egc-touch.visible { display: block; }
    #egc-touch .joystick { position: absolute; bottom: 32px; left: 32px;
      width: 140px; height: 140px; pointer-events: auto; border-radius: 50%;
      background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.06), rgba(0,0,0,0.3));
      border: 2px solid rgba(255,200,60,0.4); }
    #egc-touch .knob { position: absolute; left: 50%; top: 50%;
      transform: translate(-50%, -50%); width: 60px; height: 60px; border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #ffe080, #d49520);
      border: 2px solid #ffe080; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
    #egc-touch .actions { position: absolute; bottom: 32px; right: 32px;
      display: grid; grid-template-columns: repeat(3, 64px); grid-template-rows: repeat(3, 64px);
      gap: 8px; pointer-events: none; }
    #egc-touch .btn { pointer-events: auto; border-radius: 50%; display: flex;
      align-items: center; justify-content: center; font-size: 22px; color: #fff;
      background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.18), rgba(0,0,0,0.4));
      border: 2px solid rgba(255,200,60,0.5); user-select: none; touch-action: none; }
    #egc-touch .btn:active { transform: scale(0.92); }
    #egc-touch .btn.jump { background: radial-gradient(circle at 30% 30%, #5da8ff, #1a5d9e); }
    #egc-touch .btn.break { background: radial-gradient(circle at 30% 30%, #ff6464, #8e2020); }
    #egc-touch .btn.place { background: radial-gradient(circle at 30% 30%, #6ce080, #2a7030); }
    #egc-fs { position: fixed; top: 8px; right: 8px; z-index: 70; padding: 8px 14px;
      background: rgba(0,0,0,0.5); color: #ffc83c; border: 1px solid rgba(255,200,60,0.5);
      border-radius: 6px; cursor: pointer; font-size: 13px; display: none; }
    </style>
"""

MOBILE_HTML = """
    <!-- EG Craft mobile UI — injected by scripts/post_build.py -->
    <div id="egc-loader">
      <div class="logo">EG Craft</div>
      <div class="sub">من إنتاج مالك حسن عاشور © 2025</div>
      <button class="start-btn" id="egc-start">▶ ابدأ اللعب</button>
      <div class="notice">
        حقوق الملكية © 2025 مالك حسن عاشور. جميع الحقوق محفوظة.<br />
        يُمنع النسخ أو التوزيع دون إذن كتابي.
      </div>
    </div>
    <div id="egc-touch">
      <div class="joystick" id="joystick"><div class="knob" id="knob"></div></div>
      <div class="actions">
        <div class="btn" data-key="e"     style="grid-area:1/1">🎒</div>
        <div class="btn" data-key="space2" style="grid-area:1/2">🚀</div>
        <div class="btn" data-key="shift" style="grid-area:2/1">📥</div>
        <div class="btn jump"  data-key="space"  style="grid-area:2/2">⤴</div>
        <div class="btn break" data-mouse="left"  style="grid-area:2/3">⛏</div>
        <div class="btn place" data-mouse="right" style="grid-area:3/3">▣</div>
      </div>
    </div>
    <button id="egc-fs">⛶ ملء الشاشة</button>
    <script src="mobile.js" async></script>
    <script>
      // Wire up the loader: hide it once pygbag reports the game is ready,
      // and show the touch controls on mobile devices.
      (function(){
        var loader = document.getElementById('egc-loader');
        var startBtn = document.getElementById('egc-start');
        var fsBtn = document.getElementById('egc-fs');
        var touch = document.getElementById('egc-touch');
        function isMobile() {
          return /android|iphone|ipod|ipad|iemobile|blackberry|opera mini|mobile|tablet/i
            .test(navigator.userAgent || '');
        }
        function hideLoader() {
          if (loader) loader.style.display = 'none';
          if (isMobile() && touch) touch.classList.add('visible');
          if (fsBtn) fsBtn.style.display = 'block';
        }
        // Show the start button after a short delay (lets the WASM
        // loader finish initialising).
        setTimeout(function(){
          if (startBtn) startBtn.style.display = 'inline-block';
        }, 1500);
        if (startBtn) startBtn.addEventListener('click', function(){
          var el = document.documentElement;
          if (el.requestFullscreen) el.requestFullscreen();
          else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
          try { (screen.orientation||{}).lock && screen.orientation.lock('landscape'); } catch(_){}
          hideLoader();
        });
        // Auto-hide loader on desktop after 3s
        if (!isMobile()) setTimeout(hideLoader, 3000);
        // Listen for pygbag readiness (it sets window.shell when ready)
        var iv = setInterval(function(){
          if (window.shell && window.shell.uptime) {
            clearInterval(iv);
            // Don't auto-hide on mobile — wait for the start button
            if (!isMobile()) hideLoader();
          }
        }, 500);
      })();
    </script>
"""


def inject_mobile_ui(build_dir: Path) -> None:
    """Inject the EG Craft mobile UI into pygbag's generated index.html."""
    idx = build_dir / "index.html"
    text = idx.read_text(encoding="utf-8")

    # 1. Inject CSS right before </head>
    if "egcraft-mobile-css" not in text:
        text = text.replace("</head>", MOBILE_CSS + "\n</head>")

    # 2. Inject HTML right before </body>
    # Use a marker that only appears in the HTML block (not the CSS):
    # `id="egc-loader"` is the HTML attribute; `#egc-loader` is the CSS selector.
    if 'id="egc-loader"' not in text:
        text = text.replace("</body>", MOBILE_HTML + "\n</body>")

    idx.write_text(text, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: post_build.py <build_web_dir> [project_root]", file=sys.stderr)
        return 2
    build_dir = Path(argv[1]).resolve()
    project_root = Path(argv[2]).resolve() if len(argv) > 2 else Path.cwd()

    if not build_dir.is_dir():
        raise SystemExit(f"post_build: build dir {build_dir} does not exist")

    print(f"[post_build] build_dir   = {build_dir}")
    print(f"[post_build] project_root = {project_root}")

    # 1. Rename the apk to a stable name
    old_stem, new_stem = rename_apk(build_dir)
    print(f"[post_build] renamed apk: {old_stem}.apk -> {new_stem}.apk")

    # 2. Patch every reference to the old name in index.html
    patch_index_refs(build_dir, old_stem, new_stem)
    print(f"[post_build] patched index.html refs: {old_stem} -> {new_stem}")

    # 3. Copy mobile.js + manifest
    copy_web_assets(project_root, build_dir)
    print("[post_build] copied mobile.js + manifest.webmanifest")

    # 4. Inject the mobile UI into pygbag's index.html
    inject_mobile_ui(build_dir)
    print("[post_build] injected mobile UI into index.html")

    print("[post_build] done.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
