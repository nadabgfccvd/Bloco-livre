#!/usr/bin/env python3
"""Deeper banner / crown geometry on 07_clear.png:
- The banner band occupies y 100..179 (mean cx 360.8) — that is ABOVE the board (board top=190). 
  Claim says banner band #F6C445 rows? and underlay rows 466..698 centered 582?? That seems wrong
  versus what we measure: gold mass rows 466..698 has cx 327.6.
- White hairline rows 532..560: these are INSIDE the board — maybe star sparkle, not hairline.
- Crown cluster bbox y 392..472, spread rx 256 ry 40: that's an arc of stars near TOP of board center,
  not a full ellipse rx252/ry219. Verify star count by connected-component analysis.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png'); p = px(im); w,h = im.size

def gold_at(x, y):
    c = p[x,y]
    return c[0] > 180 and c[1] > 130 and c[2] < 150 and c[0] > c[2]+40

# connected components (4-neigh) over board zone for gold
seen = set(); comps = []
for y in range(190, 866):
    for x in range(20, 696):
        if (x,y) in seen or not gold_at(x,y): continue
        stack=[(x,y)]; seen.add((x,y)); comp=[]
        while stack:
            cx,cy = stack.pop(); comp.append((cx,cy))
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                nx,ny = cx+dx, cy+dy
                if 20<=nx<696 and 190<=ny<866 and (nx,ny) not in seen and gold_at(nx,ny):
                    seen.add((nx,ny)); stack.append((nx,ny))
        comps.append(comp)

sizes = sorted([len(c) for c in comps], reverse=True)
print(f'gold components in board: {len(comps)}, sizes: {sizes[:25]}')
big = [c for c in comps if len(c) > 40]
print('components >40px:', len(big))
for c in sorted(big, key=len, reverse=True)[:20]:
    xs=[q[0] for q in c]; ys=[q[1] for q in c]
    print(f'  size {len(c):4d} bbox x {min(xs):3d}..{max(xs):3d} y {min(ys):3d}..{max(ys):3d} center ({(min(xs)+max(xs))//2},{(min(ys)+max(ys))//2})')
