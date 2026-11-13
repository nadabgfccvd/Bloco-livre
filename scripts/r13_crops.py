"""R13 forensic - PASS 5: visual crops for eyeballing + render page images."""
import numpy as np
from PIL import Image
import os

R12 = '/home/z/my-project/critic_shots/r12/'
R13 = '/home/z/my-project/critic_shots/r13/'
OUT = '/tmp/critic_crops_r13'
os.makedirs(OUT, exist_ok=True)

def crop(src, box, dst, scale=3):
    im = Image.open(src).convert('RGB').crop(box)
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    im.save(dst)
    print(dst, im.size)

# 1. Streak instrument (r13 vs r12) - hero
crop(R13 + '01_hero.png', (24, 1230, 696, 1260), f'{OUT}/01_streak_r13.png')
crop(R12 + '01_hero.png', (24, 1230, 696, 1260), f'{OUT}/01_streak_r12.png')
# 2. streak on clear screen
crop(R13 + '07_clear.png', (24, 1230, 696, 1260), f'{OUT}/07_streak_clear_r13.png')
# 3. Board corner w/ vignette + wells (top-left quadrant incl star)
crop(R13 + '01_hero.png', (24, 190, 360, 530), f'{OUT}/02_board_topleft_r13.png')
crop(R12 + '01_hero.png', (24, 190, 360, 530), f'{OUT}/02_board_topleft_r12.png')
# 4. Star cell closeup (0,1) in hero: x[24,108] y[274,360]
crop(R13 + '01_hero.png', (14, 270, 118, 366), f'{OUT}/03_star_r13.png')
crop(R12 + '01_hero.png', (14, 270, 118, 366), f'{OUT}/03_star_r12.png')
# 5. Confetti area on clear (top band)
crop(R13 + '07_clear.png', (0, 0, 720, 190), f'{OUT}/04_confetti_top_r13.png')
crop(R12 + '07_clear.png', (0, 0, 720, 190), f'{OUT}/04_confetti_top_r12.png')
# 6. Confetti bottom
crop(R13 + '07_clear.png', (0, 866, 720, 1000), f'{OUT}/05_confetti_bottom_r13.png')
# 7. tray
crop(R13 + '01_hero.png', (24, 860, 696, 1142), f'{OUT}/06_tray_r13.png')
# 8. header of hero
crop(R13 + '01_hero.png', (0, 0, 720, 190), f'{OUT}/08_header_r13.png')
# 9. clear screen full small
crop(R13 + '07_clear.png', (0, 0, 720, 1440), f'{OUT}/09_clear_full_r13.png', scale=1)
crop(R12 + '07_clear.png', (0, 0, 720, 1440), f'{OUT}/09_clear_full_r12.png', scale=1)

# also full hero at 1x for context
crop(R13 + '01_hero.png', (0, 0, 720, 1440), f'{OUT}/10_hero_full_r13.png', scale=1)
crop(R13 + '03_skin1.png', (0, 0, 720, 1440), f'{OUT}/11_skin1_full_r13.png', scale=1)
crop(R13 + '06_full.png', (0, 0, 720, 1440), f'{OUT}/12_fullboard_full_r13.png', scale=1)
print("done")
