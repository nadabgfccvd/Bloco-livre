from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
# Check cell row boundaries: vertical gutters
isgut=(np.abs(a-np.array([24,32,46])).sum(2)<30)
# vertical gutter runs at column x=180 (inside horizontal gutter)
colg=isgut[:,180]
runs=[];s=None
for y in range(100,900):
    if colg[y] and s is None: s=y
    if not colg[y] and s is not None:
        if y-s>=4: runs.append((s,y))
        s=None
print('vertical gutter runs at x180:',runs)
# count: 8 cells → 9 horizontal gutters (incl borders)? runs len should be 9
# horizontal gutter runs at y=275 (a horizontal gutter row)
rowg=isgut[275,:]
runs2=[];s=None
for x in range(0,720):
    if rowg[x] and s is None: s=x
    if not rowg[x] and s is not None:
        if x-s>=4: runs2.append((s,x))
        s=None
print('horizontal gutter runs at y275:',runs2)
