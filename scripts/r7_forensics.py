#!/usr/bin/env python3
"""R7 pixel forensics: global structure scan of all 7 screenshots + R6 diffs.
Writes crops to /tmp/critic_crops_r7/ and prints measured evidence.
"""
import os
from PIL import Image

R7 = "/home/z/my-project/critic_shots/r7"
R6 = "/home/z/my-project/critic_shots/r6"
OUT = "/tmp/critic_crops_r7"
os.makedirs(OUT, exist_ok=True)

names = ["01_hero.png","02_skin0.png","03_skin1.png","04_skin2.png","05_skin3.png","06_full.png","07_clear.png"]

def load(p):
    return Image.open(p).convert("RGB")

def row_profile(img, y, x0=0, x1=None):
    """mean RGB of a row segment + luminance"""
    if x1 is None: x1 = img.width
    px = [img.getpixel((x,y)) for x in range(x0, min(x1, img.width))]
    if not px: return None
    r = sum(p[0] for p in px)/len(px); g = sum(p[1] for p in px)/len(px); b = sum(p[2] for p in px)/len(px)
    return (r,g,b, 0.299*r+0.587*g+0.114*b)

def col_profile(img, x, y0=0, y1=None):
    if y1 is None: y1 = img.height
    px = [img.getpixel((x,y)) for y in range(y0, min(y1, img.height))]
    if not px: return None
    r = sum(p[0] for p in px)/len(px); g = sum(p[1] for p in px)/len(px); b = sum(p[2] for p in px)/len(px)
    return (r,g,b, 0.299*r+0.587*g+0.114*b)

print("="*80)
print("GLOBAL STRUCTURE SCAN (720x1440 each)")
print("="*80)
for n in names:
    p = os.path.join(R7, n)
    if not os.path.exists(p):
        print(n, "MISSING"); continue
    img = load(p)
    W,H = img.size
    # sample luminance rows every 20px to find bands
    print(f"\n--- {n} ---")
    bands = []
    prev_lum = None
    for y in range(0, H, 4):
        pr = row_profile(img, y)
        if pr is None: continue
        lum = pr[3]
        if prev_lum is not None and abs(lum - prev_lum) > 18:
            bands.append((y, round(prev_lum), round(lum)))
        prev_lum = lum
    # compress: only first 30 transitions
    print("row luminance transitions (y, old, new):")
    for b in bands[:40]:
        print("   ", b)
    if len(bands) > 40:
        print(f"    ... {len(bands)} transitions total")

print("\n" + "="*80)
print("DONE structure scan")
