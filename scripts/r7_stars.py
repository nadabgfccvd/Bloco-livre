#!/usr/bin/env python3
"""Estrela-mor star size, ring stars, halo circle radius, occupancy bar pips, HUD text heights.
Also skin diffs 02-05 vs R6."""
import os
from PIL import Image
import numpy as np

R7 = "/home/z/my-project/critic_shots/r7"
R6 = "/home/z/my-project/critic_shots/r6"
OUT = "/tmp/critic_crops_r7"
CELL = 85.0   # measured grid pitch on hero

def load(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(int)

# ---------------- STAR + HALO on 07_clear ----------------
cl = load(os.path.join(R7,"07_clear.png"))
H,W = cl.shape[:2]
r,g,b = cl[...,0], cl[...,1], cl[...,2]
lum = 0.299*r+0.587*g+0.114*b

# Board center: x=360, y ~ (123+1254)/2 = 688. Band center y=447.
# Star sits center of board below banner. Find bright cluster near (360, 688)
def bright_cluster(a, y0,y1,x0,x1, thr=200):
    rr,gg,bb = a[...,0],a[...,1],a[...,2]
    luml = 0.299*rr+0.587*gg+0.114*bb
    m = luml > thr
    seg = m[y0:y1, x0:x1]
    ys,xs = np.where(seg)
    return ys,xs,segl if False else (ys+y0 if len(ys) else [], xs+x0 if len(xs) else [])

# star region: center 360,688; search 260..460 x 588..788
ys, xs, _ = bright_cluster(cl, 588, 800, 250, 470, thr=190)
if len(xs):
    print(f"star candidate: n={len(xs)} bbox x{xs.min()}..{xs.max()} y{ys.min()}..{ys.max()}")
    wpx = xs.max()-xs.min()+1; hpx = ys.max()-ys.min()+1
    print(f"  size {wpx}x{hpx}px = {wpx/CELL:.2f} x {hpx/CELL:.2f} cell (claim estrela-mor 0.72 cell)")
else:
    print("no star cluster at board center (thr=190)")

# ring stars: bright clusters elsewhere in glory zone but outside banner
mask = lum > 170
mask[380:515,:] = False
# remove the big board area? board is y588..1254 dark w/ pieces. restrict glory annulus y100..580
glory = mask.copy()
glory[580:,:] = False
glory[:, :40] = False; glory[:, 680:] = False
ys,xs = np.where(glory)
print(f"\nglory bright px (y100-580, x40-680): {len(xs)} bbox x{xs.min()}..{xs.max()} y{ys.min()}..{ys.max()}")

# cluster via simple connected labeling
from scipy import ndimage
lbl, n = ndimage.label(glory)
print(f"connected components: {n}")
sizes = ndimage.sum(glory, lbl, range(1,n+1))
order = np.argsort(sizes)[::-1]
COMS = ndimage.center_of_mass(glory, lbl, range(1,n+1))
print("top 12 clusters by size:")
stars = []
for i in order[:12]:
    cid = i+1
    if sizes[i] < 8: continue
    comy, comx = COMS[i]
    ys_, xs_ = np.where(lbl==cid)
    bw = xs_.max()-xs_.min()+1; bh = ys_.max()-ys_.min()+1
    r_c = np.hypot(comx-360, comy-447)
    stars.append((sizes[i], comx, comy, bw, bh, r_c))
    print(f"  size={int(sizes[i]):4d} com=({comx:.0f},{comy:.0f}) bbox {bw}x{bh}px r={r_c:.0f}")
if stars:
    big = max(stars, key=lambda s:s[0])
    wstars = [s for s in stars if s[0] < big[0]*0.5]
    if wstars:
        avgw = np.mean([s[3] for s in wstars]); avgh = np.mean([s[4] for s in wstars])
        print(f"ring stars avg bbox: {avgw:.0f}x{avgh:.0f}px = {avgw/CELL:.2f} cell (claim <=0.48)")
    print(f"major star bbox {big[3]}x{big[4]}px = {big[3]/CELL:.2f} cell (claim 0.72)")

# halo: circle of gold px around band? compute radial profile of goldish
goldish = (r>170)&(g>110)&(b<120)
cy, cx = 447, 360
yy, xx = np.mgrid[0:H, 0:W]
rad = np.hypot(xx-cx, yy-cy)
for r0 in range(60, 600, 20):
    sel = (rad>=r0)&(rad<r0+20)&goldish
    if sel.sum() > 0:
        print(f"halo radial bin r{r0}-{r0+20}: gold px={sel.sum():5d} frac={sel.mean()*100:.1f}%")

# ---------------- Occupancy bar (06_full + 01_hero) ----------------
for fn, tag in [("06_full.png","FULL"),("01_hero.png","HERO"),("02_skin0.png","SKIN0")]:
    a = load(os.path.join(R7, fn))
    rr,gg,bb = a[...,0],a[...,1],a[...,2]
    # bar: find horizontal strip of colored segments below board? search y1260..1420
    zone = slice(1255, 1440)
    zr = a[zone, :, :]
    zlum = 0.299*zr[...,0]+0.587*zr[...,1]+0.114*zr[...,2]
    colored = (zr.max(axis=2)-zr.min(axis=2) > 50) & (zr.max(axis=2)>80)
    rowc = colored.sum(axis=1)
    print(f"\n--- {tag} occupancy-bar zone y1255-1440 ---")
    best = np.argmax(rowc)
    print(f"max colored row: y={1255+best} count={rowc[best]}")
    # color of best row: green or red?
    br = colored[best]
    seg = zr[best][br]
    if len(seg):
        print(f"row colors mean RGB={seg.mean(axis=0).round(0)}  (green if G dominant, red if R dominant)")
    # pips: contiguous colored column groups on that row
    cols_ = np.where(br)[0]
    groups=[]
    if len(cols_):
        s=cols_[0]; p=cols_[0]
        for x in cols_[1:]:
            if x-p>2: groups.append((s,p)); s=x
            p=x
        groups.append((s,p))
    print(f"pip column groups: {len(groups)}")
    for (gs,ge) in groups[:20]:
        print(f"   x{gs}..{ge} width={ge-gs+1}px")
    # vertical thickness of each pip
    for (gs,ge) in groups[:12]:
        colstrip = colored[:, gs:ge+1].sum(axis=1)
        nz = np.where(colstrip>0)[0]
        if len(nz): print(f"   pip x{gs}-{ge}: y{1255+nz.min()}..{1255+nz.max()} h={nz.max()-nz.min()+1}px")

# ---------------- HUD text heights: PONTOS vs RECORDE (hero) ----------------
a = load(os.path.join(R7,"01_hero.png"))
white = (a[...,0]>200)&(a[...,1]>200)&(a[...,2]>200)
print("\n--- HERO HUD white text groups (y0..130) ---")
seg = white[0:130, :]
rows_ = np.where(seg.sum(axis=1) > 8)[0]
groups=[]
if len(rows_):
    s=rows_[0]; p=rows_[0]
    for y in rows_[1:]:
        if y-p>3: groups.append((s,p)); s=y
        p=y
    groups.append((s,p))
for gs,ge in groups:
    h = ge-gs+1
    s2 = white[gs:ge+1,:]
    cols_ = np.where(s2.sum(axis=0)>0)[0]
    xex = f"{cols_.min()}..{cols_.max()}" if len(cols_) else "-"
    print(f"  y{gs}..{ge} h={h}px ({h/CELL:.2f} cell) x {xex}")

# crop HUD full width for record
Image.open(os.path.join(R7,"01_hero.png")).crop((0,0,720,130)).save(os.path.join(OUT,"hero_hud_full.png"))
Image.open(os.path.join(R7,"07_clear.png")).crop((100,100,620,700)).save(os.path.join(OUT,"clear_glory2.png"))

# ---------------- SKIN DIFFS vs R6 ----------------
print("\n--- skin diffs vs R6 ---")
pairs = [("02_skin0.png","02_skin0.png"),("03_skin1.png","03_skin1.png"),("04_skin2.png","04_skin2.png"),("05_skin3.png","05_skin3.png"),("06_full.png","06_full.png")]
for r7n, r6n in pairs:
    A = load(os.path.join(R7,r7n)); B = load(os.path.join(R6,r6n))
    if A.shape != B.shape: print(r7n, "shape mismatch"); continue
    d = np.abs(A-B).max(axis=2)
    print(f"{r7n}: changed>30 = {(d>30).mean()*100:.1f}%")

# halo crop R6 for comparison
Image.open(os.path.join(R6,"07_clear.png")).crop((100,100,620,700)).save(os.path.join(OUT,"r6_glory_zone.png"))
print("\ndone")
