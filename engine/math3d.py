# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Hand-written math library for EG Craft (numpy-backed).

Spec ref: §5.2 — perspective, look_at, normalize, cross, dot,
rotate_y, clamp, lerp, smoothstep. Right-handed convention.
"""
from __future__ import annotations

import math
from typing import Tuple

import numpy as np

Vec3 = np.ndarray  # shape (3,) float32
Mat4 = np.ndarray  # shape (4, 4) float32


def vec3(x: float, y: float, z: float) -> Vec3:
    return np.array([x, y, z], dtype=np.float32)


def normalize(v: Vec3) -> Vec3:
    n = float(np.linalg.norm(v))
    if n < 1e-12:
        return v.copy()
    return (v / n).astype(np.float32)


def cross(a: Vec3, b: Vec3) -> Vec3:
    return np.cross(a, b).astype(np.float32)


def dot(a: Vec3, b: Vec3) -> float:
    return float(np.dot(a, b))


def rotate_y(angle_rad: float) -> Mat4:
    """4×4 rotation matrix around the Y axis."""
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return np.array([
        [ c, 0.0,  s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0,  c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)


def translate(x: float, y: float, z: float) -> Mat4:
    return np.array([
        [1.0, 0.0, 0.0, x],
        [0.0, 1.0, 0.0, y],
        [0.0, 0.0, 1.0, z],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)


def scale(sx: float, sy: float, sz: float) -> Mat4:
    return np.array([
        [sx,  0.0, 0.0, 0.0],
        [0.0,  sy, 0.0, 0.0],
        [0.0, 0.0,  sz, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)


def perspective(fov_deg: float, aspect: float,
                near: float = 0.1, far: float = 1000.0) -> Mat4:
    """Standard GL right-handed perspective matrix."""
    fov_rad = math.radians(fov_deg)
    f = 1.0 / math.tan(fov_rad / 2.0)
    nf = 1.0 / (near - far)
    return np.array([
        [f / aspect, 0.0, 0.0,                  0.0],
        [0.0,        f,   0.0,                  0.0],
        [0.0,        0.0, (far + near) * nf,    2.0 * far * near * nf],
        [0.0,        0.0, -1.0,                0.0],
    ], dtype=np.float32)


def look_at(eye: Vec3, center: Vec3, up: Vec3 | None = None) -> Mat4:
    """Right-handed view matrix (camera looking from eye to center)."""
    if up is None:
        up = vec3(0.0, 1.0, 0.0)
    f = normalize(center - eye)
    s = normalize(cross(f, up))
    u = cross(s, f)
    return np.array([
        [ s[0],  u[1], -f[0], -dot(s, eye)],
        [ s[1],  u[1], -f[1], -dot(u, eye)],
        [ s[2],  u[2], -f[2],  dot(f, eye)],
        [ 0.0,   0.0,   0.0,   1.0],
    ], dtype=np.float32)


def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else (hi if v > hi else v)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_vec3(a: Vec3, b: Vec3, t: float) -> Vec3:
    return (a + (b - a) * t).astype(np.float32)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    if edge1 == edge0:
        return 0.0
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def deg2rad(d: float) -> float:
    return math.radians(d)


def rad2deg(r: float) -> float:
    return math.degrees(r)


def mat4_identity() -> Mat4:
    return np.eye(4, dtype=np.float32)


def mat4_mul(a: Mat4, b: Mat4) -> Mat4:
    return (a @ b).astype(np.float32)


def mat4_transpose(m: Mat4) -> Mat4:
    return m.T.astype(np.float32)


def extract_translation(m: Mat4) -> Vec3:
    return np.array([m[0, 3], m[1, 3], m[2, 3]], dtype=np.float32)


def extract_forward(m: Mat4) -> Vec3:
    # Third column, negated for right-handed view
    return vec3(-m[0, 2], -m[1, 2], -m[2, 2])


def extract_right(m: Mat4) -> Vec3:
    return vec3(m[0, 0], m[1, 0], m[2, 0])


def extract_up(m: Mat4) -> Vec3:
    return vec3(m[0, 1], m[1, 1], m[2, 1])
