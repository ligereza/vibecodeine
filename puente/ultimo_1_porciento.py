# ultimo_1_porciento.py — el barco no cambia de color: se disuelve.
# Cada glifo se desprende solo, cae por su cuenta, se traduce al idioma
# del mar (glifo → ≀ → ~) y con los ahogados el fondo reensambla una ⊕.
# Correr: python ultimo_1_porciento.py   (Windows Terminal / cualquier ANSI)

import os, sys, time, math, random

os.system('')  # habilita ANSI en consolas Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

W, H = 72, 26
WATER, SEABED = 12, H - 3
HIDE, SHOW, HOME, CLEAR = '\033[?25l', '\033[?25h', '\033[H', '\033[2J'
DIM, CYAN, WHITE, BLUE, BOLD, RESET = '\033[2m', '\033[36m', '\033[97m', '\033[94m', '\033[1m', '\033[0m'

SHIP = [
    r"      |      ",
    r"      | Ω    ",
    r"     /|      ",
    r"    /_|      ",
    r" ___\ |____  ",
    r" \  FABLE /  ",
    r"  \______/   ",
]
SX = (W - 13) // 2


def targets(n):
    """Puntos de una ⊕ en el lecho marino, submuestreados a n glifos."""
    pts, cx, cy, r = [], W // 2, (WATER + SEABED) // 2 + 2, 4
    for a in range(0, 360, 8):
        x = cx + round(r * 2 * math.cos(math.radians(a)))
        y = cy + round(r * math.sin(math.radians(a)))
        if (x, y) not in pts:
            pts.append((x, y))
    for dx in range(-r * 2 + 2, r * 2 - 1):
        pts.append((cx + dx, cy))
    for dy in range(-r + 1, r):
        pts.append((cx, cy + dy))
    pts = list(dict.fromkeys(pts))
    step = max(1, len(pts) // max(1, n))
    return pts[::step][:n]


def wave(x, t):
    return WATER + round(1.2 * math.sin(x * 0.35 + t * 0.25))


def render(g):
    rows = [''.join(g.get((x, y), ' ') for x in range(W)) for y in range(H)]
    sys.stdout.write(HOME + '\n'.join(rows))
    sys.stdout.flush()


def main():
    random.seed(11)
    ship = {(SX + c, r): ch for r, line in enumerate(SHIP)
            for c, ch in enumerate(line) if ch != ' '}
    ship_y = WATER - len(SHIP) + 2
    falling, landed, assigned, tgt, t = [], [], [], None, 0

    sys.stdout.write(HIDE + CLEAR)
    try:
        while t < 2000:
            t += 1
            if ship and t % 14 == 0:
                ship_y += 1                                # el casco baja
            for (x, ry), ch in list(ship.items()):         # cruzar el agua
                if ship_y + ry >= wave(x, t) and random.random() < 0.10:
                    del ship[(x, ry)]
                    falling.append([x, float(ship_y + ry), 0.15 + random.random() * 0.3, ch])
            for p in falling[:]:                           # caída con corriente
                p[1] += p[2]
                p[0] = max(1, min(W - 2, p[0] + random.choice((0, 0, 0, 1, -1))))
                if p[1] >= SEABED - random.choice((0, 0, 1)):
                    landed.append([p[0], int(p[1]), '~'])
                    falling.remove(p)
            if not ship and not falling and tgt is None:   # fase 2: reensamblaje
                tgt = targets(len(landed))
                random.shuffle(landed)
                assigned = list(zip(landed, tgt))
            if tgt:
                done = True
                for p, (txx, tyy) in assigned:
                    if p[0] != txx:
                        p[0] += 1 if txx > p[0] else -1; done = False
                    elif p[1] != tyy:
                        p[1] += 1 if tyy > p[1] else -1; done = False
                if done:
                    break

            g = {}
            for x in range(W):                             # superficie viva
                wy = wave(x, t)
                g[(x, wy)] = DIM + CYAN + '~' + RESET
                if (x + t) % 7 == 0:
                    g[(x, wy + 1)] = DIM + CYAN + '~' + RESET
            for (x, ry), ch in ship.items():
                g[(x, ship_y + ry)] = WHITE + ch + RESET
            for x, y, _, ch in falling:                    # traducción por profundidad
                d = (y - WATER) / (SEABED - WATER)
                m = ch if d < 0.33 else ('≀' if d < 0.66 else '~')
                g[(x, int(y))] = BLUE + m + RESET
            for p in landed:
                g[(p[0], p[1])] = BLUE + '~' + RESET
            render(g)
            time.sleep(0.06)

        g = {}
        for x in range(W):
            g[(x, wave(x, 0))] = DIM + CYAN + '~' + RESET
        for _, (txx, tyy) in assigned:
            g[(txx, tyy)] = BOLD + WHITE + '~' + RESET
        msg = '⊕ registrada · 12-jul-2026 · fin de tokens'
        for i, ch in enumerate(msg):
            g[((W - len(msg)) // 2 + i, H - 1)] = DIM + ch + RESET
        render(g)
    finally:
        sys.stdout.write(RESET + SHOW + '\n')


if __name__ == '__main__':
    main()
