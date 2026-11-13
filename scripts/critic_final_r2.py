#!/usr/bin/env python3
"""Final checks: star-ring distribution in 07, tray bounds + piece overflow extent in 01."""
from PIL import Image

SRC = '/home/z/my-project/critic_shots/r2'

# Star ring distribution: bucket the bright pixels by y to see if they form a ring around board center
im7 = Image.open(f'{SRC}/07_clear.png').convert('RGB')
buckets = {}
for y in range(205, 890, 2):
    n = 0
    for x in range(20, 700, 2):
        r, g, b = im7.getpixel((x, y))
        if (r > 220 and g > 200 and b < 160) or (r > 235 and g > 235 and b > 235):
            n += 1
    if n: buckets[y] = n
ys = sorted(buckets)
print('bright-pixel y-distribution in board area (y:count):')
for y in ys:
    if buckets[y] > 5: print(f'  y={y}: {buckets[y]}')
print('total rows with bright pixels:', len(ys), 'peak rows:', sorted(buckets.items(), key=lambda kv: -kv[1])[:5])

# Confetti distribution across whole screen (rows 0-1440)
conf_rows = {}
for y in range(0, 1440, 4):
    n = 0
    for x in range(0, 720, 4):
        r, g, b = im7.getpixel((x, y))
        mx, mn = max(r, g, b), min(r, g, b)
        if mx > 150 and (mx - mn) > 60: n += 1
    if n > 3: conf_rows[y] = n
print()
print('confetti rows (y:count) sample:', list(conf_rows.items())[:12], '... total active rows:', len(conf_rows))

# Tray bounds in 01: find panel edges by scanning column x=360 for panel-like luminance shift
im1 = Image.open(f'{SRC}/01_main_classic.png').convert('RGB')
print()
print('col x=360 RGB from y=860 to 1200 (step 5):')
for y in range(860, 1201, 5):
    print(f'  y={y}: {im1.getpixel((360, y))}', end='')
    if (y//5) % 4 == 3: print()
print()
# extent of orange piece in 01
x_lo, x_hi, y_lo, y_hi = 9999, 0, 9999, 0
for y in range(850, 1250):
    for x in range(0, 720):
        r, g, b = im1.getpixel((x, y))
        if r > 180 and g > 120 and b < 120:
            x_lo, x_hi = min(x_lo, x), max(x_hi, x)
            y_lo, y_hi = min(y_lo, y), max(y_hi, y)
print('orange piece bbox in 01: x', x_lo, '-', x_hi, ' y', y_lo, '-', y_hi, f'({x_hi-x_lo}x{y_hi-y_lo}px)')
