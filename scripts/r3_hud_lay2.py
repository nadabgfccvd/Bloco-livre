from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
bgp=np.array([20,21,33])
# The score bar text: find bright text pixels within y105-170, x120-640
zone=a[105:170,120:640]
bright=(zone.sum(2)>450)
ys,xs=np.nonzero(bright)
print('text px count',len(ys))
# column histogram to find word boundaries
colh=bright.sum(0)
# print word runs (cols with >0)
runs=[];s=None
for i,v in enumerate(colh):
    if v>0 and s is None: s=i
    if v==0 and s is not None:
        if i-s>3: runs.append((120+s,120+i))
        s=None
print('word x-runs:',runs)
# row histogram per word
for x0,x1 in runs:
    sub=bright[:,x0-120:x1-120]
    rh=sub.sum(1)
    yy=np.nonzero(rh>0)[0]
    print(f'word x{x0}-{x1}: y{105+yy.min()}-{105+yy.max()} height={yy.max()-yy.min()+1} maxrow={rh.max()}')
# letter frequency (gaps inside words)
print()
print('=== letter gaps inside each word ===')
for x0,x1 in runs:
    sub=colh[x0-120:x1-120]
    gaps=[];s=None
    for i,v in enumerate(sub):
        if v==0 and s is None: s=i
        if v>0 and s is not None:
            if i-s>0: gaps.append((x0+s,x0+i,i-s))
            s=None
    print(f'word x{x0}-{x1} letter gaps:',gaps)
