#!/usr/bin/env python3
"""Locate occupancy bar by finding small rounded rects / dots under or over the board.
Approach: connected-component analysis of colored non-piece pixels OUTSIDE board area
(y<123, y>1254) across all 7 shots; classify each component shape + color."""
import os
from PIL import Image
import numpy as np
from scipy import ndimage

R7 = "/home/z/my-project/critic_shots/r7"
OUT = "/tmp/critic_crops_r7"
def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(int)

names = ["01_hero.png","02_skin0.png","03_skin1.png","04_skin2.png","05_skin3.png","06_full.png","07_clear.png"]

for fn in names:
    a = load(os.path.join(R7,fn))
    H,W = a.shape[:2]
    sat = a.max(axis=2)-a.min(axis=2)
    colored = (sat>60)&(a.max(axis=2)>90)
    # exclude board 123..1254 and banner 380..515
    m = colored.copy()
    m[123:1255, :] = False
    m[380:516, :] = False
    # also exclude top HUD y0..130? keep it, we want everything
    lbl, n = ndimage.label(m)
    sizes = ndimage.sum(m, lbl, range(1,n+1))
    comps = []
    for i in range(n):
        if sizes[i] < 12: continue
        ys_, xs_ = np.where(lbl==i+1)
        bw = xs_.max()-xs_.min()+1; bh = ys_.max()-ys_.min()+1
        if bw>500 or bh>300: continue  # huge = background artifact
        seg = a[ys_.min():ys_.max()+1, xs_.min():xs_.max()+1].reshape(-1,3)
        seg = seg[seg.max(axis=1)>90]
        mean_rgb = seg.mean(axis=0).round(0) if len(seg) else None
        comps.append((int(sizes[i]), xs_.min(), ys_.min(), bw, bh, tuple(mean_rgb) if mean_rgb is not None else None))
    comps.sort(key=lambda c: -c[0])
    print(f"\n--- {fn}: {len(comps)} components (size>=12) ---")
    for c in comps[:18]:
        sz,x,y,bw,bh,rgb = c
        kind = "dot/pip" if (6<=bw<=14 and 6<=bh<=14) else ("bar-seg" if bh<=10 or bw<=10 else "blob")
        print(f"  sz={sz:5d} at ({x:3d},{y:4d}) {bw:3d}x{bh:3d} rgb={rgb} {kind}")

# 06_full: does anything turn red at 81%? Look at ring color change r6->r7 06_full was 0% diff
# maybe bar is grayscale? look for gray pips: bright gray dots outside board
a = load(os.path.join(R7,"06_full.png"))
lum = 0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]
m = (lum>120) & (lum<200)
m[123:1255,:]=False; m[380:516,:]=False
lbl,n = ndimage.label(m)
sizes = ndimage.sum(m,lbl,range(1,n+1))
found=0
for i in range(n):
    if sizes[i]<12: continue
    ys_,xs_ = np.where(lbl==i+1)
    bw=xs_.max()-xs_.min()+1; bh=ys_.max()-ys_.min()+1
    if bw>500 or bh>300: continue
    seg = a[ys_.min():ys_.max()+1, xs_.min():xs_.max()+1].reshape(-1,3)
    print(f"06_full gray comp: sz={int(sizes[i])} at ({xs_.min()},{ys_.min()}) {bw}x{bh} rgb={seg.mean(axis=0).round(0)}")
    found+=1
    if found>15: break

# 06_full vs 02_skin0 diff (same skin, different fill) to isolate dynamic UI
A = load(os.path.join(R7,"06_full.png")); B = load(os.path.join(R7,"02_skin0.png"))
d = np.abs(A-B).max(axis=2)
print("\n06_full vs 02_skin0: changed>30 =", f"{(d>30).mean()*100:.1f}%")
# per-zone
for (yA,yB,lbl) in [(0,123,"above board"),(123,1255,"board"),(1255,1440,"below board")]:
    print(f"  {lbl}: {(d[yA:yB]>30).mean()*100:.1f}%")
# where exactly above board?
ch = d[0:123,:]>30
rows_ = np.where(ch.sum(axis=1)>3)[0]
print("changed rows above board:", rows_[:20], "count", len(rows_))
