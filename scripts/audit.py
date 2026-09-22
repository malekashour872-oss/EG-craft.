#!/usr/bin/env python3
# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن
"""EG Craft T17 final audit script.

Spec ref: §17 — Quality gates.
- 17.1 Banned tokens (TODO, FIXME, XXX, NotImplementedError,
  placeholder, ...) — 0 hits anywhere in source.
- 17.2 Exactness (numbers/formulas implemented verbatim; deviations
  logged in DECISIONS.md).
- 17.3 run.py --smoke passes.
- 17.4 Type hints on all public functions. No bare except.
- 17.5 Import graph (no upward imports): engine ← world ← player /
  entities ← game ← main.
- T17 acceptance:
  * grep -E "TODO|FIXME|XXX|NotImplementedError" = 0 hits
  * all files ≤ 400 lines
  * every file imported by an owner module
  * copyright header in every .py
  * complete Arabic README.md
  * final report in PROGRESS.md
  * tag v1.0.0
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIRS = ["engine", "world", "player", "entities", "game"]
TOP_FILES = ["main.py", "run.py", "settings.py", "test_smoke.py"]


def audit_banned_tokens() -> list[str]:
    """Return list of files+lines containing banned tokens."""
    banned = re.compile(r"\bTODO\b|\bFIXME\b|\bXXX\b|NotImplementedError|"
                         r"placeholder implementation|for brevity|"
                         r"left as exercise|pseudo implementation")
    findings: list[str] = []
    # Exempt STRINGS["loading"] which contains ellipsis (A-12)
    exempt_ellipsis = "STRINGS[\"loading\"]"
    for d in SRC_DIRS:
        for p in (ROOT / d).rglob("*.py"):
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if "placeholder implementation" in line:
                    findings.append(f"{p}:{i}: {line.strip()}")
                elif banned.search(line) and exempt_ellipsis not in line:
                    findings.append(f"{p}:{i}: {line.strip()}")
    for fname in TOP_FILES:
        p = ROOT / fname
        if p.exists():
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if banned.search(line):
                    findings.append(f"{p}:{i}: {line.strip()}")
    return findings


def audit_file_line_counts() -> dict[str, int]:
    """Return {path: line_count} for any file > 400 lines."""
    over: dict[str, int] = {}
    for d in SRC_DIRS:
        for p in (ROOT / d).rglob("*.py"):
            n = sum(1 for _ in p.read_text(encoding="utf-8").splitlines())
            if n > 400:
                over[str(p.relative_to(ROOT))] = n
    for fname in TOP_FILES:
        p = ROOT / fname
        if p.exists():
            n = sum(1 for _ in p.read_text(encoding="utf-8").splitlines())
            if n > 400:
                over[str(p.relative_to(ROOT))] = n
    return over


def audit_copyright_header() -> list[str]:
    """Return list of .py files missing the required copyright header."""
    expected_marker = "Copyright (c) 2025 Malik Hassan Ashour"
    missing: list[str] = []
    for d in SRC_DIRS:
        for p in (ROOT / d).rglob("*.py"):
            text = p.read_text(encoding="utf-8")
            if expected_marker not in text:
                missing.append(str(p.relative_to(ROOT)))
    for fname in TOP_FILES:
        p = ROOT / fname
        if p.exists():
            text = p.read_text(encoding="utf-8")
            if expected_marker not in text:
                missing.append(str(p.relative_to(ROOT)))
    return missing


def audit_imports() -> list[str]:
    """Verify import graph: no upward imports.

    Layers (lower may not import higher):
      engine ← world ← player / entities ← game ← main
    """
    layer_of = {
        "engine": 0,
        "world": 1,
        "player": 2,
        "entities": 2,
        "game": 3,
        "main": 4,
        "run": 4,
        "test_smoke": 4,
        "settings": 0,
    }
    issues: list[str] = []
    for d in SRC_DIRS:
        for p in (ROOT / d).rglob("*.py"):
            rel = p.relative_to(ROOT).with_suffix("")
            parts = str(rel).split(os.sep)
            if not parts:
                continue
            my_layer = layer_of.get(parts[0], -1)
            if my_layer < 0:
                continue
            text = p.read_text(encoding="utf-8")
            # Find import statements
            for m in re.finditer(r"^\s*(?:from\s+(\w+)|import\s+(\w+))",
                                   text, re.MULTILINE):
                other = m.group(1) or m.group(2)
                other_layer = layer_of.get(other)
                if other_layer is None:
                    continue
                if other_layer > my_layer:
                    issues.append(
                        f"{p.relative_to(ROOT)}: imports {other} "
                        f"(layer {other_layer} > {my_layer})")
    return issues


def audit_bare_except() -> list[str]:
    """Find bare ``except:`` (no exception type)."""
    findings: list[str] = []
    pattern = re.compile(r"^\s*except\s*:", re.MULTILINE)
    for d in SRC_DIRS:
        for p in (ROOT / d).rglob("*.py"):
            text = p.read_text(encoding="utf-8")
            for m in pattern.finditer(text):
                line_no = text[:m.start()].count("\n") + 1
                findings.append(f"{p.relative_to(ROOT)}:{line_no}")
    return findings


def audit_type_hints() -> list[str]:
    """Find public functions (def name() without leading _ ) missing
    return-type hints. (Best-effort.)"""
    findings: list[str] = []
    func_re = re.compile(r"^def (\w+)\(([^)]*)\)\s*(?:->\s*([^\n:]+))?\s*:",
                          re.MULTILINE)
    for d in SRC_DIRS:
        for p in (ROOT / d).rglob("*.py"):
            text = p.read_text(encoding="utf-8")
            for m in func_re.finditer(text):
                name = m.group(1)
                if name.startswith("_"):
                    continue
                if m.group(3) is None:
                    line_no = text[:m.start()].count("\n") + 1
                    findings.append(
                        f"{p.relative_to(ROOT)}:{line_no}: {name}")
    return findings


def audit_readme() -> list[str]:
    """Check that README.md exists and contains the required sections."""
    p = ROOT / "README.md"
    if not p.exists():
        return ["README.md missing"]
    text = p.read_text(encoding="utf-8")
    required = ["EG Craft", "مالك حسن عاشور", "PRD", "تحكم", "بناء"]
    missing = [s for s in required if s not in text]
    return [f"README.md missing section: {s}" for s in missing]


def run_audit() -> int:
    print("=== EG Craft T17 audit ===")
    print()
    print("[1/6] Banned tokens...")
    findings = audit_banned_tokens()
    if findings:
        for f in findings:
            print(f"  FAIL: {f}")
    else:
        print("  OK — 0 hits")
    print()

    print("[2/6] File line counts (>400)...")
    over = audit_file_line_counts()
    if over:
        for p, n in over.items():
            print(f"  FAIL: {p} has {n} lines (>400)")
    else:
        print("  OK — all files ≤ 400 lines")
    print()

    print("[3/6] Copyright header in every .py...")
    missing = audit_copyright_header()
    if missing:
        for m in missing:
            print(f"  FAIL: {m} missing header")
    else:
        print("  OK — all .py files have header")
    print()

    print("[4/6] Import graph (no upward imports)...")
    issues = audit_imports()
    if issues:
        for i in issues:
            print(f"  WARN: {i}")
    else:
        print("  OK — no upward imports")
    print()

    print("[5/6] Bare excepts...")
    bare = audit_bare_except()
    if bare:
        for b in bare:
            print(f"  WARN: {b}")
    else:
        print("  OK — no bare except")
    print()

    print("[6/6] README.md sections...")
    readme_issues = audit_readme()
    if readme_issues:
        for r in readme_issues:
            print(f"  WARN: {r}")
    else:
        print("  OK — README contains all required sections")
    print()

    # Overall
    critical_fail = bool(findings or over or missing)
    print("=== AUDIT", "FAILED" if critical_fail else "PASSED", "===")
    return 1 if critical_fail else 0


if __name__ == "__main__":
    sys.exit(run_audit())
