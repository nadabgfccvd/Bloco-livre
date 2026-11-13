#!/usr/bin/env python3
"""Refine: where is the occupancy bar? profile y1230-1440 zone.
Star center: search only the ring-annulus. HUD: labels vs values heights."""
import os
from PIL import Image
import numpy as np

R7 = "/home/z/my-project/critic_shots/r7"
OUT = "/tmp/critic_crops_r7"
def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(int)

a = load(os.path.join(R7,"01_hero.png"))
H,W = a.shape[:2]

# --- bottom zone content map: what's at y1255..1440? ---
z = a[1255:1440]
zl = 0.299*z[...,0]+0.587*z[...,1]+0.114*z[...,2]
print("bottom zone rows: y, mean-lum, colored-frac, dominant colors")
sat = (z.max(axis=2)-z.min(axis=2))
colored = (sat>60)&(z.max(axis=2)>90)
for yy in range(0, 185, 6):
    row = z[yy]
    rl = (0.299*row[:,0]+0.587*row[:,1]+0.114*row[:,2]).mean()
    cf = colored[yy].mean()
    # dominant bright color on row
    sel = np.where(colored[yy])[0]
    dom = row[sel].mean(axis=0).round(0) if len(sel)>4 else None
    print(f"  y{1255+yy}: lum={rl:6.1f} colored={cf*100:4.1f}% dom={dom}")

# the 4 groups x22..695 at y1289..1340 are probably 4 big buttons (152-157px wide)
# check their inner colors individually
for (x0,x1) in [(22,178),(195,350),(367,522),(539,695)]:
    seg = a[1289:1341, x0:x1]
    # cluster colors: hue histogram
    rr,gg,bb = seg[...,0].ravel(), seg[...,1].ravel(), seg[...,2].ravel()
    mx = np.maximum(np.maximum(rr,gg),bb); mn = np.minimum(np.minimum(rr,gg),bb)
    bright = (mx>100)&(mx-mn>50)
    if bright.sum()>20:
        brr, bgg, bbb = rr[bright], gg[bright], bb[bright]
        print(f"button x{x0}-{x1}: bright-px={bright.sum()} meanRGB=({brr.mean():.0f},{bgg.mean():.0f},{bbb.mean():.0f})")

# --- find the occupancy bar: look for a HORIZONTAL row of small regularly spaced
# colored dashes anywhere y100..1260 (side or above board) ---
print("\nsearching for pip-row (regular small colored dashes):")
for y0,y1,lbl in [(130,360,"upper area"),(500,600,"banner flanks"),(840,1250,"board sides")]:
    z2 = a[y0:y1]
    sat2 = (z2.max(axis=2)-z2.min(axis=2))
    col2 = (sat2>70)&(z2.max(axis=2)>100)
    rowsc = col2.sum(axis=1)
    for i in np.argsort(rowsc)[::-1][:5]:
        if rowsc[i] < 30: continue
        y = y0+i
        cols_ = np.where(col2[i])[0]
        # count groups
        if len(cols_):
            gs=[]; s=cols_[0]; p=cols_[0]
            for x in cols_[1:]:
                if x-p>3: gs.append((s,p)); s=x
                p=x
            gs.append((s,p))
            widths = [ge-gs_+1 for gs_,ge in gs]
            print(f"  {lbl} y={y}: colored px={int(rowsc[i])}, groups={len(gs)}, widths={widths[:14]}")

# --- HUD label heights: PONTOS/RECORDE labels vs digit values ---
# white groups y0..130 gave one group y30..52 h=23. That seems small.
# check gold/colored text (score digits may be colored not white)
print("\nHUD zone y0..130 full color scan:")
z3 = a[0:130]
lum3 = 0.299*z3[...,0]+0.587*z3[...,1]+0.114*z3[...,2]
bright3 = lum3>90
rows3 = bright3.sum(axis=1)
groups=[]
nz = np.where(rows3>5)[0]
if len(nz):
    s=nz[0]; p=nz[0]
    for y in nz[1:]:
        if y-p>4: groups.append((s,p)); s=y
        p=y
    groups.append((s,p))
for gs,ge in groups:
    h=ge-gs+1
    s4 = bright3[gs:ge+1]
    cols_ = np.where(s4.sum(axis=0)>0)[0]
    # split left/right halves
    left = cols_[cols_<360]; right = cols_[cols_>=360]
    def span(c):
        return f"{c.min()}..{c.max()}" if len(c) else "-"
    print(f"  y{gs}..{ge} h={h}px left x {span(left)} right x {span(right)}")
    # color of left vs right text
    for lbl, cc in [("left",left),("right",right)]:
        if len(cc):
            px = z3[gs:ge+1, cc.max():cc.max()+1]
            seg = z3[gs:ge+1, cc.min():cc.max()+1]
            br = seg.reshape(-1,3)[seg.reshape(-1,3).max(axis=1)>100]
            if len(br): print(f"     {lbl} mean bright RGB={br.mean(axis=0).round(0)}")

# crop
Image.open(os.path.join(R7,"01_hero.png")).crop((0,1255,720,1440)).save(os.path.join(OUT,"hero_bottom_zone.png"))
Image.open(os.path.join(R7,"01_hero.png")).crop((0,0,720,130)).resize((1440,260)).save(os.path.join(OUT,"hero_hud_zoom.png"))
print("saved hero_bottom_zone.png, hero_hud_zoom.png")
