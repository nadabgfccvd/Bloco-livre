#!/usr/bin/env python3
"""Find the occupancy bar precisely: scan ALL rows of hero for rows whose colored
pixels form >=8 narrow groups of similar width (pips). Also classify bar color
on 06_full vs 01_hero, and check 06_full board fill (81% claim)."""
import os
from PIL import Image
import numpy as np

R7 = "/home/z/my-project/critic_shots/r7"
OUT = "/tmp/critic_crops_r7"
def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(int)

def pip_scan(a, y0, y1, label, min_groups=6, max_gap=3):
    best = None
    sat = a.max(axis=2)-a.min(axis=2)
    colored = (sat>60)&(a.max(axis=2)>90)
    for y in range(y0, y1):
        cols_ = np.where(colored[y])[0]
        if len(cols_) < 30: continue
        gs=[]; s=cols_[0]; p=cols_[0]
        for x in cols_[1:]:
            if x-p>max_gap: gs.append((s,p)); s=x
            p=x
        gs.append((s,p))
        widths = np.array([ge-gs_+1 for gs_,ge in gs])
        if len(gs) >= min_groups:
            # regular spacing?
            centers = np.array([(gs_+ge)/2 for gs_,ge in gs])
            if len(centers)>2:
                spacings = np.diff(centers)
                reg = spacings.std()/max(spacings.mean(),1) < 0.25
                if reg:
                    score = len(gs)
                    if best is None or score > best[0]:
                        best = (score, y, gs, widths)
    if best:
        score, y, gs, widths = best
        print(f"  {label}: pip-row at y={y}: {len(gs)} pips, widths={list(widths)}")
        centers = [int((gs_+ge)/2) for gs_,ge in gs]
        print(f"    centers={centers}")
        # vertical extent & color of each pip
        satm = (a.max(axis=2)-a.min(axis=2))
        colm = (satm>60)&(a.max(axis=2)>90)
        for (gs_,ge) in gs[:14]:
            strip = colm[:, gs_:ge+1].sum(axis=1)
            nz = np.where(strip > (ge-gs_)*0.5)[0]
            if len(nz):
                yy0,yy1 = nz.min(), nz.max()
                seg = a[yy0:yy1+1, gs_:ge+1].reshape(-1,3)
                seg = seg[seg.max(axis=1)>90]
                print(f"    pip x{gs_}-{ge}: y{yy0}..{yy1} h={yy1-yy0+1}px color={seg.mean(axis=0).round(0) if len(seg) else '-'}")
        return y
    print(f"  {label}: NO pip-row found")
    return None

for fn, tag in [("01_hero.png","HERO"), ("06_full.png","FULL"), ("07_clear.png","CLEAR")]:
    a = load(os.path.join(R7, fn))
    print(f"--- {tag} ---")
    pip_scan(a, 0, 140, "top strip")
    pip_scan(a, 130, 400, "upper mid")
    pip_scan(a, 505, 620, "below banner")
    pip_scan(a, 1230, 1440, "bottom strip")

# 06_full: board occupancy (danger 81%)
a = load(os.path.join(R7,"06_full.png"))
CELL=85.0; X0=24; Y0=123
occ=0; tot=0
for iy in range(13):
    for ix in range(8):
        ya=int(Y0+iy*CELL+CELL*0.3); yb=int(Y0+iy*CELL+CELL*0.7)
        xa=int(X0+ix*CELL+CELL*0.3); xb=int(X0+ix*CELL+CELL*0.7)
        cell = a[ya:yb, xa:xb]
        cm = cell.max(axis=2).astype(int).mean()
        cs = (cell.max(axis=2)-cell.min(axis=2)).astype(int).mean()
        tot+=1
        if cm>75 or cs>50: occ+=1
print(f"\n06_full board occupancy: {occ}/{tot} = {occ/tot*100:.1f}% (claim 81% danger)")

# check banner on 06_full: gold + text?
r,g,b = a[...,0],a[...,1],a[...,2]
gold = (r>170)&(g>110)&(g<210)&(b<110)
rowgold = gold[:, 60:660].sum(axis=1)
band = [y for y in range(300,620) if rowgold[y]>150]
print(f"06_full gold band rows: {band[:5]}...{band[-5:] if band else 'NONE'} count={len(band)}")
white = (r>225)&(g>225)&(b>225)
seg = white[405:495, 60:660].sum(axis=1)
nz = [y for y in range(405,495) if seg[y-405]>12]
print(f"06_full white text rows in band: {nz[:3]}...{nz[-3:] if nz else 'NONE'} count={len(nz)}")

# danger color: any red pulsing element? scan for red-dominant pixels in 06_full
red = (r>150)&(r-g>60)&(r-b>60)
print(f"06_full red px total: {red.sum()} ; rows>100px: {[int(y) for y in np.where(red.sum(axis=1)>100)[0][:12]]}")

# crop 06_full banner + board
Image.open(os.path.join(R7,"06_full.png")).crop((60,340,660,560)).save(os.path.join(OUT,"full_banner.png"))
Image.open(os.path.join(R7,"06_full.png")).crop((24,123,696,1254)).save(os.path.join(OUT,"full_board.png"))
print("saved full_board.png")
