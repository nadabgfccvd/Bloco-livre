#!/usr/bin/env python3
"""Last checks:
1) 01_main_classic board is EMPTY (0/64) — a 'main classic' shot with empty board? That's the
   still/idle frame presumably. Verify pieces exist anywhere (tray has pieces: 908 colored cells).
2) Perfect-clear payoff: 07_clear board contains star crown; does the board still show pieces?
   The clear frame: board shows dark wells + crown. Confirm empty board (no pieces) in 07_clear:
3) HUD label sizes: label cap 23px for both PONTOS and RECORDE; values 16 vs 13px.
   Claim: 0.24cell=20px / 0.19cell=16px. => values match 16px for PONTOS value! and RECORDE value 13
   (0.15cell). Claim sizes don't match labels (23px both). PARTIAL.
4) One more check: banner 'slide offset' — in R5 07_clear was there an offset banner? compare
   gold wedge position r5 vs r6: r5 clear had cyan wash instead (ascii). Actually r5 wedge?
   Measure goldish wedge in r5 clear.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from r6_occupancy import cell_filled, XCELLS, YCELLS

im = load('07_clear.png')
filled = sum(cell_filled(im, x0,x1,y0,y1) for (y0,y1) in YCELLS for (x0,x1) in XCELLS)
print('07_clear piece cells:', filled, '/64 (expect 0 for perfect clear)')

im5 = load('07_clear.png', R5)
print()
print('== R5 clear: gold distribution (is there any gold at all?) ==')
p5 = px(im5)
g = 0
for y in range(0,1440,2):
    for x in range(0,720,2):
        if is_goldish(p5[x,y]): g += 1
print('goldish px (stride2):', g*4, 'approx total')

c = sum(1 for y in range(0,1440,2) for x in range(0,720,2) if is_cyanish(p5[x,y]))
print('cyanish px (stride2):', c*4, 'approx total')

# r6 clear cyan check
im6 = load('07_clear.png'); p6 = px(im6)
cy = sum(1 for y in range(0,1440,2) for x in range(0,720,2) if is_cyanish(p6[x,y]))
print('R6 clear cyanish px:', cy*4)
