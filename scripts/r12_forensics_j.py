#!/usr/bin/env python3
"""R12 part J: resolve header LEFT column (x26-185) — is that a column of currency/HUD?
Map HUD text at top. Then identify star: probably ABOVE band centered x360 as pale-blue motif?
Scan x=360 rows 196-360 for ANY non-flat structure. Also map x 619-692."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

imh = load(R12 + '01_hero.png')
R, G, B = imh[:,:,0], imh[:,:,1], imh[:,:,2]

# LEFT gold column x26-185: what is it? sample colors
print("LEFT column sample colors (x=100, y 196..356 step 8):")
for y in range(196, 360, 8):
    print(y, (R[y,100], G[y,100], B[y,100]), "x=150:", (R[y,150], G[y,150], B[y,150]))

# Row 221-264 x26-185 and 280-348: two blocks. These are HUD score/level boxes?
# Check text-like variance in those blocks vs flat fill
box1 = imh[221:265, 26:186]
print("\nbox1 y221-264 x26-185 unique colors:", len(np.unique(box1.reshape(-1,3), axis=0)))
box2 = imh[280:349, 26:186]
print("box2 y280-348 unique colors:", len(np.unique(box2.reshape(-1,3), axis=0)))

# The star claim: center x360. What is above the band at x300-420, y230-355?
print("\n=== x=360, y230..356 full color dump (every 4) ===")
for y in range(230, 360, 4):
    print(y, (R[y,360], G[y,360], B[y,360]))

# x 619-692 cluster rows?
gold = (R > 200) & (G > 150) & (B < 200) & (R - B > 80)
ys, xs = np.where(gold)
m = (ys >= 190) & (ys < 365) & (xs >= 620)
print("\nRIGHT cluster rows:", sorted(set(ys[m])) if m.sum() else "none")
m2 = (ys >= 190) & (ys < 365) & (xs < 200) & (ys >= 264) & (ys < 280)
print("gap rows 264-280 left:", sorted(set(ys[(ys>=264)&(ys<280)&(xs<200)])))
