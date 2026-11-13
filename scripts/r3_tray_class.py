from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
for name in ['02_skin0.png','06_full.png']:
    a=np.array(Image.open(base+name).convert('RGB')).astype(int)
    print(f'=== {name} tray piece bounding boxes (bright, cell-scale blocks) ===')
    # find piece blocks: colors significantly brighter than (24,32,46) tray bg, in 5x5 blobs
    bright=(a[:,:,0]+a[:,:,1]+a[:,:,2]>150)
    zone=bright[880:1120,:]
    # connected components quick: label by rows/cols runs
    ys,xs=np.nonzero(zone)
    pts=set(zip(xs.tolist(),(ys+880).tolist()))
    seen=set();comps=[]
    import collections
    for p in list(pts):
        if p in seen: continue
        q=collections.deque([p]);comp=[];seen.add(p)
        while q:
            x,y=q.popleft();comp.append((x,y))
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                n=(x+dx,y+dy)
                if n in pts and n not in seen:
                    seen.add(n);q.append(n)
        comps.append(comp)
    comps=[c for c in comps if len(c)>60]
    for c in comps:
        xs_=[p[0] for p in c]; ys_=[p[1] for p in c]
        x0,x1=min(xs_),max(xs_);y0,y1=min(ys_),max(ys_)
        m=np.array([a[y,x] for x,y in c]).mean(0)
        print(f'  bbox x{x0}-{x1} y{y0}-{y1} (w={x1-x0+1},h={y1-y0+1}) n={len(c)} mean=({m[0]:.0f},{m[1]:.0f},{m[2]:.0f})')
