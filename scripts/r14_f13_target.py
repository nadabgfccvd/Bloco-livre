#!/usr/bin/env python3
"""R14 pass 13: targeted bevel hunt on +delta diff pixels; shadow A/B y340-440; top-strip diff identity."""
import os, collections
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"
def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]

a = Image.open(os.path.join(R13,"01_hero.png")).convert("RGB")
b = Image.open(os.path.join(R14,"01_hero.png")).convert("RGB")

print("=== A. ADDED-bright pixels (delta +12..+45) in board area: geometry ===")
added=[]
for y in range(190,866):
    for x in range(24,696):
        pa=a.getpixel((x,y)); pb=b.getpixel((x,y))
        d=lum(pb)-lum(pa)
        if 12<=d<=45:
            added.append((x,y,d))
print(f"  count: {len(added)}")
if added:
    xs=[p[0] for p in added]; ys=[p[1] for p in added]
    print(f"  bbox x[{min(xs)}..{max(xs)}] y[{min(ys)}..{max(ys)}]")
    # y-x histogram: a single diagonal line -> one dominant y-x value
    ymx=collections.Counter(p[1]-p[0] for p in added)
    top=ymx.most_common(10)
    print(f"  y-x histogram top: {top}")
    # x+y histogram (anti-diagonal)
    xpy=collections.Counter(p[1]+p[0] for p in added)
    print(f"  x+y histogram top: {xpy.most_common(5)}")
    # row histogram
    rows=collections.Counter(p[1] for p in added)
    print(f"  row histogram top: {rows.most_common(8)}")
    # col histogram
    cols=collections.Counter(p[0] for p in added)
    print(f"  col histogram top: {cols.most_common(8)}")
    # sample the strongest deltas
    strong=sorted(added,key=lambda p:-p[2])[:15]
    print(f"  strongest: {strong}")

print("\n=== B. top strip diff identity (y0-190) ===")
ta=[]; tb=[]
for y in range(0,190):
    for x in range(0,720):
        if a.getpixel((x,y))!=b.getpixel((x,y)):
            ta.append((x,y))
xs=[p[0] for p in ta]; ys=[p[1] for p in ta]
if ta:
    print(f"  changed px: {len(ta)} bbox x[{min(xs)}..{max(xs)}] y[{min(ys)}..{max(ys)}]")
    rows=collections.Counter(p[1] for p in ta)
    print(f"  rows most: {rows.most_common(6)}")

print("\n=== C. SHADOW A/B full zone y336-460 x240-600 (07_clear) ===")
ca = Image.open(os.path.join(R13,"07_clear.png")).convert("RGB")
cb = Image.open(os.path.join(R14,"07_clear.png")).convert("RGB")
for thr in (50, 70, 90):
    na=nb=0; pa=[]; pb=[]
    for y in range(336,460):
        for x in range(240,600):
            if lum(ca.getpixel((x,y)))<thr: na+=1; pa.append((x,y))
            if lum(cb.getpixel((x,y)))<thr: nb+=1; pb.append((x,y))
    ca_ = (sum(p[0] for p in pa)/len(pa), sum(p[1] for p in pa)/len(pa)) if pa else None
    cb_ = (sum(p[0] for p in pb)/len(pb), sum(p[1] for p in pb)/len(pb)) if pb else None
    print(f"  thr<{thr}: R13 n={na} centroid=({ca_[0]:.0f},{ca_[1]:.0f}) | R14 n={nb} centroid=({cb_[0]:.0f},{cb_[1]:.0f})")

# diff between r13/r14 clear in star zone: where exactly did pixels change?
print("\n=== D. clear-shot star-zone diff map (y188-360) ===")
diffgrid=[]
for y in range(188,360,4):
    row=[]
    for x in range(240,600,4):
        d=0; n=0
        for dy in range(4):
            for dx in range(4):
                if ca.getpixel((x+dx,y+dy))!=cb.getpixel((x+dx,y+dy)): d+=1
                n+=1
        row.append('#' if d>6 else ('+' if d>2 else ('.' if d>0 else ' ')))
    diffgrid.append((y,"".join(row)))
for y,l in diffgrid: print(f"  {y:3d}|{l}")
