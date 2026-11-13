from PIL import Image
import numpy as np
base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'07_clear.png').convert('RGB')).astype(int)
s0=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)

# 1) confetti count: small bright clusters in top HUD zone y0-190 & board ring
bright=(a.sum(2)>450)
mask=bright.copy(); mask[190:,:]=False
ys,xs=np.nonzero(mask)
pts=set(zip(xs.tolist(),ys.tolist()))
import collections
seen=set();comps=[]
for p in list(pts):
    if p in seen: continue
    q=collections.deque([p]);comp=[];seen.add(p)
    while q:
        x,y=q.popleft();comp.append((x,y))
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                n=(x+dx,y+dy)
                if n in pts and n not in seen: seen.add(n);q.append(n)
    comps.append(comp)
comps=[c for c in comps if 4<len(c)<400]
print('confetti-like clusters y0-190:',len(comps),'sizes',sorted(len(c) for c in comps)[:40])
cent=[(int(np.mean([p[0] for p in c])),int(np.mean([p[1] for p in c]))) for c in comps]
print('centroids:',cent[:30])

# 2) banner text: what does it say? bright text y1055-1090 x-range
zone=a[1050:1095,:]
b=(zone.sum(2)>420)
ys,xs=np.nonzero(b)
print('banner bright bbox: x',xs.min(),xs.max(),'y',1050+ys.min(),1050+ys.max())

# 3) danger HUD score difference (06 vs 02 numerals)
full=np.array(Image.open(base+'06_full.png').convert('RGB')).astype(int)
for arr,lab in [(s0,'calm'),(full,'full')]:
    z=arr[108:170,507:620]
    br=(z.sum(2)>450)
    ys,xs=np.nonzero(br)
    print(f'{lab} score numeral bbox y{108+ys.min()}-{108+ys.max()} x{507+xs.min()}-{507+xs.max()} h={ys.max()-ys.min()+1}')

# 4) tray piece scale: 1x4 green vertical = width 53px vs board cell 76px. ratio
print('board cell width ~76px (col run 26-102), tray piece cell width=53px → scale=0.70')
# 5) count tray pieces in 07 (from ascii: left 1 piece x114-182 70px 2x2?, mid x326-394 70px, right x515-682 green big)
# tray in 07:
bright7=(a.sum(2)>200)
tz=bright7[880:1120,:]
colh=tz.sum(0)
runs=[];s=None
for i,v in enumerate(colh):
    if v>3 and s is None: s=i
    if v<=3 and s is not None:
        if i-s>10: runs.append((s,i))
        s=None
print('07 tray piece x-runs:',runs)

# 6) trophy/right HUD in 07 vs 02: star trophy colors y124-152
print('07 trophy px y124-152 x648-675:',a[140,660],a[138,670],s0[140,660])

# 7) empty cell "well" structure: measure top inner shadow and bottom rim on empty cell (col0,row1)
x0,x1=26,102; y0,y1=281,352
cx=64; 
prof=[]
for dy in range(0,71,5):
    m=s0[y0+dy,cx-10:cx+10].reshape(-1,3).mean(0)
    prof.append((y0+dy,tuple(np.round(m,0))))
print('empty cell vertical profile (col0,row1):')
for p in prof: print('  ',p)
