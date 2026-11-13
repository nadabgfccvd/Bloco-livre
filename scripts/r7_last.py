#!/usr/bin/env python3
"""Final checks:
A) R6 01_main_classic vs R7 01_hero diff (new content or rename?)
B) green px hunt on hero + full (occupancy bar green claim)
C) banner x-extent vs text x-extent (overflow?)
D) y60-80 strip: pips or text? (per-shot compare)
E) ring-star sizes R6 vs R7 clear shots
F) halo completeness around board center (360,688) and (360,447)
G) spoke count: alternating pattern summary
"""
import os
from PIL import Image
import numpy as np
from scipy import ndimage

R7 = "/home/z/my-project/critic_shots/r7"
R6 = "/home/z/my-project/critic_shots/r6"
OUT = "/tmp/critic_crops_r7"
def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(int)
CELL=85.0

# A) hero vs r6 main
A = load(os.path.join(R7,"01_hero.png")); B = load(os.path.join(R6,"01_main_classic.png"))
d = np.abs(A-B).max(axis=2)
print("A) R7 01_hero vs R6 01_main_classic: changed>30 =", f"{(d>30).mean()*100:.1f}%")
for (yA,yB,lbl) in [(0,123,"HUD"),(123,380,"above board/banner off"),(380,516,"banner zone"),(516,1255,"board"),(1255,1440,"bottom UI")]:
    print(f"   {lbl}: {(d[yA:yB]>30).mean()*100:.1f}%")
# board content diff specifically
print("   board rows changed>30 by row-block:",
      [f"y{y}-{y+100}: {(d[y:y+100]>30).mean()*100:.0f}%" for y in range(123,1255,100)])

# B) green hunt on hero and full
for fn in ["01_hero.png","06_full.png","02_skin0.png"]:
    a = load(os.path.join(R7,fn))
    r,g,b = a[...,0],a[...,1],a[...,2]
    green = (g>100)&(g-r>40)&(g-b>40)
    print(f"\nB) {fn}: green px = {green.sum()}")
    if green.sum()>50:
        ys,xs = np.where(green)
        print(f"   bbox x{xs.min()}..{xs.max()} y{ys.min()}..{ys.max()}")
        lbl,n = ndimage.label(green)
        sizes = ndimage.sum(green,lbl,range(1,n+1))
        for i in np.argsort(sizes)[::-1][:6]:
            if sizes[i]<20: break
            ys_,xs_ = np.where(lbl==i+1)
            print(f"   green comp sz={int(sizes[i])} at ({xs_.min()},{ys_.min()}) {xs_.max()-xs_.min()+1}x{ys_.max()-ys_.min()+1}")

# C) banner overflow: band x-extent vs white text x-extent (07_clear)
a = load(os.path.join(R7,"07_clear.png"))
r,g,b = a[...,0],a[...,1],a[...,2]
gold = (r>170)&(g>110)&(g<210)&(b<110)
band = gold[396:499,:]
cols_ = np.where(band.sum(axis=0)>20)[0]
print(f"\nC) band x-extent: {cols_.min()}..{cols_.max()} (width {cols_.max()-cols_.min()+1})")
white = (r>225)&(g>225)&(b>225)
seg = white[414:470,:]
cols2 = np.where(seg.sum(axis=0)>0)[0]
print(f"   text x-extent: {cols2.min()}..{cols2.max()} (width {cols2.max()-cols2.min()+1})")
print(f"   text inside band horizontally: {cols2.min()>=cols_.min() and cols2.max()<=cols_.max()}")

# D) y60-80 strip: pips or text? compare hero vs full
for fn in ["01_hero.png","06_full.png","02_skin0.png","07_clear.png"]:
    a = load(os.path.join(R7,fn))
    strip = a[60:82, 140:580]
    lum = 0.299*strip[...,0]+0.587*strip[...,1]+0.114*strip[...,2]
    m = lum>100
    # column groups = glyphs/pips
    colsum = m.sum(axis=0)
    cols_ = np.where(colsum>0)[0]
    gs=[]
    if len(cols_):
        s=cols_[0]; p=cols_[0]
        for x in cols_[1:]:
            if x-p>1: gs.append((s,p)); s=x
            p=x
        gs.append((s,p))
    widths = [ge-gs_+1 for gs_,ge in gs]
    print(f"\nD) {fn} y60-82 strip: {len(gs)} glyph/pip groups, widths={widths[:24]}")

# E) ring stars R6 vs R7 clear
for tag, p in [("R7", os.path.join(R7,"07_clear.png")), ("R6", os.path.join(R6,"07_clear.png"))]:
    a = load(p)
    lum = 0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]
    m = lum>170
    m[380:516,:]=False; m[580:,:]=False; m[:,:40]=False; m[:,680:]=False
    lbl,n = ndimage.label(m)
    sizes = ndimage.sum(m,lbl,range(1,n+1))
    stars=[]
    for i in range(n):
        if sizes[i]<8: continue
        ys_,xs_ = np.where(lbl==i+1)
        bw=xs_.max()-xs_.min()+1; bh=ys_.max()-ys_.min()+1
        if bw>300 or bh>250: continue
        stars.append((int(sizes[i]), bw, bh, xs_.min(), ys_.min()))
    stars.sort(key=lambda s:-s[0])
    print(f"\nE) {tag} bright clusters (top 8):")
    for s in stars[:8]:
        print(f"   sz={s[0]:5d} {s[1]}x{s[2]}px ({s[1]/CELL:.2f} cell) at ({s[3]},{s[4]})")
    print(f"   total clusters>=8px: {len(stars)}")

# F) halo completeness around (360,688) board center, radius bands up to 7.6*85=646
a = load(os.path.join(R7,"07_clear.png"))
r,g,b = a[...,0],a[...,1],a[...,2]
gold = (r>170)&(g>110)&(b<110)
yy,xx = np.mgrid[0:a.shape[0],0:a.shape[1]]
for cy,cx,lbl in [(688,360,"board ctr"),(447,360,"band ctr")]:
    rad = np.hypot(xx-cx, yy-cy)
    ang = (np.degrees(np.arctan2(yy-cy,xx-cx))+360)%360
    print(f"\nF) gold coverage around {lbl} ({cx},{cy}):")
    for rA in range(100, 660, 60):
        cov = []
        for i in range(36):
            s = (rad>=rA)&(rad<rA+60)&(ang>=i*10)&(ang<i*10+10)&gold
            cov.append(s.sum())
        nz = sum(1 for c in cov if c>5)
        print(f"   r{rA}-{rA+60}: bins with gold: {nz}/36, max px/bin={max(cov)}")

# G) spoke alternation summary (already have per-bin data; summarize quadrant means)
lum = 0.299*r+0.587*g+0.114*b
bright = lum>160
bright[380:516,:]=False
ys,xs = np.where(bright)
cy,cx = 447,360
rr = np.hypot(xs-cx,ys-cy); ang=(np.degrees(np.arctan2(ys-cy,xs-cx))+360)%360
sel=(rr>100)&(rr<540)
rr,ang = rr[sel],ang[sel]
# per 15-deg bin rmax
prof=[]
for i in range(24):
    s=(ang>=i*15)&(ang<i*15+15)
    if s.sum()>3: prof.append(rr[s].max())
print("\nG) spoke rmax per 15deg:", [int(p) for p in prof])
diffs = np.diff(prof)
alt = sum(1 for k in range(len(prof)-2) if (prof[k]-prof[k+1])*(prof[k+1]-prof[k+2])<0)
print(f"   direction changes (alternation score): {alt} of {len(prof)-2}")
