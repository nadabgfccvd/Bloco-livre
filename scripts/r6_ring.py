#!/usr/bin/env python3
"""Crown visibility check: on R6 clear the board contains gold stars ring (visible in still) —
seen in ASCII as g clusters + dark band rows in middle. On R5 the board had a huge CYAN wash (c) instead.
Now: tray dim, banner underlay rows 466..698 claim, and the 'always visible in still' question.
R6 ASCII rows 11-16 show a dark band (dots) — the board wells are DIMMED inside the star ellipse?
Measure: board interior luminance in clear shot: center region vs edges.
Also measure the star ring: is it 12 stars + 1 major? From connected components: 12 stars sizes
743-1929 + major 15634 + 2 small side sparks (138, 96, 72). The 15634 'major' is actually the
banner/wedge shape above center, not a star. Let's isolate: components within ellipse ring radius
190..270: count them.
"""
import sys, math
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png'); p = px(im)
cx, cy = 358, 528

def gold_at(x, y):
    c = p[x,y]
    return c[0] > 180 and c[1] > 130 and c[2] < 150 and c[0] > c[2]+40

# list all components again with ellipse radius classification
seen = set(); comps = []
for y in range(190, 866):
    for x in range(20, 696):
        if (x,y) in seen or not gold_at(x,y): continue
        stack=[(x,y)]; seen.add((x,y)); comp=[]
        while stack:
            ax,ay = stack.pop(); comp.append((ax,ay))
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx,ny = ax+dx, ay+dy
                if 20<=nx<696 and 190<=ny<866 and (nx,ny) not in seen and gold_at(nx,ny):
                    seen.add((nx,ny)); stack.append((nx,ny))
        comps.append(comp)

ring = []; inner = []
for c in comps:
    if len(c) < 60: continue
    mx = sum(q[0] for q in c)/len(c); my = sum(q[1] for q in c)/len(c)
    r = math.hypot(mx-cx, my-cy)
    a = math.degrees(math.atan2(-(my-cy), mx-cx)) % 360
    tag = 'ring' if 185 <= r <= 275 else 'inner'
    (ring if tag=='ring' else inner).append((len(c), round(mx), round(my), round(r), round(a,1), tag))
ring.sort(key=lambda t: t[4])
print('ring components (r 185..275):')
for t in ring: print('   size %5d at (%3d,%3d) r=%3d ang=%5.1f' % t[:5])
print(f'ring star count (>=60px): {len(ring)}')
print()
print('inner components (r<185 or >275):')
for t in sorted(inner, key=lambda t:-t[0]): print('   size %5d at (%3d,%3d) r=%3d ang=%5.1f' % t[:5])
