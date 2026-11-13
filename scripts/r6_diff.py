#!/usr/bin/env python3
"""BAR unique colors: R6 238 vs R5 3 — that's the real delta! The R5 bar was a flat 3-color
strip; R6 bar has gradient + pips + label = 238 colors. Builder's '138 vs 19' probably counted
some sub-zone; directionally TRUE (massive color richness increase) but numbers differ.
Let's also do the danger diff crop r6 vs r5 06_full (whole image diff stats), and produce
final crops list. Then verify 'engine 24/24 + vmDemo' is not checkable from pixels (note it).
Also verify claim 'banner band #F6C445 with white hairline': we found NO F6C445 band anywhere;
white hairline only as HUD text rows. The gold wedge colors: (231,184,65) close to F6C445=246,196,69
(E67) — 231,184,65 is exactly #E7B841 — the band is E7B841-ish, not F6C445. PARTIAL.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from PIL import Image, ImageChops
import subprocess

# r6 vs r5 full danger diff
a = load('06_full.png'); b = load('06_full.png', R5)
diff = ImageChops.difference(a, b)
d = diff.load()
tot = 0; n = 0
for y in range(0, 1440, 4):
    for x in range(0, 720, 4):
        c = d[x,y]; tot += max(c); n += 1
print(f'r6 vs r5 06_full: mean max-channel diff = {tot/n:.1f}')

# celebration diff
a = load('07_clear.png'); b = load('07_clear.png', R5)
diff = ImageChops.difference(a, b); d = diff.load()
tot = 0
for y in range(0, 1440, 4):
    for x in range(0, 720, 4):
        c = d[x,y]; tot += max(c)
print(f'r6 vs r5 07_clear: mean max-channel diff = {tot/n:.1f}')

# save danger diff crop
Image.blend(a, b, 0.5).crop((0, 0, 720, 900)).save('/tmp/critic_crops_r6/danger_diff_blend.png')
print(subprocess.run(['ls', '/tmp/critic_crops_r6'], capture_output=True, text=True).stdout)
