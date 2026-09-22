# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

# EG Craft — لعبة صندوق الرمال العربية

**النسخة التجارية v2.0**

**حقوق الملكية** — © 2025 **مالك حسن عاشور**. جميع الحقوق المملوكة محفوظة.
هذه اللعبة ملكية حصرية؛ يُمنع النسخ أو التوزيع أو التعديل دون إذن كتابي
من المالك.

---

## 1. نظرة عامة / Overview

EG Craft is a voxel sandbox game (Minecraft-style) written from scratch
in Python 3.10+ using raw OpenGL 3.3 Core. The engine, world
generation, Perlin noise, meshing, physics, entity AI, hybrid
genetics, UI, save format, and audio synthesis are **hand-written** —
no third-party game engine, no asset files.

### v2.0 Commercial Edition — what's new
- **Mobile-first deployment**: auto-detects mobile browsers when
  deployed to Vercel/GitHub Pages; auto-enables touch controls
  (joystick + action buttons + look-area + hotbar mini-selector) and
  prompts the player to enter fullscreen + lock landscape orientation
  + unlock audio on first tap.
- **Expanded block catalogue**: 104 blocks (was 21) — obsidian,
  netherrack, end_stone, glowstone, soul_sand, bricks, sandstone,
  snow, ice, cactus, pumpkin, bookshelf, jukebox, brewing_stand,
  enchanting_table, lever, redstone_lamp, redstone_wire,
  redstone_torch, repeater, piston, sticky_piston, furnace_lit,
  anvil, cauldron, lantern, dragon_egg, lava, magma_block,
  emerald_ore, emerald_block, deepslate + 5 deepslate-ore variants,
  moss_block, azalea, calcite, tuff, basalt, blackstone, netherite,
  crying_obsidian, respawn_anchor, amethyst, budding_amethyst,
  dripstone, powder_snow, note_block, glass_pane, iron_bars, doors,
  fences, slabs ×5, stairs ×5, buttons, pressure plates, rails ×4,
  flowers ×3, mushrooms ×2, vines, lily_pads, ferns.
- **Expanded item catalogue**: ~150 new items — netherite, emerald,
  quartz, amethyst, buckets (water/lava/milk), fish (cod/salmon/
  tropical/pufferfish), bread, cookies, cake, pumpkin_pie, apple,
  golden_apple, sugar, paper, books (×4), map, compass, clock,
  spyglass, ender_pearl, ender_eye, blaze_rod, ghast_tear,
  nether_star, prismarine_shard, shulker_shell, scute, phantom
  membrane, heart_of_sea, nautilus_shell, conduit, dragon_breath,
  totem_of_undying, shulker_box, flower_pot, name_tag, saddle, lead,
  horse_armor ×3, shears, flint_and_steel, fire_charge, end_crystal,
  dragon_head, turtle_helmet, trident, shield, bow, crossbow,
  firework_rocket, firework_star, ink_sac, lapis_lazuli, honey ×3,
  22 potions, 15 music discs.
- **Expanded biomes**: jungle, savanna, taiga, swamp, mountains,
  mushroom, ocean, deep_ocean (extends the spec's desert/forest/
  plains).
- **Expanded species**: 72 base species (was 45) → registry now
  **1062 entries** (was 1035). New: villagers ×6, axolotl, allay,
  panda, frog, tadpole, goat_screaming, strider, hoglin,
  piglin_brute, warden, iron_golem, snow_golem, shulker,
  ender_dragon (boss), wither (boss), elder_guardian (boss),
  cod_fish, salmon_fish, tropical_fish, pufferfish.
- **Redstone-like automation**: lever, button, pressure plate,
  repeater, lamp, piston + sticky_piston (stubs).
- **Enchanting + brewing stubs**: enchanting_table, brewing_stand,
  22 potion recipes.
- **Boss system stubs**: ender_dragon (HP 200), wither (HP 300),
  elder_guardian (HP 120), warden (HP 250).
- **Commercial polish**: save slots, settings profiles, statistics
  tracker (play_time, blocks_broken, blocks_placed, mobs_killed,
  deaths, distance_walked), music variations, branding logo,
  version 2.0.0-commercial.
- **Multi-platform CI**: builds for Windows + Linux + macOS +
  pygbag web bundle (mobile-first).

### Key features (v1.0 baseline)
- **21 block IDs** (0–20): grass, dirt, stone, cobble, sand, gravel,
  log, leaves, planks, glass, water, bedrock, coal/iron/gold/diamond
  ores, crafting_table, furnace, chest, torch.
- **45 base species** (20 passive + 25 hostile) + **990 hybrid pairs**
  = **1035 registered** species with deterministic genetics.
- **Procedural textures** (256×256 atlas, 32 tiles) and **procedural
  audio** (11 sounds + 60 s ambient music loop) — zero binary asset
  files.
- **Arabic UI 100%**: hand-written Arabic text shaper (no
  arabic_reshaper / python-bidi), right-to-left layout, Cairo font.
- **Survival + Creative** modes, day/night cycle (600 s), sun/moon,
  stars, fog, underwater tint.
- **Desktop build**: Windows / Linux / macOS EXE via PyInstaller.
  **Web build**: pygbag + GitHub Pages + Vercel (mobile-aware).

---

## 2. PRD / Build specification

The full build specification is in
**`EG-Craft-Master-Build-Specification.pdf`** (22 pages, 18 tasks
T0–T17). Every numeric value, formula, and string is exact. The v2.0
commercial edition extends (not replaces) the spec — see
**DECISIONS.md → L-2** for the full expansion log.

### Runtime stack
- Python 3.10+
- pygame 2.5.2 (window, input, audio playback)
- PyOpenGL 3.1.7 (raw GL 3.3 Core bindings)
- numpy 1.26.4 (math, world data, procedural generation)
- pyinstaller 6.3.0 (desktop EXE build)
- pygbag 0.9.1 (web build, mobile-first)

### Forbidden
Any game engine or rendering framework (Ursina, Panda3D, ModernGL,
Pyglet, Arcade, Cocos, Kivy), fixed-function pipeline
(glBegin/glEnd/glVertex), GLUT, immediate mode.

---

## 3. التحكم / Controls

### Desktop

| الإجراء | المفتاح | Action | Key |
|---|---|---|---|
| تحريك اللاعب | W A S D | Move | W A S D |
| القفز | مسافة | Jump | Space |
| الركض | Ctrl (مع W) | Sprint | Ctrl (with W) |
| التسلل | Shift | Sneak | Shift |
| الطيران (الإبداعي) | مسافة ×2 | Toggle fly | Double-tap Space |
| النظر | الماوس | Look | Mouse |
| تكسير الكتلة | زر الفأرة الأيسر | Mine block | LMB (hold) |
| وضع كتلة | زر الفأرة الأيمن | Place block | RMB |
| المخزون | E | Inventory | E |
| سجل الكائنات | B | Species log | B |
| حفظ | F5 | Save | F5 |
| تحميل | F9 | Load | F9 |
| إيقاف مؤقت | ESC | Pause | ESC |
| تصحيح F3 | F3 | Debug overlay | F3 |
| اختيار الشريط | 1–9 / عجلة الماوس | Hotbar | 1–9 / wheel |

### Mobile (touch — auto-detected on phone browsers)

| الإجراء | المدخل | Action | Input |
|---|---|---|---|
| تحريك اللاعب | ذراع التحكم الأيسر | Move | left joystick |
| النظر | السحب على اليمين | Look | swipe right area |
| القفز | زر ⤴ | Jump | tap ⤴ button |
| التسلل | زر 📥 | Sneak | hold 📥 button |
| الطيران | زر 🚀 | Toggle fly | tap 🚀 button |
| تكسير الكتلة | زر ⛏ | Mine block | hold ⛏ button |
| وضع كتلة | زر ▣ | Place block | tap ▣ button |
| المخزون | زر 🎒 | Inventory | tap 🎒 button |
| اختيار الشريط | شريط 1-9 | Hotbar | tap slot 1-9 |

When you open EG Craft on a phone, you'll see the splash loader with
an "ابدأ اللعب" button. Tapping it:
1. Requests fullscreen (so the address bar is hidden).
2. Locks landscape orientation.
3. Unlocks the audio context (browsers require a user gesture).
4. Hides the loader and reveals the touch UI.

---

## 4. البناء / Build

### Setup
```bash
pip install -r requirements.txt
```

### Run (desktop)
```bash
python main.py                 # default seed 12345, 1280×720
python run.py --debug          # debug logging + screenshots
python run.py --seed 42 --res 1920x1080
```

### Smoke tests
```bash
python run.py --smoke
# or
python test_smoke.py
```
Headless assertions: boot, worldgen, meshing, DDA, physics, crafting,
genetics, registry (≥1035), shaping, daynight, save/load.

### Final audit (T17)
```bash
python scripts/audit.py
```
Checks banned tokens, file line counts ≤400, copyright header in
every .py, no upward imports, no bare except, README sections.

### Build desktop binaries (Windows/Linux/macOS)
```bash
pyinstaller --onefile --noconsole --name EG-Craft \
  --add-data "assets:assets" main.py
```

### Build web (pygbag, mobile-first)
```bash
pip install pygbag==0.9.1
pygbag --build .
python scripts/post_build.py build/web .
# Output: build/web/  — deploy to GitHub Pages or Vercel
```

`scripts/post_build.py` performs three essential post-build steps:
1. Renames the generated `<folder>.apk` to a stable `egcraft.apk`
   (pygbag 0.9.1 ignores `--app_name`, so the apk name is otherwise
   derived from the build folder — unpredictable on Vercel).
2. Patches every reference to the old apk name inside `index.html`.
3. Injects the EG Craft mobile UI (splash, joystick, action buttons)
   into pygbag's generated `index.html` and copies `mobile.js` +
   `manifest.webmanifest` into the build output.

### Deploy to Vercel
Push the repo to GitHub, then import on Vercel. `vercel.json` defines:
- `buildCommand`: `pip install --user pygbag==0.9.1 && python -m pygbag --build . && python scripts/post_build.py build/web .`
- `outputDirectory`: `build/web`
- `functions`: `{}` (no serverless functions — this is a static deploy)
- `cleanUrls`: true
- `rewrites`: SPA fallback to `/index.html`
- `headers`: COOP/COEP for Emscripten worker isolation + long-cache
  headers for `.apk` / `.js` / `.wasm` assets

> **Vercel + Python note**: Vercel auto-detects `main.py` +
> `requirements.txt` at the project root and tries to import `main`
> as a Python serverless function, expecting an `app` object. EG Craft
> is NOT a serverless function — it's a static pygbag bundle. To
> satisfy Vercel's build-time check, `main.py` exposes a minimal
> ASGI v3.0 stub named `app` that is never invoked at runtime.

---

## 5. البنية / Project layout

```
EG-Craft/
  main.py            # async entry; splash → menu → game; touch bridge
  run.py             # CLI: --smoke | --debug | --seed N | --res WxH
  settings.py        # Settings dataclass
  test_smoke.py      # headless assertions
  LICENSE  COPYRIGHT.md  README.md  PROGRESS.md  DECISIONS.md  vercel.json
  requirements.txt  .gitignore
  engine/    window.py shaders.py camera.py math3d.py texture.py
             arabic_text.py nametag.py perf.py touch.py
  world/     noise.py blocks.py blocks_expansion.py chunk.py
             worldgen.py world.py
  player/    physics.py raycast.py mining.py inventory.py
  entities/  entity.py species.py registry.py spawner.py ai.py
             projectiles.py particles.py items_drop.py hybrid.py
  game/      modes.py survival.py daynight.py crafting.py
             block_entities.py sounds.py music.py ui.py screens.py
             i18n.py save.py logging_setup.py perf.py
  assets/fonts/  assets/saves/  assets/screenshots/
  web/       index.html  mobile.js  manifest.webmanifest  (pygbag output)
  .github/workflows/build.yml  deploy.yml
  scripts/   download_fonts.py  audit.py
```

---

## 6. حقوق الملكية / Rights

© 2025 **مالك حسن عاشور**. جميع الحقوق المملوكة محفوظة.

This game and all creative and source works associated with it are
proprietary to Malik Hassan Ashour. Copying, distribution, modification,
or commercial exploitation without written permission from the owner
is prohibited. The notices appear in: the window title, splash
screen, main-menu footer, rights screen, LICENSE, COPYRIGHT.md, and
every source file's header.

Contact: `contact: [owner email]`

---

## 7. النشر على Vercel — Mobile auto-detection

When the project is deployed to Vercel (or any static host),
`web/index.html` is the SPA shell that loads the pygbag bundle +
`web/mobile.js`. The JS detects mobile browsers via:

1. **User-Agent**: matches `android|iphone|ipod|ipad|iemobile|
   blackberry|opera mini|mobile|tablet`
2. **Touch capability**: `ontouchstart in window`,
   `navigator.maxTouchPoints > 0`
3. **Viewport**: `width <= 900 && height <= 900`
4. **Pixel ratio**: `devicePixelRatio >= 1.5` (high-DPI phone)

On detection, the loader:
1. Shows touch-controls overlay (joystick + action buttons + look-area
   + hotbar mini-selector)
2. Shows a fullscreen button (⛶ ملء الشاشة) in the corner
3. Displays an "ابدأ اللعب" button that:
   - Enters fullscreen (`requestFullscreen` / webkit variants)
   - Locks landscape orientation (`screen.orientation.lock('landscape')`)
   - Unlocks AudioContext (browsers require user gesture for audio)
   - Hides the loader

On desktop, the loader auto-hides after 800 ms and WASD + mouse
are the only controls.

The Python side (`engine/touch.py`) polls `window.EGC.input` via
pygbag's `import js` interop and synthesises the same key/mouse
events that pygame uses. The bridge is a no-op on desktop.
