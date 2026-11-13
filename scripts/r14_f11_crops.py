#!/usr/bin/env python3
"""R14 pass 11: save crops for viewing + final measurements (skin variety, hero top, y535 line A/B)."""
import os
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"
OUT = "/tmp/critic_crops_r14"
os.makedirs(OUT, exist_ok=True)

def save_crop(src, box, name):
    im = Image.open(src).convert("RGB")
    im.crop(box).save(os.path.join(OUT, name))
    print("saved", name, box)

# 1. star + gap + band + shadow (clear shot)
save_crop(os.path.join(R14,"07_clear.png"), (240, 180, 560, 400), "r14_star_gap_shadow.png")
# 2. corner vignette wells (hero)
save_crop(os.path.join(R14,"01_hero.png"), (24, 190, 240, 360), "r14_corner_wells.png")
# 3. streak strip with ticks (hero)
save_crop(os.path.join(R14,"01_hero.png"), (100, 1200, 620, 1290), "r14_streak_ticks.png")
# 4. confetti zone (clear)
save_crop(os.path.join(R14,"07_clear.png"), (0, 120, 720, 350), "r14_confetti.png")
# 5. r13 star for A/B
save_crop(os.path.join(R13,"07_clear.png"), (240, 180, 560, 400), "r13_star_gap.png")
# 6. r13 confetti A/B
save_crop(os.path.join(R13,"07_clear.png"), (0, 120, 720, 350), "r13_confetti.png")
# 7. r13 corner wells A/B
save_crop(os.path.join(R13,"01_hero.png"), (24, 190, 240, 360), "r13_corner_wells.png")
# 8. board+HUD composite (hero)
save_crop(os.path.join(R14,"01_hero.png"), (0, 1150, 720, 1300), "r14_hud.png")
