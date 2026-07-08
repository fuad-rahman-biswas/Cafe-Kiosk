"""
shapes.py - simple vector icon drawing using raw OpenGL primitives.

Keeping icons as procedural geometry (rather than image textures) keeps the
prototype dependency-free and demonstrates direct use of the OpenGL API
for 2D vector illustration, in the spirit of the assignment brief.
"""
import math
from OpenGL.GL import *


def _circle(cx, cy, r, segments=32):
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segments + 1):
        a = 2 * math.pi * i / segments
        glVertex2f(cx + math.cos(a) * r, cy + math.sin(a) * r)
    glEnd()


def _circle_outline(cx, cy, r, segments=32, width=2.0):
    glLineWidth(width)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        a = 2 * math.pi * i / segments
        glVertex2f(cx + math.cos(a) * r, cy + math.sin(a) * r)
    glEnd()


def _rect(x, y, w, h):
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def draw_roti(cx, cy, size, color):
    """Roti canai icon: folded square with crease lines, cooked-golden patches."""
    w = size * 0.6
    x, y = cx - w / 2, cy - w / 2

    glColor3f(*color)
    _rect(x, y, w, w)

    # browned patches (irregular blotches, mamak-griddle look)
    darker = tuple(max(0.0, c - 0.18) for c in color)
    glColor3f(*darker)
    _circle(cx - w * 0.18, cy + w * 0.15, w * 0.10)
    _circle(cx + w * 0.20, cy - w * 0.10, w * 0.08)
    _circle(cx + w * 0.05, cy + w * 0.22, w * 0.06)

    # fold crease lines
    glColor3f(*[c * 0.6 for c in color])
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex2f(x + w * 0.33, y)
    glVertex2f(x + w * 0.33, y + w)
    glVertex2f(x + w * 0.66, y)
    glVertex2f(x + w * 0.66, y + w)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(x, y + w * 0.5)
    glVertex2f(x + w, y + w * 0.5)
    glEnd()


def draw_nasi_lemak(cx, cy, size, color):
    """Nasi lemak icon: banana-leaf triangle parcel with rice, egg, sambal."""
    w = size * 0.62
    h = size * 0.55
    # banana leaf wrap (triangle)
    glColor3f(0.20, 0.45, 0.20)
    glBegin(GL_TRIANGLES)
    glVertex2f(cx, cy + h / 2)
    glVertex2f(cx - w / 2, cy - h / 2)
    glVertex2f(cx + w / 2, cy - h / 2)
    glEnd()

    # rice mound (paler triangle inset)
    glColor3f(*color)
    glBegin(GL_TRIANGLES)
    glVertex2f(cx, cy + h * 0.28)
    glVertex2f(cx - w * 0.32, cy - h * 0.32)
    glVertex2f(cx + w * 0.32, cy - h * 0.32)
    glEnd()

    # boiled egg half (small white oval with yolk)
    glColor3f(0.98, 0.96, 0.90)
    _circle(cx - w * 0.14, cy - h * 0.05, size * 0.09)
    glColor3f(0.95, 0.75, 0.25)
    _circle(cx - w * 0.14, cy - h * 0.05, size * 0.04)

    # sambal (red wedge)
    glColor3f(0.75, 0.18, 0.12)
    glBegin(GL_TRIANGLES)
    glVertex2f(cx + w * 0.10, cy - h * 0.10)
    glVertex2f(cx + w * 0.28, cy - h * 0.32)
    glVertex2f(cx + w * 0.05, cy - h * 0.32)
    glEnd()

    # peanuts/anchovies (tiny dots)
    glColor3f(0.55, 0.35, 0.15)
    for dx in (-0.05, 0.02, 0.09):
        _circle(cx + dx * w, cy - h * 0.25, size * 0.02)


def draw_noodles(cx, cy, size, color):
    """Fried noodles icon: bowl with wavy noodle strands and garnish."""
    bowl_w = size * 0.62
    bowl_h = size * 0.30
    bx, by = cx - bowl_w / 2, cy - size * 0.28

    # bowl (trapezoid)
    glColor3f(0.92, 0.90, 0.88)
    glBegin(GL_QUADS)
    glVertex2f(bx + bowl_w * 0.12, by)
    glVertex2f(bx + bowl_w * 0.88, by)
    glVertex2f(bx + bowl_w, by + bowl_h)
    glVertex2f(bx, by + bowl_h)
    glEnd()

    # noodle mound
    glColor3f(*color)
    _circle(cx, by + bowl_h + size * 0.02, size * 0.30)

    # wavy noodle strand highlights
    glColor3f(*[min(1.0, c + 0.15) for c in color])
    glLineWidth(2.0)
    for offset in (-0.14, 0.0, 0.14):
        glBegin(GL_LINE_STRIP)
        for t in range(8):
            ft = t / 7
            nx = cx + offset * size + math.sin(ft * 6 + offset * 10) * size * 0.05
            ny = by + bowl_h - size * 0.05 + ft * size * 0.22
            glVertex2f(nx, ny)
        glEnd()

    # garnish (green onion flecks + red chili sliver)
    glColor3f(0.30, 0.55, 0.25)
    for dx, dy in ((-0.10, 0.10), (0.05, 0.14), (0.15, 0.06)):
        _circle(cx + dx * size, by + bowl_h + dy * size, size * 0.02)
    glColor3f(0.75, 0.15, 0.10)
    _rect(cx + size * 0.08, by + bowl_h + size * 0.10, size * 0.10, size * 0.03)


def draw_teh_tarik(cx, cy, size, color, pull_phase=0.0):
    """Teh tarik icon: a single glass with a distinct frothy top layer (the
    hallmark look of pulled tea) and rising steam, animated with small
    bubbles drifting across the foam line."""
    top_w = size * 0.40
    bottom_w = size * 0.30
    h = size * 0.55
    bottom_y = cy - h / 2
    top_y = cy + h / 2
    foam_h = h * 0.16
    foam_y = top_y - foam_h

    darker = tuple(max(0.0, c - 0.28) for c in color)

    # tea body (below the foam line)
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(cx - bottom_w / 2, bottom_y)
    glVertex2f(cx + bottom_w / 2, bottom_y)
    glVertex2f(cx + top_w / 2, foam_y)
    glVertex2f(cx - top_w / 2, foam_y)
    glEnd()

    # frothy top layer - the visual signature of teh tarik
    glColor3f(0.94, 0.87, 0.72)
    glBegin(GL_QUADS)
    glVertex2f(cx - top_w / 2, foam_y)
    glVertex2f(cx + top_w / 2, foam_y)
    glVertex2f(cx + top_w / 2, top_y)
    glVertex2f(cx - top_w / 2, top_y)
    glEnd()

    # glass outline so it reads clearly as a vessel
    glColor3f(*darker)
    glLineWidth(2.5)
    glBegin(GL_LINE_LOOP)
    glVertex2f(cx - bottom_w / 2, bottom_y)
    glVertex2f(cx + bottom_w / 2, bottom_y)
    glVertex2f(cx + top_w / 2, top_y)
    glVertex2f(cx - top_w / 2, top_y)
    glEnd()
    # foam/tea boundary line
    glBegin(GL_LINES)
    glVertex2f(cx - top_w / 2 + 2, foam_y)
    glVertex2f(cx + top_w / 2 - 2, foam_y)
    glEnd()

    # small foam bubbles, gently animated
    glColor3f(1, 1, 1)
    for i, ox in enumerate((-0.20, 0.0, 0.20)):
        bob = math.sin(pull_phase * 2 + i) * foam_h * 0.15
        _circle(cx + ox * top_w, foam_y + foam_h * 0.5 + bob, size * 0.022, segments=10)

    # rising steam
    glColor3f(0.6, 0.6, 0.6)
    glLineWidth(2.0)
    for i, offset in enumerate((-0.16, 0.16)):
        glBegin(GL_LINE_STRIP)
        for t in range(10):
            ft = t / 9
            sx = cx + offset * top_w + math.sin(ft * 4 + pull_phase + i) * top_w * 0.12
            sy = top_y + 4 + ft * h * 0.75
            glVertex2f(sx, sy)
        glEnd()


def draw_cup(cx, cy, size, color, steam_phase=0.0):
    """Kopi cup icon (tapered body + arc handle) with an animated steam curl."""
    top_w = size * 0.62
    bottom_w = size * 0.48
    h = size * 0.5
    top_y = cy + h / 2
    bottom_y = cy - h / 2

    # tapered body (trapezoid)
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(cx - bottom_w / 2, bottom_y)
    glVertex2f(cx + bottom_w / 2, bottom_y)
    glVertex2f(cx + top_w / 2, top_y)
    glVertex2f(cx - top_w / 2, top_y)
    glEnd()

    # handle as a smooth arc, not a full circle
    handle_cx = cx + top_w / 2 + size * 0.10
    handle_cy = cy
    glColor3f(*color)
    glLineWidth(5.0)
    glBegin(GL_LINE_STRIP)
    segs = 20
    for i in range(segs + 1):
        a = math.radians(-100 + 200 * i / segs)
        hx = handle_cx + math.cos(a) * size * 0.13
        hy = handle_cy + math.sin(a) * size * 0.17
        glVertex2f(hx, hy)
    glEnd()

    # rim highlight (subtle band just inside the top edge)
    glColor4f(1, 1, 1, 0.85)
    band_h = h * 0.10
    glBegin(GL_QUADS)
    glVertex2f(cx - top_w / 2 + 2, top_y - band_h)
    glVertex2f(cx + top_w / 2 - 2, top_y - band_h)
    glVertex2f(cx + top_w / 2 - 2, top_y - 1)
    glVertex2f(cx - top_w / 2 + 2, top_y - 1)
    glEnd()

    # steam (two soft curls, animated by phase)
    glColor3f(0.65, 0.65, 0.65)
    glLineWidth(2.0)
    for i, offset in enumerate((-0.16, 0.16)):
        glBegin(GL_LINE_STRIP)
        for t in range(10):
            ft = t / 9
            sx = cx + offset * top_w + math.sin(ft * 4 + steam_phase + i) * top_w * 0.10
            sy = top_y + 4 + ft * h * 0.9
            glVertex2f(sx, sy)
        glEnd()


def draw_cold_drink(cx, cy, size, color):
    w, h = size * 0.5, size * 0.65
    x, y = cx - w / 2, cy - h / 2
    # cup (tapered look approximated with rect)
    glColor4f(color[0], color[1], color[2], 0.85)
    _rect(x, y, w, h)
    # ice cubes
    glColor3f(1, 1, 1)
    _rect(x + w * 0.15, y + h * 0.55, w * 0.25, w * 0.25)
    _rect(x + w * 0.55, y + h * 0.65, w * 0.25, w * 0.25)
    # straw
    glColor3f(0.9, 0.2, 0.2)
    glLineWidth(4.0)
    glBegin(GL_LINES)
    glVertex2f(cx + w * 0.15, y + h)
    glVertex2f(cx + w * 0.30, y + h + size * 0.22)
    glEnd()


ICON_DRAW_FNS = {
    "roti": draw_roti,
    "nasi_lemak": draw_nasi_lemak,
    "noodles": draw_noodles,
    "teh_tarik": draw_teh_tarik,
    "cup": draw_cup,
    "kopi": draw_cup,
    "cold": draw_cold_drink,
}

_PHASE_ICONS = {"cup", "kopi"}       # animated via steam_phase
_PULL_ICONS = {"teh_tarik"}          # animated via pull_phase


def draw_icon(icon_key, cx, cy, size, color, steam_phase=0.0):
    fn = ICON_DRAW_FNS.get(icon_key, draw_cup)
    if icon_key in _PHASE_ICONS:
        fn(cx, cy, size, color, steam_phase)
    elif icon_key in _PULL_ICONS:
        fn(cx, cy, size, color, steam_phase)
    else:
        fn(cx, cy, size, color)


def draw_checkmark(cx, cy, size, progress, color=(0.25, 0.55, 0.30), width=8.0):
    """Animated checkmark that draws itself in as `progress` goes 0 -> 1."""
    p1 = (cx - size * 0.35, cy)
    p2 = (cx - size * 0.08, cy - size * 0.3)
    p3 = (cx + size * 0.4, cy + size * 0.35)

    def lerp(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    glColor3f(*color)
    glLineWidth(width)
    glBegin(GL_LINE_STRIP)
    if progress <= 0.5:
        t = progress / 0.5
        end = lerp(p1, p2, t)
        glVertex2f(*p1)
        glVertex2f(*end)
    else:
        t = (progress - 0.5) / 0.5
        end = lerp(p2, p3, t)
        glVertex2f(*p1)
        glVertex2f(*p2)
        glVertex2f(*end)
    glEnd()

    # circle ring around checkmark, fades in
    if progress > 0.1:
        alpha = min(1.0, (progress - 0.1) / 0.4)
        glColor4f(color[0], color[1], color[2], alpha * 0.8)
        _circle_outline(cx, cy, size * 0.62, segments=48, width=4.0)
