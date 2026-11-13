from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
# 1x5 piece: x515-682 w=167 h=167?? That's a square-ish blob 167 wide AND tall. Measure precisely.
zone=a[880:1120,505:690]
# piece cell detection: find piece blocks: distinct bright colors
# scan rows of the piece region for color runs
for y in [925,950,1000,1050,1080]:
    row=a[y,505:690]
    runs=[];prev=None;start=505
    for x in range(505,690):
        t=tuple(row[x])
        if prev is None: prev=t;continue
        if max(abs(t[i]-prev[i]) for i in range(3))>12:
            runs.append((start,x,tuple(int(v) for v in row[start])))
            start=x;prev=t
    runs.append((start,690,tuple(int(v) for v in row[start])))
    print(f'y={y}: {runs}')
print()
# vertical extent at x=550
x=550
col=a[880:1120,x]
runs=[];prev=None;start=880
for y in range(880,1120):
    t=tuple(col[y])
    if prev is None: prev=t;continue
    if max(abs(t[i]-prev[i]) for i in range(3))>12:
        runs.append((start,y,tuple(int(v) for v in col[start])))
        start=y;prev=t
runs.append((start,1120,tuple(int(v) for v in col[start])))
print(f'x={550}: {runs}')
