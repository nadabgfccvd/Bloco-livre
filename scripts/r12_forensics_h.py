#!/usr/bin/env python3
"""R12 part H: whole-hero scan for gold star pixels; then star geometry + skins + streak + board."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

imh = load(R12 + '01_hero.png')
R, G, B = imh[:,:,0], imh[:,:,1], imh[:,:,2]

# Gold/yellow anything above y<360 (star zone) anywhere in hero
gold = (R > 200) & (G > 150) & (B < 200) & (R - B > 80)
ys, xs = np.where(gold)
m = ys < 365
print("gold px above y365: n=", m.sum())
if m.sum():
    print("  rows", ys[m].min(), "->", ys[m].max(), "cols", xs[m].min(), "->", xs[m].max())
    # histogram rows
    import collections
    cnt = collections.Counter(ys[m])
    top = sorted(cnt.items())[:8]
    print("  rows histogram (first):", top)
    print("  rows histogram (last):", sorted(cnt.items())[-8:])

# The BAND: gold at rows 365-435. Star: gold at rows?? Let's find all gold regions and cluster by rows.
cnt = collections.Counter(ys[m])
rows_sorted = sorted(cnt)
# cluster rows with gaps
clusters = []
if rows_sorted:
    start = prev = rows_sorted[0]
    for r in rows_sorted[1:]:
        if r - prev > 6:
            clusters.append((start, prev))
            start = r
        prev = r
    clusters.append((start, prev))
print("row-clusters of gold above y365:", clusters)

# same for r11 to see the change
im11 = load(R11 + '01_hero.png')
R1, G1, B1 = im11[:,:,0], im11[:,:,1], im11[:,:,2]
gold1 = (R1 > 200) & (G1 > 150) & (B1 < 200) & (R1 - B1 > 80)
ys1, xs1 = np.where(gold1)
m1 = ys1 < 365
print("r11 gold px above y365: n=", m1.sum())
if m1.sum():
    cnt1 = collections.Counter(ys1[m1])
    rs = sorted(cnt1)
    cl = []
    if rs:
        s = p = rs[0]
        for r in rs[1:]:
            if r - p > 6:
                cl.append((s, p)); s = r
            p = r
        cl.append((s, p))
    print("r11 row-clusters:", cl)

# check y243-347 claim: count gold px in y240-350 in r12
m2 = (ys >= 240) & (ys <= 350)
print("r12 gold px y240-350:", m2.sum())
if m2.sum():
    print("   rows", ys[m2].min(), "->", ys[m2].max(), "cols", xs[m2].min(), "->", xs[m2].max())

# width of star at y=300 if exists
for yy in (250, 280, 300, 330, 345):
    sel = m & (ys == yy)
    if sel.sum():
        print(f"r12 gold row y={yy}: x {xs[sel].min()}..{xs[sel].max()}  n={sel.sum()}")
    else:
        print(f"r12 gold row y={yy}: none")

# What about star maybe drawn in different palette (white/platinum)? Look for ANY pixels y230-350 that differ strongly from the two bg blues.
lum = imh.mean(axis=2)
bg = ((R//8==4) | (R//8==5))
for yy in range(228, 356, 4):
    row_dev = []
    for x in range(240, 480):
        r, g, b = R[yy,x], G[yy,x], B[yy,x]
        if not (20 <= r <= 90 and 25 <= g <= 105 and 40 <= b <= 130):
            row_dev.append((x, (r,g,b)))
    if row_dev:
        print(f"y={yy}: non-bg px n={len(row_dev)} e.g. {row_dev[:3]}..{row_dev[-3:]}")
