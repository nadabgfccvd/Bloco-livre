#!/usr/bin/env python3
"""The 'band' y396..479: the row extents show a wedge whose top-right narrows downward-left.
This looks like a diagonal sweep/underlay. The claim says underlay centered cx, rows 466..698, center 582.
Our measurement: gold mass exists from y~390 to y~479 in a wedge; below y=480 in-board gold is the star ring.
Let's find the true banner: look for a horizontal band INSIDE 466..698 range on 07_clear.
Also verify what the dark holes are (letters?) — dark columns x 80..460 with ~1000 px per bin means
solid dark mass on the left half within the band bbox... that's not letters; likely unlit area.
Let me render crops for visual analysis and do a proper column profile of the whole gold zone.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png')

crops = {
  'celebration_top': (0, 0, 720, 200),        # rays + banner
  'board_crown': (0, 200, 720, 900),           # star crown inside board
  'board_crown_zoom': (60, 250, 660, 560),     # top half crown
  'tray_clear': (0, 950, 720, 1110),
  'hud_main': (0, 0, 720, 200),
  'streak_main': (0, 1118, 720, 1300),
}
for name, box in crops.items():
    im.crop(box).save(f'/tmp/critic_crops_r6/{name}.png')
    print('saved', name, box)

im1 = load('01_main_classic.png')
im1.crop((0, 0, 720, 200)).save('/tmp/critic_crops_r6/hud_main_classic.png')
im1.crop((0, 1118, 720, 1440)).save('/tmp/critic_crops_r6/streak_full_main.png')
im2 = load('06_full.png')
im2.crop((0, 0, 720, 900)).save('/tmp/critic_crops_r6/danger_full_top.png')
im2.crop((0, 1118, 720, 1440)).save('/tmp/critic_crops_r6/streak_full_danger.png')
for n in ['02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png']:
    load(n).crop((0, 190, 720, 870)).save(f'/tmp/critic_crops_r6/board_{n}')
    print('saved board crop', n)
# r5 vs r6 diff crop for celebration
im5 = load('07_clear.png', R5)
im5.crop((0, 0, 720, 900)).save('/tmp/critic_crops_r6/celebration_r5_top.png')
print('saved r5 celebration comparison')
import subprocess
print(subprocess.run(['ls','-la','/tmp/critic_crops_r6'],capture_output=True,text=True).stdout)
