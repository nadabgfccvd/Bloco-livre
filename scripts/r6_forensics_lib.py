#!/usr/bin/env python3
"""R6 brutal art-director forensics: PIL-only pixel measurements (no rendering available)."""
import os, sys, math, json
from collections import Counter
from PIL import Image

R6 = '/home/z/my-project/critic_shots/r6'
R5 = '/home/z/my-project/critic_shots/r5'
CROPS = '/tmp/critic_crops_r6'
os.makedirs(CROPS, exist_ok=True)

def load(name, root=R6):
    return Image.open(os.path.join(root, name)).convert('RGB')

def px(im):
    return im.load()

def clamp(v): return max(0, min(255, v))

def lum(p): return 0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2]

def hue_deg(p):
    r, g, b = [v/255 for v in p]
    mx, mn = max(r,g,b), min(r,g,b)
    d = mx - mn
    if d == 0: return None, 0
    if mx == r: h = 60*(((g-b)/d) % 6)
    elif mx == g: h = 60*(((b-r)/d) + 2)
    else: h = 60*(((r-g)/d) + 4)
    return h, d

def is_goldish(p, tol=42):
    r, g, b = p
    return r > 150 and g > 110 and b < 160 and r > b + 40 and g > b + 20 and abs(r - g) < 90

def is_cyanish(p):
    r, g, b = p
    return g > 120 and b > 120 and b > r + 40 and g > r + 30

def stats(im, box):
    im2 = im.crop(box)
    w, h = im2.size
    data = list(im2.getdata())
    lums = [lum(p) for p in data]
    n = len(lums)
    return {
        'box': box, 'n': n,
        'mean_lum': sum(lums)/n,
        'p10': sorted(lums)[int(n*0.1)],
        'p90': sorted(lums)[int(n*0.9)],
        'gold_px': sum(1 for p in data if is_goldish(p)),
        'cyan_px': sum(1 for p in data if is_cyanish(p)),
        'warm_px': sum(1 for p in data if p[0] > p[2] + 25),
        'cool_px': sum(1 for p in data if p[2] > p[0] + 25),
        'top_colors': Counter(data).most_common(6),
    }

def col_profile(im, x0, x1, y0, y1, label):
    """Average color of a rect region."""
    p = px(im)
    tot = [0,0,0]; n = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = p[x, y]; tot[0]+=c[0]; tot[1]+=c[1]; tot[2]+=c[2]; n+=1
    return (label, tuple(round(t/n,1) for t in tot), n) if n else (label, None, 0)

def scanline_lum(im, y, x0=0, x1=None):
    p = px(im)
    if x1 is None: x1 = im.size[0]
    vals = [lum(p[x, y]) for x in range(x0, x1)]
    return sum(vals)/len(vals)

def occupancy_grid(im, grid_box, gx=8, gy=8, bg_test=None):
    """Detect which cells of the board are 'filled' by comparing each cell to the empty-well color."""
    x0, y0, x1, y1 = grid_box
    cw, ch = (x1-x0)/gx, (y1-y0)/gy
    p = px(im)
    filled = 0; cells = []
    for gy_i in range(gy):
        row = ''
        for gx_i in range(gx):
            cx0 = int(x0 + gx_i*cw); cy0 = int(y0 + gy_i*ch)
            # sample center patch of the cell
            rs=gs=bs=n=0
            for dy in range(int(cy0+ch*0.3), int(cy0+ch*0.75)):
                for dx in range(int(cx0+cw*0.3), int(cx0+cw*0.75)):
                    c = p[dx, dy]; rs+=c[0]; gs+=c[1]; bs+=c[2]; n+=1
            mean = (rs/n, gs/n, bs/n) if n else (0,0,0)
            # a cell is "filled" if it deviates strongly from dark empty well
            dev = abs(mean[0]-20)+abs(mean[1]-22)+abs(mean[2]-32)
            f = dev > 40
            cells.append((gx_i, gy_i, mean, f))
            filled += f
            row += '#' if f else '.'
        print('   ', row)
    return filled, cells

def dump_json(obj, path):
    with open(path, 'w') as f:
        json.dump(obj, f, indent=1, default=str)

if __name__ == '__main__':
    im = load('01_main_classic.png')
    w, h = im.size
    # coarse luminance map by rows/cols to find UI zones
    print('== row luminance profile (every 40px) ==')
    for y in range(0, h, 40):
        print(f'y={y:4d} lum={scanline_lum(im, y):6.1f}')
