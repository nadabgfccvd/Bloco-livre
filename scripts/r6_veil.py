#!/usr/bin/env python3
"""Track = x135..706 => 572px wide... that overlaps the right-side text elements (603..707 = combo pips/stars?).
The bar fill in full shot is x137..499. The track for the bar itself: separate the dim track (lum 40-75,
non-blue) from text. Track region x137..499 => 363px = 0.50w. Claimed 0.62w=446. PARTIAL.
Now danger verification: hot veil OVER board. Compare 06_full board area vs 01_main board:
board zone mean_lum 111.8 (full) vs 50.3 (main empty). Wait, full board is full of pieces so lum naturally high.
Compare EMPTY cells in full board (rows 7-8): wells warm? measured well samples (35,23,29),(37,25,33):
r>b by 6-12 => slightly warm but claim 'wells warm in full 32%'. Let's compute % of empty-well pixels
that are warm across the two empty rows (y 782..866) in 06_full vs 01_main empty well colors.
Also 'hot veil alpha 70k over board': empty wells in main are (41,52,73) blue; in full (35,23,29)-(49,37,46):
dark red-brown. Red channel dominant? (35,23,29): r-g=12, r-b=6 => warm-shifted dark = veil present.
Measure precisely: hue of empty-well pixels in full vs main.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

def well_pixels(root, name, rows=(782, 866)):
    im = load(name, root); p = px(im)
    out = []
    for y in range(rows[0]+8, rows[1]-8):
        for x in range(28, 688):
            c = p[x,y]
            if not (abs(c[0]-24)<10 and abs(c[1]-32)<10 and abs(c[2]-46)<10):  # skip grid lines
                out.append(c)
    return out

for root, name, tag in [(R6,'06_full.png','R6 full empty rows'), (R6,'01_main_classic.png','R6 main all-empty'),
                          (R5,'06_full.png','R5 full empty rows')]:
    pxs = well_pixels(root, name)
    warm = sum(1 for c in pxs if c[0] > c[2] + 8)
    cool = sum(1 for c in pxs if c[2] > c[0] + 8)
    print(f'{tag}: n={len(pxs)} warm {warm} ({100*warm/len(pxs):.0f}%) cool {cool} ({100*cool/len(pxs):.0f}%)')
    cc = Counter(pxs)
    print('   top:', cc.most_common(5))
