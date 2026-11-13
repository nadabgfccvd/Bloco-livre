#!/usr/bin/env python3
"""Final pieces:
1) Danger diff between R6 and R5 full shot is small (6.4 mean) — the danger state barely changed
   visually between rounds except warm wells (22% warm) and streak bar. Verify the 'k formula'
   reach: R5 06_full also had same occupancy? measure R5 06_full occupancy grid.
2) 'warm/cool edges 391/930': measured left edge warm 638 cool 2725, right same => warm/cool edge
   = 638/2725, not 391/930. Builder's numbers off, but direction: edges cool-dominant (bg navy).
3) skins: check piece color variety per skin (02_skin0 shows 5+ piece colors; neon 03_skin1 dark
   low-lum (45.8) — very dark board; 05_skin3 pale).
4) Also check 02_skin0 (Clássico mid-game) shows occupancy 40/64 = 62.5% => mid-game consistent.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from r6_occupancy import XCELLS, YCELLS, cell_filled

im = load('06_full.png', R5)
filled = 0
for (y0,y1) in YCELLS:
    line = ''
    for (x0,x1) in XCELLS:
        f = cell_filled(im, x0,x1,y0,y1)
        filled += f; line += '#' if f else '.'
    print(line)
print('R5 06_full filled:', filled, '/64')

# edge measurement on r6 full (already): warm 638 cool 2725 per 20px strip over 676 rows.
# Builder claims 391/930. Recompute with tighter warm def (r-b>25):
im = load('06_full.png'); p = px(im)
lw = sum(1 for y in range(190,866) for x in range(0,20) if p[x,y][0] > p[x,y][2] + 25)
lc = sum(1 for y in range(190,866) for x in range(0,20) if p[x,y][2] > p[x,y][0] + 25)
rw = sum(1 for y in range(190,866) for x in range(700,720) if p[x,y][0] > p[x,y][2] + 25)
rc = sum(1 for y in range(190,866) for x in range(700,720) if p[x,y][2] > p[x,y][0] + 25)
print(f'edges (r-b>25): left warm {lw} cool {lc} | right warm {rw} cool {rc} | total warm {lw+rw} cool {lc+rc}')
