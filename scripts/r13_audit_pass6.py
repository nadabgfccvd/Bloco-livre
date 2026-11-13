"""R13 forensic - PASS 6: delta maps (wells, star, streak head), green confetti, star r12/r13 position."""
import numpy as np
from PIL import Image
from scipy import ndimage

R12 = '/home/z/my-project/critic_shots/r12/'
R13 = '/home/z/my-project/critic_shots/r13/'
X0, X1, Y0, Y1, CELL = 24, 696, 190, 866, 84

def arr(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float64)

def lum(a):
    return a.mean(axis=2)

# ---------- 1. WELL DELTA MAP: what actually changed inside empty wells ----------
print("=" * 100)
print("1. EMPTY-WELL DELTA MAP (r13 - r12), 01_hero well(0,0)")
print("=" * 100)
a12, a13 = arr(R12 + '01_hero.png'), arr(R13 + '01_hero.png')
bx, by = X0 + 0 * CELL, Y0 + 0 * CELL
d = lum(a13[by:by+CELL, bx:bx+CELL]) - lum(a12[by:by+CELL, bx:bx+CELL])
print("delta luminance map (84x84), quantized to 5:")
q = (d / 5).round().astype(int)
sym = {-4:'M',-3:'m',-2:'-',-1:'.',0:' ',1:'.',2:'+',3:'P',4:'H'}
for row in q:
    print(''.join(sym.get(v, '?') for v in row))
print(f"delta stats: mean={d.mean():.2f} min={d.min():.1f} max={d.max():.1f} "
      f"changed>4: {(np.abs(d)>4).sum()}px  neg<-4: {(d<-4).sum()} pos>4: {(d>4).sum()}")

# same for skin1
a12s, a13s = arr(R12 + '03_skin1.png'), arr(R13 + '03_skin1.png')
bx, by = X0 + 2 * CELL, Y0 + 0 * CELL
d = lum(a13s[by:by+CELL, bx:bx+CELL]) - lum(a12s[by:by+CELL, bx:bx+CELL])
print(f"\nskin1 well(2,0): mean={d.mean():.2f} min={d.min():.1f} max={d.max():.1f} changed>4: {(np.abs(d)>4).sum()}px")
q = (d / 5).round().astype(int)
for row in q[::2]:  # every other row for brevity
    print(''.join(sym.get(v, '?') for v in row))

# ---------- 2. STAR POSITION r12 vs r13 ----------
print("\n" + "=" * 100)
print("2. STAR r12 vs r13 (same cell?): vertical position of warm blob in cell")
print("=" * 100)
for shot in ['01_hero.png', '02_skin0.png', '06_full.png']:
    a12, a13 = arr(R12 + shot), arr(R13 + shot)
    res = []
    for tag, a in [('r12', a12), ('r13', a13)]:
        best = None
        for gy in range(8):
            for gx in range(8):
                bx, by = X0 + gx * CELL, Y0 + gy * CELL
                cell_img = a[by:by+CELL, bx:bx+CELL]
                r, g, b = cell_img[..., 0], cell_img[..., 1], cell_img[..., 2]
                warm = ((r > 150) & (r > b + 50) & (g > 100) & (g < r)).sum()
                if warm > 300 and (best is None or warm > best[0]):
                    best = (warm, gx, gy, bx, by)
        if best is None:
            res.append((tag, None)); continue
        warm, gx, gy, bx, by = best
        cell_img = a[by:by+CELL, bx:bx+CELL]
        r, g, b = cell_img[..., 0], cell_img[..., 1], cell_img[..., 2]
        warm_col = ((r > 150) & (r > b + 50) & (g > 100) & (g < r))
        rowfrac = warm_col.mean(axis=1)
        rows = np.where(rowfrac > 0.15)[0]
        res.append((tag, (gx, gy, rows.min(), rows.max(), rows.max()-rows.min())))
    print(f"{shot}: r12={res[0][1]}  r13={res[1][1]}  (cell gx,gy, topRow, botRow, height)")

# ---------- 3. STAR SHADOW: dark px below star bottom in r13 vs r12 ----------
print("\n" + "=" * 100)
print("3. STAR SHADOW (dark px under star, offset +6px)")
print("=" * 100)
for shot in ['01_hero.png', '02_skin0.png', '06_full.png']:
    a12, a13 = arr(R12 + shot), arr(R13 + shot)
    out = []
    for tag, a in [('r12', a12), ('r13', a13)]:
        best = None
        for gy in range(8):
            for gx in range(8):
                bx, by = X0 + gx * CELL, Y0 + gy * CELL
                cell_img = a[by:by+CELL, bx:bx+CELL]
                r, g, b = cell_img[..., 0], cell_img[..., 1], cell_img[..., 2]
                warm = ((r > 150) & (r > b + 50) & (g > 100) & (g < r)).sum()
                if warm > 300 and (best is None or warm > best[0]):
                    best = (warm, gx, gy, bx, by)
        warm, gx, gy, bx, by = best
        cell_img = a[by:by+CELL, bx:bx+CELL]
        L = lum(cell_img)
        r, g, b = cell_img[..., 0], cell_img[..., 1], cell_img[..., 2]
        warm_col = ((r > 150) & (r > b + 50) & (g > 100) & (g < r))
        rowfrac = warm_col.mean(axis=1)
        rows = np.where(rowfrac > 0.15)[0]
        bot = rows.max()
        # well background estimate: rows of empty well sides (columns 0-8 and 76-84, rows below star)
        zone = L[bot+2:bot+18, 10:74]
        side = L[bot+2:bot+18, 2:8].mean() if bot+18 < 84 else None
        dark = (zone < zone.mean() - 15).sum()
        out.append((tag, zone.mean(), dark, bot))
    print(f"{shot}: r12 zone_mean={out[0][1]:5.1f} darkpx={out[0][2]:3d} | r13 zone_mean={out[1][1]:5.1f} darkpx={out[1][2]:3d} | star bottom row r12={out[0][3]} r13={out[1][3]}")

# ---------- 4. STREAK HEAD: tip bright 4px ----------
print("\n" + "=" * 100)
print("4. STREAK HEAD at fill tip (alpha 230, 4px)")
print("=" * 100)
for shot in ['01_hero.png', '02_skin0.png', '04_skin2.png', '06_full.png']:
    a = arr(R13 + shot)
    strip = lum(a[1238:1252, 24:696])
    prof = strip.mean(axis=0)
    # fill tip: rightmost column > 100
    fill_cols = np.where(prof > 100)[0]
    if len(fill_cols) == 0:
        print(f"{shot}: no fill"); continue
    tip = fill_cols.max()
    w = prof[tip-10:tip+1]
    print(f"{shot}: fill tip x={24+tip} last10 prof={np.round(w,1).tolist()}")
    # vertical anatomy at 3px before tip
    col = strip[:, tip-3]
    print(f"    col x={24+tip-3} vertical: {np.round(col,1).tolist()}")

# ---------- 5. GREEN CONFETTI search (relaxed threshold, outside board) ----------
print("\n" + "=" * 100)
print("5. GREEN confetti search (r13, outside board, relaxed)")
print("=" * 100)
a = arr(R13 + '07_clear.png')
r, g, b = a[..., 0], a[..., 1], a[..., 2]
mask = np.zeros(a.shape[:2], bool)
mask[0:190, :] = True; mask[866:1440, :] = True
mask[:, 0:24] = True; mask[:, 696:720] = True
grn = (g > 100) & (g > r + 25) & (g > b + 25) & mask
print(f"green px (g>r+25,g>b+25): {grn.sum()}")
if grn.sum() > 0:
    lbl, n = ndimage.label(grn)
    sizes = ndimage.sum(grn, lbl, range(1, n + 1))
    big = sizes[sizes >= 3]
    print(f"  blobs>=3px: {len(big)} sizes med={np.median(big):.0f} max={big.max():.0f}")
    ys, xs = np.where(grn)
    print(f"  y-range {ys.min()}-{ys.max()} x-range {xs.min()}-{xs.max()}")
# cyan similar
cyn = (b > 100) & (b > r + 25) & (g > r + 15) & mask
pur = (r > 90) & (b > 90) & (g < r - 15) & (g < b - 15) & mask
pnk = (r > 110) & (b > 60) & (g < r - 25) & mask
print(f"cyan px: {cyn.sum()}  purple px: {pur.sum()}  pink px: {pnk.sum()}")
for nm, m in [('cyan', cyn), ('purple', pur), ('pink', pnk), ('green', grn)]:
    if m.sum() > 0:
        lbl, n = ndimage.label(m)
        sizes = ndimage.sum(m, lbl, range(1, n + 1))
        big = sizes[sizes >= 2]
        print(f"  {nm}: {m.sum()}px, {n} raw, {len(big)} blobs>=2, med={np.median(big):.0f} max={big.max():.0f}" if len(big) else f"  {nm}: {m.sum()}px")

# r12 same for delta
a12 = arr(R12 + '07_clear.png')
r, g, b = a12[..., 0], a12[..., 1], a12[..., 2]
grn12 = (g > 100) & (g > r + 25) & (g > b + 25) & mask
cyn12 = (b > 100) & (b > r + 25) & (g > r + 15) & mask
pur12 = (r > 90) & (b > 90) & (g < r - 15) & (g < b - 15) & mask
print(f"r12 same masks: green={grn12.sum()} cyan={cyn12.sum()} purple={pur12.sum()}")
