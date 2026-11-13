from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
for y in [925,950,1000,1050,1080]:
    row=a[y]
    runs=[];prev=None;start=505
    for x in range(505,690):
        t=tuple(int(v) for v in row[x])
        if prev is None: prev=t;continue
        if max(abs(t[i]-prev[i]) for i in range(3))>12:
            runs.append((start,x,tuple(int(v) for v in row[start])))
            start=x;prev=t
    runs.append((start,690,tuple(int(v) for v in row[start])))
    print(f'y={y}: {runs}')
print()
x=550
col=a[:,x]
runs=[];prev=None;start=880
for y in range(880,1120):
    t=tuple(int(v) for v in col[y])
    if prev is None: prev=t;continue
    if max(abs(t[i]-prev[i]) for i in range(3))>12:
        runs.append((start,y,tuple(int(v) for v in col[start])))
        start=y;prev=t
runs.append((start,1120,tuple(int(v) for v in col[start])))
print(f'x=550 vertical: {runs}')
