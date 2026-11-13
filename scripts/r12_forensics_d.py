#!/usr/bin/env python3
"""R12 part D: locate burst center in 07_clear, verify star geometry claim, make crops."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

im7 = load(R12 + '07_clear.png')
lum7 = im7.mean(axis=2)

# find burst: very bright pixels in board area
ys, xs = np.where(lum7 > 200)
print("bright>200: n=", len(ys))
if len(ys):
    print("rows", ys.min(), ys.max(), "cols", xs.min(), xs.max())
    # exclude HUD text (y<190)
    m = ys > 190
    print("board-only rows", ys[m].min(), ys[m].max(), "cols", xs[m].min(), xs[m].max())
    print("centroid:", xs[m].mean(), ys[m].mean())

# r11 vs r12 in 07_clear: where did it change?
a = load(R11 + '07_clear.png'); b = load(R12 + '07_clear.png')
d = np.abs(a-b).mean(axis=2)
ys2, xs2 = np.where(d > 6)
if len(ys2):
    print("07_clear changed rows", ys2.min(), ys2.max(), "cols", xs2.min(), xs2.max())

# --------- STAR geometry in hero (per claim: body y243-347, band top y354, gap 7) ---------
imh = load(R12 + '01_hero.png')
lumh = imh.mean(axis=2)

# The star sits on dark header bg (lum ~34-75). Find bright pixels in x 260..460, y 230..355
sub = lumh[225:360, 240:480]
th = 100
ys3, xs3 = np.where(sub > th)
if len(ys3):
    ylo, yhi = 225+ys3.min(), 225+ys3.max()
    xlo, xhi = 240+xs3.min(), 240+xs3.max()
    print(f"\nHERO star-ish bright>100 rows {ylo}..{yhi} cols {xlo}..{xhi}")
else:
    print("\nno bright star pixels >100 in that window")

# Column band: find where the horizontal band begins. Look at rows 300..470 for a row where
# a wide horizontal strip (x 40..680) is bright
print("\nband search (frac of cols 40-680 with lum>100):")
for y in range(280, 470, 2):
    frac = (lumh[y, 40:680] > 100).mean()
    if frac > 0.3:
        print(y, round(frac,2))

# tray top per geometry: tray panel y~860-1142
print("\n=== CROPS ===")
crops = {
    'hero_header_star_band.png': (0, 150, 720, 470),       # star + band + HUD
    'hero_tray_gradient.png':   (0, 830, 720, 960),        # tray rim gradient
    'clear_burst.png':          (120, 150, 620, 700),      # burst region
    'hero_full_board.png':      (0, 0, 720, 1300),
}
for nm, box in crops.items():
    src = R12 + ('07_clear.png' if 'clear' in nm or 'burst' in nm else '01_hero.png')
    Image.open(src).crop(box).save('/tmp/critic_crops_r12/' + nm)
    print("saved", nm, box)

# also crop same regions from r11 for visual A/B
Image.open(R11+'01_hero.png').crop((0, 830, 720, 960)).save('/tmp/critic_crops_r12/r11_hero_tray_gradient.png')
Image.open(R11+'01_hero.png').crop((0, 150, 720, 470)).save('/tmp/critic_crops_r12/r11_hero_header_star_band.png')
print("saved r11 A/B crops")
