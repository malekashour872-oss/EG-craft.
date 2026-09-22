@echo off
REM ═══ EG Craft ═══
REM Copyright (c) 2025 Malik Hassan Ashour. All rights reserved.
REM Build EG-Craft.exe on Windows using the canonical spec file.
REM
REM Usage:  build.bat
REM Output: dist\EG-Craft.exe

setlocal
cd /d %~dp0

REM Ensure deps are installed in the active Python.
python -m pip install -r requirements.txt

REM Build using the .spec file. The spec handles:
REM   - bundling assets/
REM   - egcraft_rt.py runtime hook (chdir to _MEIPASS + writable dir)
REM   - hidden imports for pygame, numpy, OpenGL_accelerate
REM   - --noconsole (no black cmd window alongside the game)
pyinstaller --noconfirm --clean EG-Craft.spec

if errorlevel 1 (
    echo Build FAILED with exit code %errorlevel%.
    exit /b %errorlevel%
)

echo.
echo Build OK. Output: dist\EG-Craft.exe
endlocal
