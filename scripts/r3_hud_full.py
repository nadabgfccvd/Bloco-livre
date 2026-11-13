from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
# full-width word map across HUD rows using bright threshold
zone=a[0:170,0:720]
bright=(zone.sum(2)>450)
colh=bright.sum(0)
runs=[];s=None
for i,v in enumerate(colh):
    if v>0 and s is None: s=i
    if v==0 and s is not None:
        if i-s>3: runs.append((s,i))
        s=None
print('bright word x-runs across HUD:',runs)
for x0,x1 in runs:
    sub=bright[:,x0:x1]
    yy=np.nonzero(sub.any(1))[0]
    print(f'  x{x0}-{x1}: y{yy.min()}-{yy.max()} h={yy.max()-yy.min()+1}')
print()
# lower threshold for dim text (score numerals maybe dimmer)
zone2=a[0:170,0:720]
dim=((zone2.sum(2)>240)&(zone2.sum(2)<=450))
colh2=dim.sum(0)
runs2=[];s=None
for i,v in enumerate(colh2):
    if v>0 and s is None: s=i
    if v==0 and s is not None:
        if i-s>3: runs2.append((s,i))
        s=None
print('dim word runs:',runs2)
for x0,x1 in runs2:
    sub=dim[:,x0:x1]
    yy=np.nonzero(sub.any(1))[0]
    print(f'  x{x0}-{x1}: y{yy.min()}-{yy.max()} h={yy.max()-yy.min()+1}')
