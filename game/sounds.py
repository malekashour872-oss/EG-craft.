# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Procedural audio (zero audio files).

Spec ref: §13 — SR = 22050, mono, int16. Helpers: tone(freq, dur,
decay_exp) and noise(dur, lowpass_hz, decay). Generate
pygame.mixer.Sound via pygame.sndarray.make_sound(numpy int16).
Volume via settings.sfx.

11 sound recipes (per A-13, including the missing death recipe):
- dig:           noise(0.08, 1200, 6)
- place:         tone(320, 0.05, 8) + click
- break:         noise(0.14, 800, 5)
- step:          noise(0.05, 900, 10), volume 0.4
- jump:          tone(240, 0.08, 6)
- hurt:          tone(180→90 sweep, 0.2), square-ish via harmonic
- eat:           3 × click spaced 0.15 s
- explosion:     noise(0.5, 400, 2), volume 0.9
- click_ui:      tone(600, 0.03, 10)
- craft:         tone(520, 0.1, 4) + tone(660, 0.1, 4) delayed 0.08
- death:         falling tone sweep 400→60 + noise tail (A-13)
"""
from __future__ import annotations

import logging
import math
from typing import Optional

import numpy as np

log = logging.getLogger("egcraft.sounds")

SAMPLE_RATE = 22050


def _to_int16(samples: np.ndarray) -> np.ndarray:
    return np.clip(samples * 32767, -32767, 32767).astype(np.int16)


def tone(freq: float, dur: float, decay_exp: float = 6.0,
         sr: int = SAMPLE_RATE) -> np.ndarray:
    """Pure tone with exponential decay."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    env = np.exp(-t * decay_exp)
    wave = np.sin(2 * math.pi * freq * t) * env
    return _to_int16(wave)


def tone_sweep(freq_start: float, freq_end: float, dur: float,
               decay_exp: float = 4.0,
               sr: int = SAMPLE_RATE,
               square_harmonics: bool = False) -> np.ndarray:
    """Sweep tone (e.g. hurt sound)."""
    n = int(dur * sr)
    t = np.arange(n, dtype=np.float32) / sr
    freq = freq_start + (freq_end - freq_start) * (t / dur)
    phase = 2 * math.pi * np.cumsum(freq) / sr
    wave = np.sin(phase)
    if square_harmonics:
        wave = np.sign(wave) * 0.7 + wave * 0.3
    env = np.exp(-t * decay_exp)
    return _to_int16(wave * env)


def noise(dur: float, lowpass_hz: float = 800,
          decay_exp: float = 5.0,
          sr: int = SAMPLE_RATE) -> np.ndarray:
    """White noise low-pass filtered, with exponential decay."""
    n = int(dur * sr)
    raw = np.random.uniform(-1, 1, size=n).astype(np.float32)
    # Simple one-pole low-pass
    alpha = math.exp(-2 * math.pi * (lowpass_hz / sr))
    out = np.zeros(n, dtype=np.float32)
    prev = 0.0
    for i in range(n):
        prev = (1 - alpha) * raw[i] + alpha * prev
        out[i] = prev
    t = np.arange(n, dtype=np.float32) / sr
    env = np.exp(-t * decay_exp)
    return _to_int16(out * env)


def click(sr: int = SAMPLE_RATE, dur: float = 0.02,
          freq: float = 1200.0) -> np.ndarray:
    """Short click."""
    return tone(freq, dur, decay_exp=15.0, sr=sr)


def _mix(*arrays: np.ndarray) -> np.ndarray:
    """Mix multiple int16 arrays of equal length (zero-pad)."""
    n = max(len(a) for a in arrays)
    out = np.zeros(n, dtype=np.float32)
    for a in arrays:
        out[:len(a)] += a.astype(np.float32) / 32767.0
    return _to_int16(np.clip(out, -1.0, 1.0))


def _delay(arr: np.ndarray, delay_s: float,
           sr: int = SAMPLE_RATE) -> np.ndarray:
    """Zero-pad the start of an array by delay_s seconds."""
    n = int(delay_s * sr)
    return np.concatenate([np.zeros(n, dtype=arr.dtype), arr])


# ─────────────────────────────────────────────────────────────
# 11 sound recipes (A-13)
# ─────────────────────────────────────────────────────────────
def make_dig():
    return noise(0.08, 1200, 6)


def make_place():
    return _mix(tone(320, 0.05, 8), click())


def make_break():
    return noise(0.14, 800, 5)


def make_step():
    n = noise(0.05, 900, 10)
    return (n.astype(np.float32) * 0.4).astype(np.int16)


def make_jump():
    return tone(240, 0.08, 6)


def make_hurt():
    return tone_sweep(180, 90, 0.2, decay_exp=4.0,
                       square_harmonics=True)


def make_eat():
    return _mix(_delay(click(), 0.0),
                _delay(click(), 0.15),
                _delay(click(), 0.30))


def make_explosion():
    n = noise(0.5, 400, 2)
    return (n.astype(np.float32) * 0.9).astype(np.int16)


def make_click_ui():
    return tone(600, 0.03, 10)


def make_craft():
    return _mix(tone(520, 0.1, 4),
                _delay(tone(660, 0.1, 4), 0.08))


def make_death():
    """A-13: death recipe — falling tone sweep 400→60 + noise tail."""
    sweep = tone_sweep(400, 60, 0.6, decay_exp=2.5)
    tail = noise(0.4, 200, 3)
    return _mix(sweep, _delay(tail, 0.3))


ALL_SOUNDS = {
    "dig":       make_dig,
    "place":     make_place,
    "break":     make_break,
    "step":      make_step,
    "jump":      make_jump,
    "hurt":      make_hurt,
    "eat":       make_eat,
    "explosion": make_explosion,
    "click_ui":  make_click_ui,
    "craft":     make_craft,
    "death":     make_death,
}


class SoundManager:
    """Instantiate and play procedural sounds."""

    def __init__(self, sfx_volume: float = 1.0,
                 enabled: bool = True) -> None:
        self.sfx_volume = max(0.0, min(1.0, sfx_volume))
        self.enabled = enabled
        self.sounds: dict[str, object] = {}
        if enabled:
            try:
                import pygame
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16,
                                   channels=1, buffer=512)
                self._mixer_ok = True
            except Exception as exc:  # noqa: BLE001
                log.warning("pygame.mixer init failed: %r", exc)
                self._mixer_ok = False
        else:
            self._mixer_ok = False

    def _make_sound(self, name: str):
        """Lazily build a pygame Sound from the int16 array."""
        if not self._mixer_ok:
            return None
        if name in self.sounds:
            return self.sounds[name]
        builder = ALL_SOUNDS.get(name)
        if builder is None:
            return None
        try:
            import pygame
            import pygame.sndarray as sndarray
            arr = builder()
            snd = sndarray.make_sound(arr)
            self.sounds[name] = snd
            return snd
        except Exception as exc:  # noqa: BLE001
            log.warning("Failed to make sound %s: %r", name, exc)
            return None

    def play(self, name: str) -> None:
        if not self.enabled or not self._mixer_ok:
            return
        snd = self._make_sound(name)
        if snd is not None:
            snd.set_volume(self.sfx_volume)
            snd.play()

    def set_volume(self, v: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, v))

    def all_instantiated(self) -> bool:
        """Return True if all 11 sounds can be instantiated."""
        for name in ALL_SOUNDS:
            arr = ALL_SOUNDS[name]()
            if not isinstance(arr, np.ndarray) or arr.size == 0:
                return False
        return True
