#!/usr/bin/env python3
"""R12 part O (final measurements): star geometry precise; tray per-row diff all shots;
streak bar; gem facet quality; danger/red scan."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'
NAMES = ['01_hero','02_skin0','03_skin1','04_skin2','05_skin3','06_full','07_clear']

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

def star_body(im):
    """gold star body only (not pale glow), rows 200..350, x 230..530"""
    R, G, B = im[:,:,0], im[:,:,1], im[:,:,2]
    gold = (R > 200) & (G > 140) & (B < 200) & (R - B > 60)
    zone = np.zeros_like(gold); zone[200:351, 230:530] = True
    m = gold & zone
    ys, xs = np.where(m)
    return m, ys, xs

print("=== STAR BODY (gold only, x230-530, y200-350) in 07_clear ===")
res = {}
for tag in ('r11','r12'):
    im = load((R11 if tag=='r11' else R12) + '07_clear.png')
    m, ys, xs = star_body(im)
    if len(ys):
        ylo, yhi, xlo, xhi = ys.min(), ys.max(), xs.min(), xs.max()
        # widest row
        cnt = np.bincount(ys, minlength=360)
        widest = cnt.max(); ywid = cnt.argmax()
        res[tag] = (ylo, yhi, xlo, xhi, len(ys), widest, ywid)
        print(f"{tag}: rows {ylo}..{yhi}  cols {xlo}..{xhi}  px={len(ys)}  widest={widest}px @y={ywid}")
    else:
        print(tag, "none")

# banner top: first row >=340 with wide GOLD (R>200,G>140) frac
for tag in ('r11','r12'):
    im = load((R11 if tag=='r11' else R12) + '07_clear.png')
    R, G, B = im[:,:,0], im[:,:,1], im[:,:,2]
    gold = (R > 200) & (G > 140) & (B < 200) & (R - B > 60)
    for y in range(335, 365):
        frac = gold[y, 40:680].mean()
        if frac > 0.9:
            print(f"{tag} banner solid-gold top = {y} (frac {frac:.2f})"); break

# gap: star body bottom vs banner top (r12)
if 'r12' in res:
    yhi = res['r12'][1]
    print("r12 star bottom:", yhi, "-> gap to band top (see banner top above)")

# ray/glow: pale pixels around star
for tag in ('r11','r12'):
    im = load((R11 if tag=='r11' else R12) + '07_clear.png')
    R, G, B = im[:,:,0], im[:,:,1], im[:,:,2]
    pale = (R > 220) & (G > 190) & (B > 120) & (B < 230)
    zone = np.zeros_like(pale); zone[180:351, 230:530] = True
    m = pale & zone
    ys, xs = np.where(m)
    print(f"{tag} pale-glow px y180-350 x230-530: n={len(ys)}", f"rows {ys.min()}..{ys.max()}" if len(ys) else "")

# ===== TRAY per-row diff, every row 828..900 =====
print("\n=== TRAY diff r12-r11, EVERY row 828..900 (mean |diff| x40-680) ===")
for nm in NAMES:
    a = load(R11+nm+'.png'); b = load(R12+nm+'.png')
    d = np.abs(a-b).mean(axis=2)[:, 40:680]
    steps = []
    prev = None
    for y in range(828, 901):
        v = round(d[y].mean(), 1)
        steps.append(f"{y}:{v}")
    print(nm, " ".join(steps))

# ===== STREAK bar =====
print("\n=== STREAK zone y1230..1260 (hero): gold frac, x extent ===")
for nm in NAMES:
    im = load(R12+nm+'.png')
    R, G, B = im[:,:,0], im[:,:,1], im[:,:,2]
    gold = (R > 200) & (G > 150) & (B < 130)
    band = gold[1230:1260, :]
    ys, xs = np.where(band)
    if len(xs):
        print(f"{nm}: streak gold px={len(xs)} x {xs.min()}..{xs.max()} rows {1230+ys.min()}..{1230+ys.max()}")
    else:
        lum = im.mean(axis=2)[1230:1260, :]
        print(f"{nm}: no gold streak; zone max lum {lum.max():.0f}")

# ===== GEM FACET QUALITY: sample 3 cells in hero =====
print("\n=== GEM cells (hero): unique colors, edge AA steps ===")
im = load(R12+'01_hero.png')
for (cx, cy, label) in [(2,2,'cell(2,2)'), (5,3,'cell(5,3)'), (1,6,'cell(1,6)'), (6,5,'cell(6,5)')]:
    x0, y0 = 24 + cx*84, 190 + cy*84
    cell = im[y0+8:y0+76, x0+8:x0+76]
    q = (cell//10)
    uniq = len(np.unique(q.reshape(-1,3), axis=0))
    # horizontal gradient across gem center line: count distinct steps
    mid = cell[cell.shape[0]//2, :, :]
    steps = len(set(map(tuple, (mid//10).tolist())))
    print(f"{label}: uniq colors(10)={uniq}  mid-row steps={steps}")

# ===== DANGER / RED scan =====
print("\n=== RED px scan (R>180, G<90, B<90) all shots ===")
for nm in NAMES:
    im = load(R12+nm+'.png')
    R, G, B = im[:,:,0], im[:,:,1], im[:,:,2]
    red = (R > 180) & (G < 90) & (B < 90)
    ys, xs = np.where(red)
    zones = {}
    for y, x in zip(ys.tolist(), xs.tolist()):
        z = 'hud' if y < 190 else ('board' if y < 866 else ('tray' if y < 1150 else 'below'))
        zones[z] = zones.get(z, 0) + 1
    print(nm, "red px:", len(ys), zones)

# ===== BOTTOM BAR y1288..1320 and y1400..1436: what's there (nav/labels) =====
print("\n=== bottom text zones luminance presence ===")
for nm in ['01_hero','06_full']:
    im = load(R12+nm+'.png')
    lum = im.mean(axis=2)
    for (y0,y1,label) in [(1288,1324,'y1288-1323'),(1404,1436,'y1404-1435'),(1200,1220,'y1200-1219')]:
        z = lum[y0:y1, :]
        frac = (z > 60).mean()
        print(nm, label, "bright frac", round(frac,3), "max", round(z.max(),0))
