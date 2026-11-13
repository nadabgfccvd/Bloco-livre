#!/usr/bin/env python3
"""R12 part N: star geometry in 07_clear vs r11; band top; gap. Skins ASCII + palettes.
Streak bar geometry. Tray zone finer ASCII."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

def star_mask(im):
    R, G, B = im[:,:,0], im[:,:,1], im[:,:,2]
    gold = (R > 200) & (G > 140) & (B < 200) & (R - B > 60)
    pale = (R > 230) & (G > 200) & (B > 140)
    return gold | pale

for tag, path in [('r12', R12+'07_clear.png'), ('r11', R11+'07_clear.png')]:
    im = load(path)
    m = star_mask(im)
    zone = np.zeros_like(m); zone[210:360, :] = True
    m = m & zone
    ys, xs = np.where(m)
    print(f"[{tag}] star-zone pixels: n={len(ys)}", end="")
    if len(ys):
        # restrict to central cluster x 240..500 (exclude left HUD column x<200)
        sel = (xs >= 240) & (xs <= 520)
        print(f" | central: n={sel.sum()} rows {ys[sel].min()}..{ys[sel].max()} cols {xs[sel].min()}..{xs[sel].max()}", end="")
        if sel.sum():
            ylo, yhi = ys[sel].min(), ys[sel].max()
            # widest row
            ymid = (ylo+yhi)//2
            row = m[ymid, 240:520]
            xs2 = np.where(row)[0]
            print(f" | height={yhi-ylo+1} width@mid={xs2.max()-xs2.min()+1}")
    else:
        print()

# band top in 07_clear (celebration banner): first row with wide gold
im7 = load(R12+'07_clear.png')
lum7 = im7.mean(axis=2)
for y in range(340, 380):
    frac = (lum7[y, 40:680] > 150).mean()
    if frac > 0.5:
        print("r12 07_clear banner top:", y, "frac", round(frac,2)); break
im11c = load(R11+'07_clear.png')
lum11c = im11c.mean(axis=2)
for y in range(340, 380):
    frac = (lum11c[y, 40:680] > 150).mean()
    if frac > 0.5:
        print("r11 07_clear banner top:", y, "frac", round(frac,2)); break

# r11 star bottom
im11 = load(R11+'07_clear.png')
m11 = star_mask(im11)
zone = np.zeros_like(m11); zone[210:360, :] = True
m11z = m11 & zone
ys, xs = np.where(m11z)
sel = (xs >= 240) & (xs <= 520)
if sel.sum():
    print("r11 star rows:", ys[sel].min(), "..", ys[sel].max())

# ===== SKINS: palette diversity + layout =====
print("\n===== SKIN PALETTE STATS =====")
for nm in ['02_skin0','03_skin1','04_skin2','05_skin3','06_full']:
    im = load(R12+nm+'.png')
    q = (im//24).reshape(-1,3)
    uniq = len(np.unique(q, axis=0))
    # board area variance
    board = im[190:866, 24:696]
    print(f"{nm}: quantized(24) colors={uniq}  board std={board.std():.1f} mean={board.mean():.1f}")
