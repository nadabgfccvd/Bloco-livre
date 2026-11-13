#!/usr/bin/env python3
"""R14 pass 8: R13 vs R14 A/B on wells, rims, gaps (vignette truth) + band shadow + confetti aspect A/B."""
import os, math
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"
def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]
def wc(c,r): return (66+c*84, 232+r*84)

def patch_mean(im, cx, cy, rad):
    vals=[lum(im.getpixel((int(cx+dx),int(cy+dy)))) for dy in range(-rad,rad+1,2) for dx in range(-rad,rad+1,2)]
    return sum(vals)/len(vals)

def ab_report(shot):
    a = Image.open(os.path.join(R13,shot)).convert("RGB")
    b = Image.open(os.path.join(R14,shot)).convert("RGB")
    print(f"\n=== A/B {shot} (R13 -> R14) ===")
    print("  EMPTY-well interiors (only wells empty in BOTH):")
    pairs=[]
    for r in range(8):
        for c in range(8):
            cx,cy=wc(c,r)
            la=patch_mean(a,cx,cy,12); lb=patch_mean(b,cx,cy,12)
            if la<95 and lb<95:
                d=math.hypot(cx-360,cy-526)/84
                pairs.append((d,la,lb,c,r))
    for d,la,lb,c,r in sorted(pairs):
        print(f"    well({c},{r}) d={d:4.2f}: R13={la:5.1f} R14={lb:5.1f} delta={lb-la:+6.1f}")
    if pairs:
        inner=[(la,lb) for d,la,lb,_,_ in pairs if d<=2.2]
        outer=[(la,lb) for d,la,lb,_,_ in pairs if d>=3.5]
        if inner and outer:
            ia=sum(x[0] for x in inner)/len(inner); ib=sum(x[1] for x in inner)/len(inner)
            oa=sum(x[0] for x in outer)/len(outer); ob=sum(x[1] for x in outer)/len(outer)
            print(f"    inner: R13 {ia:.1f} -> R14 {ib:.1f} ({(ib-ia)/ia*100:+.1f}%) | outer: R13 {oa:.1f} -> R14 {ob:.1f} ({(ob-oa)/oa*100:+.1f}%)")
            print(f"    R13 corner/center ratio: {(oa-ia)/ia*100:+.1f}% | R14: {(ob-ib)/ib*100:+.1f}%")
    print("  Background gap midpoints (between wells), corner vs center:")
    for (gx,gy,tag) in [(108,274,"corner-gap(0/1,0/1)"),(360,524,"center-gap(3/4,3/4)"),(612,778,"corner-gap(6/7,6/7)"),(444,442,"mid-gap")]:
        la=patch_mean(a,gx,gy,5); lb=patch_mean(b,gx,gy,5)
        print(f"    {tag}: R13={la:5.1f} R14={lb:5.1f} delta={lb-la:+6.1f}")
    print("  Well RIM (top-left rim px of well(0,0) and well(3,3)) luminance:")
    for (c,r,tag) in [(0,0,"corner well(0,0) rim"),(3,3,"center well(3,3) rim"),(7,7,"corner well(7,7) rim"),(4,3,"center well(4,3) rim")]:
        cx,cy=wc(c,r)
        # rim = ring at radius ~34 from center (well is ~72 wide)
        pts=[]
        for ang in range(0,360,15):
            x=int(cx+34*math.cos(math.radians(ang))); y=int(cy+34*math.sin(math.radians(ang)))
            pts.append(lum(a.getpixel((x,y)))); pts.append(lum(b.getpixel((x,y))))
        la=sum(pts[0::2])/len(pts[0::2]); lb=sum(pts[1::2])/len(pts[1::2])
        print(f"    {tag}: R13={la:5.1f} R14={lb:5.1f} delta={lb-la:+6.1f}")
    print("  PIECE faces (wells occupied in both, piece-similar):")
    occ=[]
    for r in range(8):
        for c in range(8):
            cx,cy=wc(c,r)
            la=patch_mean(a,cx,cy,12); lb=patch_mean(b,cx,cy,12)
            if la>110 and lb>110:
                d=math.hypot(cx-360,cy-526)/84
                occ.append((d,la,lb,c,r))
    for d,la,lb,c,r in sorted(occ)[:6]+sorted(occ)[-6:]:
        print(f"    piece({c},{r}) d={d:4.2f}: R13={la:5.1f} R14={lb:5.1f} delta={lb-la:+6.1f}")
    if occ:
        inner=[(la,lb) for d,la,lb,_,_ in occ if d<=2.2]
        outer=[(la,lb) for d,la,lb,_,_ in occ if d>=3.5]
        if inner and outer:
            ia=sum(x[0] for x in inner)/len(inner); ib=sum(x[1] for x in inner)/len(inner)
            oa=sum(x[0] for x in outer)/len(outer); ob=sum(x[1] for x in outer)/len(outer)
            print(f"    pieces inner: R13 {ia:.1f} -> R14 {ib:.1f} | outer: R13 {oa:.1f} -> R14 {ob:.1f}")
            print(f"    piece corner/center: R13 {(oa-ia)/ia*100:+.1f}% -> R14 {(ob-ib)/ib*100:+.1f}%")

ab_report("01_hero.png")
ab_report("02_skin0.png")
ab_report("06_full.png")
