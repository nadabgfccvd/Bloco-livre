#!/usr/bin/env python3
"""Banner text vs banner band. The rows y60..179 hold a big gold mass narrowing to center at top,
widening downward -> that's the RAYS + banner. Claim: banner band #F6C445 with white hairline.
Find horizontal runs of exact-ish band color (246,196,69 +-12) per row; find hairline rows
adjacent. Check banner text (dark text on gold?) — 'PARABÉNS'?
Also: what sits between y180..190 and is there a slide offset? Check band left/right extents symmetry.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

im = load('07_clear.png'); p = px(im)

def near(c, t, tol):
    return all(abs(c[i]-t[i]) <= tol for i in range(3))

# banner band candidates: rows containing many (246,196,69)-ish pixels
print('== band-color rows ==')
band_rows = {}
for y in range(0, 400):
    xs = [x for x in range(0, 720) if near(p[x,y], (246,196,69), 22)]
    if len(xs) > 40:
        band_rows[y] = (min(xs), max(xs), len(xs))
if band_rows:
    ys = sorted(band_rows)
    print('rows:', ys[0], '..', ys[-1])
    for y in ys[:5] + ys[len(ys)//2:len(ys)//2+1] + ys[-5:]:
        print(f'   y={y}: x {band_rows[y][0]}..{band_rows[y][1]} n={band_rows[y][2]} center={(band_rows[y][0]+band_rows[y][1])/2:.0f}')
else:
    print('NO band-color rows found (F6C445 not present)')

# white hairline: rows just above/below band with bright white runs
print()
print('== white-ish run rows in y 0..400 ==')
for y in range(0, 400):
    xs = [x for x in range(0, 720) if p[x,y][0] > 230 and p[x,y][1] > 230 and p[x,y][2] > 220]
    if len(xs) > 60:
        print(f'   y={y}: n={len(xs)} x {min(xs)}..{max(xs)}')

# Banner text? dark pixels inside band area y 100..180
print()
print('== dark text inside gold zone (y 100..180): columns with dark px ==')
dark_cols = Counter()
for y in range(100, 180):
    for x in range(0, 720):
        c = p[x,y]
        if lum(c) < 90 and near(c, (0,0,0), 60):
            dark_cols[x] += 1
print('dark columns count:', len(dark_cols), 'total dark px:', sum(dark_cols.values()))
if dark_cols:
    xs = sorted(dark_cols)
    print('dark text bbox x', xs[0], '..', xs[-1])
    ys = [y for y in range(100,180) if any(lum(p[x,y])<90 for x in range(xs[0], xs[-1]+1))]
    print('dark text bbox y', min(ys), '..', max(ys))
    # sample the dark color
    print('dark sample colors:', Counter([p[x,y] for x in range(xs[0],xs[-1]+1,2) for y in range(100,180) if lum(p[x,y])<90]).most_common(3))
