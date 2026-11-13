#!/usr/bin/env python3
"""Final verification pass:
1. Star on 07_clear: isolate star at board center region properly (x300-420, y620-760),
   excluding rays. Measure vs ring stars (already have: ring 0.45 cell).
2. Ray spoke lengths: alternating 6.9-cell long x 0.34 wide vs 3.8-cell x 0.18.
   Measure angular bin lengths and widths along circumference.
3. Halo radius: gold ring completeness (all 360 degrees at r=?).
4. Pips: 04_skin2 pips at y1310 — measure width exactly; check color on 06_full for red.
5. HUD: 06_full HUD text groups (PONTOS value vs RECORDE height).
"""
import os
from PIL import Image
import numpy as np
from scipy import ndimage

R7 = "/home/z/my-project/critic_shots/r7"
OUT = "/tmp/critic_crops_r7"
def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(int)
CELL = 85.0

# ---- 1. STAR at board center on 07_clear ----
a = load(os.path.join(R7,"07_clear.png"))
r,g,b = a[...,0],a[...,1],a[...,2]
lum = 0.299*r+0.587*g+0.114*b
# board center approx (360, 688). star region exclude rays: inner box x330-390 y660-720
reg = lum[640:740, 320:400]
print("star inner box (x320-400,y640-740) luminance stats:", reg.min(), reg.max(), reg.mean().round(1))
thr = 200
m = lum > thr
# isolate connected star: flood from (360, 690) approx center
cy0, cx0 = 690, 360
# find if bright at that point
print("lum at (360,690):", lum[690,360], "at (360,688):", lum[688,360])
lbl, n = ndimage.label(m)
# which component contains center
def comp_at(y,x):
    if 0<=y<a.shape[0] and 0<=x<a.shape[1]:
        return lbl[y,x]
    return 0
cid = comp_at(690,360)
print(f"component at board center: {cid}")
if cid:
    ys_,xs_ = np.where(lbl==cid)
    bw=xs_.max()-xs_.min()+1; bh=ys_.max()-ys_.min()+1
    print(f"STAR: bbox x{xs_.min()}..{xs_.max()} y{ys_.min()}..{ys_.max()} => {bw}x{bh}px = {bw/CELL:.2f}x{bh/CELL:.2f} cell (claim 0.72)")

# ---- 2. RAYS: bright spokes radiating from band/board center (360,447) ----
cy, cx = 447, 360
bright = lum > 160
# exclude banner rows 380..515 and star component area
mask = bright.copy()
mask[380:516,:] = False
ys,xs = np.where(mask)
rr = np.hypot(xs-cx, ys-cy)
ang = (np.degrees(np.arctan2(ys-cy, xs-cx)) + 360) % 360
# rays zone: r between 100 and 520
sel = (rr>100)&(rr<520)
ys2,xs2,rr2,ang2 = ys[sel],xs[sel],rr[sel],ang[sel]
# per 5-deg bin: max radius => spoke lengths
print("\nray length per 5-deg bin (rmax, n):")
bins = np.arange(0,360,5)
lens=[]
for i in range(72):
    s = (ang2>=bins[i])&(ang2<bins[i]+5)
    if s.sum()>2:
        rmax = rr2[s].max()
        lens.append((bins[i], rmax, int(s.sum())))
for (b_,rmax,nn) in lens:
    bar = '#'*int(rmax/20)
    print(f"  {b_:3d}: rmax={rmax:5.0f} ({rmax/CELL:4.1f} cell) n={nn:4d} {bar}")
# alternating pattern check: sort by rmax, see bimodal
if lens:
    rmaxs = np.array([l[1] for l in lens])
    big = rmaxs[rmaxs> rmaxs.mean()]
    small = rmaxs[rmaxs<=rmaxs.mean()]
    print(f"bimodal: big spokes mean {big.mean():.0f}px = {big.mean()/CELL:.1f} cell; small {small.mean():.0f}px = {small.mean()/CELL:.1f} cell (claim 6.9 / 3.8 cell)")
# spoke width: at radius 300, angular width of bright runs
print("\nspoke widths at r 280-320 (angular run length):")
selw = (rr2>280)&(rr2<320)
if selw.sum():
    a2 = np.sort(ang2[selw])
    runs=[]; s=a2[0]; p=a2[0]
    for v in a2[1:]:
        if v-p>3: runs.append(p-s); s=v
        p=v
    runs.append(p-s)
    runs = np.array(runs)
    print(f"  angular runs deg: {[round(float(x),1) for x in runs if x>1]}")
    print(f"  approx widths at r=300: deg->px: {[round(float(x)*np.pi/180*300,1) for x in runs if x>1]}")

# ---- 3. HALO completeness: gold ring radius around center ----
gold = (r>170)&(g>110)&(b<120)&((np.abs(r-g*1.35))<60)
yy,xx = np.mgrid[0:a.shape[0],0:a.shape[1]]
rad = np.hypot(xx-cx, yy-cy)
print("\nhalo: gold coverage per 20deg angle at radius bands 380-470:")
for rA, rB in [(380,400),(400,420),(420,440),(440,460),(460,480)]:
    angcov = []
    for i in range(36):
        s = (rad>=rA)&(rad<rB)&(ang_bin:=((np.degrees(np.arctan2(yy-cy, xx-cx))+360)%360)>=i*10)&(((np.degrees(np.arctan2(yy-cy, xx-cx))+360)%360)<i*10+10)&gold
        angcov.append(1 if s.sum()>3 else 0)
    print(f"  r{rA}-{rB}: coverage in {sum(angcov)}/36 bins")

# ---- 4. PIPS on 04_skin2 (y1310 row): exact widths; 06_full same row color ----
for fn in ["04_skin2.png","06_full.png","01_hero.png","02_skin0.png","03_skin1.png","05_skin3.png"]:
    aa = load(os.path.join(R7,fn))
    seg = aa[1305:1320, 20:700]
    s_m = (seg.max(axis=2)-seg.min(axis=2)>40)&(seg.max(axis=2)>80)
    rows_ = s_m.sum(axis=1)
    print(f"\n{fn} y1305-1320 colored-row sums: {rows_.tolist()}")
    best = np.argmax(rows_)
    if rows_[best] > 10:
        br = s_m[best]
        cols_ = np.where(br)[0]
        gs=[]; s=cols_[0]; p=cols_[0]
        for x in cols_[1:]:
            if x-p>2: gs.append((s,p)); s=x
            p=x
        gs.append((s,p))
        print(f"  row y={1305+best}: groups {[(int(gs_),int(ge),ge-gs_+1) for gs_,ge in gs]}")
        # color each
        for gs_,ge in gs:
            px = seg[best, gs_:ge+1]
            print(f"    x{gs_+20}-{ge+20}: rgb={px.mean(axis=0).round(0)}")

# ---- 5. HUD 06_full: text heights ----
af = load(os.path.join(R7,"06_full.png"))
lumf = 0.299*af[...,0]+0.587*af[...,1]+0.114*af[...,2]
whitef = lumf>150
seg = whitef[0:123,:]
rows_ = np.where(seg.sum(axis=1)>6)[0]
groups=[]
if len(rows_):
    s=rows_[0]; p=rows_[0]
    for y in rows_[1:]:
        if y-p>3: groups.append((s,p)); s=y
        p=y
    groups.append((s,p))
print("\n06_full HUD text groups (y0-123):")
for gs,ge in groups:
    h=ge-gs+1
    s2 = whitef[gs:ge+1,:]
    cols_ = np.where(s2.sum(axis=0)>0)[0]
    left = cols_[cols_<360]; right = cols_[cols_>=360]
    print(f"  y{gs}..{ge} h={h}px ({h/CELL:.2f} cell) left x{left.min() if len(left) else '-'}..{left.max() if len(left) else '-'} right x{right.min() if len(right) else '-'}..{right.max() if len(right) else '-'}")

# crop pip rows
Image.open(os.path.join(R7,"04_skin2.png")).crop((0,1280,720,1360)).save(os.path.join(OUT,"skin2_piprow.png"))
Image.open(os.path.join(R7,"06_full.png")).crop((0,1280,720,1360)).save(os.path.join(OUT,"full_piprow.png"))
Image.open(os.path.join(R7,"07_clear.png")).crop((250,560,470,820)).save(os.path.join(OUT,"clear_star_big.png"))
print("\nsaved skin2_piprow.png, full_piprow.png, clear_star_big.png")
