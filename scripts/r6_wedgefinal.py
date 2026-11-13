#!/usr/bin/env python3
"""The dark region within the wedge is not letter-like: it's a contiguous dark mass (the un-gold
wedge interior = the empty wells showing through where gold alpha is low, or dark gradient).
No banner text exists. The wedge = diagonal gold sweep with no text => 'banner' has NO text,
asymmetric diagonal. FINAL SUMMARY of all measurements for scoring."""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter
from PIL import Image

# Verify wedge vs banner: sample a horizontal cut through wedge y=440 to see color pattern
im = load('07_clear.png'); p = px(im)
print('== wedge row y=440 color sequence (x 80..640 step 20) ==')
for x in range(80, 660, 40):
    c = p[x,440]
    print(f'   x={x:3d}: ({c[0]:3d},{c[1]:3d},{c[2]:3d})')

# Check gold fan text: maybe text is dark navy on gold at y 120..170 (earlier dark columns
# x 0..719 at y100..125 = edges only). So no text on fan either.
# Verify one more: is there ANY text in the celebration besides HUD? bright white rows y31..53
# are the HUD labels (PONTOS/RECORDE white). In clear shot letters at 383..415 & 424..446 are
# taller (48px) and gold-tinted (111,104,80) — maybe a 'PARABÉNS' word in gold at same spot?
print()
print('== clear HUD letters rows 29..76 clusters ==')
cols = {}
for y in range(29, 77):
    for x in range(200, 520):
        c = p[x,y]
        if lum(c) > 100:
            cols.setdefault(x, []).append(y)
xs = sorted(cols)
cl = []
for x in xs:
    if cl and x - cl[-1][-1] <= 7: cl[-1].append(x)
    else: cl.append([x])
print('letter clusters:', [(c[0], c[-1]) for c in cl])
for c in cl:
    ys = [y for y in range(29,77) if any(lum(p[x,y])>100 for x in range(c[0],c[-1]+1))]
    print(f'   x{c[0]}..{c[-1]}: rows {min(ys)}..{max(ys)}')
