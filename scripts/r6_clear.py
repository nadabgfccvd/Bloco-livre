#!/usr/bin/env python3
"""07_clear.png celebration forensics (the payoff frame).
Claims to verify:
- gold halo behind board: fixed #FFE08A / #FFF7D8, 3 layers alpha 96/72/60
- 12 glory rays alternating alpha 110
- banner band #F6C445 with white hairline, underlay centered on board cx (no slide), rows 466..698
- crown of 12 gold stars + 1 major star INSIDE board over wells, rx=3*cell ry=2.6*cell, visible in still
- gold in-board 3155px, halo outside 216px
- tray dimmed 55% vs main (134 vs 165 lum)
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png'); p = px(im); w,h = im.size
print('size', im.size)

# region stats
regions = {
  'board (20,190,696,866)': (20,190,696,866),
  'halo left edge (0,190,20,866)': (0,190,20,866),
  'halo right edge (700,190,720,866)': (700,190,720,866),
  'halo above (0,110,720,190)': (0,110,720,190),
  'halo below (0,866,720,950)': (0,866,720,950),
  'tray (0,950,720,1110)': (0,950,720,1110),
  'streak strip (0,1118,720,1440)': (0,1118,720,1440),
}
for k, b in regions.items():
    st = stats(im, b)
    print(f"{k}: mean_lum {st['mean_lum']:.1f} gold {st['gold_px']} cyan {st['cyan_px']} warm {st['warm_px']} cool {st['cool_px']}")
    print('   top colors:', st['top_colors'][:4])

# compare tray luminance vs 01_main_classic tray
im1 = load('01_main_classic.png')
st_tr_r6clear = stats(im, (0,950,720,1110))
st_tr_main = stats(im1, (0,950,720,1110))
print()
print(f"tray lum main={st_tr_main['mean_lum']:.1f}  clear={st_tr_r6clear['mean_lum']:.1f}  ratio={st_tr_r6clear['mean_lum']/st_tr_main['mean_lum']:.3f}")

# gold color cluster analysis in board + around
gold_pixels = {}
for y in range(0, h, 2):
    for x in range(0, w, 2):
        c = p[x,y]
        if is_goldish(c):
            key = c
            gold_pixels[key] = gold_pixels.get(key,0)+1
print()
print('== distinct goldish sample colors (top 12) ==')
for c, n in sorted(gold_pixels.items(), key=lambda kv: -kv[1])[:12]:
    print('   ', c, n)
