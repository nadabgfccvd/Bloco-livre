#!/usr/bin/env python3
"""R12 part M: spoke measurement from actual burst core in 07_clear.
Burst core approx x270-450 y230-345. Find bright core center, then measure ray widths along
rings. Also measure the clear banner (rows 358-460) and confetti (470-500)."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

im = load(R12 + '07_clear.png')
lum = im.mean(axis=2)
R, G, B = im[:,:,0], im[:,:,1], im[:,:,2]

# bright core: lum>230 rows 190..356
m = np.zeros_like(lum, dtype=bool)
m[190:357, :] = lum[190:357, :] > 235
ys, xs = np.where(m)
print("core pixels n=", len(ys), "rows", ys.min(), ys.max(), "cols", xs.min(), xs.max())
cx, cy = xs.mean(), ys.mean()
print("core centroid:", round(cx,1), round(cy,1))

# Use centroid as burst center
cx, cy = int(round(cx)), int(round(cy))

# measure ring occupancy for r in 60..130 at th=200
def ring_profile(r, th=200):
    n = 3600
    a = np.linspace(0, 2*np.pi, n, endpoint=False)
    hits = np.zeros(n, bool)
    for i, ang in enumerate(a):
        for d in (-2,-1,0,1,2):
            x = int(round(cx + (r+d)*np.cos(ang))); y = int(round(cy + (r+d)*np.sin(ang)))
            if 0 <= x < 720 and 0 <= y < 1440 and lum[y, x] > th:
                hits[i] = True; break
    frac = hits.mean()
    # runs
    runs = []
    i = 0
    while i < n:
        if hits[i]:
            j = i
            while j < n and hits[j]:
                j += 1
            runs.append((i, j)); i = j
        else:
            i += 1
    if len(runs) > 1 and runs[0][0] == 0 and runs[-1][1] == n:
        runs[-1] = (runs[-1][0], runs[-1][1]+runs[0][1]); runs = runs[1:]
    ch = [round((b-a)/n*2*np.pi*r,1) for a,b in runs]
    return frac, ch

for r in (80, 90, 100, 110, 120, 130):
    frac, ch = ring_profile(r)
    small = [c for c in ch if 2 < c <= 20]
    print(f"r={r}: frac={frac:.2f} runs={ch}")
    print(f"    spoke-like 2-20px: {sorted(small)} (n={len(small)}, mean={np.mean(small) if small else 0:.1f})")

# r11 07_clear same zone for comparison: was there a burst at all?
im11 = load(R11 + '07_clear.png')
lum11 = im11.mean(axis=2)
m11 = lum11[190:357, :] > 235
print("\nr11 core px n=", m11.sum())

# banner rows 358..460: is that the big gold band? measure its height and structure
band = lum[358:460, :]
print("banner rows 358-459 mean per row (first/last 10):")
for y in range(358, 460, 8):
    print(y, round(band[y-358, :].mean(),1))
