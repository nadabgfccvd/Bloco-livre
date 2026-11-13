from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
calm=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
full=np.array(Image.open(base+'06_full.png').convert('RGB')).astype(int)

def zone_means(a,label):
    g=a[200:830,186:194].reshape(-1,3).mean(0)
    print(f'{label} gutter(186-194)=({g[0]:.1f},{g[1]:.1f},{g[2]:.1f})')
    fm=a[200:830,36:100].reshape(-1,3).mean(0)
    print(f'{label} left rail (board panel) mean=({fm[0]:.1f},{fm[1]:.1f},{fm[2]:.1f})')
    pbg=a[1240:1280,300:400].reshape(-1,3).mean(0)
    print(f'{label} page bg=({pbg[0]:.1f},{pbg[1]:.1f},{pbg[2]:.1f})')
    # outer border ring around board: x36-100 includes stars area though. use x=24-36 strip (between page bg and board panel)?
    ring=a[200:830,24:36].reshape(-1,3).mean(0)
    print(f'{label} x24-36 strip=({ring[0]:.1f},{ring[1]:.1f},{ring[2]:.1f})')
zone_means(calm,'CALM(02)')
print()
zone_means(full,'FULL(06)')
print()
# Count cells horizontally on a mid-row in calm shot
y=482
for arr,lab in [(calm,'calm'),(full,'full')]:
    row=arr[y]
    # gutter color detection: (24,32,46)
    isgut=(np.abs(row-np.array([24,32,46])).sum(1)<30)
    runs=[];s=None
    for x in range(100,700):
        if isgut[x] and s is None: s=x
        if not isgut[x] and s is not None:
            if x-s>=4: runs.append((s,x))
            s=None
    print(f'{lab} y{y} gutter runs:',runs)
