"""R13 forensic - PASS 4: hue clustering on clear-screen confetti + star shadow under board star."""
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

# ---------- 1. Confetti hue census (k-means-free: HSV hue histogram on saturated px) ----------
print("=" * 100)
print("1. CONFETTI hue census, 07_clear (saturated bright non-piece px, HSV)")
print("=" * 100)
for tag, base in [('r12', R12), ('r13', R13)]:
    a = arr(base + '07_clear.png')
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(axis=2); mn = a.min(axis=2)
    mxv = mx.astype(int); delta = (mx - mn).astype(int)
    sat = delta > 50
    bright = mx > 80
    m = sat & bright
    # exclude board pieces region and star area: focus on background zones
    n_px = int(m.sum())
    print(f"\n{tag}: ALL saturated bright px = {n_px}")
    # hue histogram in 24 bins
    import colorsys
    hist = np.zeros(24)
    ys, xs = np.where(m)
    samp = min(len(ys), 40000)
    idx = np.random.RandomState(7).choice(len(ys), samp, replace=False)
    for i in idx:
        h = colorsys.rgb_to_hsv(r[ys[i], xs[i]] / 255, g[ys[i], xs[i]] / 255, b[ys[i], xs[i]] / 255)[0]
        hist[int(h * 24) % 24] += 1
    scale = len(ys) / samp
    names = ['red','red-org','org','org-yel','yel','yel-grn','grn','grn-cy','cyan','cyan-blu','blu','blu-pur','purple','pur-pnk','pnk','pnk-red']
    for i in range(24):
        if hist[i] * scale > 200:
            print(f"   hue bin {i:2d} ({names[i%16]:8s}): {hist[i]*scale:8.0f} px")

# where are confetti px (excluding board region)?
print("\n  Confetti px OUTSIDE board (x<24 or x>696 or y<190 or y>866):")
for tag, base in [('r12', R12), ('r13', R13)]:
    a = arr(base + '07_clear.png')
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(axis=2); mn = a.min(axis=2)
    m = ((mx - mn) > 50) & (mx > 80)
    mask = np.zeros_like(m); mask[0:190, :] = True; mask[866:1440, :] = True
    mask[:, 0:24] = True; mask[:, 696:720] = True
    m2 = m & mask
    ys, xs = np.where(m2)
    # blob analysis
    lbl, n = ndimage.label(m2)
    sizes = ndimage.sum(m2, lbl, range(1, n + 1))
    big = (sizes > 6).sum()
    print(f"   {tag}: {m2.sum():6d} px outside board, {n} raw blobs, {big} blobs >6px, "
          f"size med={np.median(sizes) if n else 0:.0f} max={sizes.max() if n else 0:.0f}")

# blob size distribution in r13 (2-size claim: 9-15 and 4-7)
print("\n  r13 confetti blob sizes (outside board):")
a = arr(R13 + '07_clear.png')
r, g, b = a[..., 0], a[..., 1], a[..., 2]
mx = a.max(axis=2); mn = a.min(axis=2)
m = ((mx - mn) > 40) & (mx > 70)
mask = np.zeros_like(m); mask[0:190, :] = True; mask[866:1440, :] = True
mask[:, 0:24] = True; mask[:, 696:720] = True
m2 = m & mask
lbl, n = ndimage.label(m2)
sizes = ndimage.sum(m2, lbl, range(1, n + 1))
keep = sizes[sizes > 3]
if len(keep):
    print(f"   blobs={len(keep)} sizes: min={keep.min():.0f} p25={np.percentile(keep,25):.0f} med={np.median(keep):.0f} p75={np.percentile(keep,75):.0f} max={keep.max():.0f}")
    small = ((keep >= 4) & (keep <= 15)).sum()
    print(f"   blobs in 4-15px range: {small}/{len(keep)}")

# ---------- 2. STAR on board: star piece in board with shadow ----------
print("\n" + "=" * 100)
print("2. BOARD STAR + SHADOW: star piece (5-point, scy-0.42*cell, body 0.70*cell ~59px)")
print("=" * 100)
# star piece sits in a board cell. Find within board: warm blob with spikes
for shot in ['01_hero.png', '02_skin0.png', '06_full.png']:
    a = arr(R13 + shot)
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
        print(f"{shot}: no warm star cell in board"); continue
    warm, gx, gy, bx, by = best
    print(f"{shot}: star cell ({gx},{gy}) warm px={warm}")
    # vertical profile of star column: find star body y-extent and dark band below
    cell_img = a[by:by+CELL, bx:bx+CELL]
    L = lum(cell_img)
    r, g, b = cell_img[..., 0], cell_img[..., 1], cell_img[..., 2]
    warm_col = ((r > 150) & (r > b + 50) & (g > 100) & (g < r))
    rowfrac = warm_col.mean(axis=1)
    star_rows = np.where(rowfrac > 0.2)[0]
    if len(star_rows) == 0:
        print("   no star rows"); continue
    sy0, sy1 = star_rows.min(), star_rows.max()
    print(f"   star rows y[{by+sy0},{by+sy1}] height={sy1-sy0}px (body claim ~59px)")
    # shadow: rows below star, dark compared to neighbor cells at same rows
    bg_est = lum(a[by+sy1+3:by+sy1+18, bx+10:bx+74]).mean()
    same_row_other = lum(a[by+sy1+3:by+sy1+18, bx+CELL+4:min(bx+2*CELL, 696)]).mean() if bx+CELL+4 < 696 else None
    print(f"   below-star zone mean={bg_est:5.1f}" + (f" vs right-neighbor same rows={same_row_other:5.1f}" if same_row_other else ""))

# ---------- 3. STREAK instrument: tick marks and head ----------
print("\n" + "=" * 100)
print("3. STREAK: ticks (4px wide, alpha170) + head (4px, alpha230) + gloss top 45%")
print("=" * 100)
a = arr(R13 + '01_hero.png')
strip = a[STREAK_Y0:STREAK_Y1, X0:X1] if False else a[1238:1252, 24:696]
Ls = strip.mean(axis=2)
prof = Ls.mean(axis=0)  # x-profile
# head: find rightmost bright run >=3 px
bright = prof > prof.max() * 0.55
runs = []
inrun = False
for i, v in enumerate(bright):
    if v and not inrun: start = i; inrun = True
    elif not v and inrun: runs.append((start, i)); inrun = False
if inrun: runs.append((start, len(bright)))
print(f"  x-profile bright runs (>{prof.max()*0.55:.0f}): {runs}")
# ticks: periodic 4px-wide semi-bright marks in dark zone
# detect columns notably above local median
med = np.median(prof)
tickish = (prof > med + 12) & (prof < prof.max() * 0.5)
tr = []
inrun = False
for i, v in enumerate(tickish):
    if v and not inrun: start = i; inrun = True
    elif not v and inrun: tr.append((start + 24, i + 24)); inrun = False
if inrun: tr.append((start + 24, len(tickish) + 24))
print(f"  tick-candidate runs (med={med:.1f}): {tr[:30]}")

# vertical 2-tone gloss check: top 45% of fill brighter?
fill_cols = runs[0] if runs else (100, 260)
seg = Ls[:, fill_cols[0]:fill_cols[1]]
top, bot = seg[:6], seg[6:]
print(f"  fill zone top rows mean={top.mean():5.1f} bottom rows mean={bot.mean():5.1f} (gloss delta={top.mean()-bot.mean():5.1f})")
