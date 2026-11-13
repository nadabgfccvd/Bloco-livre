"""R13 forensic - PASS 2: streak instrument anatomy + board micro-texture + star shadow."""
import numpy as np
from PIL import Image

R12 = '/home/z/my-project/critic_shots/r12/'
R13 = '/home/z/my-project/critic_shots/r13/'
SHOTS = ['01_hero.png','02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png','06_full.png','07_clear.png']
X0, X1 = 24, 696
STREAK_Y0, STREAK_Y1 = 1238, 1252

def arr(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float64)

def lum(a):
    return a.mean(axis=2)

# ---------- A. STREAK METER ANATOMY ----------
print("=" * 100)
print("A. STREAK METER ANATOMY (y1238-1252, x24-696)")
print("=" * 100)
for shot in SHOTS:
    a = arr(R13 + shot)
    strip = lum(a[STREAK_Y0:STREAK_Y1, X0:X1])
    row = strip.mean(axis=0)  # avg over 14 rows -> profile along x
    # find fill extent: bright pixels vs dark track
    bright = row > row.mean()
    # track bounds: columns that are not pure background
    nz = np.where(row > 8)[0]
    if len(nz) == 0:
        print(f"{shot}: empty strip"); continue
    # column-wise std (vertical structure: rim, fill, gloss, ticks, head)
    colstd = strip.std(axis=0)
    # dark track detection: darkest 20% of active columns
    act = nz
    dark_thr = np.percentile(row[act], 15)
    dark_cols = (row <= dark_thr + 6).sum()
    bright_cols = (row > np.percentile(row[act], 90)).sum()
    print(f"{shot}: active x[{X0+nz[0]},{X0+nz[-1]}] len={nz[-1]-nz[0]+1}px  "
          f"colstd max={colstd.max():5.1f} min={colstd[act].min():5.1f}  "
          f"bright cols(>p90)={bright_cols}  dark cols(<p15+6)={dark_cols}  "
          f"profile mean={row[act].mean():5.1f}")

# vertical profile of the instrument: sample a fill column and a dark column
print("\n  Vertical structure at 3 sample columns (01_hero):")
a = arr(R13 + '01_hero.png')
for x in [60, 200, 340, 500, 660]:
    col = a[STREAK_Y0:STREAK_Y1, x].mean(axis=1)
    print(f"   x={x}: vals={['%5.1f' % v for v in col]}")

# ---------- B. BOARD MICRO-TEXTURE: per-well diagonal lines ----------
print("\n" + "=" * 100)
print("B. BOARD MICRO-TEXTURE (empty well diagonal lines, alpha 16)")
print("=" * 100)
# find an empty well: lowest-luminance-variance 84x84 block inside board
for shot in ['01_hero.png', '02_skin0.png', '03_skin1.png']:
    a = arr(R13 + shot)
    best = None
    for gy in range(8):
        for gx in range(8):
            bx, by = X0 + gx * 84, 190 + gy * 84
            well = lum(a[by+4:by+80, bx+4:bx+80])
            v = well.std()
            # want low std (empty well, no piece) but check micro-lines via high-pass
            if best is None or v < best[0]:
                best = (v, gx, gy, bx, by, well)
    v, gx, gy, bx, by, well = best
    # high-pass: diagonal structure -> compare diagonal means vs off-diagonal
    hp = well - np.array([well.mean()] * well.shape[0])[:, None]
    # gradient along diag
    diag_line = np.trace(np.abs(hp)) / 76
    # autocorr-style: count pixels above small threshold forming thin lines
    thr = well.mean() + 5
    line_px = (well > thr).sum()
    print(f"{shot}: emptiest well ({gx},{gy}) std={v:5.2f}  pixels>mean+5: {line_px:4d}/5776 ({line_px/5776*100:4.1f}%)  diag-activity={diag_line:5.2f}")

# r12 comparison on same wells
print("\n  r12 same-position wells:")
for shot in ['01_hero.png', '02_skin0.png']:
    a12 = arr(R12 + shot)
    a13 = arr(R13 + shot)
    for (gx, gy) in [(3, 4), (5, 5)]:
        bx, by = X0 + gx * 84, 190 + gy * 84
        w12 = lum(a12[by+4:by+80, bx+4:bx+80]); w13 = lum(a13[by+4:by+80, bx+4:bx+80])
        print(f"   {shot} well({gx},{gy}): std r12={w12.std():5.2f} r13={w13.std():5.2f}  "
              f"thin-line px(>m+5) r12={(w12>w12.mean()+5).sum():4d} r13={(w13>w13.mean()+5).sum():4d}")

# ---------- C. STAR FLOAT: drop shadow under star ----------
print("\n" + "=" * 100)
print("C. STAR DROP SHADOW (dark px under star, offset +0.07*cell = +6px)")
print("=" * 100)
# star drawn at score position; look in header/title area and clear screen.
# Search whole image for the star: high-brightness yellowish blob. Then measure dark px below it.
def find_star(a):
    g = lum(a)
    r, gch, b = a[..., 0], a[..., 1], a[..., 2]
    starish = (g > 200) & (r > 180) & (gch > 150) & (b < r)  # warm bright
    ys, xs = np.where(starish)
    return ys, xs, starish

for shot in SHOTS:
    a = arr(R13 + shot)
    ys, xs, mask = find_star(a)
    if len(ys) < 30:
        print(f"{shot}: no star found ({len(ys)} px)")
        continue
    # cluster: take largest blob bounding box
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    print(f"{shot}: star bbox x[{x0},{x1}] y[{y0},{y1}] ({x1-x0}x{y1-y0}px, {len(ys)} px)")
    # shadow: region below star bbox, offset ~6px, same width
    sx0, sx1 = x0 - 5, x1 + 5
    sy0 = min(y1 + 3, 1400); sy1 = min(y1 + 26, 1440)
    if sy1 - sy0 > 4 and sx1 > sx0:
        sh = lum(a[sy0:sy1, sx0:sx1])
        # background estimate: pixels left/right of star at same y range
        bgL = lum(a[sy0:sy1, max(0, x0 - 60):max(6, x0 - 20)])
        bgR = lum(a[sy0:sy1, min(719, x1 + 20):min(719, x1 + 60)])
        bg = np.median(np.concatenate([bgL.ravel(), bgR.ravel()])) if (bgL.size + bgR.size) else sh.mean()
        dark = (sh < bg - 12).sum()
        print(f"    shadow zone y[{sy0},{sy1}] x[{sx0},{sx1}]: dark px (<bg-12, bg={bg:5.1f}) = {dark}  zone mean={sh.mean():5.1f}")
