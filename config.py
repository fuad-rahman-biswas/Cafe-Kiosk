"""
config.py - static data & constants for the Kedai Mamak Pak Din kiosk.

Note: "Pak Din" is a generic, fictional stall name (not a real chain) —
chosen to represent the mamak stall business type broadly, per the
assignment's "local organisation" brief.
"""

WINDOW_W, WINDOW_H = 1000, 680

ORG_NAME = "Kedai Mamak Pak Din"
CURRENCY = "RM"

BG_COLOR = (0.98, 0.95, 0.87, 1.0)
TEXT_DARK = (0.20, 0.12, 0.08)
TEXT_LIGHT = (1.0, 1.0, 1.0)
ACCENT = (0.72, 0.14, 0.10)          # mamak signage red
ACCENT_LIGHT = (0.95, 0.75, 0.30)    # gold/turmeric yellow
SUCCESS = (0.20, 0.55, 0.28)
MUTED_GREY = (0.55, 0.55, 0.55)

CATEGORIES = ["Nasi & Mee", "Roti", "Minuman"]

MENU_ITEMS = [
    # name, price (RM), category, icon key, color
    {"name": "Nasi Lemak",         "price": 6.50, "cat": "Nasi & Mee", "icon": "nasi_lemak", "color": (0.85, 0.80, 0.68)},
    {"name": "Mee Goreng",         "price": 7.00, "cat": "Nasi & Mee", "icon": "noodles",    "color": (0.80, 0.45, 0.20)},
    {"name": "Maggi Goreng",       "price": 7.50, "cat": "Nasi & Mee", "icon": "noodles",    "color": (0.75, 0.35, 0.18)},
    {"name": "Nasi Goreng Kampung","price": 7.50, "cat": "Nasi & Mee", "icon": "nasi_lemak", "color": (0.70, 0.55, 0.30)},
    {"name": "Mee Rebus",          "price": 7.00, "cat": "Nasi & Mee", "icon": "noodles",    "color": (0.65, 0.40, 0.15)},
    {"name": "Nasi Goreng Ayam",   "price": 8.00, "cat": "Nasi & Mee", "icon": "nasi_lemak", "color": (0.90, 0.65, 0.30)},

    {"name": "Roti Canai",         "price": 2.20, "cat": "Roti",       "icon": "roti",       "color": (0.90, 0.72, 0.35)},
    {"name": "Roti Telur",         "price": 3.00, "cat": "Roti",       "icon": "roti",       "color": (0.92, 0.78, 0.40)},
    {"name": "Roti Tissue",        "price": 5.00, "cat": "Roti",       "icon": "roti",       "color": (0.88, 0.68, 0.30)},
    {"name": "Murtabak",           "price": 8.00, "cat": "Roti",       "icon": "roti",       "color": (0.75, 0.55, 0.25)},
    {"name": "Roti Bom",           "price": 3.50, "cat": "Roti",       "icon": "roti",       "color": (0.85, 0.65, 0.28)},
    {"name": "Roti Planta",        "price": 2.50, "cat": "Roti",       "icon": "roti",       "color": (0.93, 0.80, 0.45)},

    {"name": "Teh Tarik",          "price": 3.00, "cat": "Minuman",    "icon": "teh_tarik",  "color": (0.72, 0.50, 0.28)},
    {"name": "Kopi O",             "price": 2.80, "cat": "Minuman",    "icon": "kopi",       "color": (0.30, 0.18, 0.10)},
    {"name": "Teh O Ais",          "price": 2.50, "cat": "Minuman",    "icon": "cold",       "color": (0.55, 0.35, 0.20)},
    {"name": "Milo Ais",           "price": 4.00, "cat": "Minuman",    "icon": "cold",       "color": (0.40, 0.25, 0.15)},
    {"name": "Air Bandung",        "price": 3.50, "cat": "Minuman",    "icon": "cold",       "color": (0.85, 0.45, 0.55)},
    {"name": "Limau Ais",          "price": 3.00, "cat": "Minuman",    "icon": "cold",       "color": (0.70, 0.75, 0.30)},
]

# Mamak stalls typically don't charge SST and instead round the final total
# to the nearest 5 sen (Malaysia's smallest circulating coin denomination).
ROUNDING_INCREMENT = 0.05

# grid layout for menu screen (2 rows x 4 cols = up to 8 items per category)
GRID_COLS = 4
GRID_ROWS = 2
GRID_X, GRID_Y = 40, 325
CARD_W, CARD_H = 205, 205
CARD_GAP = 15

# screen identifiers
SCREEN_SPLASH = "splash"
SCREEN_MENU = "menu"
SCREEN_CART = "cart"
SCREEN_CONFIRM = "confirm"
SCREEN_RECEIPT = "receipt"

SCREEN_ORDER = [SCREEN_MENU, SCREEN_CART, SCREEN_CONFIRM, SCREEN_RECEIPT]


def round_to_nearest(amount, increment=ROUNDING_INCREMENT):
    return round(amount / increment) * increment
