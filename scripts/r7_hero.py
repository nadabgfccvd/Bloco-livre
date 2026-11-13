#!/usr/bin/env python3
"""Hero shot forensics: board bounds, cell pitch via autocorrelation,
occupancy %, HUD label sizes, demo-button check."""
import os
from PIL import Image
import numpy as np

R7 = "/home/z/my-project/critic_shots/r7"
OUT = "/tmp/critic_crops_r7"
img = Image.open(os.path.join(R7, "01_hero.png")).convert("RGB")
a = np.asarray(img).astype(int)
H, W = a.shape[:2]
r, g, b = a[...,0], a[...,1], a[...,2]
lum = 0.299*r + 0.587*g + 0.114*b

print(f"hero {W}x{H}")

# --- find board: dark cells region with saturated piece colors ---
# saturation proxy
mx = a.max(axis=2); mn = a.min(axis=2)
sat = mx - mn
colored = (sat > 60) & (mx > 90)

ys, xs = np.where(colored)
print(f"colored px: {len(xs)} bbox x{xs.min()}..{xs.max()} y{ys.min()}..{ys.max()}")

# column histogram of colored pixels to find board x-extent
colh = colored.sum(axis=0)
# find dense x range
dense = [x for x in range(W) if colh[x] > 8]
if dense:
    print(f"x with colored>8px: {min(dense)}..{max(dense)} (board-ish columns)")
rowh = colored.sum(axis=1)
densey = [y for y in range(H) if rowh[y] > 8]
if densey:
    print(f"y with colored>8px: {min(densey)}..{max(densey)}")

# --- grid pitch: autocorrelation of column-wise luminance variance inside board ---
def pitch_autocorr(sig, lo=8, hi=90):
    sig = sig - sig.mean()
    best, bestlag = 0, 0
    for lag in range(lo, hi):
        c = (sig[:-lag] * sig[lag:]).sum()
        if c > best: best, bestlag = c, lag
    return bestlag, best

# use edge energy: gradient magnitude along x within board rows
x0, x1 = (min(dense)-6, max(dense)+6) if dense else (60,660)
y0, y1 = (min(densey)-6, max(densey)+6) if densey else (600,1300)
x0=max(0,x0); y0=max(0,y0); x1=min(W,x1); y1=min(H,y1)
print(f"board ROI approx x{x0}..{x1} y{y0}..{y1}")

sub = lum[y0:y1, x0:x1]
gx = np.abs(np.diff(sub, axis=1)).sum(axis=0)   # per column edge energy
gy = np.abs(np.diff(sub, axis=0)).sum(axis=1)   # per row edge energy
px, cx = pitch_autocorr(gx)
py, cy = pitch_autocorr(gy)
print(f"x pitch ~{px}px (score {cx:.0f}); y pitch ~{py}px (score {cy:.0f})")

# refine: strongest grid line columns in ROI
cols = np.argsort(gx)[-40:]
cols = sorted(cols + x0)
print("strongest x-edge cols:", cols)
rows_ = np.argsort(gy)[-40:]
rows_ = sorted(rows_ + y0)
print("strongest y-edge rows:", rows_)

# --- occupancy: cluster colored+dark-filled cells ---
# occupied if pixel distinctly non-background. background = dark (lum<40) uniform
# measure per-cell using pitch
if px > 8:
    ncols = round((x1-x0)/px)
    nrows = round((y1-y0)/py)
    print(f"grid approx {ncols} cols x {nrows} rows, cell={px}px")
    occ = 0; tot = 0
    for iy in range(nrows):
        for ix in range(ncols):
            ya = y0 + iy*py + py//4; yb = ya + max(2, py//2)
            xa = x0 + ix*px + px//4; xb = xa + max(2, px//2)
            cell = a[ya:yb, xa:xb]
            cm = cell.max(axis=2).astype(int).mean()
            cs = (cell.max(axis=2)-cell.min(axis=2)).astype(int).mean()
            tot += 1
            if cm > 70 or cs > 45:
                occ += 1
    print(f"occupied {occ}/{tot} = {occ/tot*100:.1f}% (claim ~28% of 3249 sampled)")

# --- HUD: text rows above board (y0.. maybe 100..500) ---
# white-ish text on dark
white = (r>200)&(g>200)&(b>200)
for yy in range(0, min(y0, 600), 1):
    pass
seg = white[0:y0, 60:660]
rows_with_ink = np.where(seg.sum(axis=1) > 20)[0]
groups = []
if len(rows_with_ink):
    s = rows_with_ink[0]; p = rows_with_ink[0]
    for y in rows_with_ink[1:]:
        if y-p>4: groups.append((s,p)); s=y
        p=y
    groups.append((s,p))
print("HUD/white text row groups above board:")
for gs,ge in groups:
    h = ge-gs+1
    seg2 = white[gs:ge+1, 60:660]
    cols_ = np.where(seg2.sum(axis=0)>0)[0]
    xex = f"{cols_.min()+60}..{cols_.max()+60}" if len(cols_) else "-"
    print(f"  y{gs}..{ge} h={h}px  x-extent {xex}  ink={seg2.sum()}")

# --- demo button check: look for big bright rectangles below board ---
below = a[y1:min(H,y1+140), :]
bl = 0.299*below[...,0]+0.587*below[...,1]+0.114*below[...,2]
bright_rows = np.where(bl.mean(axis=1) > 60)[0]
print(f"below-board bright rows (mean lum>60): {len(bright_rows)} of {bl.shape[0]}")

# crop board + HUD
Image.open(os.path.join(R7,"01_hero.png")).convert("RGB").crop((x0-10, 0, x1+10, y1+20)).save(os.path.join(OUT,"hero_board_full.png"))
Image.open(os.path.join(R7,"01_hero.png")).convert("RGB").crop((0, 0, W, min(H, y0-20) if y0>80 else 300)).save(os.path.join(OUT,"hero_hud.png"))
print("crops saved: hero_board_full.png, hero_hud.png")
