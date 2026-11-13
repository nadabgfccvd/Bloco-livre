#!/usr/bin/env python3
"""Verify: (a) 06 board fill %, (b) 01 tray piece overflow, (c) 07 star ring pixel hunt."""
from PIL import Image

SRC = '/home/z/my-project/critic_shots/r2'

# board grid: x0=15,y0=200, w=690, 8 cells -> pitch 86.25
def cell_centers():
    pts = []
    for i in range(8):
        for j in range(8):
            cy = int(200 + 86.25*i + 43)
            cx = int(15 + 86.25*j + 43)
            pts.append((cx, cy, i, j))
    return pts

im_empty = Image.open(f'{SRC}/01_main_classic.png').convert('RGB')  # empty board
empty_ref = [im_empty.getpixel((cx, cy)) for cx, cy, _, _ in cell_centers()]

for name in ['02_skin0', '03_skin1', '04_skin2', '05_skin3', '06_full', '07_clear']:
    im = Image.open(f'{SRC}/{name}.png').convert('RGB')
    filled = 0
    for (cx, cy, _, _), ref in zip(cell_centers(), empty_ref):
        p = im.getpixel((cx, cy))
        if max(abs(p[k]-ref[k]) for k in range(3)) > 40:
            filled += 1
    print(f'{name}: board fill ~{filled}/64 = {100*filled/64:.0f}%')

print()
# (b) tray overflow in 01: is the orange piece drawn above y=905 (tray top) / below 1080?
im1 = Image.open(f'{SRC}/01_main_classic.png').convert('RGB')
def row_has_color(y, x0, x1, thresh=60):
    hits = []
    for x in range(x0, x1, 2):
        p = im1.getpixel((x, y))
        if max(p)-min(p) > thresh:  # saturated = piece color
            hits.append((x, p))
    return hits[:3]
for y in [870, 880, 890, 896, 905, 910, 1060, 1075, 1090, 1100, 1110, 1120, 1130, 1140, 1150, 1160]:
    h = row_has_color(y, 100, 720)
    print(f'y={y}: saturated piece pixels:', h if h else 'none')

print()
# (c) star ring hunt in 07: bright yellow/white star pixels INSIDE board area, excluding bottom 2 rows
im7 = Image.open(f'{SRC}/07_clear.png').convert('RGB')
stars = []
for y in range(210, 680, 2):   # board area above the banner/bottom rows
    for x in range(20, 700, 2):
        r, g, b = im7.getpixel((x, y))
        if r > 220 and g > 200 and b < 160:  # gold/yellow star
            stars.append((x, y))
        elif r > 235 and g > 235 and b > 235:
            stars.append((x, y))
print('star-like bright pixels above y=680 in board:', len(stars), stars[:10])
