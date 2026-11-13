from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'05_skin3.png').convert('RGB')).astype(int)
def hr(y,x0,x1,thr=8):
    runs=[];prev=None;start=x0
    for x in range(x0,x1):
        t=tuple(int(v) for v in a[y,x])
        if prev is None: prev=t;continue
        if max(abs(t[i]-prev[i]) for i in range(3))>thr:
            runs.append((start,x,tuple(int(v) for v in a[y,start])))
            start=x;prev=t
    runs.append((start,x1,tuple(int(v) for v in a[y,start])))
    return runs
print('skin3 y482 block x110-190:')
for r in hr(482,110,190): print('  ',r)
print()
col=a[:,233]
runs=[];prev=None;start=180
for y in range(180,840):
    t=tuple(int(v) for v in col[y])
    if prev is None: prev=t;continue
    if max(abs(t[i]-prev[i]) for i in range(3))>8:
        runs.append((start,y,tuple(int(v) for v in col[start])))
        start=y;prev=t
runs.append((start,840,tuple(int(v) for v in col[start])))
print('skin3 vertical x233:')
for r in runs: print('  ',r)
