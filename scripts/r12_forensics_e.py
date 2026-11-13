#!/usr/bin/env python3
"""R12 part E: burst center search + spoke widths; star/band precise geometry; tray strip map."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

# ============ 1. BURST CENTER SEARCH in 07_clear ============
im7 = load(R12 + '07_clear.png')
lum7 = im7.mean(axis=2)

def ring_std(cx, cy, r):
    a = np.linspace(0, 2*np.pi, 720, endpoint=False)
    xs = np.clip((cx + r*np.cos(a)).round().astype(int), 0, 719)
    ys = np.clip((cy + r*np.sin(a)).round().astype(int), 0, 1439)
    v = lum7[ys, xs]
    return v.std()

best = None
for cy in range(240, 460, 4):
    for cx in range(280, 440, 4):
        s = np.mean([ring_std(cx, cy, r) for r in (70, 85, 100, 115)])
        if best is None or s > best[0]:
            best = (s, cx, cy)
print("burst center search (max ring angular std): score=%.1f center=(%d,%d)" % best)

s, cx, cy = best
# refine +-3
for cy2 in range(cy-3, cy+4):
    for cx2 in range(cx-3, cx+4):
        s2 = np.mean([ring_std(cx2, cy2, r) for r in (70, 85, 100, 115)])
        if s2 > best[0]:
            best = (s2, cx2, cy2)
s, cx, cy = best
print("refined center=(%d,%d) score=%.1f" % (cx, cy, s))

# luminance at claimed center (360,323)
print("lum at claimed (360,323):", lum7[323, 360], " at found center:", lum7[cy, cx])

# ============ 2. SPOKE CHORDS at multiple radii, high threshold ============
def chords_at(center, r, th):
    cx, cy = center
    n = 2880
    a = np.linspace(0, 2*np.pi, n, endpoint=False)
    hits = np.zeros(n)
    for i, ang in enumerate(a):
        bestv = 0
        for d in (-2, -1, 0, 1, 2):
            x = int(round(cx + (r+d)*np.cos(ang))); y = int(round(cy + (r+d)*np.sin(ang)))
            if 0 <= x < 720 and 0 <= y < 1440:
                bestv = max(bestv, lum7[y, x])
        hits[i] = bestv
    on = hits > th
    runs = []
    i = 0
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            runs.append((i, j)); i = j
        else:
            i += 1
    if len(runs) > 1 and runs[0][0] == 0 and runs[-1][1] == n:
        runs[-1] = (runs[-1][0], runs[-1][1] + runs[0][1]); runs = runs[1:]
    ch = [round((b-a)/n*2*np.pi*r, 1) for a, b in runs]
    return ch

for r in (88.2, 96.6, 105.0):
    for th in (170, 200):
        ch = chords_at((cx, cy), r, th)
        big = [c for c in ch if c > 20]
        small = sorted(c for c in ch if 2 < c <= 20)
        print(f"chords r={r} th={th}: all={ch}")
        print(f"   -> spoke-like (2-20px): {small}  n={len(small)} mean={np.mean(small) if small else 0:.1f}; >20px artifacts: {big}")

# ============ 3. STAR + BAND in hero (color isolation) ============
imh = load(R12 + '01_hero.png')
Rh, Gh, Bh = imh[:,:,0], imh[:,:,1], imh[:,:,2]
lumh = imh.mean(axis=2)

# gold/yellow star: R>150, G>120, B<120, R-B>60
gold = (Rh > 150) & (Gh > 110) & (Bh < 130) & (Rh - Bh > 70)
ys, xs = np.where(gold)
ys = ys[(ys > 150) & (ys < 500)]
if len(ys):
    sel = (ys, xs[(np.where(gold)[0] > 150) & (np.where(gold)[0] < 500)])
print("\nHERO gold pixels y150-500: n=", len(ys), "rows", ys.min() if len(ys) else None, "->", ys.max() if len(ys) else None)

# any bright pixels rows 200-360 (what/where are they?)
for y0, y1 in [(196, 274), (274, 358), (358, 442)]:
    band = lumh[y0:y1, 24:696]
    ys2, xs2 = np.where(band > 150)
    if len(xs2):
        print(f"rows {y0}-{y1}: bright>150 n={len(xs2)} x-extent {24+xs2.min()}..{24+xs2.max()}")
        # column histogram clusters
        cols = np.unique(24+xs2)
        # cluster columns within 40px
        clusters = []
        start = prev = cols[0]
        for c in cols[1:]:
            if c - prev > 40:
                clusters.append((start, prev)); start = c
            prev = c
        clusters.append((start, prev))
        print(f"   x-clusters: {clusters}")
    else:
        print(f"rows {y0}-{y1}: no bright>150")

# band top precise: rows 350-375, mean over x where band exists
for y in range(350, 380):
    row = lumh[y, 24:696]
    print(y, "mean", round(row.mean(),1), "max", round(row.max(),1), "frac>100:", round((row>100).mean(),2))
