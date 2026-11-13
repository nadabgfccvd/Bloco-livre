#!/usr/bin/env python3
"""Tray pieces in clear shot: 524 colored cells at mean lum 75 vs main 908 cells at 160.
Dim ratio = 75/160 = 0.47 => ~53% dim. Claim 'tray dim 134 vs 165 lum' => 134/165=0.81.
Their numbers wrong BUT dimming IS real and strong (~53%). Also 'single focal point'.
Bar track: lum signature shows track at lum 2*26=52 across x~136..~500 (the '02's) => yes,
full-width dim track EXISTS behind the green fill. Track x 137..499 = 363 wide. Claim w*0.62=446
=> measured 363 = 0.50*w. PARTIAL on width; but is there a 446 track? Track maybe 137..582?
Check the track bounds precisely (lum ~52 region).
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('01_main_classic.png'); p = px(im)
print('== track bounds row y=1246 (lum band 40..70) ==')
xs = [x for x in range(0,720) if 40 < lum(p[x,1246]) < 75]
print('track x:', min(xs), '..', max(xs), 'width', max(xs)-min(xs)+1)

# pips at 25% of track? dark notches crossing the track
print()
print('== vertical dark notches in track (x 137..500, y 1236..1255) ==')
for x in range(137, 500):
    col = [p[x,y] for y in range(1236, 1256)]
    if all(lum(c) < 35 for c in col[8:16]):
        print('   notch at x=', x)

# '%' label? find '% do tabuleiro' text: bright spans row 1310: x44..96 (left word), 108..154, 251..292,
# 403..460, 471..483, 586..641. So multiple text groups. Sample colors and heights.
print()
print('== strip text bands heights ==')
for y0,y1 in [(1300,1330),(1400,1435)]:
    ys = {}
    for y in range(y0,y1):
        n = sum(1 for x in range(0,720) if lum(p[x,y])>100)
        if n>5: ys[y]=n
    if ys:
        kk = sorted(ys)
        print(f'   band {y0}-{y1}: rows {kk[0]}..{kk[-1]} peak {max(ys.values())}')
