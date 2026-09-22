#!/usr/bin/env bash
# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour. All rights reserved.
# Build EG-Craft binary on Linux/macOS using the canonical spec file.
#
# Usage:  ./build.sh
# Output: dist/EG-Craft
set -euo pipefail
cd "$(dirname "$0")"

# Ensure deps are installed in the active Python.
python3 -m pip install -r requirements.txt

# Build using the .spec file. The spec handles:
#   - bundling assets/
#   - egcraft_rt.py runtime hook (chdir to _MEIPASS + writable dir)
#   - hidden imports for pygame, numpy, OpenGL_accelerate
#   - --noconsole (no terminal window alongside the game)
pyinstaller --noconfirm --clean EG-Craft.spec

echo
echo "Build OK. Output: dist/EG-Craft"
