#!/usr/bin/env python3
"""Objective pixel measurements for Round-2 claim verification."""
from PIL import Image
import colorsys

SRC = '/home/z/my-project/critic_shots/r2'

def px(img, x, y): return img.getpixel((x, y))
def avg(img, x0, y0, x1, y1, step=2):
    n = r = g = b = 0
    for y in range(y0, y1, step):
        for x in range(x0, x1, step):
            p = img.getpixel((x, y)); r += p[0]; g += p[1]; b += p[2]; n += 1
    return (r//n, g//n, b//n)
def hue_deg(rgb):
    h, l, s = colorsys.rgb_to_hls(*(c/255 for c in rgb))
    return round(h*360), round(s*100), round(l*100)

# ---------- 1. DANGER TINT: compare 06_full vs 02_skin0 ----------
print('=== DANGER TINT AUDIT (06_full vs 02_skin0) ===')
for name in ['02_skin0', '06_full']:
    im = Image.open(f'{SRC}/{name}.png').convert('RGB')
    frame = avg(im, 10, 200, 710, 215)          # board top frame strip
    frameL = avg(im, 10, 200, 25, 890)          # left frame strip
    bg_top = avg(im, 0, 0, 720, 30)             # background top
    bg_side = avg(im, 0, 400, 12, 800)          # background beside board
    empty_cell = avg(im, 40, 640, 80, 680)      # try an empty-ish cell area (bottom-left)
    print(f'{name}: frameTop{hue_deg(frame)} frameL{hue_deg(frameL)} bgTop{hue_deg(bg_top)} bgSide{hue_deg(bg_side)} cellProbe{hue_deg(empty_cell)} raw={frame}')

# also compare same frame rows between the two shots directly
im02 = Image.open(f'{SRC}/02_skin0.png').convert('RGB')
im06 = Image.open(f'{SRC}/06_full.png').convert('RGB')
d = [abs(im06.getpixel((x,207))[i]-im02.getpixel((x,207))[i]) for x in range(20,700,10) for i in range(3)]
print('frame top strip |06-02| avg diff:', sum(d)/len(d), ' max:', max(d))
d2 = [abs(im06.getpixel((x,3))[i]-im02.getpixel((x,3))[i]) for x in range(0,720,10) for i in range(3)]
print('bg top strip |06-02| avg diff:', sum(d2)/len(d2), ' max:', max(d2))

# ---------- 2. PIXEL SKIN: empty cell color + corner profile ----------
print()
print('=== PIXEL SKIN EMPTY CELL (05_skin3) ===')
im5 = Image.open(f'{SRC}/05_skin3.png').convert('RGB')
# scan row y=230 (inside board, top rows empty) across cells
row = [im5.getpixel((x, 230)) for x in range(20, 700, 6)]
uniq = sorted(set(row))
print('y=230 sampled colors:', uniq[:8], '... total', len(uniq))
print('empty-cell area hue/sat/lum:', hue_deg(avg(im5, 60, 215, 340, 260)))
print('board interior bg (between cells):', hue_deg(avg(im5, 40, 202, 680, 216)))
# corner rounding probe: take an empty cell ~ (60..130, 215..280): walk diagonal
c = avg(im5, 70, 225, 130, 285)
print('one empty cell avg:', c, hue_deg(c))

# ---------- 3. BOARD SHADOW: luminance profile below board bottom ----------
print()
print('=== BOARD BOTTOM SHADOW PROFILE (02_skin0) ===')
for y in [870, 880, 890, 900, 905, 915, 930, 950, 1000, 1060]:
    print(f'y={y}: L avg =', avg(im02, 100, y, 620, y+1, 4))
print('=== same for neon (03) ===')
im3 = Image.open(f'{SRC}/03_skin1.png').convert('RGB')
for y in [880, 895, 905, 940]:
    print(f'y={y}:', avg(im3, 100, y, 620, y+1, 4))

# ---------- 4. CELEBRATION: confetti + banner + flash presence ----------
print()
print('=== CELEBRATION (07_clear) ===')
im7 = Image.open(f'{SRC}/07_clear.png').convert('RGB')
# confetti = bright saturated pixels in top 140px
sat_count = 0; total = 0
for y in range(0, 140, 2):
    for x in range(0, 720, 2):
        r, g, b = im7.getpixel((x, y)); total += 1
        mx, mn = max(r, g, b), min(r, g, b)
        if mx > 150 and (mx - mn) > 60: sat_count += 1
print(f'bright saturated pixels in top band: {sat_count}/{total} = {100*sat_count/total:.1f}%')
# banner: find the cyan ribbon band ~y430-550
band = avg(im7, 0, 430, 720, 550)
print('banner band avg:', band, hue_deg(band))
# star ring: sample ring region around board center — count bright yellow/white pixels in annulus
cx, cy = 360, 545
ring_bright = 0
for y in range(205, 890, 3):
    for x in range(20, 700, 3):
        r, g, b = im7.getpixel((x, y))
        ddx, ddy = x - cx, y - cy
        dist = (ddx*ddx + ddy*ddy) ** 0.5
        if 150 < dist < 260 and r > 200 and g > 200: ring_bright += 1
print('bright white-ish pixels in board-center annulus r150-260:', ring_bright)
# flash: check whether background got lighter overall vs 02
print('bg top 07:', avg(im7, 0, 0, 720, 30), ' vs 02:', avg(im02, 0, 0, 720, 30))

# ---------- 5. DEAD SPACE % of screen ----------
print()
print('=== DEAD SPACE % (y1120-1285 flat?) ===')
im1 = Image.open(f'{SRC}/01_main_classic.png').convert('RGB')
for name, im in [('01', im1), ('02', im02), ('07', im7)]:
    band = avg(im, 0, 1120, 720, 1285)
    ys = [y for y in range(1100, 1300, 2) if max(abs(im.getpixel((360, y))[i]-band[i]) for i in range(3)) < 8]
    print(f'{name}: dead band avg {band} rows within tolerance: {len(ys)*2}px of 200px band')

# ---------- 6. VIGNETTE check: corner vs center brightness ----------
print()
print('=== VIGNETTE (01 main) ===')
tl = avg(im1, 5, 5, 60, 60); ctr = avg(im1, 300, 640, 420, 760); br = avg(im1, 660, 1380, 715, 1435)
print('corner TL:', tl, 'center:', ctr, 'corner BR:', br)
