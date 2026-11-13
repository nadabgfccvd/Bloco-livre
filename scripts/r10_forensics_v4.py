import os
from PIL import Image
import numpy as np

R9='/home/z/my-project/critic_shots/r9/07_clear.png'
R10='/home/z/my-project/critic_shots/r10/07_clear.png'
LOG=[]
def P(s=''):
    print(s); LOG.append(str(s))

def analyze(path,tag):
    a=np.asarray(Image.open(path).convert('RGB')).astype(int)
    R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
    yy,xx=np.ogrid[0:a.shape[0],0:a.shape[1]]
    near=(xx-360)**2+(yy-327)**2 < 90**2
    bright=near&(R>150)&((R-B)>60)
    ys,xs=np.nonzero(bright)
    cx,cy=float(xs.mean()),float(ys.mean())
    P('\n=== v4 %s: star body centroid=(%.1f,%.1f) claim~(360,%.1f); bright px=%d' % (tag,cx,cy,528-2.42*84,len(ys)))
    dist=np.sqrt((xx-cx)**2+(yy-cy)**2)
    for name,cond in (('UPPER hemi',yy<=cy-2),('LOWER hemi',yy>=cy+2)):
        ann=(dist>=58)&(dist<=115)&cond&(xx>170)&(xx<550)
        if ann.sum()==0:
            P('%s annulus px=0' % name); continue
        ys2,xs2=np.nonzero(ann)
        if name.startswith('UPPER'):
            t=np.arctan2(cy-ys2,xs2-cx)
        else:
            t=np.arctan2(ys2-cy,xs2-cx)
        ti=((t/np.pi)*60).astype(int)
        Rbin=np.zeros(60); cnt=np.zeros(60)
        for i in range(60):
            m=ti==i
            if m.any():
                Rbin[i]=R[ys2[m],xs2[m]].mean(); cnt[i]=m.sum()
        bg=np.median(Rbin[cnt>0])
        peaks=(Rbin-bg)>18
        runs=[];inrun=False
        for i,c in enumerate(peaks):
            if c and not inrun: s_=i;inrun=True
            elif not c and inrun: runs.append((s_,i));inrun=False
        if inrun: runs.append((s_,60))
        merged=[]
        for s_,e in runs:
            if merged and s_-merged[-1][1]<=2: merged[-1]=(merged[-1][0],e)
            else: merged.append((s_,e))
        P('%s: bg R=%.0f, spoke peaks=%d at %s' % (name,bg,len(merged),['%.2f pi'%((s_+e)/120.0) for s_,e in merged]))
        P('  bin meanR (3deg bins, 0=right .. 0.5=up .. 1=left): '+' '.join(('%.0f'%v) if c>0 else '.' for v,c in zip(Rbin,cnt)))
    body=(dist<40)&(R>140)&((R-B)>50)
    ys3=np.nonzero(body)[0]
    if len(ys3):
        P('star body bottom y=%d vs band top 355 -> overlap %d px below band top' % (ys3.max(),ys3.max()-355))
    glowrow=[]
    for r0 in range(40,140,10):
        m=(dist>=r0)&(dist<r0+10)&(yy<cy)
        if m.sum()>10: glowrow.append('r%d:%.0f'%(r0,R[m].mean()))
    P('glow falloff upper hemi meanR: '+' '.join(glowrow))

analyze(R10,'R10')
analyze(R9,'R9')
with open('/home/z/my-project/download/r10_review/measurements_r10_v4.txt','w') as f:
    f.write('\n'.join(LOG))
P('done')
