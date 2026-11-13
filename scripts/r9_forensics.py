#!/usr/bin/env python3
"""R9 art-direction forensics for Bloco Livre, shot 07_clear.png (celebration).
Geometry: board 8x8, x24-696, y190-866, cell 84px; tray y880-1110; streak y1240-1250."""
import os, hashlib, math
from PIL import Image
from collections import Counter

R9 = '/home/z/my-project/critic_shots/r9'
R8 = '/home/z/my-project/critic_shots/r8'
OUT = '/tmp/critic_crops_r9'
os.makedirs(OUT, exist_ok=True)

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

print('=== FILE IDENTITY r8 vs r9 ===')
for f in sorted(os.listdir(R9)):
    same = os.path.exists(R8 + '/' + f) and md5(R9 + '/' + f) == md5(R8 + '/' + f)
    print('  %-16s %s' % (f, 'IDENTICAL' if same else 'DIFFERS'))

im9 = Image.open(R9 + '/07_clear.png').convert('RGB')
im8 = Image.open(R8 + '/07_clear.png').convert('RGB')
W, H = im9.size
p9, p8 = im9.load(), im8.load()
print('07_clear size:', im9.size)

# ---------- band detection ----------
def frac_warm(p, y):
    n = 0; tot = 0
    for x in range(0, W, 3):
        rr, gg, bb = p[x, y]; tot += 1
        if rr >= 150 and (rr - bb) >= 50 and gg >= 90:
            n += 1
    return n / tot

def band_runs(p):
    runs = []; cur = None
    for y in range(H):
        if frac_warm(p, y) > 0.5:
            if cur is None: cur = [y, y]
            else: cur[1] = y
        elif cur is not None:
            runs.append(tuple(cur)); cur = None
    if cur: runs.append(tuple(cur))
    return [r for r in runs if r[1] - r[0] >= 20]

b9 = band_runs(p9); b8 = band_runs(p8)
print('=== GOLD BAND ROWS ===')
print('  r9 runs (y0,y1,h):', [(a, b, b - a + 1) for a, b in b9])
print('  r8 runs (y0,y1,h):', [(a, b, b - a + 1) for a, b in b8])

def row_mode(p, y):
    c = Counter()
    for x in range(0, W, 4):
        rr, gg, bb = p[x, y]
        c[(rr // 12, gg // 12, bb // 12)] += 1
    q, n = c.most_common(1)[0]
    return (q[0] * 12 + 6, q[1] * 12 + 6, q[2] * 12 + 6)

bt9 = b9[0][0] if b9 else 321
gold9 = row_mode(p9, (b9[0][0] + b9[0][1]) // 2) if b9 else (255, 200, 40)
bg9 = row_mode(p9, max(0, bt9 - 30))
print('  r9 band gold color ~', gold9, ' page bg above band ~', bg9)

# band x extent (row at band center)
yc9 = (b9[0][0] + b9[0][1]) // 2
cols = [x for x in range(W) if (lambda c: c[0] >= 150 and c[0] - c[2] >= 50 and c[1] >= 90)(p9[x, yc9])]
print('  r9 band x-extent at y%d: %d..%d (width %d, screen W %d)' % (yc9, min(cols), max(cols), max(cols) - min(cols) + 1, W))

# ---------- diff regions r8 -> r9 ----------
print('=== DIFF REGIONS (r9 vs r8, 07_clear) ===')
diffrows = []
for y in range(H):
    n = 0
    for x in range(0, W, 2):
        a = p9[x, y]; b = p8[x, y]
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2]) > 30:
            n += 1
    if n > 3: diffrows.append(y)
if diffrows:
    groups = []; s = diffrows[0]; prev = s
    for y in diffrows[1:]:
        if y - prev <= 3: prev = y
        else: groups.append((s, prev)); s = y; prev = y
    groups.append((s, prev))
    for g0, g1 in groups:
        xs = [x for y in range(g0, g1 + 1, 2) for x in range(0, W, 2)
              if abs(p9[x, y][0] - p8[x, y][0]) + abs(p9[x, y][1] - p8[x, y][1]) + abs(p9[x, y][2] - p8[x, y][2]) > 30]
        print('  rows y%d-%d (%dpx) cols x%d-%d' % (g0, g1, g1 - g0 + 1, min(xs), max(xs)))

# ---------- object components (celebration graphics) ----------
def components(p, y0, y1, bg, gold, x0=0, x1=None):
    x1 = W if x1 is None else x1
    obj = [[False] * (x1 - x0) for _ in range(y1 - y0)]
    for y in range(y0, y1):
        for x in range(x0, x1):
            rr, gg, bb = p[x, y]
            dg = abs(rr - gold[0]) + abs(gg - gold[1]) + abs(bb - gold[2])
            db = abs(rr - bg[0]) + abs(gg - bg[1]) + abs(bb - bg[2])
            if dg > 90 and db > 50:
                obj[y - y0][x - x0] = True
    seen = [[False] * (x1 - x0) for _ in range(y1 - y0)]
    comps = []
    for yy in range(y1 - y0):
        for xx in range(x1 - x0):
            if obj[yy][xx] and not seen[yy][xx]:
                stack = [(xx, yy)]; seen[yy][xx] = True; pix = []
                while stack:
                    cx, cy = stack.pop(); pix.append((cx, cy))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < x1 - x0 and 0 <= ny < y1 - y0 and obj[ny][nx] and not seen[ny][nx]:
                                seen[ny][nx] = True; stack.append((nx, ny))
                xs = [a for a, _ in pix]; ys = [b for _, b in pix]
                comps.append(dict(n=len(pix), bbox=(x0 + min(xs), y0 + min(ys), x0 + max(xs), y0 + max(ys)),
                                  cx=x0 + sum(xs) / len(pix), cy=y0 + sum(ys) / len(pix)))
    comps.sort(key=lambda c: -c['n'])
    return comps, obj

Y0, Y1 = 240, 510
c9, obj9 = components(p9, Y0, Y1, bg9, gold9)
print('=== R9 CELEBRATION COMPONENTS (region y240-510) ===')
for c in c9[:14]:
    x0, y0, x1, y1 = c['bbox']
    print('  n=%-6d bbox x%d-%d y%d-%d (w%d h%d) centroid (%.0f,%.0f)' % (c['n'], x0, x1, y0, y1, x1 - x0 + 1, y1 - y0 + 1, c['cx'], c['cy']))

star = c9[0]
sx, sy = star['cx'], star['cy']
sb = star['bbox']
print('  STAR(assumed largest): bbox w=%d h=%d  (0.78*84=%.1f) centroid y=%.0f' % (sb[2] - sb[0] + 1, sb[3] - sb[1] + 1, 0.78 * 84, sy))

# text cluster: small comps in y360-440 excluding star
tcomps = [c for c in c9[1:] if 360 <= c['cy'] <= 440 and c['n'] < star['n'] / 3]
if tcomps:
    tx0 = min(c['bbox'][0] for c in tcomps); tx1 = max(c['bbox'][2] for c in tcomps)
    ty0 = min(c['bbox'][1] for c in tcomps); ty1 = max(c['bbox'][3] for c in tcomps)
    bandc = (b9[0][0] + b9[0][1]) / 2
    print('  TEXT cluster: x%d-%d y%d-%d (h%d) center y=%.0f  band center y=%.0f  offset %+.1f px' % (tx0, tx1, ty0, ty1, ty1 - ty0 + 1, (ty0 + ty1) / 2, bandc, (ty0 + ty1) / 2 - bandc))

# spoke ray analysis from star centroid
print('=== R9 RAY EXTENT / WIDTH from star centroid ===')
res = []
for deg in range(0, 360, 5):
    rad = math.radians(deg)
    far = 0
    for r in range(6, 200):
        x = int(sx + r * math.cos(rad)); y = int(sy + r * math.sin(rad))
        if 0 <= x < W and Y0 <= y < Y1 and obj9[y - Y0][x]:
            far = r
    if far > 40: res.append((deg, far))
starR = max((sb[2] - sb[0], sb[3] - sb[1])) / 2
print('  star half-extent %.0f px; ray extents (deg:len):' % starR, res)
widths = []
for deg, far in res:
    R = starR + 12
    rad = math.radians(deg)
    w = 0
    for off in range(-10, 11):
        x = int(sx + R * math.cos(rad) - off * math.sin(rad))
        y = int(sy + R * math.sin(rad) + off * math.cos(rad))
        if 0 <= x < W and Y0 <= y < Y1 and obj9[y - Y0][x]:
            w += 1
    widths.append((deg, far, w))
print('  spoke widths at R=starR+12 (deg, length, width px):', [t for t in widths if t[1] > starR + 15])

# edge touch check for all celebration comps
allx0 = min(c['bbox'][0] for c in c9 if c['n'] > 50); allx1 = max(c['bbox'][2] for c in c9 if c['n'] > 50)
ally0 = min(c['bbox'][1] for c in c9 if c['n'] > 50); ally1 = max(c['bbox'][3] for c in c9 if c['n'] > 50)
print('  celebration object envelope: x%d-%d y%d-%d  (screen %dx%d) edge margins L%d R%d T%d B%d' % (allx0, allx1, ally0, ally1, W, H, allx0, W - 1 - allx1, ally0, H - 1 - ally1))

# ---------- R8 celebration for comparison ----------
bt8 = b8[0][0] if b8 else 400
gold8 = row_mode(p8, (b8[0][0] + b8[0][1]) // 2) if b8 else (255, 200, 40)
bg8 = row_mode(p8, max(0, bt8 - 30))
Y08, Y18 = 200, 700
c8, obj8 = components(p8, Y08, Y18, bg8, gold8)
print('=== R8 CELEBRATION COMPONENTS (region y200-700) ===')
for c in c8[:10]:
    x0, y0, x1, y1 = c['bbox']
    print('  n=%-6d bbox x%d-%d y%d-%d (w%d h%d) centroid (%.0f,%.0f)' % (c['n'], x0, x1, y0, y1, x1 - x0 + 1, y1 - y0 + 1, c['cx'], c['cy']))
if c8:
    s8 = c8[0]['bbox']
    print('  R8 star/rays bbox: x%d-%d y%d-%d  touches screen edge: %s' % (s8[0], s8[2], s8[1], s8[3], (s8[0] <= 2 or s8[2] >= W - 3 or s8[1] <= 2 or s8[3] >= H - 3)))

# ---------- hairline scan (dark rows) ----------
def dark_rows(p, x0, x1):
    runs = []; cur = None
    for y in range(H):
        n = 0; tot = 0
        for x in range(x0, x1, 3):
            if sum(p[x, y]) < 270: n += 1
            tot += 1
        if n / tot > 0.55:
            if cur is None: cur = [y, y]
            else: cur[1] = y
        elif cur is not None:
            runs.append(tuple(cur)); cur = None
    if cur: runs.append(tuple(cur))
    return runs
print('=== DARK HORIZONTAL BARS (x24-696) ===')
print('  r9:', [(a, b, b - a + 1) for a, b in dark_rows(p9, 24, 696)])
print('  r8:', [(a, b, b - a + 1) for a, b in dark_rows(p8, 24, 696)])

# ---------- board cell emptiness ----------
def board_cells(p):
    empty = 0; filled = []
    for row in range(8):
        for col in range(8):
            x0 = 24 + col * 84 + 12; y0 = 190 + row * 84 + 12
            vals = [p[x, y] for y in range(y0, y0 + 60, 5) for x in range(x0, x0 + 60, 5)]
            spread = max(max(v[i] for v in vals) for i in range(3)) - min(min(v[i] for v in vals) for i in range(3))
            if spread < 14: empty += 1
            else: filled.append((row, col, round(spread)))
    return empty, filled
e9, f9 = board_cells(p9)
print('=== BOARD (r9 clear) ===')
print('  empty cells: %d/64  filled/non-uniform: %s' % (e9, f9[:12]))
band_bot = b9[0][1] if b9 else 466
below = [c for c in f9 if c[0] >= 4]
print('  rows 4-7 (32 cells, tops y526-778 all below band bottom %d): all empty = %s' % (band_bot, not below))

# ---------- crops ----------
crops = [
    ('c1_band_r9.png', im9.crop((0, 240, W, 500))),
    ('c2_star_r9.png', im9.crop((max(0, sb[0] - 70), max(0, sb[1] - 70), min(W, sb[2] + 70), min(H, sb[3] + 70)))),
    ('c3_band_r8.png', im8.crop((0, 240, W, 500)) if b8 and abs((b8[0][0] + b8[0][1]) / 2 - 370) < 30 else im8.crop((0, 200, W, 700))),
    ('c4_board_below_r9.png', im9.crop((0, 466, W, 880)).resize((W // 2, (880 - 466) // 2))),
    ('c5_tray_r9.png', im9.crop((0, 870, W, H)).resize((W // 2, (H - 870) // 2))),
    ('c6_full_r9.png', im9.resize((W // 2, H // 2))),
    ('c7_full_r8.png', im8.resize((W // 2, H // 2))),
]
for name, img in crops:
    img.save(OUT + '/' + name)
    print('saved', OUT + '/' + name, img.size)

# ---------- ASCII map of r9 band region ----------
def ascii_map(p, y0, y1, bg, gold, step=8):
    lines = []
    for y in range(y0, y1, step):
        s = ''
        for x in range(0, W, step):
            rr, gg, bb = p[x, y]
            dg = abs(rr - gold[0]) + abs(gg - gold[1]) + abs(bb - gold[2])
            db = abs(rr - bg[0]) + abs(gg - bg[1]) + abs(bb - bg[2])
            s += '#' if (dg > 90 and db > 50) else ('G' if dg < 40 else '.')
        lines.append('%4d %s' % (y, s))
    return '\n'.join(lines)
print('=== ASCII MAP r9 (y250-490, 8px/char; #=graphic G=gold .=bg) ===')
print(ascii_map(p9, 250, 490, bg9, gold9))
