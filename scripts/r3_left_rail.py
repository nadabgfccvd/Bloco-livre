from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
print('=== left rail x40-100, what is the gold thing? horizontal scan y=482, y=718 ===')
for y in [482,718,300,900,1000]:
    row=a[y,0:105]
    runs=[]
    prev=None;start=0
    for x in range(105):
        t=tuple(row[x])
        if prev is None: prev=t; continue
        if max(abs(t[i]-prev[i]) for i in range(3))>10:
            runs.append((start,x,tuple(int(v) for v in row[start])))
            start=x;prev=t
    runs.append((start,105,tuple(int(v) for v in row[start])))
    print(f'y={y}: {runs}')
print()
print('=== right rail x=720 scanline y=482 ===')
for y in [482,718]:
    row=a[y,615:720]
    runs=[]
    prev=None;start=615
    for x in range(615,720):
        t=tuple(row[x-615])
        if prev is None: prev=t; continue
        if max(abs(t[i]-prev[i]) for i in range(3))>10:
            runs.append((start,x,tuple(int(v) for v in a[y,start])))
            start=x;prev=t
    runs.append((start,720,tuple(int(v) for v in a[y,start])))
    print(f'y={y}: {runs}')
