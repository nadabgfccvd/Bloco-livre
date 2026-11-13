#!/usr/bin/env python3
"""R9 final consolidated measurements. Geometry: board 8x8 x24-696 y190-866 cell84; tray y880-1110; streak y1240-1250."""
import math, os
from PIL import Image

p9 = Image.open('/home/z/my-project/critic_shots/r9/07_clear.png').convert('RGB').load()
p8 = Image.open('/home/z/my-project/critic_shots/r8/07_clear.png').convert('RGB').load()
W, H = 720, 1440

def warm(c):  # gold-ish (band, star, spokes)
    return c[0] > 180 and (c[0] - c[2]) > 60 and c[1] > 120
def bright(c):  # star core bright yellow
    return sum(c) > 540 and (c[0] - c[2]) > 80

# ---- 1. BAND rows (fraction of x40..680 warm) ----
def band(p):
    rows = [y for y in range(200, 500) if sum(1 for x in range(40, 680, 4) if warm(p[x, y])) / 160 > 0.55]
    if not rows: return None
    return min(rows), max(rows)
b9, b8 = band(p9), band(p8)
print('BAND r9: y%d-%d h=%d   (claim y321-466 h145)' % (b9[0], b9[1], b9[1] - b9[0] + 1))
print('BAND r8: y%d-%d h=%d' % (b8[0], b8[1], b8[1] - b8[0] + 1))
yc9 = (b9[0] + b9[1]) // 2
cols9 = [x for x in range(W) if warm(p9[x, yc9])]
print('BAND r9 x-extent at y%d: %d-%d (margins L%d R%d)' % (yc9, min(cols9), max(cols9), min(cols9), W - 1 - max(cols9)))

# ---- 2. TEXT bbox (dark pixels inside band rows) ----
def textbbox(p, b):
    pts = [(x, y) for y in range(b[0], b[1] + 1) for x in range(30, 690) if sum(p[x, y]) < 260]
    if not pts: return None
    xs = [a for a, _ in pts]; ys = [q for _, q in pts]
    return min(xs), max(xs), min(ys), max(ys)
t9 = textbbox(p9, b9); t8 = textbbox(p8, b8)
tc = (t9[2] + t9[3]) / 2; bc = (b9[0] + b9[1]) / 2
print('TEXT r9: x%d-%d y%d-%d (h%d) center y%.0f vs band center y%.0f offset %+.0f px   (claim y379-417 c398 vs 394 = +4)' % (t9[0], t9[1], t9[2], t9[3], t9[3] - t9[2] + 1, tc, bc, tc - bc))
t8c = (t8[2] + t8[3]) / 2; b8c = (b8[0] + b8[1]) / 2
print('TEXT r8: y%d-%d center %.0f vs band center %.0f offset %+.0f px' % (t8[2], t8[3], t8c, b8c, t8c - b8c))

# ---- 3. STAR core (bright blob above band center) ----
def blob(p, y0, y1, test):
    pts = [(x, y) for y in range(y0, y1) for x in range(W) if test(p[x, y])]
    if not pts: return None
    xs = [a for a, _ in pts]; ys = [q for _, q in pts]
    return dict(x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), n=len(pts),
                cx=sum(xs) / len(xs), cy=sum(ys) / len(ys))
s9 = blob(p9, 200, b9[1] - 2, bright)
print('STAR r9 bright blob: x%d-%d y%d-%d (w%d h%d) centroid (%.0f,%.0f)  claim 0.78*84=%.0f px' % (
    s9['x0'], s9['x1'], s9['y0'], s9['y1'], s9['x1'] - s9['x0'] + 1, s9['y1'] - s9['y0'] + 1, s9['cx'], s9['cy'], 0.78 * 84))
s8 = blob(p8, 200, b8[1] - 2, bright)
if s8: print('STAR r8 bright blob: x%d-%d y%d-%d (w%d h%d)' % (s8['x0'], s8['x1'], s8['y0'], s8['y1'], s8['x1'] - s8['x0'] + 1, s8['y1'] - s8['y0'] + 1))

# ---- 4. SPOKES: warm pixels above band top, excluding star core bbox ----
def spokes(p, b, s):
    top = b[0]
    pts = [(x, y) for y in range(150, top - 1) for x in range(W)
           if warm(p[x, y]) and not (s['x0'] - 2 <= x <= s['x1'] + 2 and s['y0'] - 2 <= y <= s['y1'] + 2)]
    if not pts: return []
    # cluster by proximity
    seen = set(); groups = []
    import sys; sys.setrecursionlimit(10000)
    P = set(pts)
    for pt in pts:
        if pt in seen: continue
        stack = [pt]; seen.add(pt); comp = []
        while stack:
            c = stack.pop(); comp.append(c)
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    q = (c[0] + dx, c[1] + dy)
                    if q in P and q not in seen: seen.add(q); stack.append(q)
        groups.append(comp)
    out = []
    for comp in groups:
        xs = [a for a, _ in comp]; ys = [q for _, q in comp]
        if len(comp) < 30: continue
        out.append(dict(x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), n=len(comp),
                        cx=sum(xs) / len(xs), cy=sum(ys) / len(ys)))
    return out
sp9 = spokes(p9, b9, s9)
print('SPOKES r9 (warm comps above band, excl. star): %d' % len(sp9))
for c in sp9: print('   n=%d x%d-%d y%d-%d centroid (%.0f,%.0f) w%d' % (c['n'], c['x0'], c['x1'], c['y0'], c['y1'], c['cx'], c['cy'], c['x1'] - c['x0'] + 1))
sp8 = spokes(p8, b8, s8) if s8 else []
print('SPOKES/rays r8 comps: %d  extents:' % len(sp8))
for c in sp8[:10]: print('   n=%d x%d-%d y%d-%d w%d h%d' % (c['n'], c['x0'], c['x1'], c['y0'], c['y1'], c['x1'] - c['x0'] + 1, c['y1'] - c['y0'] + 1))

# spoke widths via radial scan from star centroid (r beyond core)
sx, sy = s9['cx'], s9['cy']
coreR = max(s9['x1'] - s9['x0'], s9['y1'] - s9['y0']) / 2
print('star coreR ~%.0f' % coreR)
rad = []
for deg in range(0, 360, 10):
    r = math.radians(deg); far = 0
    for rr in range(int(coreR) - 5, 160):
        x, y = int(sx + rr * math.cos(r)), int(sy + rr * math.sin(r))
        if 0 <= x < W and 150 <= y < b9[1] and warm(p9[x, y]): far = rr
    if far > coreR + 6: rad.append((deg, far))
print('radial warm extents beyond core (deg,len):', rad)

# ---- 5. EDGE TOUCH ----
allwarm = [(x, y) for y in range(110, b9[1] + 3) for x in range(W) if warm(p9[x, y])]
xs = [a for a, _ in allwarm]; ys = [q for _, q in allwarm]
print('CELEBRATION warm envelope r9: x%d-%d y%d-%d  margins L%d R%d T%d (screen 720x1440)' % (min(xs), max(xs), min(ys), max(ys), min(xs), W - 1 - max(xs), min(ys)))
aw8 = [(x, y) for y in range(110, 700) for x in range(W) if warm(p8[x, y])]
x8 = [a for a, _ in aw8]; y8 = [q for _, q in aw8]
print('CELEBRATION warm envelope r8: x%d-%d y%d-%d  touches edge: %s' % (min(x8), max(x8), min(y8), max(y8), min(x8) <= 2 or max(x8) >= W - 3 or min(y8) <= 2))

# ---- 6. BOARD rows 4-7 emptiness (32 cells below band) ----
bad = []
for row in range(4, 8):
    for col in range(8):
        x0 = 24 + col * 84 + 14; y0 = 190 + row * 84 + 14
        vals = [sum(p9[x, y]) / 3 for y in range(y0, y0 + 56, 4) for x in range(x0, x0 + 56, 4)]
        m = sum(vals) / len(vals)
        sd = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5
        if sd > 7: bad.append((row, col, round(sd, 1)))
print('BOARD rows4-7 r9: non-uniform cells (sd>7): %s  -> 32/32 empty: %s' % (bad if bad else 'none', not bad))
# also rows 0-3 for context
bad03 = []
for row in range(0, 4):
    for col in range(8):
        x0 = 24 + col * 84 + 14; y0 = 190 + row * 84 + 14
        vals = [sum(p9[x, y]) / 3 for y in range(y0, y0 + 56, 4) for x in range(x0, x0 + 56, 4)]
        m = sum(vals) / len(vals)
        sd = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5
        if sd > 7: bad03.append((row, col))
print('BOARD rows0-3 r9: cells with content/overlay: %d/32 (covered by celebration)' % len(bad03))

# ---- 7. HAIRLINES thin dark rows ----
def hair(p, y0, y1):
    rows = [y for y in range(y0, y1) if sum(1 for x in range(24, 696, 4) if sum(p[x, y]) < 300) / 169 > 0.8]
    runs = []
    if rows:
        s = prev = rows[0]
        for y in rows[1:]:
            if y - prev <= 1: prev = y
            else: runs.append((s, prev)); s = prev = y
        runs.append((s, prev))
    return [(a, c, c - a + 1) for a, c in runs if 1 <= c - a + 1 <= 10]
print('HAIRLINES r9 y866-1260:', hair(p9, 866, 1260))
print('HAIRLINES r8 y866-1260:', hair(p8, 866, 1260))
print('HAIRLINES r9 y1150-1300 full width:', hair(p9, 1150, 1300))
print('HAIRLINES r8 y1150-1300 full width:', hair(p8, 1150, 1300))
# vertical hairlines in tray
def vhair(p):
    cols = [x for x in range(0, W) if sum(1 for y in range(884, 1106, 4) if sum(p[x, y]) < 300) / 56 > 0.8]
    runs = []
    if cols:
        s = prev = cols[0]
        for x in cols[1:]:
            if x - prev <= 1: prev = x
            else: runs.append((s, prev)); s = prev = x
        runs.append((s, prev))
    return [(a, c, c - a + 1) for a, c in runs]
print('V-HAIRLINES r9 tray:', vhair(p9))
print('V-HAIRLINES r8 tray:', vhair(p8))

# ---- 8. STREAK strip y1240-1250 ----
def strip(p):
    out = []
    for y in range(1235, 1256):
        cs = [p[x, y] for x in range(24, 696, 8)]
        nz = [c for c in cs if sum(c) > 330]
        out.append((y, len(nz), cs[0], cs[30]))
    return out
print('STREAK r9 (y, bright-frac/84, left, mid):', strip(p9))
print('STREAK r8:', strip(p8))

# ---- 9. tray preview count ----
def trayblobs(p):
    cols = [x for x in range(24, 696) if sum(1 for y in range(890, 1100, 5) if sum(p[x, y]) > 380) / 42 > 0.35]
    if not cols: return 0, []
    groups = []; s = prev = cols[0]
    for x in cols[1:]:
        if x - prev > 30: groups.append((s, prev)); s = prev = x
        prev = x
    groups.append((s, prev))
    return len(groups), groups
print('TRAY bright groups r9:', trayblobs(p9))

# crop for record
im = Image.open('/home/z/my-project/critic_shots/r9/07_clear.png').convert('RGB')
im.crop((0, 150, 720, 520)).save('/tmp/critic_crops_r9/c14_celebration_full_r9.png')
im.crop((0, 850, 720, 1290)).save('/tmp/critic_crops_r9/c15_lower_r9.png')
Image.open('/home/z/my-project/critic_shots/r8/07_clear.png').crop((0, 150, 720, 700)).save('/tmp/critic_crops_r9/c16_celebration_full_r8.png')
print('done')
