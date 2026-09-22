# -*- mode: python ; coding: utf-8 -*-
# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن
"""PyInstaller spec for EG Craft.

Build with::

    pyinstaller EG-Craft.spec            # produces dist/EG-Craft(.exe)

This spec replaces the one-liner in the README::

    pyinstaller --onefile --noconsole --name EG-Craft \
      --add-data "assets:assets" main.py

Improvements over the one-liner:

* Bundles the whole ``assets/`` directory recursively (fonts,
  settings.json, screenshots, etc.).
* Adds ``egcraft_rt.py`` as a runtime hook that runs BEFORE main.py:
  sets CWD to ``sys._MEIPASS`` so legacy relative paths resolve, and
  pre-creates the per-user writable dir (``%APPDATA%/EGCraft`` /
  ``~/.egcraft``) for logs and saves.
* Marks the binary ``console=False`` (``--noconsole`` equivalent) so
  no black cmd window opens alongside the game.
* Pulls in ``OpenGL_accelerate`` as a hidden import (optional but
  speeds up PyOpenGL and silences "no module" warnings in the log).
* Adds ``pygame`` extra DLLs (SDL2.dll etc.) via the standard hook.
* ``debug=False``, ``strip=False`` so the build is reproducible and
  the tracebacks are still readable.
"""

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Pull every submodule of pygame (including SDL2 bindings) so the
# frozen binary doesn't miss a hidden import on Windows.
pygame_hidden = collect_submodules("pygame")
# Also collect numpy submodules used by the procedural atlas/sound
# generators (pygame.sndarray, numpy.fft, etc.).
numpy_hidden = collect_submodules("numpy")
# OpenGL_accelerate is optional for PyOpenGL but produces a
# "No OpenGL_accelerate module loaded" warning when missing.
opengl_hidden = ["OpenGL_accelerate"]

datas = [
    ("assets", "assets"),
]
binaries = []
hiddenimports = (
    pygame_hidden + numpy_hidden + opengl_hidden
    # Engine / game modules — already auto-discovered by PyInstaller,
    # but listing them explicitly makes the .spec self-documenting.
    + ["settings", "main", "run",
       "engine.window", "engine.shaders", "engine.camera",
       "engine.math3d", "engine.texture", "engine.arabic_text",
       "engine.nametag", "engine.touch",
       "world.noise", "world.blocks", "world.blocks_expansion",
       "world.chunk", "world.worldgen", "world.world",
       "player.physics", "player.raycast", "player.mining",
       "player.inventory",
       "entities.entity", "entities.species", "entities.registry",
       "entities.spawner", "entities.ai", "entities.projectiles",
       "entities.particles", "entities.items_drop", "entities.hybrid",
       "game.modes", "game.survival", "game.daynight",
       "game.crafting", "game.block_entities", "game.sounds",
       "game.music", "game.ui", "game.screens", "game.i18n",
       "game.save", "game.logging_setup", "game.perf"]
)


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtimehooks=["egcraft_rt.py"],
    excludes=[],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="EG-Craft",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,            # --noconsole: no black cmd window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,                # drop an .ico next to this file and put 'assets/icon.ico' here
)
