#!/usr/bin/env python3
"""Clean up: import guard caused re-runs. Direct analysis only.
Also final HUD: 01_main has empty board - the 'main classic' shot is at game start.
Check the 01_main tray has piece colors => fine.
Compose the ASCII of tray and streak for final judgment."""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

im = load('07_clear.png'); p = px(im)
print('== dark-on-gold text: correct y window ==')
# maybe the text sits y 105..125 with looser dark def
cols = {}
for y in range(90, 140):
    for x in range(40, 690):
        c = p[x,y]
        if lum(c) < 110 and c[0] < c[1]:
            cols.setdefault(x, []).append(y)
xs = sorted(cols)
if xs:
    cl = []
    for x in xs:
        if cl and x - cl[-1][-1] <= 8: cl[-1].append(x)
        else: cl.append([x])
    print('clusters:', [(c[0], c[-1]) for c in cl])
else:
    print('none')

# Tray ascii for main
im2 = load('01_main_classic.png')
print()
print('== tray zone ascii (y 950..1110) ==')
iml = im2.convert('L').crop((0, 950, 720, 1110)).resize((72, 14))
pl = iml.load()
for y in range(14):
    print(''.join(' .:-=+*#%@'[min(9, pl[x,y]*10//256)] for x in range(72)))
