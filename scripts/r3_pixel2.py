from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'05_skin3.png').convert('RGB')).astype(int)
# Block ramp: take an occupied block, scan across it: expect 2 tones, hard steps.
# From cell map: block colors e.g. (241,144,75) orange at row2 col2-4; (255,132,123) red; (192,148,255) purple
# Scan a horizontal line inside a block: y=482 row, col1 (110-187)
row=a[482,110:190]
runs=[];prev=None;start=110
for x in range(110,190):
    t=tuple(int(v) for v in row[x])
    if prev is None: prev=t;continue
    if max(abs(t[i]-prev[i]) for i in range(3))>8:
        runs.append((start,x,tuple(int(v) for v in row[start])))
        start=x;prev=t
runs.append((start,190,tuple(int(v) for v in row[start])))
print('skin3 block row y482 x110-190 color runs:',runs)
# vertical scan inside block col x=150
col=a[193:833,150]
runs=[];prev=None;start=193
for y in range(193,833):
    t=tuple(int(v) for v in col[y])
    if prev is None: prev=t;continue
    if max(abs(t[i]-prev[i]) for i in range(3))>8:
        runs.append((start,y,tuple(int(v) for v in col[start])))
        start=y;prev=t
runs.append((start,833,tuple(int(v) for v in col[start])))
print('skin3 vertical scan x150 (long):')
for r in runs: print('  ',r)
