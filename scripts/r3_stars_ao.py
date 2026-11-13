from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'

def gold_clusters(name):
    a=np.array(Image.open(base+name).convert('RGB')).astype(int)
    # star gold candidates: r>200, g>150, b in 60..160, outside board rect (x100-693, y193-833)
    mask=(a[:,:,0]>200)&(a[:,:,1]>140)&(a[:,:,2]<180)&(a[:,:,2]>50)
    # zero out board interior and HUD and tray
    mask[:170,:]=False; mask[833:,:]=False   # keep only board vertical zone
    mask[:,100:694]=False                   # outside board horizontally
    ys,xs=np.nonzero(mask)
    print(f'{name}: gold-ish px outside board (board zone only): {len(ys)}')
    # cluster by proximity
    pts=list(zip(xs.tolist(),ys.tolist()))
    clusters=[]
    for p in pts:
        placed=False
        for c in clusters:
            if any(abs(p[0]-q[0])<40 and abs(p[1]-q[1])<40 for q in c):
                c.append(p); placed=True; break
        if not placed: clusters.append([p])
    # merge clusters iteratively
    changed=True
    while changed:
        changed=False
        for i in range(len(clusters)):
            for j in range(i+1,len(clusters)):
                if any(abs(p[0]-q[0])<40 and abs(p[1]-q[1])<40 for p in clusters[i] for q in clusters[j]):
                    clusters[i]+=clusters[j]; del clusters[j]; changed=True; break
            if changed: break
    big=[c for c in clusters if len(c)>30]
    print(f'   clusters>=30px: {len(big)}  sizes={[len(c) for c in big]}')
    for c in big:
        cx=sum(p[0] for p in c)/len(c); cy=sum(p[1] for p in c)/len(c)
        print(f'   centroid=({cx:.0f},{cy:.0f})')
    return a

a=gold_clusters('02_skin0.png')
print()
# colors of those star pixels
mask=(a[:,:,0]>200)&(a[:,:,1]>140)&(a[:,:,2]<180)&(a[:,:,2]>50)
mask[:170,:]=False; mask[833:,:]=False; mask[:,100:694]=False
ys,xs=np.nonzero(mask)
cols=a[ys,xs]
print('star px color mean:',cols.mean(0).round(1),'min',cols.min(0),'max',cols.max(0))
# distinct
u=np.unique(cols.reshape(-1,3),axis=0)
print('distinct star colors:',len(u),u[:12])

print()
print('=== AO check: col0 vertical x=60 skin0 ===')
b=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
col=b[:,60]
prev=None;start=170
for y in range(170,880):
    t=tuple(col[y])
    if prev is None: prev=t; continue
    if max(abs(t[i]-prev[i]) for i in range(3))>6:
        print(f'  y{start:3d}-{y:3d} len={y-start:3d} rgb={tuple(int(v) for v in col[start])}')
        start=y; prev=t
