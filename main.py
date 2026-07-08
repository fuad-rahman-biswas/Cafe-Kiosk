"""
Kedai Mamak Pak Din - Self-Order Kiosk (Beta Prototype v2)
HCI Assignment 2

A multi-screen interactive kiosk demonstrating layered visual and audio
interaction techniques, built with OpenGL/GLUT + pygame.mixer.

Screens: Splash -> Menu -> Cart -> Order Confirmation -> Receipt -> (loop)

See README.md and the design rationale document for the HCI justification
behind each visual/audio choice.
"""
import sys
import time
import math

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import config as C
import shapes
from audio import AudioManager

# ---------------------------------------------------------------------------
# Global mutable state
# ---------------------------------------------------------------------------

state = {
    "screen": C.SCREEN_SPLASH,
    "prev_screen": None,
    "transition_start": time.time(),
    "transition_dur": 0.35,
    "splash_start": time.time(),
    "hover_key": None,
    "active_category": C.CATEGORIES[0],
    "cart": {},                # item name -> quantity
    "pulse": {},                # item name -> pulse start time
    "confirm_start": None,
    "receipt_start": None,
    "receipt_lines_shown": 0,
    "order_number": 1000,
    "window_w": C.WINDOW_W,
    "window_h": C.WINDOW_H,
}

audio = None  # set in main()


# ---------------------------------------------------------------------------
# Screen transition helper
# ---------------------------------------------------------------------------

def go_to(screen, play_sound=True):
    state["prev_screen"] = state["screen"]
    state["screen"] = screen
    state["transition_start"] = time.time()
    if play_sound and audio:
        audio.play("whoosh")
    if screen == C.SCREEN_CONFIRM:
        state["confirm_start"] = time.time()
    if screen == C.SCREEN_RECEIPT:
        state["receipt_start"] = time.time()
        state["receipt_lines_shown"] = 0


def transition_alpha():
    """0 -> 1 fade progress since last screen change."""
    elapsed = time.time() - state["transition_start"]
    return min(1.0, elapsed / state["transition_dur"])


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------

def draw_text(x, y, text, color=C.TEXT_DARK, font=None, alpha=1.0):
    if font is None:
        font = GLUT_BITMAP_HELVETICA_18
    glColor4f(color[0], color[1], color[2], alpha)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))


def text_width(text, font=None):
    if font is None:
        font = GLUT_BITMAP_HELVETICA_18
    return sum(glutBitmapWidth(font, ord(ch)) for ch in text)


def draw_rect(x, y, w, h, color, alpha=1.0):
    glColor4f(color[0], color[1], color[2], alpha)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def draw_rect_outline(x, y, w, h, color, line_width=2.0, alpha=1.0):
    glColor4f(color[0], color[1], color[2], alpha)
    glLineWidth(line_width)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def draw_progress_breadcrumb(x, y, active_screen, alpha=1.0):
    labels = ["Menu", "Cart", "Confirm", "Receipt"]
    keys = C.SCREEN_ORDER
    gap = 95
    active_index = keys.index(active_screen) if active_screen in keys else 0

    # connector lines first (behind dots), so text below is never crossed
    glLineWidth(2.0)
    for i in range(len(keys) - 1):
        cx1 = x + i * gap
        cx2 = x + (i + 1) * gap
        done = active_index > i
        color = C.ACCENT if done else C.MUTED_GREY
        glColor4f(color[0], color[1], color[2], alpha)
        glBegin(GL_LINES)
        glVertex2f(cx1 + 9, y)
        glVertex2f(cx2 - 9, y)
        glEnd()

    for i, (label, key) in enumerate(zip(labels, keys)):
        cx = x + i * gap
        is_active = key == active_screen
        is_done = active_index > i
        color = C.ACCENT if (is_active or is_done) else C.MUTED_GREY

        glColor4f(color[0], color[1], color[2], alpha)
        glBegin(GL_TRIANGLE_FAN)
        segs = 20
        for s in range(segs + 1):
            a = 2 * math.pi * s / segs
            glVertex2f(cx + math.cos(a) * 6, y + math.sin(a) * 6)
        glEnd()

        lw = text_width(label)
        draw_text(cx - lw / 2, y - 20, label, color, alpha=alpha)


# ---------------------------------------------------------------------------
# Screen: SPLASH
# ---------------------------------------------------------------------------

def draw_splash(alpha):
    W, H = state["window_w"], state["window_h"]
    now = time.time()
    t = now - state["splash_start"]

    # animated teh tarik "pull" as the signature logo
    bob = math.sin(t * 1.4) * 6
    shapes.draw_icon("teh_tarik", W / 2, H / 2 + 90 + bob, 280, C.ACCENT, steam_phase=t * 2.0)

    title = C.ORG_NAME
    draw_text(W / 2 - text_width(title, GLUT_BITMAP_TIMES_ROMAN_24) / 2, H / 2 - 100,
               title, C.TEXT_DARK, GLUT_BITMAP_TIMES_ROMAN_24, alpha=alpha)

    sub = "Self-Order Kiosk"
    draw_text(W / 2 - text_width(sub) / 2, H / 2 - 125, sub, (0.4, 0.3, 0.25), alpha=alpha)

    # pulsing "tap to start" prompt
    pulse = 0.6 + 0.4 * math.sin(t * 3)
    prompt = "Tap anywhere to start"
    draw_text(W / 2 - text_width(prompt) / 2, H / 2 - 190, prompt, C.ACCENT, alpha=pulse)


# ---------------------------------------------------------------------------
# Screen: MENU
# ---------------------------------------------------------------------------

def category_tab_rect(index):
    x = C.GRID_X + index * 170
    y = C.WINDOW_H - 130
    return x, y, 160, 34


def menu_item_rect(index):
    col = index % C.GRID_COLS
    row = index // C.GRID_COLS
    x = C.GRID_X + col * (C.CARD_W + C.CARD_GAP)
    y = C.GRID_Y - row * (C.CARD_H + C.CARD_GAP)
    return x, y, C.CARD_W, C.CARD_H


def items_in_active_category():
    return [it for it in C.MENU_ITEMS if it["cat"] == state["active_category"]]


def draw_menu(alpha):
    W, H = state["window_w"], state["window_h"]
    now = time.time()

    draw_text(C.GRID_X, H - 40, C.ORG_NAME, C.TEXT_DARK, GLUT_BITMAP_TIMES_ROMAN_24, alpha=alpha)
    draw_text(C.GRID_X, H - 62, "Tap a category, then tap items to add them to your order", (0.4, 0.3, 0.25), alpha=alpha)

    draw_progress_breadcrumb(W - 560, H - 25, C.SCREEN_MENU, alpha=alpha)

    # category tabs
    for i, cat in enumerate(C.CATEGORIES):
        x, y, w, h = category_tab_rect(i)
        active = cat == state["active_category"]
        hovered = state["hover_key"] == ("tab", i)
        color = C.ACCENT if active else (C.ACCENT_LIGHT if hovered else (0.88, 0.83, 0.75))
        draw_rect(x, y, w, h, color, alpha=alpha)
        draw_rect_outline(x, y, w, h, C.ACCENT, alpha=alpha)
        tcol = C.TEXT_LIGHT if active else C.TEXT_DARK
        draw_text(x + 14, y + 10, cat, tcol, alpha=alpha)

    # item cards
    items = items_in_active_category()
    for i, item in enumerate(items):
        x, y, w, h = menu_item_rect(i)
        key = ("item", item["name"])
        hovered = state["hover_key"] == key

        card_color = (1.0, 1.0, 1.0)
        draw_rect(x, y, w, h, card_color, alpha=alpha)
        border_color = C.ACCENT if hovered else (0.8, 0.75, 0.68)
        draw_rect_outline(x, y, w, h, border_color, line_width=2.5 if hovered else 1.5, alpha=alpha)

        # click pulse scaling on the icon
        scale = 1.0
        if item["name"] in state["pulse"]:
            elapsed = now - state["pulse"][item["name"]]
            if elapsed < 0.18:
                scale = 1.0 + 0.12 * math.sin(elapsed / 0.18 * math.pi)
            else:
                del state["pulse"][item["name"]]

        icon_cy = y + h - 70
        shapes.draw_icon(item["icon"], x + w / 2, icon_cy, 90 * scale, item["color"], steam_phase=now * 2.0)

        draw_text(x + 16, y + 40, item["name"], C.TEXT_DARK, GLUT_BITMAP_HELVETICA_18, alpha=alpha)
        draw_text(x + 16, y + 16, f"{C.CURRENCY} {item['price']:.2f}", (0.4, 0.3, 0.25), alpha=alpha)

        qty = state["cart"].get(item["name"], 0)
        if qty > 0:
            bx, by = x + w - 30, y + h - 30
            draw_rect(bx - 15, by - 15, 30, 30, C.SUCCESS, alpha=alpha)
            badge = str(qty)
            draw_text(bx - text_width(badge) / 2, by - 6, badge, C.TEXT_LIGHT, alpha=alpha)

    # cart button (bottom right, floating)
    total_items = sum(state["cart"].values())
    cart_btn = cart_button_rect()
    hovered = state["hover_key"] == "cart_btn"
    draw_rect(*cart_btn, C.ACCENT if not hovered else C.ACCENT_LIGHT, alpha=alpha)
    label = f"View Cart ({total_items})" if total_items else "View Cart"
    draw_text(cart_btn[0] + 20, cart_btn[1] + 12, label, C.TEXT_LIGHT, alpha=alpha)

    # mute button
    draw_mute_button(alpha)


def cart_button_rect():
    return (state["window_w"] - 220, 30, 190, 40)


def draw_mute_button(alpha=1.0):
    x, y, w, h = state["window_w"] - 100, state["window_h"] - 40, 70, 26
    hovered = state["hover_key"] == "mute_btn"
    draw_rect(x, y, w, h, C.MUTED_GREY if not hovered else (0.4, 0.4, 0.4), alpha=alpha)
    label = "UNMUTE" if (audio and audio.muted) else "MUTE"
    draw_text(x + 8, y + 7, label, C.TEXT_LIGHT, alpha=alpha)


def mute_button_rect():
    return (state["window_w"] - 100, state["window_h"] - 40, 70, 26)


# ---------------------------------------------------------------------------
# Screen: CART
# ---------------------------------------------------------------------------

def cart_row_rects():
    rows = []
    y = state["window_h"] - 150
    for name in list(state["cart"].keys()):
        rows.append((name, 60, y, state["window_w"] - 120, 56))
        y -= 66
    return rows


def draw_cart(alpha):
    W, H = state["window_w"], state["window_h"]
    draw_text(60, H - 40, "Your Order", C.TEXT_DARK, GLUT_BITMAP_TIMES_ROMAN_24, alpha=alpha)
    draw_progress_breadcrumb(W - 560, H - 25, C.SCREEN_CART, alpha=alpha)

    if not state["cart"]:
        draw_text(60, H - 100, "Your cart is empty. Go back to the menu to add items.", (0.4, 0.3, 0.25), alpha=alpha)

    subtotal = 0.0
    for name, x, y, w, h in cart_row_rects():
        item = next(it for it in C.MENU_ITEMS if it["name"] == name)
        qty = state["cart"][name]
        line_total = item["price"] * qty
        subtotal += line_total

        draw_rect(x, y, w, h, (1, 1, 1), alpha=alpha)
        draw_rect_outline(x, y, w, h, (0.8, 0.75, 0.68), alpha=alpha)

        shapes.draw_icon(item["icon"], x + 35, y + h / 2, 40, item["color"])
        draw_text(x + 70, y + h - 26, name, C.TEXT_DARK, alpha=alpha)
        draw_text(x + 70, y + 10, f"{C.CURRENCY} {item['price']:.2f} each", (0.5, 0.45, 0.4), alpha=alpha)

        # quantity stepper
        minus_r = (x + w - 220, y + h / 2 - 14, 28, 28)
        plus_r = (x + w - 130, y + h / 2 - 14, 28, 28)
        draw_rect(*minus_r, C.ACCENT_LIGHT, alpha=alpha)
        draw_text(minus_r[0] + 10, minus_r[1] + 7, "-", C.TEXT_DARK, alpha=alpha)
        draw_text(x + w - 185, y + h / 2 - 7, str(qty), C.TEXT_DARK, alpha=alpha)
        draw_rect(*plus_r, C.ACCENT_LIGHT, alpha=alpha)
        draw_text(plus_r[0] + 8, plus_r[1] + 7, "+", C.TEXT_DARK, alpha=alpha)

        draw_text(x + w - 80, y + h / 2 - 7, f"{C.CURRENCY} {line_total:.2f}", C.TEXT_DARK, alpha=alpha)

    rounded_total = C.round_to_nearest(subtotal)
    rounding_diff = rounded_total - subtotal

    panel_y = 90
    draw_rect(W - 300, panel_y, 240, 130, (1, 1, 1), alpha=alpha)
    draw_rect_outline(W - 300, panel_y, 240, 130, (0.8, 0.75, 0.68), alpha=alpha)
    draw_text(W - 288, panel_y + 100, f"Subtotal: {C.CURRENCY} {subtotal:.2f}", C.TEXT_DARK, alpha=alpha)
    draw_text(W - 288, panel_y + 76, f"Rounding: {C.CURRENCY} {rounding_diff:+.2f}", C.TEXT_DARK, alpha=alpha)
    draw_text(W - 288, panel_y + 44, f"Total: {C.CURRENCY} {rounded_total:.2f}", C.TEXT_DARK, GLUT_BITMAP_HELVETICA_18, alpha=alpha)

    # back / checkout buttons
    back_r = back_button_rect()
    draw_rect(*back_r, C.MUTED_GREY if state["hover_key"] != "back_btn" else (0.4, 0.4, 0.4), alpha=alpha)
    draw_text(back_r[0] + 18, back_r[1] + 12, "Back to Menu", C.TEXT_LIGHT, alpha=alpha)

    checkout_r = checkout_button_rect()
    can_checkout = bool(state["cart"])
    ccolor = C.SUCCESS if can_checkout else (0.7, 0.7, 0.7)
    if state["hover_key"] == "checkout_btn" and can_checkout:
        ccolor = tuple(min(1.0, c + 0.1) for c in ccolor)
    draw_rect(*checkout_r, ccolor, alpha=alpha)
    draw_text(checkout_r[0] + 30, checkout_r[1] + 12, "Checkout", C.TEXT_LIGHT, alpha=alpha)

    draw_mute_button(alpha)


def back_button_rect():
    return (60, 30, 180, 40)


def checkout_button_rect():
    return (state["window_w"] - 260, 30, 190, 40)


# ---------------------------------------------------------------------------
# Screen: CONFIRM
# ---------------------------------------------------------------------------

def draw_confirm(alpha):
    W, H = state["window_w"], state["window_h"]
    elapsed = time.time() - (state["confirm_start"] or time.time())
    progress = min(1.0, elapsed / 0.6)

    shapes.draw_checkmark(W / 2, H / 2 + 40, 160, progress, C.SUCCESS)

    if progress >= 1.0:
        msg = "Order Confirmed!"
        draw_text(W / 2 - text_width(msg, GLUT_BITMAP_TIMES_ROMAN_24) / 2, H / 2 - 80,
                   msg, C.TEXT_DARK, GLUT_BITMAP_TIMES_ROMAN_24, alpha=alpha)
        sub = f"Order #{state['order_number']}"
        draw_text(W / 2 - text_width(sub) / 2, H / 2 - 105, sub, (0.4, 0.3, 0.25), alpha=alpha)

        btn = continue_button_rect()
        draw_rect(*btn, C.ACCENT if state["hover_key"] != "continue_btn" else C.ACCENT_LIGHT, alpha=alpha)
        draw_text(btn[0] + 30, btn[1] + 12, "View Receipt", C.TEXT_LIGHT, alpha=alpha)


def continue_button_rect():
    W, H = state["window_w"], state["window_h"]
    return (W / 2 - 100, H / 2 - 170, 200, 40)


# ---------------------------------------------------------------------------
# Screen: RECEIPT
# ---------------------------------------------------------------------------

def draw_receipt(alpha):
    W, H = state["window_w"], state["window_h"]
    now = time.time()
    elapsed = now - (state["receipt_start"] or now)

    paper_w, paper_h = 340, 420
    px, py = W / 2 - paper_w / 2, H / 2 - paper_h / 2 + 20

    draw_rect(px, py, paper_w, paper_h, (1, 1, 1), alpha=alpha)
    draw_rect_outline(px, py, paper_w, paper_h, (0.7, 0.65, 0.6), alpha=alpha)

    draw_text(px + 20, py + paper_h - 40, C.ORG_NAME, C.TEXT_DARK, GLUT_BITMAP_HELVETICA_18, alpha=alpha)
    draw_text(px + 20, py + paper_h - 62, f"Order #{state['order_number']}", (0.4, 0.3, 0.25), alpha=alpha)
    draw_rect_outline(px + 15, py + paper_h - 72, paper_w - 30, 1, (0.7, 0.65, 0.6), alpha=alpha)

    # "printing" animation: lines reveal one at a time, each with a tick sound
    lines_needed = state["receipt_lines_shown"]
    max_lines = int(elapsed / 0.28)
    if max_lines > lines_needed and lines_needed < len(state["cart"]):
        state["receipt_lines_shown"] += 1
        if audio:
            audio.play("tick")

    subtotal = 0.0
    y = py + paper_h - 100
    for i, (name, qty) in enumerate(state["cart"].items()):
        if i >= state["receipt_lines_shown"]:
            break
        item = next(it for it in C.MENU_ITEMS if it["name"] == name)
        line_total = item["price"] * qty
        subtotal += line_total
        draw_text(px + 20, y, f"{qty}x {name}", C.TEXT_DARK, alpha=alpha)
        draw_text(px + paper_w - 90, y, f"{C.CURRENCY} {line_total:.2f}", C.TEXT_DARK, alpha=alpha)
        y -= 24

    if state["receipt_lines_shown"] >= len(state["cart"]):
        rounded_total = C.round_to_nearest(subtotal)
        rounding_diff = rounded_total - subtotal
        y -= 10
        draw_rect_outline(px + 15, y + 14, paper_w - 30, 1, (0.7, 0.65, 0.6), alpha=alpha)
        draw_text(px + 20, y - 10, f"Subtotal: {C.CURRENCY} {subtotal:.2f}", C.TEXT_DARK, alpha=alpha)
        draw_text(px + 20, y - 32, f"Rounding: {C.CURRENCY} {rounding_diff:+.2f}", C.TEXT_DARK, alpha=alpha)
        draw_text(px + 20, y - 58, f"Total: {C.CURRENCY} {rounded_total:.2f}", C.TEXT_DARK, GLUT_BITMAP_HELVETICA_18, alpha=alpha)
        draw_text(px + 20, y - 90, "Terima kasih! Thank you!", (0.4, 0.3, 0.25), alpha=alpha)

        btn = new_order_button_rect()
        draw_rect(*btn, C.ACCENT if state["hover_key"] != "neworder_btn" else C.ACCENT_LIGHT, alpha=alpha)
        draw_text(btn[0] + 20, btn[1] + 12, "Start New Order", C.TEXT_LIGHT, alpha=alpha)


def new_order_button_rect():
    W = state["window_w"]
    return (W / 2 - 100, 60, 200, 40)


# ---------------------------------------------------------------------------
# Master display / reshape / idle
# ---------------------------------------------------------------------------

def display():
    glClearColor(*C.BG_COLOR)
    glClear(GL_COLOR_BUFFER_BIT)

    alpha = transition_alpha()

    screen = state["screen"]
    if screen == C.SCREEN_SPLASH:
        draw_splash(alpha)
    elif screen == C.SCREEN_MENU:
        draw_menu(alpha)
    elif screen == C.SCREEN_CART:
        draw_cart(alpha)
    elif screen == C.SCREEN_CONFIRM:
        draw_confirm(alpha)
    elif screen == C.SCREEN_RECEIPT:
        draw_receipt(alpha)

    glutSwapBuffers()


def reshape(w, h):
    state["window_w"], state["window_h"] = w, h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def idle():
    glutPostRedisplay()


# ---------------------------------------------------------------------------
# Input handling
# ---------------------------------------------------------------------------

def point_in_rect(px, py, x, y, w, h):
    return x <= px <= x + w and y <= py <= y + h


def gl_y(win_y):
    return state["window_h"] - win_y


def mouse(button, glut_state, x, y):
    if button != GLUT_LEFT_BUTTON or glut_state != GLUT_DOWN:
        return
    gy = gl_y(y)
    screen = state["screen"]

    if screen == C.SCREEN_SPLASH:
        go_to(C.SCREEN_MENU)
        return

    if screen == C.SCREEN_MENU:
        handle_menu_click(x, gy)
    elif screen == C.SCREEN_CART:
        handle_cart_click(x, gy)
    elif screen == C.SCREEN_CONFIRM:
        btn = continue_button_rect()
        if point_in_rect(x, gy, *btn):
            go_to(C.SCREEN_RECEIPT)
    elif screen == C.SCREEN_RECEIPT:
        btn = new_order_button_rect()
        if point_in_rect(x, gy, *btn) and state["receipt_lines_shown"] >= len(state["cart"]):
            state["cart"] = {}
            state["order_number"] += 1
            go_to(C.SCREEN_SPLASH)
            state["splash_start"] = time.time()


def handle_menu_click(x, gy):
    for i in range(len(C.CATEGORIES)):
        rx, ry, rw, rh = category_tab_rect(i)
        if point_in_rect(x, gy, rx, ry, rw, rh):
            state["active_category"] = C.CATEGORIES[i]
            audio.play("click")
            return

    for i, item in enumerate(items_in_active_category()):
        rx, ry, rw, rh = menu_item_rect(i)
        if point_in_rect(x, gy, rx, ry, rw, rh):
            state["cart"][item["name"]] = state["cart"].get(item["name"], 0) + 1
            state["pulse"][item["name"]] = time.time()
            audio.play("click")
            return

    if point_in_rect(x, gy, *cart_button_rect()):
        go_to(C.SCREEN_CART)
        return

    if point_in_rect(x, gy, *mute_button_rect()):
        audio.toggle_mute()
        return


def handle_cart_click(x, gy):
    for name, rx, ry, rw, rh in cart_row_rects():
        minus_r = (rx + rw - 220, ry + rh / 2 - 14, 28, 28)
        plus_r = (rx + rw - 130, ry + rh / 2 - 14, 28, 28)
        if point_in_rect(x, gy, *minus_r):
            state["cart"][name] -= 1
            if state["cart"][name] <= 0:
                del state["cart"][name]
            audio.play("step_down")
            return
        if point_in_rect(x, gy, *plus_r):
            state["cart"][name] += 1
            audio.play("step_up")
            return

    if point_in_rect(x, gy, *back_button_rect()):
        go_to(C.SCREEN_MENU)
        return

    if point_in_rect(x, gy, *checkout_button_rect()) and state["cart"]:
        audio.play("confirm")
        go_to(C.SCREEN_CONFIRM, play_sound=False)
        return

    if point_in_rect(x, gy, *mute_button_rect()):
        audio.toggle_mute()
        return


def motion(x, y):
    gy = gl_y(y)
    screen = state["screen"]
    hover = None

    if screen == C.SCREEN_MENU:
        for i in range(len(C.CATEGORIES)):
            if point_in_rect(x, gy, *category_tab_rect(i)):
                hover = ("tab", i)
        for i, item in enumerate(items_in_active_category()):
            if point_in_rect(x, gy, *menu_item_rect(i)):
                hover = ("item", item["name"])
        if point_in_rect(x, gy, *cart_button_rect()):
            hover = "cart_btn"
        if point_in_rect(x, gy, *mute_button_rect()):
            hover = "mute_btn"
    elif screen == C.SCREEN_CART:
        if point_in_rect(x, gy, *back_button_rect()):
            hover = "back_btn"
        if point_in_rect(x, gy, *checkout_button_rect()):
            hover = "checkout_btn"
        if point_in_rect(x, gy, *mute_button_rect()):
            hover = "mute_btn"
    elif screen == C.SCREEN_CONFIRM:
        if point_in_rect(x, gy, *continue_button_rect()):
            hover = "continue_btn"
    elif screen == C.SCREEN_RECEIPT:
        if point_in_rect(x, gy, *new_order_button_rect()):
            hover = "neworder_btn"

    state["hover_key"] = hover


def keyboard(key, x, y):
    if key in (b"\x1b", b"q"):
        audio.quit()
        sys.exit(0)
    if key == b"m":
        audio.toggle_mute()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    global audio
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    glutInitWindowSize(C.WINDOW_W, C.WINDOW_H)
    glutCreateWindow(f"{C.ORG_NAME} Kiosk - HCI Assignment 2 Prototype".encode())

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    audio = AudioManager()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutPassiveMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)

    reshape(C.WINDOW_W, C.WINDOW_H)
    glutMainLoop()


if __name__ == "__main__":
    main()
