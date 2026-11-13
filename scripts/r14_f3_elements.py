#!/usr/bin/env python3
"""R14 pass 3: star geometry, float gap, drop shadow, confetti shape/rotation, bevel line."""
import os, math
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"

def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]

def star_profile(im, label):
    """Column scan of the hero star: per-row count of gold px + extents, y140-380."""
    print(f"\n--- STAR vertical profile {label} ---")
    W,H = im.size
    for y in range(140, 380, 6):
        cnt=0; xs=[]
        for x in range(20, 700):
            r,g,b = im.getpixel((x,y))[:3]
            if r>150 and g>110 and b<110 and (r-b)>60:
                cnt+=1; xs.append(x)
        if cnt:
            print(f"  y={y}: n={cnt:3d} x[{min(xs)}..{max(xs)}] w={max(xs)-min(xs)}")

def shadow_dark(im, label):
    """Below star: dark shadow pixels in gap band and on band top."""
    print(f"\n--- SHADOW {label} ---")
    # gap band y336-354: what's there (dark px <60 lum)
    for (y0,y1,tag) in [(330,356,"gap zone"),(356,375,"band top"),(375,400,"band upper")]:
        dark=0; tot=0; xs=[]; ys=[]
        for y in range(y0,y1):
            for x in range(180, 540):
                l = lum(im.getpixel((x,y)))
                tot+=1
                if l<60: dark+=1; xs.append(x); ys.append(y)
        if dark:
            print(f"  {tag} y{y0}-{y1}: dark px={dark}/{tot} bbox=({min(xs)},{min(ys)},{max(xs)},{max(ys)})")
        else:
            print(f"  {tag} y{y0}-{y1}: dark px=0")

def shadow_offset(im, label):
    """Find the star silhouette (gold) and the dark shadow blob under it, compare centroids."""
    # star body: strongest gold mass y140-340
    star_px=[]
    for y in range(140,345):
        for x in range(20,700):
            r,g,b = im.getpixel((x,y))[:3]
            if r>150 and g>110 and b<110 and (r-b)>60:
                star_px.append((x,y))
    print(f"\n--- SHADOW OFFSET {label}: star gold px={len(star_px)}")
    if not star_px: 
        print("  no star found"); return
    sx = sum(p[0] for p in star_px)/len(star_px)
    sy = sum(p[1] for p in star_px)/len(star_px)
    print(f"  star centroid=({sx:.0f},{sy:.0f}) bbox x[{min(p[0] for p in star_px)}..{max(p[0] for p in star_px)}] y[{min(p[1] for p in star_px)}..{max(p[1] for p in star_px)}]")
    # shadow: dark blob (lum<60) within y [star_bottom .. star_bottom+40], x within star x-range
    ybot = max(p[1] for p in star_px)
    xmin,xmax = min(p[0] for p in star_px), max(p[0] for p in star_px)
    sh=[]
    for y in range(ybot, min(ybot+50, 460)):
        for x in range(xmin-20, xmax+20):
            l = lum(im.getpixel((x,y)))
            if l < 55:
                sh.append((x,y))
    if sh:
        hx = sum(p[0] for p in sh)/len(sh); hy = sum(p[1] for p in sh)/len(sh)
        print(f"  dark blob under star: n={len(sh)} centroid=({hx:.0f},{hy:.0f}) bbox x[{min(p[0] for p in sh)}..{max(p[0] for p in sh)}] y[{min(p[1] for p in sh)}..{max(p[1] for p in sh)}]")
        print(f"  star bottom y={ybot}  shadow top y={min(p[1] for p in sh)} -> gap {min(p[1] for p in sh)-ybot}px")
        print(f"  centroid offset dx={hx-sx:+.1f} dy={hy-sy:+.1f}")
    else:
        print("  no dark blob under star")

def confetti_stats(im, label):
    """Saturated non-gold px count + connected component shape/aspect analysis."""
    from collections import deque
    W,H = im.size
    sat_mask = {}
    nongold=0
    pts=[]
    for y in range(0,H):
        for x in range(0,W):
            r,g,b = im.getpixel((x,y))[:3]
            mx,mn = max(r,g,b), min(r,g,b)
            if mx>60 and (mx-mn)/mx > 0.45 and not (r>150 and g>110 and b<110 and (r-b)>60):
                nongold+=1; pts.append((x,y))
    print(f"\n--- CONFETTI {label}: saturated non-gold px={nongold}")
    # small flood fill label on subset: use pts set
    ptset = set(pts)
    seen=set(); comps=[]
    for p in pts:
        if p in seen: continue
        q=deque([p]); seen.add(p); comp=[]
        while q:
            c=q.popleft(); comp.append(c)
            for d in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                n=(c[0]+d[0], c[1]+d[1])
                if n in ptset and n not in seen:
                    seen.add(n); q.append(n)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    print(f"  components={len(comps)} sizes(top10)={[len(c) for c in comps[:10]]}")
    aspects=[]
    squares=0
    for c in comps:
        if len(c)<12: continue
        xs=[p[0] for p in c]; ys=[p[1] for p in c]
        w=max(xs)-min(xs)+1; h=max(ys)-min(ys)+1
        a=w/h
        aspects.append(round(a,2))
        fill = len(c)/(w*h)
        if 0.85<=a<=1.18 and fill>0.5:
            squares+=1
    print(f"  components>=12px: {sum(1 for c in comps if len(c)>=12)} aspect ratios={sorted(set(aspects))}")
    print(f"  square-like (0.85-1.18 aspect, >50% fill): {squares}")

def bevel_line(im, label):
    """Diagonal line detection: pixels brighter than local background along diagonal in board area."""
    print(f"\n--- BEVEL {label} ---")
    W,H=im.size
    # scan board region y190-866, x24-696 for high-gradient diagonal structures:
    # sample random diagonals and count pixels with lum > neighbors by delta>8
    hits=0; pts=[]
    for y in range(200, 860, 2):
        for x in range(30, 690, 2):
            l = lum(im.getpixel((x,y)))
            lA = lum(im.getpixel((x+2,y+2)))  # along diagonal
            lB = lum(im.getpixel((x+2,y)))     # along horizontal
            lC = lum(im.getpixel((x,y+2)))     # along vertical
            if abs(l-lA)>10 and abs(l-lB)<6 and abs(l-lC)<6:
                hits+=1; pts.append((x,y))
    print(f"  diagonal-structure px (2px stride, board area): {hits}")
    if pts:
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        print(f"  bbox x[{min(xs)}..{max(xs)}] y[{min(ys)}..{max(ys)}]")
        # cluster by line
        # print a few sample points
        print(f"  sample: {pts[:12]}")

for s, tag in [("01_hero.png","R14-hero"),("07_clear.png","R14-clear"),("03_skin1.png","R14-skin1")]:
    im = Image.open(os.path.join(R14,s)).convert("RGB")
    star_profile(im, tag)
    shadow_dark(im, tag)
    shadow_offset(im, tag)
    confetti_stats(im, tag)
    bevel_line(im, tag)
