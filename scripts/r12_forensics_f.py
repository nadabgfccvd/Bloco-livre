#!/usr/bin/env python3
"""R12 part F: verify star (280-523 cluster) vs band; hero trays; skin shots; streak."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

imh = load(R12 + '01_hero.png')
lumh = imh.mean(axis=2)

# Star cluster: x 280..523 bright rows. Band presumably x 111..185 & 619..692 (side elements).
print("=== STAR cluster (x280-523) row-by-row vertical extent, y230..365 ===")
for y in range(230, 366, 3):
    seg = lumh[y, 280:524]
    n = (seg > 150).sum()
    if n:
        xs = np.where(seg > 150)[0]
        print(y, "n=", n, "x", 280+xs.min(), "..", 280+xs.max(), "max", round(seg.max(),0))
    else:
        print(y, "-")

# find star body extent precisely with looser threshold
print("\n=== star rows with any px>110 (x280-523) ===")
rows = []
for y in range(220, 366):
    if (lumh[y, 280:524] > 110).any():
        rows.append(y)
print("rows:", rows[0] if rows else None, "..", rows[-1] if rows else None, "count", len(rows))

# gap between star bottom and band top
band_top = 365  # from frac>100 rising at 365-366
if rows:
    print("star bottom:", rows[-1], "band top (bright frac rise):", band_top, "GAP:", band_top - rows[-1])

# horizontal star extent at mid
if rows:
    ymid = rows[len(rows)//2]
    seg = lumh[ymid, 200:600]
    xs = np.where(seg > 110)[0]
    print("star mid row", ymid, "x", 200+xs.min(), "..", 200+xs.max(), "width", xs.max()-xs.min())

# ============ TRAY: measure the rim gradient profile in absolute terms ============
print("\n=== HERO tray absolute luminance rows 855..900 (x40-680) ===")
for y in range(855, 901, 2):
    print(y, round(lumh[y, 40:680].mean(),1), round(lumh[y, 40:680].max(),1))

# compare to r11
im11 = load(R11 + '01_hero.png')
print("\n=== r11 HERO tray rows 855..900 ===")
for y in range(855, 901, 2):
    print(y, round(im11.mean(axis=2)[y, 40:680].mean(),1), round(im11.mean(axis=2)[y, 40:680].max(),1))
