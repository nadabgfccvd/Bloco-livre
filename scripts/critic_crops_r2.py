#!/usr/bin/env python3
"""Round-2 critic crops for Bloco Livre. Generates >=12 detail views from the 7 r2 screenshots."""
from PIL import Image, ImageFilter
import os

SRC = '/home/z/my-project/critic_shots/r2'
OUT = '/tmp/critic_crops_r2'
os.makedirs(OUT, exist_ok=True)

# Layout anchors from forensic vision maps (720x1440):
# wordmark 35-100, HUD 115-200, board 200-890 (x 15-705), tray 905-1100, footer 1285-1350, credit 1405-1435
B = (15, 200, 705, 890)      # board box

def crop(src, name, box, scale=1):
    im = Image.open(os.path.join(SRC, src)).convert('RGB')
    c = im.crop(box)
    if scale != 1:
        c = c.resize((c.width*scale, c.height*scale), Image.NEAREST if scale >= 2 else Image.BILINEAR)
    p = os.path.join(OUT, name)
    c.save(p)
    print(f'{name:34s} {c.size}  <- {src} {box}')

# 1-4: board close-up per skin (top-left quadrant + center, moderate zoom)
crop('02_skin0.png', 'A_board_classic.png',      (15, 200, 400, 560))
crop('03_skin1.png', 'B_board_neon.png',         (15, 200, 400, 560))
crop('04_skin2.png', 'C_board_gema.png',         (15, 200, 400, 560))
crop('05_skin3.png', 'D_board_pixel.png',        (15, 200, 400, 560))

# 5: pixel-skin single-cell super close-up 3x nearest (aliasing audit)
crop('05_skin3.png', 'E_pixel_cell_3x.png',     (60, 240, 260, 440), scale=3)

# 6: classic block edge 3x (bevel/gloss audit)
crop('02_skin0.png', 'F_classic_block_3x.png',  (100, 480, 320, 700), scale=3)

# 7: neon block edge 3x
crop('03_skin1.png', 'G_neon_block_3x.png',      (100, 480, 320, 700), scale=3)

# 8: gem block facet 3x
crop('04_skin2.png', 'H_gema_block_3x.png',      (100, 480, 320, 700), scale=3)

# 9: HUD crop (both scores + trophy)
crop('01_main_classic.png', 'I_hud.png',         (0, 105, 720, 210))

# 10: tray crop (full-width, incl. ghost slots)
crop('06_full.png', 'J_tray.png',               (0, 895, 720, 1115))

# 11: footer buttons crop
crop('01_main_classic.png', 'K_footer.png',     (0, 1275, 720, 1360))

# 12: celebration banner close-up
crop('07_clear.png', 'L_clear_banner.png',      (0, 380, 720, 600))

# 13: celebration confetti top band
crop('07_clear.png', 'M_clear_confetti.png',    (0, 0, 720, 120))

# 14: wordmark + tagline
crop('01_main_classic.png', 'N_wordmark.png',  (0, 20, 720, 110))

# 15: credit line
crop('01_main_classic.png', 'O_credit.png',     (0, 1395, 720, 1440))

# 16: full-board danger frame crop (06) — board + surrounding bg for tint audit
crop('06_full.png', 'Q_full_frame.png',         (0, 180, 720, 920))

# 17: board bottom edge + shadow zone (classic) — depth audit
crop('02_skin0.png', 'P_shadow_zone.png',       (0, 860, 720, 940), scale=2)

# 18: dead-band evidence crop
crop('02_skin0.png', 'R_deadband.png',         (0, 1100, 720, 1300))

print('done')
