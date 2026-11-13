from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'07_clear.png').convert('RGB')).astype(int)
s0=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)

print('=== 1) STAR RING: gold clusters in ring zone around board (exclude board cells x26-694 y193-833, exclude tray y880+, exclude HUD y<190) ===')
# ring zone = board vertical span y190-840, x outside cells: x0-26 & x694-720 is thin; claim radius cell*4.6=336 → circle would extend beyond board edges.
gold=(a[:,:,0]>200)&(a[:,:,1]>150)&(a[:,:,2]<180)
mask=gold.copy()
mask[:190,:]=False; mask[840:,:]=False
mask[:,26:695]=False  # outside board horizontally only
ys,xs=np.nonzero(mask)
print('gold px outside board cols within y190-840:',len(ys))
# Also count star clusters INSIDE board region that are NOT solid blocks: small gold clusters < 400px
zone=gold.copy()
zone[:190,:]=False; zone[840:,:]=False; zone[:,:26]=False; zone[:,695:]=False
ys,xs=np.nonzero(zone)
pts=set(zip(xs.tolist(),ys.tolist()))
import collections
comps=[]
seen=set()
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
comps=[c for c in comps if len(c)>15]
print(f'gold clusters y190-840 (inside board box): {len(comps)} sizes={[len(c) for c in comps][:25]}')

print()
print('=== 2) BANNER + tracking: letter gap analysis ===')
# wordmark letters y29-76 from skin0: bright px columns
zone=s0[29:80,150:520]
bright=(zone.sum(2)>450)
colh=bright.sum(0)
gaps=[];s=None
for i,v in enumerate(colh):
    if v==0 and s is None: s=i
    if v>0 and s is not None:
        if i-s>0: gaps.append(i-s)
        s=None
gaps=[g for g in gaps if g<25]
print('wordmark letter gaps(px):',gaps,'mean=',np.mean(gaps) if gaps else 0,'median=',np.median(gaps) if gaps else 0)
# letter stroke width: runs of bright
runs=[];s=None
for i,v in enumerate(colh):
    if v>0 and s is None: s=i
    if v==0 and s is not None:
        if i-s>2: runs.append(i-s)
        s=None
print('wordmark stroke widths(px):',runs)
# celebration banner y1055-1090
zone2=a[1055:1095,:]
b2=(zone2.sum(2)>450)
colh2=b2.sum(0)
runs2=[];s=None
for i,v in enumerate(colh2):
    if v>0 and s is None: s=i
    if v==0 and s is not None:
        if i-s>2: runs2.append((i,i-s))
        s=None
print('celebration banner letter strokes (x,w):',runs2[:30])
gaps2=[];s=None
for i,v in enumerate(colh2):
    if v==0 and s is None: s=i
    if v>0 and s is not None:
        if i-s>0: gaps2.append(i-s)
        s=None
gaps2=[g for g in gaps2 if g<25]
print('banner letter gaps(px):',gaps2,'mean=',np.mean(gaps2) if gaps2 else 0)

print()
print('=== 3) RECORDE vs PONTOS numeral heights (skin0 HUD) ===')
# left labels x24-119: letters y? measure per-char heights via bright mask
zl=s0[100:180,20:125]
bl=(zl.sum(2)>450)
rh=bl.sum(1)
yy=np.nonzero(rh>0)[0]
print(f'RECORDE-side left block: y{100+yy.min()}-{100+yy.max()} h={yy.max()-yy.min()+1}')
# right numerals x507-619
zr=s0[100:180,500:625]
br=(zr.sum(2)>450)
rh2=br.sum(1)
yy2=np.nonzero(rh2>0)[0]
print(f'PONTOS-side right block: y{100+yy2.min()}-{100+yy2.max()} h={yy2.max()-yy2.min()+1}')

print()
print('=== 4) AO: empty cells with occupied above (skin0) ===')
colx=[(26,102),(110,187),(195,271),(280,356),(364,440),(449,525),(533,610),(618,694)]
rowy=[(193,267),(281,352),(365,436),(449,522),(533,605),(618,690),(703,774),(787,833)]
grid=[]
for i in range(8):
    r=[]
    for j in range(8):
        x0,x1=colx[j]; y0,y1=rowy[i]
        cx=(x0+x1)//2; cy=(y0+y1)//2
        m=s0[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).mean(0)
        r.append('X' if m.mean()>70 else '.')
    grid.append(r)
for r in grid: print('  '+''.join(r))
print('  (X=occupied)')
# top band (y0+6..y0+18) vs mid for empty cells, split by occupied-above
res={}
for i in range(8):
    for j in range(8):
        if grid[i][j]=='.':
            x0,x1=colx[j]; y0,y1=rowy[i]
            cx=(x0+x1)//2
            top=s0[y0+4:y0+16,cx-12:cx+12].reshape(-1,3).mean(0)
            mid=s0[(y0+y1)//2-6:(y0+y1)//2+6,cx-12:cx+12].reshape(-1,3).mean(0)
            above_occ = (i>0 and grid[i-1][j]=='X')
            key='above-occupied' if above_occ else 'above-empty'
            res.setdefault(key,[]).append((top-mid))
for k,v in res.items():
    d=np.array(v)
    print(f'  empty cells {k}: n={len(v)} top-minus-mid mean=({d[:,0].mean():.1f},{d[:,1].mean():.1f},{d[:,2].mean():.1f})')

print()
print('=== 5) footer content y1288-1342 (the real "strip") ===')
zone=s0[1288:1345,:]
b=(zone.sum(2)>200)
colh=b.sum(0)
runs=[];s=None
for i,v in enumerate(colh):
    if v>0 and s is None: s=i
    if v==0 and s is not None:
        if i-s>6: runs.append((s,i))
        s=None
print('footer object x-runs:',runs)
# unique colors in footer
u,counts=np.unique(zone.reshape(-1,3),axis=0,return_counts=True)
top=sorted(zip(counts,u.tolist()),reverse=True)[:12]
print('top footer colors:',[(n,c) for n,c in top if n>100])
