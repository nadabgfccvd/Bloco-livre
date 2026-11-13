#!/usr/bin/env python3
"""Claim 2 audit: banner text INSIDE gold band + hairlines + no-rotation symmetry.
Also crops. Works on 07_clear.png (payoff) and 02_skin0.png.
"""
import os
from PIL import Image
import numpy as np

R7 = "/home/z/my-project/critic_shots/r7"
OUT = "/tmp/critic_crops_r7"
os.makedirs(OUT, exist_ok=True)

def analyze(path, tag):
    img = Image.open(path).convert("RGB")
    a = np.asarray(img).astype(int)   # H,W,3
    H, W = a.shape[:2]
    r, g, b = a[...,0], a[...,1], a[...,2]
    lum = 0.299*r + 0.587*g + 0.114*b

    # gold detector: warm, saturated yellow-gold
    gold = (r>170) & (g>110) & (g<210) & (b<110) & (r-b>90) & (abs(r-g*1.35)<60)
    white = (r>225)&(g>225)&(b>225)

    print(f"\n=== {tag} ({os.path.basename(path)}) {W}x{H} ===")
    # 1) gold band rows: count gold pixels per row in x=60..660
    xr = slice(60, 660)
    rowgold = gold[:, xr].sum(axis=1)
    band_rows = [y for y in range(300, 620) if rowgold[y] > 150]
    if band_rows:
        print(f"gold band rows (rowgold>150, y300-620): y{min(band_rows)}..{max(band_rows)}, count={len(band_rows)}")
        # contiguous cluster around expected 396-498
        core = [y for y in band_rows if 380<=y<=520]
        if core:
            print(f"  core cluster y{min(core)}..{max(core)} height={max(core)-min(core)+1}px (claim: 396..498 = 102px)")
            # gold coverage fraction inside band
            y0,y1 = min(core), max(core)
            frac = gold[y0:y1+1, 60:660].mean()
            print(f"  gold coverage inside band: {frac*100:.1f}% of x60-660 area")
            # com_x at top and middle of band
            for label, yy in [("top(396?)", 405), ("middle(447?)", 447)]:
                xs = np.where(gold[yy, 60:660])[0]
                if len(xs):
                    com = xs.mean()+60
                    print(f"  com_x of gold at y={yy} ({label}): {com:.1f} (claim 360)")
                else:
                    # search nearest row with gold
                    for dy in range(-20, 21):
                        xs = np.where(gold[yy+dy, 60:660])[0]
                        if len(xs):
                            print(f"  com_x at y={yy+dy} (nearest): {xs.mean()+60:.1f}, n={len(xs)}")
                            break
    else:
        print("no gold band rows found in y300-620 with >150 gold px/row")
        # where IS gold?
        ys = np.where(rowgold>40)[0]
        print("rows with >40 gold px:", ys[:10], "...", ys[-10:] if len(ys)>10 else "")

    # 2) white text rows INSIDE the band y396..498
    for (yA, yB, lbl) in [(405, 495, "inside band")]:
        rows = white[yA:yB, 60:660].sum(axis=1)
        nz = [y for y in range(yA,yB) if rows[y-yA] > 12]
        if nz:
            # group contiguous
            groups=[]; s=nz[0]; p=nz[0]
            for y in nz[1:]:
                if y-p>3: groups.append((s,p)); s=y
                p=y
            groups.append((s,p))
            print(f"white text row-groups in {lbl} (y{yA}-{yB}): {groups}")
            for (gs,ge) in groups:
                h = ge-gs+1
                print(f"   group y{gs}..{ge} height={h}px  (claim 55px caps cluster y414-469)")
                # x-extent of white text in that group (text ink columns)
                seg = white[gs:ge+1, 60:660]
                cols = np.where(seg.sum(axis=0)>0)[0]
                if len(cols):
                    print(f"     text x-extent: {cols.min()+60}..{cols.max()+60} width={cols.max()-cols.min()+1}px, ink px={seg.sum()}")
        else:
            print(f"NO white text rows inside band y{yA}-{yB} (threshold 12px)")
        # white coverage between text rows (should be gold dark underlay, not white)
    # dark underlay check: rows between 414-469 outside text strokes should be darker gold
    mid = 440
    seg = a[mid-2:mid+3, 100:620].reshape(-1,3)
    print(f"  sample colors y{mid} x100-620: mean={seg.mean(axis=0).round(0)}, min lum={0.299*seg[:,0].min()+0.587*seg[:,1].min()+0.114*seg[:,2].min():.0f}")

    # 3) hairlines: near-white thin rows around y389-394 / y499-504
    for y0,y1,lbl in [(380,400,"top hairline zone"),(492,515,"bottom hairline zone")]:
        rows = white[y0:y1, 60:660].sum(axis=1)
        best = max(range(y0,y1), key=lambda y: rows[y-y0])
        print(f"{lbl}: best white row y={best} count={rows[best-y0]} (of 600); rows>400: {[(y,rows[y-y0]) for y in range(y0,y1) if rows[y-y0]>400]}")

    # 4) rotation symmetry: compare band upper half vs mirrored lower half (flip)
    y0,y1 = 396, 498
    if y1 < H:
        up = lum[y0:y1].astype(float)
        dn = lum[y1-1:y0-1 if y0>0 else None:-1]
        # simpler: compare upper strip vs lower strip flipped vertically
        strip_up = a[y0+4:y0+14, 60:660]
        strip_dn = a[y1-13:y1-3, 60:660]
        d = np.abs(strip_up.astype(int) - strip_dn.astype(int)).mean()
        print(f"symmetry: mean abs diff top-strip vs bottom-strip = {d:.1f} (low = symmetric, no rotation)")
        # also com_x of white text cluster (should be ~360 if centered, unrotated)
        seg = white[414:470, 60:660]
        ys,xs = np.where(seg)
        if len(xs):
            print(f"text cluster com_x={xs.mean()+60:.1f}, com_y={ys.mean()+414:.1f} (centered if ~360/~441)")

analyze(os.path.join(R7,"07_clear.png"), "CLEAR payoff")
analyze(os.path.join(R7,"02_skin0.png"), "SKIN0 classic")

# crops
crops = [
    ("07_clear.png", (60,340,660,560), "clear_banner.png"),
    ("02_skin0.png", (60,340,660,560), "skin0_banner.png"),
    ("01_hero.png",  (60,340,660,560), "hero_banner.png"),
    ("06_full.png",  (60,340,660,560), "full_banner.png"),
]
for src, box, out in crops:
    p = os.path.join(R7, src)
    im = Image.open(p).convert("RGB").crop(box)
    im.save(os.path.join(OUT,out))
    print("saved crop", out, im.size)
