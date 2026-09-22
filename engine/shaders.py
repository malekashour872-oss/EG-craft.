# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Shader source strings and compile/link helpers.

Spec ref: §5.4 — PROGRAM_MAIN and PROGRAM_LINES, GLSL 330 core.
PROGRAM_MAIN uniforms: u_proj, u_view, u_model (mat4); u_sky_color
(vec3); u_fog_start, u_fog_end (float); u_daylight (float); u_sun_dir
(vec3); u_lights[32] (vec4 xyz+radius); u_light_count, u_time
(int, float); u_underwater (int); u_atlas (sampler2D, A-10).
Attributes: a_pos (vec3), a_uv (vec2), a_light (float).
Fragment stages: 1) sample, 2) lighting, 3) final mix, 4) fog, 5)
underwater override.
"""
from __future__ import annotations

import ctypes
from typing import Any

from OpenGL import GL as gl

# ─────────────────────────────────────────────────────────────
# PROGRAM_MAIN — voxel world shader
# ─────────────────────────────────────────────────────────────
VS_MAIN = """
#version 330 core
layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec2 a_uv;
layout(location = 2) in float a_light;

uniform mat4 u_proj;
uniform mat4 u_view;
uniform mat4 u_model;

out vec2 v_uv;
out float v_light;
out vec3 v_world_pos;

void main() {
    vec4 world = u_model * vec4(a_pos, 1.0);
    v_world_pos = world.xyz;
    v_uv = a_uv;
    v_light = a_light;
    gl_Position = u_proj * u_view * world;
}
"""

FS_MAIN = """
#version 330 core
in vec2 v_uv;
in float v_light;
in vec3 v_world_pos;

uniform vec3 u_sky_color;
uniform float u_fog_start;
uniform float u_fog_end;
uniform float u_daylight;
uniform vec3 u_sun_dir;
uniform vec4 u_lights[32];
uniform int u_light_count;
uniform float u_time;
uniform int u_underwater;
uniform sampler2D u_atlas;
uniform vec3 u_cam_pos;     // used for distance-based fog

out vec4 frag_color;

void main() {
    // 1. sample atlas
    vec4 tex = texture(u_atlas, v_uv);
    if (tex.a < 0.1) discard;

    // 2. base lighting
    float light = v_light * u_daylight;
    // torch-style point lights
    for (int i = 0; i < u_light_count; ++i) {
        vec4 L = u_lights[i];
        float r = L.w;
        float d = distance(L.xyz, v_world_pos);
        if (d < r) {
            light += 0.9 * (1.0 - d / r);
        }
    }

    // 3. final colour (clamp ambient floor to 0.04)
    vec3 final_color = tex.rgb * clamp(light, 0.04, 1.0);

    // 4. fog
    float dist = distance(u_cam_pos, v_world_pos);
    float fog_t = smoothstep(u_fog_start, u_fog_end, dist);
    vec3 fog_color = u_sky_color;
    float fog_end_eff = u_fog_end;

    // 5. underwater override
    if (u_underwater == 1) {
        fog_end_eff = 12.0;
        fog_color = vec3(0.05, 0.15, 0.35);
    }

    float fog_factor = clamp((dist - u_fog_start) /
                            max(0.0001, fog_end_eff - u_fog_start), 0.0, 1.0);
    final_color = mix(final_color, fog_color, fog_factor);

    frag_color = vec4(final_color, tex.a);
}
"""

# ─────────────────────────────────────────────────────────────
# PROGRAM_LINES — flat-colour lines (block outline, nametags)
# ─────────────────────────────────────────────────────────────
VS_LINES = """
#version 330 core
layout(location = 0) in vec3 a_pos;

uniform mat4 u_proj;
uniform mat4 u_view;
uniform mat4 u_model;

void main() {
    gl_Position = u_proj * u_view * u_model * vec4(a_pos, 1.0);
}
"""

FS_LINES = """
#version 330 core
uniform vec4 u_color;
out vec4 frag_color;
void main() {
    frag_color = u_color;
}
"""

# ─────────────────────────────────────────────────────────────
# Compile/link helpers
# ─────────────────────────────────────────────────────────────

def _log_shader_error(shader: int, kind: str, source: str) -> None:
    log_len = gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH)
    if log_len > 0:
        msg = gl.glGetShaderInfoLog(shader, log_len).decode("utf-8", "replace")
        raise RuntimeError(f"{kind} shader compile error:\n{msg}\n--- source ---\n{source}")


def _log_program_error(prog: int, kind: str) -> None:
    log_len = gl.glGetProgramiv(prog, gl.GL_INFO_LOG_LENGTH)
    if log_len > 0:
        msg = gl.glGetProgramInfoLog(prog, log_len).decode("utf-8", "replace")
        raise RuntimeError(f"{kind} program link error:\n{msg}")


def compile_shader(source: str, kind: int) -> int:
    src = source.encode("utf-8")
    buf = ctypes.c_char_p(src)
    length = ctypes.c_int(len(src))
    shader = gl.glCreateShader(kind)
    gl.glShaderSource(shader, 1, ctypes.byref(buf), ctypes.byref(length))
    gl.glCompileShader(shader)
    status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
    if not status:
        _log_shader_error(shader, "VERTEX" if kind == gl.GL_VERTEX_SHADER
                          else "FRAGMENT", source)
    return shader


def link_program(vs_src: str, fs_src: str) -> int:
    vs = compile_shader(vs_src, gl.GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, gl.GL_FRAGMENT_SHADER)
    prog = gl.glCreateProgram()
    gl.glAttachShader(prog, vs)
    gl.glAttachShader(prog, fs)
    gl.glLinkProgram(prog)
    status = gl.glGetProgramiv(prog, gl.GL_LINK_STATUS)
    if not status:
        _log_program_error(prog, "LINK")
    gl.glDeleteShader(vs)
    gl.glDeleteShader(fs)
    return prog


def make_program_main() -> int:
    return link_program(VS_MAIN, FS_MAIN)


def make_program_lines() -> int:
    return link_program(VS_LINES, FS_LINES)


def uniform_locations(prog: int) -> dict[str, int]:
    """Cache uniform locations for PROGRAM_MAIN."""
    names = [
        "u_proj", "u_view", "u_model",
        "u_sky_color", "u_fog_start", "u_fog_end",
        "u_daylight", "u_sun_dir",
        "u_lights[0]", "u_light_count", "u_time",
        "u_underwater", "u_atlas", "u_cam_pos",
        "u_color",
    ]
    out: dict[str, int] = {}
    for n in names:
        out[n] = gl.glGetUniformLocation(prog, n)
    return out


def attrib_locations(prog: int) -> dict[str, int]:
    """Cache attribute locations for PROGRAM_MAIN."""
    names = ["a_pos", "a_uv", "a_light"]
    out: dict[str, int] = {}
    for n in names:
        out[n] = gl.glGetAttribLocation(prog, n)
    return out
