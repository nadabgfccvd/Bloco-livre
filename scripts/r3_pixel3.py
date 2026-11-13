from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'05_skin3.png').convert('RGB')).astype(int)
def hr(y,x0,x1,thr=8):
    row=a[y,x0:x1]
    runs=[];prev=None;start=x0
    for x in range(x0,x1):
        t=tuple(int(v) for v in row[x])
        if prev is None: prev=t;continue
        if max(abs(t[i]-prev[i]) for i in range(3))>thr:
            runs.append((start,x,tuple(int(v) for v in row[start])))
            start=x;prev=t
    runs.append((start,x1,tuple(int(v) for v in row[start])))
    return runs
print('skin3 y482 block x110-190:',hr(482,110,190))
print()
# vertical inside an orange block: col2 x center ~233, rows 281-352 contain block? Use x=233
col=a[:,233]
runs=[];prev=None;start=0
for y in range(180,840):
    t=tuple(int(v) for v in col[y])
    if prev is None: prev=t;continue
    if max(abs(t[i]-prev[i]) for i in range(3))>8:
        runs.append((start,y,tuple(int(v) for v in col[start])))
        start=y;prev=t
runs.append((start,840,tuple(int(v) for v in col[start])))
for r in runs: print('  ',r)
