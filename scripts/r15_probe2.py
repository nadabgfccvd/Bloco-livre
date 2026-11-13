import numpy as np, os, collections
from PIL import Image
from matplotlib.colors import rgb_to_hsv as _r2h
def hsv(a): return _r2h(a)
R15='/home/z/my-project/critic_shots/r15'; R14='/home/z/my-project/critic_shots/r14'

def probe(d,tag):
    im=Image.open(os.path.join(d,'02_skin0.png')).convert('RGB')
    a=np.asarray(im).astype(np.float32)/255.0
    L=(0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2])*255
    H=hsv(a); s=H[...,1]; v=H[...,2]
    ldiff=[];rdiff=[];bdiff=[]
    for row in range(8):
        for col in range(8):
            x0=24+col*84; y0=190+row*84
            core=(slice(y0+6,y0+78),slice(x0+6,x0+78))
            if ((s[core]>0.35)&(v[core]>0.22)).mean()<0.45: continue
            # strips: left 10-30% width (~7-25px of 84), right mirror, bottom y 80-92%
            Ls=L[y0+10:y0+74, x0+8:x0+22].mean()   # left band
            Rs=L[y0+10:y0+74, x0+62:x0+76].mean()  # right band
            Bt=L[y0+67:y0+77, x0+12:x0+72].mean() # bottom rim (80-92% of 84 => y67-77)
            Md=L[y0+28:y0+50, x0+30:x0+54].mean() # middle
            ldiff.append(Ls-Rs); bdiff.append(Bt-Md)
    print(f"[{tag}] classic cells n={len(ldiff)}  Lstrip-Rstrip mean={np.mean(ldiff):+.1f} (pL>pR in {sum(x>2 for x in ldiff)}/{len(ldiff)})  bottomRim-mid mean={np.mean(bdiff):+.1f} (brighter in {sum(x>2 for x in bdiff)}/{len(bdiff)})")

probe(R14,'R14'); probe(R15,'R15')

# full-res confetti item count on clear shots (>=2px blobs, non-gold)
def items(d,tag):
    im=Image.open(os.path.join(d,'07_clear.png')).convert('RGB')
    a=np.asarray(im).astype(np.float32)/255.0; H=hsv(a)
    s=H[...,1]; v=H[...,2]; h=H[...,0]
    m=(s>0.45)&(v>0.50)&~((h>=0.08)&(h<=0.20))
    m[:186,:]=False  # confetti above/over board region too? keep all but header text: only y>~20
    m[:20,:]=False
    sizes=[]; seen=set()
    idx=np.argwhere(m)
    for (y,x) in map(tuple,idx):
        if (y,x) in seen: continue
        q=collections.deque([(y,x)]); seen.add((y,x)); n=0
        while q:
            cy,cx=q.popleft(); n+=1
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                ny,nx=cy+dy,cx+dx
                if 0<=ny<m.shape[0] and 0<=nx<m.shape[1] and m[ny,nx] and (ny,nx) not in seen:
                    seen.add((ny,nx)); q.append((ny,nx))
        sizes.append(n)
    print(f"[{tag}] confetti items full-res: total={len(sizes)}  >=2px={sum(1 for z in sizes if z>=2)}  >=6px={sum(1 for z in sizes if z>=6)}  max={max(sizes)}")
items(R14,'R14'); items(R15,'R15')

# gold sparks near star (above board y<190) in clear
def gold_spark(d,tag):
    im=Image.open(os.path.join(d,'07_clear.png')).convert('RGB')
    a=np.asarray(im).astype(np.float32)/255.0; H=hsv(a)
    s=H[...,1]; v=H[...,2]; h=H[...,0]
    m=(h>=0.09)&(h<=0.19)&(s>0.35)&(v>0.65); m[190:,:]=False
    ys,xs=np.where(m)
    sizes=[]; seen=set()
    for (y,x) in map(tuple,np.argwhere(m)):
        if (y,x) in seen: continue
        q=collections.deque([(y,x)]); seen.add((y,x)); n=0
        while q:
            cy,cx=q.popleft(); n+=1
            for dy,dx in ((1,0),(-1,0),(0,1),(0,1)):
                pass
            break
        break
    # simpler: cluster columns
    cols=np.where(m.any(0))[0]; runs=[]
    if len(cols):
        run=[cols[0],cols[0]]
        for c in cols[1:]:
            if c-run[1]<=6: run[1]=c
            else: runs.append(tuple(run)); run=[c,c]
        runs.append(tuple(run))
    print(f"[{tag}] gold sparks above board: px={int(m.sum())} x-clusters={len(runs)} at {[r[0] for r in runs][:24]}")
gold_spark(R14,'R14'); gold_spark(R15,'R15')

# danger board fill 06_full
im=Image.open(os.path.join(R15,'06_full.png')).convert('RGB')
a=np.asarray(im).astype(np.float32)/255.0; H=hsv(a); s=H[...,1]; v=H[...,2]
occ=0
for row in range(8):
    for col in range(8):
        x0=24+col*84; y0=190+row*84
        f=((s[y0+6:y0+78,x0+6:x0+78]>0.35)&(v[y0+6:y0+78,x0+6:x0+78]>0.22)).mean()
        occ+=f>0.45
print(f"[R15 06_full] board fill={occ}/64 = {occ/64*100:.0f}% (claim 81%)")

# tray content sanity on hero
im=Image.open(os.path.join(R15,'01_hero.png')).convert('RGB')
a=np.asarray(im).astype(np.float32)/255.0; H=hsv(a); s=H[...,1]; v=H[...,2]
band=slice(860,1142)
occ=int(((s[band,:]>0.35)&(v[band,:]>0.22)).sum())
print(f"[R15 hero tray] occupied px={occ} -> density over 518400: {occ/518400*100:.1f}%")

# hero: how many faces are still near-flat (std<15)?
im=Image.open(os.path.join(R15,'01_hero.png')).convert('RGB')
a=np.asarray(im).astype(np.float32)/255.0; L=(0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2])*255
H=hsv(a); s=H[...,1]; v=H[...,2]
st=[]
for row in range(8):
    for col in range(8):
        x0=24+col*84; y0=190+row*84
        core=(slice(y0+6,y0+78),slice(x0+6,x0+78))
        if ((s[core]>0.35)&(v[core]>0.22)).mean()<0.45: continue
        st.append(float(L[core].std()))
st=np.array(st)
print(f"[R15 hero] faces std<15: {(st<15).sum()}/{len(st)}  <20: {(st<20).sum()}  >40: {(st>40).sum()}")
