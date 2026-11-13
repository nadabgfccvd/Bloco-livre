#!/usr/bin/env python3
"""Danger claim math: (dangerFrac-0.55)/0.25 at 81% occupancy => k=(0.8125-0.55)/0.25=1.05 -> clamp 1.0. OK.
Occupancy 52/64 = 81.25% CONFIRMED by grid. Hot veil: empty wells warm 22% in R6 full vs 0% in R5 full
(wells were neutral/cool before). Claim 'wells warm in full 32%' — measured 22% (r>b+8) — if threshold
r>b+4: recount. Let's also check the hot veil alpha 70: expected color = bg*(0.725)+red*0.275? With
alpha 70/255=0.27: (41,52,73)*0.73 + (255,60,40)*0.27 = (105,55,63). Measured (49,37,46)... that's more
like alpha ~0.15-0.2 over a darker bg. But well pixel (77,50,65) close to alpha 0.25.
Overall: veil EXISTS over empty wells (warm shift), strength moderate.
Final: verify '138 unique colors in streak zone vs 19'. We measured 91 saturated unique colors in R6 main
vs 90 in R5 main (identical method!). The claim of 138 vs 19 is VAPOR under our method. Try their likely
method: count unique colors in the streak zone REGION (all pixels) — R6 main 1368 vs R5 main 1316: no.
Try unique colors of bar+pips+stars only: small set. Let's test 'zone' = y1118..1440 whole strip unique
colors quantized to nearest 8: probably similar. The 138 vs 19 claim looks like a fantasy number.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

def q8(c): return (c[0]//8*8, c[1]//8*8, c[2]//8*8)

for root, name, tag in [(R6,'01_main_classic.png','R6 main'), (R5,'01_main_classic.png','R5 main'),
                         (R6,'06_full.png','R6 full'), (R5,'06_full.png','R5 full')]:
    im = load(name, root); p = px(im)
    raw = set(); q = set()
    for y in range(1118, 1440):
        for x in range(0, 720):
            c = p[x,y]; raw.add(c); q.add(q8(c))
    print(f'{tag}: raw unique {len(raw)}  q8 unique {len(q)}')

# bar only colors: y 1236..1255, x 135..710
for root, name, tag in [(R6,'01_main_classic.png','R6 main bar'), (R5,'01_main_classic.png','R5 main bar')]:
    im = load(name, root); p = px(im)
    raw = set()
    for y in range(1236, 1256):
        for x in range(135, 710):
            raw.add(p[x,y])
    print(f'{tag}: unique colors {len(raw)}')
