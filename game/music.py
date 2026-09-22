# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Procedural ambient music.

Spec ref: §13.2 — 60 s ambient loop generated at startup: chord pad
Am → F → C → G, 15 s each. Per chord: 3 sine partials per note +
slow tremolo LFO 0.15 Hz + gentle low-pass noise "wind" at volume
0.05. Render to numpy int16 stereo → make_sound, loop = -1, volume =
settings.music.
"""
from __future__ import annotations

import logging
import math

import numpy as np

from game.sounds import SAMPLE_RATE, _to_int16

log = logging.getLogger("egcraft.music")

CHORD_DURATION = 15.0
TOTAL_DURATION = 60.0  # 4 chords × 15 s
LFO_FREQ = 0.15
WIND_VOLUME = 0.05

# Chord definitions (notes in Hz)
CHORDS = [
    ("Am", [220.0, 261.63, 329.63]),  # A3 C4 E4
    ("F",  [174.61, 220.0, 261.63]),  # F3 A3 C4
    ("C",  [261.63, 329.63, 392.0]),  # C4 E4 G4
    ("G",  [196.0, 246.94, 293.66]),  # G3 B3 D4
]


def _render_chord(notes: list[float], duration: float,
                  sr: int = SAMPLE_RATE) -> np.ndarray:
    """Render a chord as 3 sine partials + tremolo LFO."""
    n = int(duration * sr)
    t = np.arange(n, dtype=np.float32) / sr
    lfo = 0.5 + 0.5 * np.sin(2 * math.pi * LFO_FREQ * t)
    wave = np.zeros(n, dtype=np.float32)
    for freq in notes:
        wave += np.sin(2 * math.pi * freq * t) / len(notes)
    # Tremolo
    wave *= 0.6 + 0.4 * lfo
    # Wind noise
    rng = np.random.default_rng(0xBEE7)
    wind = rng.uniform(-1, 1, size=n).astype(np.float32)
    # Low-pass the wind
    alpha = math.exp(-2 * math.pi * (400 / sr))
    filtered = np.zeros(n, dtype=np.float32)
    prev = 0.0
    for i in range(n):
        prev = (1 - alpha) * wind[i] + alpha * prev
        filtered[i] = prev
    wave += filtered * WIND_VOLUME
    return wave


def render_music(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Render the full 60 s loop."""
    chunks = []
    for _, notes in CHORDS:
        chunks.append(_render_chord(notes, CHORD_DURATION, sr=sr))
    return np.concatenate(chunks)


class MusicManager:
    """Ambient loop player."""

    def __init__(self, music_volume: float = 0.4,
                 enabled: bool = True) -> None:
        self.music_volume = max(0.0, min(1.0, music_volume))
        self.enabled = enabled
        self._sound = None
        self._mixer_ok = False
        if enabled:
            try:
                import pygame
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16,
                                   channels=2, buffer=1024)
                self._mixer_ok = True
            except Exception as exc:  # noqa: BLE001
                log.warning("music mixer init failed: %r", exc)
                self._mixer_ok = False

    def start(self) -> None:
        if not self._mixer_ok or not self.enabled:
            return
        if self._sound is None:
            try:
                import pygame
                import pygame.sndarray as sndarray
                mono = render_music()
                stereo = np.column_stack([mono, mono])
                self._sound = sndarray.make_sound(
                    stereo.astype(np.int16))
            except Exception as exc:  # noqa: BLE001
                log.warning("music make_sound failed: %r", exc)
                return
        self._sound.set_volume(self.music_volume)
        self._sound.play(loops=-1)

    def stop(self) -> None:
        if self._sound is not None:
            self._sound.stop()

    def set_volume(self, v: float) -> None:
        self.music_volume = max(0.0, min(1.0, v))
        if self._sound is not None:
            self._sound.set_volume(self.music_volume)
