"""R13 forensic - PASS 9 (final): header star shadow, micro-texture shape at low thresh, vignette strict."""
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

# ---------- 1. HEADER STAR: blob bbox r12 vs r13 + dark px under ----------
print("=" * 100)
print("1. HEADER STAR blob (x559-674 y110-190): bbox + shadow beneath")
print("=" * 100)
for shot in ['01_hero.png', '02_skin0.png', '04_skin2.png', '06_full.png', '07_clear.png']:
    for tag, base in [('r12', R12), ('r13', R13)]:
        a = arr(base + shot)
        z = a[110:195, 540:700]
        r, g, b = z[..., 0], z[..., 1], z[..., 2]
        warm = ((r > 150) & (r > b + 50) & (g > 100) & (g < r))
        lbl, n = ndimage.label(warm)
        if n == 0:
            print(f"  {shot} {tag}: no star blob"); continue
        sizes = ndimage.sum(warm, lbl, range(1, n + 1))
        i = int(np.argmax(sizes)) + 1
        sl = ndimage.find_objects(lbl)[i - 1]
        y0, y1, x0, x1 = sl[0].start + 110, sl[0].stop + 110, sl[1].start + 540, sl[1].stop + 540
        # dark px below star bottom
        bel = a[y1+1:min(y1+22, 195), x0-4:x1+4]
        bL = lum(bel)
        side = lum(a[y1+1:min(y1+22, 195), max(540, x0-40):x0-6])
        sref = side.mean() if side.size else bL.mean()
        dark = (bL < sref - 12).sum()
        print(f"  {shot} {tag}: star {int(sizes[i-1])}px bbox x[{x0},{x1}] y[{y0},{y1}] "
              f"(h={y1-y0}) | below-zone mean={bL.mean():5.1f} ref={sref:5.1f} darkpx={dark}")

# ---------- 2. MICRO-TEXTURE shape, threshold 2, well(0,0) hero ----------
print("\n" + "=" * 100)
print("2. MICRO-TEXTURE shape: delta>2 map, well(0,0) 01_hero (84x84)")
print("=" * 100)
a12, a13 = arr(R12 + '01_hero.png'), arr(R13 + '01_hero.png')
bx, by = X0, Y0
d = lum(a13[by:by+CELL, bx:bx+CELL]) - lum(a12[by:by+CELL, bx:bx+CELL])
sym = {-3:'M',-2:'m',-1:'.',0:' ',1:'.',2:'+',3:'P'}
q = (d / 2.5).round().astype(int).clip(-3, 3)
for row in q:
    print(''.join(sym.get(v, '?') for v in row))
print(f"delta: mean={d.mean():.2f} min={d.min():.1f} max={d.max():.1f}")

# ---------- 3. VIGNETTE strict: compare far-from-structure px, corner wells vs center wells ----------
print("\n" + "=" * 100)
print("3. VIGNETTE strict: per-well mean delta (r13-r12), hero, empty wells only")
print("=" * 100)
grid = np.full((8, 8), np.nan)
for gy in range(8):
    for gx in range(8):
        bx, by = X0 + gx * CELL, Y0 + gy * CELL
        dd = np.abs(a13[by:by+CELL, bx:bx+CELL] - a12[by:by+CELL, bx:bx+CELL]).max()
        # empty well = low content AND changed (texture) -> measure mean delta
        m = lum(a13[by:by+CELL, bx:bx+CELL]) - lum(a12[by:by+CELL, bx:bx+CELL])
        grid[gy, gx] = m.mean()
print("mean-delta grid (r13-r12) all wells:")
for row in grid:
    print('  ' + ' '.join(f'{v:6.2f}' for v in row))
corner = np.nanmean([grid[0, 0], grid[0, 7], grid[7, 0], grid[7, 7]])
mid = np.nanmean(grid[3:5, 3:5])
print(f"corner wells mean-delta={corner:.3f}  center={mid:.3f}  (vignette would make corners ~-3..-8)")

# ---------- 4. Where did 07_clear change most? ----------
print("\n" + "=" * 100)
print("4. 07_clear: spatial distribution of change (r13 vs r12)")
print("=" * 100)
a12c, a13c = arr(R12 + '07_clear.png'), arr(R13 + '07_clear.png')
d = np.abs(a13c - a12c).max(axis=2)
H, W = d.shape
for yb in range(0, H, 120):
    band = d[yb:yb+120]
    pct = (band > 10).mean() * 100
    print(f"  y[{yb:4d},{yb+120:4d}]: {pct:5.1f}% changed  mean|d|={band.mean():6.2f}")

# ---------- 5. streak fill fraction & value sanity ----------
print("\n" + "=" * 100)
print("5. STREAK fill tip & scale: hero x136-342 of meter x128-596")
print("=" * 100)
a = arr(R13 + '01_hero.png')
prof = lum(a[1238:1252, 24:696]).mean(axis=0)
fill = np.where(prof > 100)[0]
print(f"fill cols x[{24+fill.min()},{24+fill.max()}] | head at x336-342 | track x352-596 | label x596-696")
pct = (fill.max() - 128) / (596 - 128) * 100
print(f"fill pct of track = {pct:.1f}%")

# ---------- 6. distinct colors in streak zone (strict quantize 4) ----------
print("\n6. streak zone distinct colors (quantize 4, x24-696 y1238-1252):")
for tag, base in [('r12', R12), ('r13', R13)]:
    a = arr(base + '01_hero.png')
    z = a[1238:1252, 24:696].astype(int)
    q = (z // 4) * 4
    flat = q[..., 0] * 65536 + q[..., 1] * 256 + q[..., 2]
    print(f"  {tag}: {len(np.unique(flat))} colors")

# ---------- 7. hero header: what changed overall (y<190) ----------
print("\n7. hero header y0-190 change census:")
d = np.abs(arr(R13 + '01_hero.png') - arr(R12 + '01_hero.png')).max(axis=2)
hd = d[0:190]
ys, xs = np.where(hd > 10)
print(f"  changed px={len(ys)} | bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]")
col_bins = {}
for x in xs:
    col_bins.setdefault(x // 60, 0)
    col_bins[x // 60] += 1
print(f"  x-histogram (60px bins): {dict(sorted(col_bins.items()))}")
