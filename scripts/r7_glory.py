#!/usr/bin/env python3
"""Deep dive: hero board exact grid + occupancy, star/ray geometry (clear shot),
glory rays + halo measurement, occupancy bar pips, R6-vs-R7 diff of clear shots."""
import os
from PIL import Image
import numpy as np

R7 = "/home/z/my-project/critic_shots/r7"
R6 = "/home/z/my-project/critic_shots/r6"
OUT = "/tmp/critic_crops_r7"
os.makedirs(OUT, exist_ok=True)

# ---------------- HERO GRID REFINED ----------------
img = Image.open(os.path.join(R7,"01_hero.png")).convert("RGB")
a = np.asarray(img).astype(int)
H,W = a.shape[:2]
lum = 0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]

# grid columns from strongest edge cols, find ~85px spacing alignment
strong_cols = [23,25,26,35,96,100,101,109,110,111,112,185,186,194,195,269,270,279,280,354,355,359,363,364,409,439,448,449,523,524,533,604,607,608,609,617,618,692,693,695]
# hypothesize grid lines at x = x0 + k*85
for x0 in [20, 22, 24, 26, 28]:
    hits = 0
    for k in range(0, 9):
        gx = x0 + k*85
        near = [c for c in strong_cols if abs(c-gx) <= 4]
        if near: hits += 1
    if hits >= 7:
        print(f"grid hypothesis x0={x0} spacing=85 hits={hits}/9")

# vertical extent of board: y123..1251? check dark grid lines
darkrow = (lum < 40)
for y in range(110, 130):
    frac = darkrow[y, 60:660].mean()
    print(f"y{y} dark-frac {frac:.2f}", end="  ")
print()
for y in range(1240, 1265, 2):
    frac = darkrow[y, 60:660].mean()
    print(f"y{y} dark-frac {frac:.2f}", end="  ")
print()

# cell occupancy with better cell model: x0=26..693 => 8 columns of ~83px?
# Try x0=26, spacing (693-26)/8 = 83.4
for x0, sp in [(26, 83.4), (24, 85)]:
    print(f"\ncell model x0={x0} spacing={sp}")
    occ=0; tot=0
    occupied_cells = []
    for iy in range(13):
        for ix in range(8):
            ya = int(123 + iy*sp + sp*0.3); yb = int(123 + iy*sp + sp*0.7)
            xa = int(x0 + ix*sp + sp*0.3); xb = int(x0 + ix*sp + sp*0.7)
            if yb >= H or xb >= W: continue
            cell = a[ya:yb, xa:xb]
            cm = cell.max(axis=2).astype(int).mean()
            cs = (cell.max(axis=2)-cell.min(axis=2)).astype(int).mean()
            tot += 1
            if cm > 75 or cs > 50:
                occ += 1
                occupied_cells.append((ix,iy))
    print(f"occupied {occ}/{tot} = {occ/tot*100:.1f}%")
    print("occupied map (col,row):", occupied_cells)

# ---------------- R6 vs R7 diff ----------------
print("\n--- R6 vs R7 diff, 07 clear shots ---")
r6i = Image.open(os.path.join(R6,"07_clear.png")).convert("RGB")
r7i = Image.open(os.path.join(R7,"07_clear.png")).convert("RGB")
d = np.abs(np.asarray(r6i).astype(int) - np.asarray(r7i).astype(int))
diff_frac = (d.max(axis=2) > 30)
print(f"pixels changed >30: {diff_frac.mean()*100:.1f}%")
# regions
for (yA,yB,lbl) in [(0,150,"HUD top"),(340,560,"banner zone"),(560,900,"upper board"),(900,1250,"lower board"),(1250,1440,"bottom UI")]:
    print(f"  {lbl} y{yA}-{yB}: {diff_frac[yA:yB].mean()*100:.1f}% changed")

# ---------------- GLORY RAYS + HALO (clear shot, around gold band) ----------------
cl = np.asarray(r7i).astype(int)
clr, clg, clb = cl[...,0], cl[...,1], cl[...,2]
lumc = 0.299*clr+0.587*clg+0.114*clb

# halo/rays: bright warm pixels OUTSIDE the gold band y396..498, x-range beyond band
goldish = (clr>170)&(clg>110)&(clb<120)
outside = goldish.copy()
outside[396:499, :] = False   # mask band itself
ys, xs = np.where(outside)
if len(xs):
    print(f"\ngold-ish px outside band: {len(xs)} bbox x{xs.min()}..{xs.max()} y{ys.min()}..{ys.max()}")
    # radial analysis around board center (360, y?) - use band center (360,447)
    cy, cx = 447, 360
    rr = np.sqrt((ys-cy)**2 + (xs-cx)**2)
    print(f"radial distances: min={rr.min():.0f} max={rr.max():.0f} mean={rr.mean():.0f}")
    # histogram of angles
    ang = np.degrees(np.arctan2(ys-cy, xs-cx)) % 360
    hist, edges = np.histogram(ang, bins=36, range=(0,360))
    print("angle histogram (10deg bins) around band center:")
    for i,h in enumerate(hist):
        print(f"   {i*10:3d}-{i*10+10:3d}: {'#'*(h//40)} {h}")
else:
    print("\nNO gold pixels outside band — no rays/halo detected?")

# bright spokes (any bright pixel, not just gold): around center
bright = lumc > 150
mask = bright.copy()
mask[380:515, :] = False   # exclude banner
ys2, xs2 = np.where(mask)
if len(xs2):
    # restrict to y 100..800 (glory area above board)
    keep = (ys2>100)&(ys2<800)
    ys2, xs2 = ys2[keep], xs2[keep]
    print(f"\nbright px in glory zone (y100-800, excl banner): {len(xs2)} bbox x{xs2.min()}..{xs2.max()} y{ys2.min()}..{ys2.max()}")
    cy, cx = 447, 360
    rr2 = np.sqrt((ys2-cy)**2+(xs2-cx)**2)
    ang2 = np.degrees(np.arctan2(ys2-cy, xs2-cx)) % 360
    hist2, _ = np.histogram(ang2, bins=36, range=(0,360))
    print("spoke angle histogram (36 bins):")
    for i,h in enumerate(hist2):
        print(f"   {i*10:3d}-{i*10+10:3d}: {'#'*(h//30)} {h}")
    # spoke length profile: for each 10deg bin, max radius of bright pixel
    print("max radius per 10-deg bin:")
    for i in range(36):
        sel = (ang2>=i*10)&(ang2<i*10+10)
        if sel.sum()>3:
            print(f"   {i*10:3d}: rmax={rr2[sel].max():.0f} n={sel.sum()}")
        else:
            print(f"   {i*10:3d}: n={sel.sum()}")

# crops: glory zone, halo ring, star
r7i.crop((100, 100, 620, 700)).save(os.path.join(OUT,"clear_glory_zone.png"))
r7i.crop((280, 380, 440, 520)).save(os.path.join(OUT,"clear_star_center.png"))
img.crop((0, 0, 720, 140)).save(os.path.join(OUT,"hero_top_hud.png"))
img.crop((0, 1240, 720, 1440)).save(os.path.join(OUT,"hero_bottom.png"))
print("\ncrops saved: clear_glory_zone.png, clear_star_center.png, hero_top_hud.png, hero_bottom.png")
