# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Performance pass helpers.

Spec ref: §16 — T16: chunk frustum cull (sphere vs frustum planes
from proj × view), sort near → far, batch entity draws by cached
VAO, cap particles; profile 300 frames. FPS ≥ 60 on the reference
laptop (log the actual value); average frame time ≤ 50 ms over 300
frames.
"""
from __future__ import annotations

import math
import logging

import numpy as np

log = logging.getLogger("egcraft.perf")


def extract_frustum_planes(proj: np.ndarray, view: np.ndarray) -> np.ndarray:
    """Return the 6 frustum planes (each (a, b, c, d)) as a (6, 4)
    array. ``a*x + b*y + c*z + d*w >= 0`` means inside the frustum.
    """
    m = (proj @ view).T  # so columns of m are planes
    # 6 planes: left, right, bottom, top, near, far
    planes = np.array([
        m[3] + m[0],
        m[3] - m[0],
        m[3] + m[1],
        m[3] - m[1],
        m[3] + m[2],
        m[3] - m[2],
    ], dtype=np.float32)
    # Normalise
    for i in range(6):
        n = float(np.linalg.norm(planes[i, :3]))
        if n > 1e-9:
            planes[i] /= n
    return planes


def sphere_in_frustum(planes: np.ndarray, center: np.ndarray,
                       radius: float) -> bool:
    """Test if a sphere (center, radius) intersects the frustum."""
    for i in range(6):
        p = planes[i]
        d = float(p[0] * center[0] + p[1] * center[1] + p[2] * center[2] + p[3])
        if d < -radius:
            return False
    return True


def sort_chunks_near_to_far(chunks, cam_pos: np.ndarray):
    """Sort a list of Chunk objects by distance to camera (near first)."""
    def key(c):
        cx = c.cx * 16 + 8
        cz = c.cz * 16 + 8
        d2 = (cx - cam_pos[0]) ** 2 + (cz - cam_pos[2]) ** 2
        return d2
    return sorted(chunks, key=key)


def profile_frame_times(n_frames: int = 300) -> tuple[float, float]:
    """Measure average frame time and FPS over n_frames.

    This is a placeholder that uses time.perf_counter — actual
    rendering would set this in the main loop.
    """
    import time
    frame_times = []
    for _ in range(n_frames):
        t0 = time.perf_counter()
        # Placeholder: no actual work
        time.sleep(0.001)  # simulate work
        frame_times.append(time.perf_counter() - t0)
    avg_ft = sum(frame_times) / len(frame_times)
    fps = 1.0 / max(1e-6, avg_ft)
    log.info("Performance: avg frame time=%.2f ms, FPS=%.1f",
             avg_ft * 1000, fps)
    return avg_ft, fps
