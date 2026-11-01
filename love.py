"""Multilingual Love Heart.

A heart made of "I love you" in 20 languages, with a name (a dedication)
glowing in the middle once the animation finishes.

Usage:
    python love.py            # dedicates to "Havya"
    python love.py Maria      # dedicates to any other name
"""

import math
import random
import sys
import turtle
import tkinter.font as tkfont
from tkinter import TclError

# ----------------------------------------------------------------- settings
NAME = " ".join(sys.argv[1:]).strip() or "Havya"

SCALE = 21          # heart size (pixels per unit of the parametric curve)
Y_OFFSET = 20       # vertical shift of the heart
DURATION = 10       # seconds to draw the whole heart
TICK = 16           # ms between animation frames
ANIM_FRAMES = 42    # frames each phrase takes to float in
LIFT = 34           # pixels each phrase floats up from
GAP = 7             # horizontal gap between phrases
SIZES = (9, 10, 11, 12)
BG = "#060208"

NAME_SIZE = 46            # preferred font size for the name
NAME_MAX_WIDTH = 380      # the name is shrunk until it fits this width
NAME_FRAMES = 80          # frames the name takes to fade in
NAME_COLOR = (1.0, 0.93, 0.94)
NAME_GLOW = (0.98, 0.10, 0.16)

FONT_CANDIDATES = ("Arial", "Segoe UI", "Helvetica", "Noto Sans", "DejaVu Sans")

PHRASES = [
    "I love you", "Seni seviyorum", "Te amo", "Je t'aime",
    "Ich liebe dich", "Ti amo", "Eu te amo", "Я тебя люблю",
    "사랑해", "愛してる", "我爱你", "मैं तुमसे प्यार करता हूँ",
    "Σ' αγαπώ", "Ik hou van jou", "Jag älskar dig", "Kocham cię",
    "ฉันรักเธอ", "Anh yêu em", "Aku cinta kamu", "Я тебе кохаю",
]

FLASH = (1.0, 0.78, 0.78)

# ------------------------------------------------------------------- state
rng = random.Random(11)
screen = None
cv = None
font_family = "Arial"
bg_rgb = (0.0, 0.0, 0.0)

_fonts = {}
active = []          # phrases still floating in
main_ids = []        # (canvas id, final color) of every finished phrase
name_items = {}      # canvas ids for the dedication
name_zone = (0.0, 0.0, 0.0)   # (center y, half width, half height) in heart coords


# ----------------------------------------------------------------- helpers
def font_for(size):
    if size not in _fonts:
        _fonts[size] = tkfont.Font(
            root=cv, family=font_family, size=size, weight="bold"
        )
    return _fonts[size]


def to_hex(c):
    return "#%02x%02x%02x" % tuple(int(max(0, min(1, v)) * 255) for v in c)


def mix(a, b, k):
    return tuple(p + (q - p) * k for p, q in zip(a, b))


def dim(c, k):
    return tuple(v * k for v in c)


def clamp(v):
    return max(0.0, min(1.0, v))


def pulse(v):
    """0 -> 1 -> 0 bump for v going 0 -> 1."""
    return math.sin(math.pi * v)


def safe_config(item, color):
    try:
        cv.itemconfig(item, fill=to_hex(color))
    except TclError:
        pass


# ------------------------------------------------------------ heart shape
def heart(a):
    x = 16 * (math.sin(a) ** 3)
    y = (
        13 * math.cos(a)
        - 5 * math.cos(2 * a)
        - 2 * math.cos(3 * a)
        - math.cos(4 * a)
    )
    return x * SCALE, y * SCALE + Y_OFFSET


POLY = [heart(2 * math.pi * i / 720) for i in range(720)]
EDGES = list(zip(POLY, POLY[1:] + POLY[:1]))
YMAX = max(p[1] for p in POLY)
YMIN = min(p[1] for p in POLY)
CY = (YMAX + YMIN) / 2


def spans(y):
    """Horizontal [left, right] intervals that are inside the heart at height y."""
    xs = []
    for (x1, y1), (x2, y2) in EDGES:
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    xs.sort()
    return list(zip(xs[0::2], xs[1::2]))


def intersect(A, B):
    out = []
    for a in A:
        for b in B:
            lo, hi = max(a[0], b[0]), min(a[1], b[1])
            if hi - lo > 14:
                out.append((lo, hi))
    return out


def radial(x, y):
    """0 at the center of the heart, ~1 at its border."""
    return math.hypot(x / (16 * SCALE), (y - CY) / (14.5 * SCALE))


def carve_name_zone(row, y, half):
    """Cut a hole in the row where the name will be written."""
    zy, zw, zh = name_zone
    if abs(y - zy) >= zh + half:
        return row
    out = []
    for lo, hi in row:
        for a, b in ((lo, min(hi, -zw)), (max(lo, zw), hi)):
            if b - a > 14:
                out.append((a, b))
    return out


def phrase_cycle():
    while True:
        order = PHRASES[:]
        rng.shuffle(order)
        yield from order


# ---------------------------------------------------------------- layout
def build():
    """Place every phrase inside the heart. Returns them in drawing order."""
    cycle = phrase_cycle()
    row_h = max(font_for(z).metrics("linespace") for z in SIZES) + 4
    half = row_h / 2
    placed = []

    y = YMAX - half
    while y > YMIN + half:
        row = intersect(spans(y + half), spans(y - half))
        row = carve_name_zone(row, y, half)

        for lo, hi in row:
            lo += 4
            hi -= 4
            cur = lo + rng.uniform(0, 8)
            line = []

            while True:
                fit = None
                for _ in range(10):
                    text = next(cycle)
                    size = rng.choice(SIZES)
                    w = font_for(size).measure(text)
                    if cur + w <= hi:
                        fit = (text, size, w)
                        break
                if not fit:
                    break
                text, size, w = fit
                line.append([cur + w / 2, text, size, w])
                cur += w + GAP

            if not line:
                continue

            if len(line) > 1:
                left = hi - (line[-1][0] + line[-1][3] / 2)
                for i, it in enumerate(line):
                    it[0] += left * i / (len(line) - 1)
            else:
                line[0][0] = (lo + hi) / 2

            for i, (x, text, size, w) in enumerate(line):
                edge = i == 0 or i == len(line) - 1
                placed.append(dict(x=x, y=y, text=text, size=size, edge=edge))

        y -= row_h

    wine = (0.58, 0.0, 0.09)
    crimson = (0.90, 0.05, 0.14)
    blood = (0.98, 0.10, 0.16)
    for p in placed:
        rad = min(1.0, radial(p["x"], p["y"]))
        base = mix(wine, crimson, 0.25 + 0.75 * rad)
        base = mix(base, blood, rng.uniform(0, 0.35) + (0.3 if p["edge"] else 0))
        p["color"] = tuple(min(1, v) for v in base)
        p["rad"] = rad

    edges = [p for p in placed if p["edge"]]
    inner = [p for p in placed if not p["edge"]]
    edges.sort(key=lambda p: math.atan2(p["x"], p["y"] - CY) % (2 * math.pi))
    inner.sort(key=lambda p: -p["rad"] + rng.uniform(0, 0.08))
    return edges + inner


# ------------------------------------------------------------- phrases
def spawn(p):
    x, y = p["x"], -p["y"]
    size, text = p["size"], p["text"]
    font = (font_family, size, "bold")
    big = (font_family, size + 1, "bold")
    hidden = to_hex(bg_rgb)

    shadow = cv.create_text(x + 2, y + 3 - LIFT, text=text, font=font, fill=hidden)
    halo = cv.create_text(x, y - LIFT, text=text, font=big, fill=hidden)
    main = cv.create_text(x, y - LIFT, text=text, font=font, fill=hidden)

    p.update(shadow=shadow, halo=halo, main=main,
             f=0, dx=rng.uniform(-10, 10))
    main_ids.append((main, p["color"]))
    active.append(p)


def animate(p):
    """Advance one phrase by one frame. Returns False when it has landed."""
    p["f"] += 1
    u = clamp(p["f"] / ANIM_FRAMES)
    e = 1 - (1 - u) ** 3           # cubic ease-out
    c = p["color"]
    x, y = p["x"], -p["y"]
    px = x + p["dx"] * (1 - e)
    py = y - (1 - e) * LIFT

    cv.itemconfig(p["shadow"], fill=to_hex(mix(bg_rgb, dim(c, 0.30), e)))
    cv.itemconfig(p["halo"], fill=to_hex(mix(bg_rgb, dim(c, 0.20), e * e)))
    cv.coords(p["shadow"], px + 2, py + 3)
    cv.coords(p["halo"], px, py)

    flash = 0.75 * pulse(clamp((u - 0.55) / 0.45))
    col = mix(mix(bg_rgb, c, e ** 1.5), FLASH, flash)
    cv.itemconfig(p["main"], fill=to_hex(col))
    cv.coords(p["main"], px, py)

    if u >= 1:
        cv.coords(p["shadow"], x + 2, y + 3)
        cv.coords(p["halo"], x, y)
        cv.coords(p["main"], x, y)
        cv.itemconfig(p["main"], fill=to_hex(c))
        return False
    return True


# ------------------------------------------------------------ dedication
def make_name_font():
    """Biggest bold font (up to NAME_SIZE) whose width fits NAME_MAX_WIDTH."""
    size = NAME_SIZE
    while size > 14:
        f = tkfont.Font(root=cv, family=font_family, size=size, weight="bold")
        if f.measure(NAME) <= NAME_MAX_WIDTH:
            break
        size -= 2
    f = tkfont.Font(root=cv, family=font_family, size=size, weight="bold")
    return size, f.measure(NAME), f.metrics("linespace")


def start_name():
    """Create the (still invisible) dedication in the middle of the heart."""
    size, _, _ = make_name_font()
    x, y = 0, -name_zone[0]
    hidden = to_hex(bg_rgb)
    name_items["glow"] = cv.create_text(
        x, y, text=NAME, font=(font_family, size + 4, "bold"), fill=hidden)
    name_items["shadow"] = cv.create_text(
        x + 2, y + 3, text=NAME, font=(font_family, size, "bold"), fill=hidden)
    name_items["main"] = cv.create_text(
        x, y, text=NAME, font=(font_family, size, "bold"), fill=hidden)


def reveal_name(frame=0):
    u = clamp(frame / NAME_FRAMES)
    e = 1 - (1 - u) ** 3
    glow = mix(bg_rgb, dim(NAME_GLOW, 0.35), e)
    shadow = mix(bg_rgb, dim(NAME_GLOW, 0.55), e)
    main = mix(mix(bg_rgb, NAME_COLOR, e), FLASH, 0.6 * pulse(u))
    cv.itemconfig(name_items["glow"], fill=to_hex(glow))
    cv.itemconfig(name_items["shadow"], fill=to_hex(shadow))
    cv.itemconfig(name_items["main"], fill=to_hex(main))
    if u < 1:
        cv.after(TICK, lambda: reveal_name(frame + 1))
    else:
        heartbeat(0)
        shimmer()


def heartbeat(t):
    """Slow, soft glow on the name once it is fully visible."""
    k = 0.5 + 0.5 * math.sin(t / 9)
    safe_config(name_items["glow"], mix(dim(NAME_GLOW, 0.25), NAME_GLOW, k * 0.55))
    safe_config(name_items["main"], mix(NAME_COLOR, FLASH, 0.35 * k))
    cv.after(40, lambda: heartbeat(t + 1))


# ---------------------------------------------------------------- loop
def shimmer():
    i, c = rng.choice(main_ids)
    safe_config(i, mix(c, FLASH, 0.6))
    cv.after(260, lambda: safe_config(i, c))
    cv.after(140, shimmer)


def run(order):
    items = iter(order)
    rate = len(order) / (DURATION * 1000 / TICK)
    state = {"acc": 0.0, "spawning": True}

    def step():
        if state["spawning"]:
            state["acc"] += rate
            try:
                while state["acc"] >= 1:
                    state["acc"] -= 1
                    spawn(next(items))
            except StopIteration:
                state["spawning"] = False

        active[:] = [p for p in active if animate(p)]

        if not state["spawning"] and not active:
            reveal_name()
            return
        cv.after(TICK, step)

    cv.after(200, step)


# ---------------------------------------------------------------- main
def pick_font():
    available = set(tkfont.families(root=cv))
    for name in FONT_CANDIDATES:
        if name in available:
            return name
    return tkfont.nametofont("TkDefaultFont", root=cv).actual("family")


def main():
    global screen, cv, font_family, bg_rgb, name_zone

    screen = turtle.Screen()
    screen.setup(800, 800)
    screen.bgcolor(BG)
    screen.title("Love Heart")
    screen.tracer(0)

    cv = screen.getcanvas()
    font_family = pick_font()
    bg_rgb = tuple(int(BG[i:i + 2], 16) / 255 for i in (1, 3, 5))

    _, name_w, name_h = make_name_font()
    name_zone = (CY, name_w / 2 + 18, name_h / 2 + 8)

    order = build()
    start_name()
    run(order)

    try:
        turtle.done()
    except (turtle.Terminator, TclError):
        pass


if __name__ == "__main__":
    main()
