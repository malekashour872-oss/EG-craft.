# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Survival helpers — re-exports of game.modes for backwards compat.

Spec ref: §11.2 survival systems; mode selection from main menu.
"""
from __future__ import annotations

from game.modes import Survival, SurvivalStats, GameMode

# Convenience aliases (other modules import from survival.py)
HP_MAX = Survival.__init__.__defaults__[0] if False else 20
HUNGER_MAX = 20

__all__ = ["Survival", "SurvivalStats", "GameMode",
           "HP_MAX", "HUNGER_MAX"]
