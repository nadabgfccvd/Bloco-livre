import os
from PIL import Image
import numpy as np

R9='/home/z/my-project/critic_shots/r9/07_clear.png'
R10='/home/z/my-project/critic_shots/r10/07_clear.png'
CROPS='/tmp/critic_crops_r10'
os.makedirs(CROPS,exist_ok=True)
LOG=[]
def P(s=''):
    print(s); LOG.append(str(s))

CX,CY=354.5,329.5   # diff-bbox center; expected cy-2.42*cell=324.7

def analyze(path,tag):
    a=np.asarray(Image.open(path).convert('RGB')).astype(int)
    H,W=a.shape[:2]
    R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
    yy,xx=np.ogrid[0:H,0:W]
    dist=np.sqrt((xx-CX)**2+(yy-CY)**2)
    warm=(R>110)&((R-B)>60)
    white=(R>215)&(G>215)&(B>200)
    dark=(abs(R-58)<=42)&(abs(G-42)<=42)&(abs(B-8)<=48)&(R>=G)&(G>=B)
    P('\n=== STAR v3 %s (center %.1f,%.1f fixed) ===' % (tag,CX,CY))
    P('radial profile: r | meanRGB | warm%% | white px | dark px   (annulus full ring)')
    for r0 in range(0,156,6):
        m=(dist>=r0)&(dist<r0+6)
        if m.sum()==0: continue
        mr,mg,mb=R[m].mean(),G[m].mean(),B[m].mean()
        P('  r%3d-%3d | %3.0f,%3.0f,%3.0f | warm %4.1f%% | w %5d | d %5d' % (
            r0,r0+6,mr,mg,mb,100*warm[m].mean(),int((warm&m&white).sum())if False else int((m&white).sum()),int((m&dark).sum())))
    # body radius: last r where warm frac >0.55 scanning outward from 0
    r_body=0
    for r0 in range(0,120,6):
        m=(dist>=r0)&(dist<r0+6)&(yy<356)
        if m.sum()>0 and warm[m].mean()>0.55: r_body=r0+6
        elif r0>12: break
    n_body=int((warm&(dist<r_body)).sum())
    P('r_body~%d px, warm px within=%d (claim body 3904; 3904px=>r=%.1f)' % (r_body,n_body,np.sqrt(3904/np.pi)))
    # outline ring
    ring=dark&(dist>=r_body*0.8)&(dist<=r_body*1.6)&(yy<356)
    n_ring=int(ring.sum())
    if n_ring:
        rys,rxs=np.nonzero(ring); rd=np.sqrt((rxs-CX)**2+(rys-CY)**2)
        P('dark outline px=%d (claim 1608) median_r=%.1f ratio=%.2f (claim 1.10r)' % (n_ring,np.median(rd),np.median(rd)/max(r_body,1)))
    else: P('dark outline px=0 (claim 1608)')
    # white core
    wc=white&(dist<r_body*1.5)
    n_w=int(wc.sum())
    if n_w:
        wys,wxs=np.nonzero(wc); wd=np.sqrt((wxs-CX)**2+(wys-CY)**2)
        P('white core px=%d max_r=%.1f ratio=%.2f (claim 0.45r)' % (n_w,wd.max(),wd.max()/max(r_body,1)))
    else: P('white core px=0')
    # spokes: warm, outside body, upper hemisphere, above band
    sp=warm&(dist>r_body*1.5)&(yy<=CY)&(yy<354)&(xx>170)&(xx<550)
    n_sp=int(sp.sum())
    P('upper-hemisphere spoke px=%d' % n_sp)
    if n_sp:
        sys_,sxs=np.nonzero(sp)
        t=np.arctan2(CY-sys_,sxs-CX)/np.pi  # 0=right 0.5=up 1=left
        hist,_=np.histogram(t,bins=120,range=(0,1))
        runs=[];inrun=False
        for i,c in enumerate(hist):
            if c>=2 and not inrun: s_=i;inrun=True
            elif c<2 and inrun: runs.append((s_,i));inrun=False
        if inrun: runs.append((s_,120))
        merged=[]
        for s_,e in runs:
            if merged and s_-merged[-1][1]<=5: merged[-1]=(merged[-1][0],e)
            else: merged.append((s_,e))
        P('distinct spokes=%d (claim 8):' % len(merged))
        for s_,e in merged:
            sel=(t>=s_/120)&(t<e/120)
            dd=np.sqrt((sxs[sel]-CX)**2+(sys_[sel]-CY)**2)
            P('   t=%.3f pi / %.0f deg | px=%d | tip_r=%.0f | lowest y=%d' % ((s_+e)/240,(s_+e)/120*180,int(sel.sum()),dd.max(),sys_[sel].max()))
        P('spoke t-range [%.3f,%.3f] pi (claim 0.08-0.92)' % (t.min(),t.max()))
    # lower hemisphere / band contact
    low=warm&(dist>r_body*1.5)&(yy>CY)&(yy<354)&(xx>170)&(xx<550)
    P('below-horizon warm px (y in (%d,354))=%d  <- claim: none' % (int(CY),int(low.sum())))
    touch=warm&(yy>=350)&(yy<356)&(xx>170)&(xx<550)
    P('warm px touching band top edge y350-355=%d' % int(touch.sum()))
    below=warm&(yy>=467)&(yy<600)&(xx>170)&(xx<550)
    P('warm px below band y467-600=%d' % int(below.sum()))
    return a

a10=analyze(R10,'r10')
a9=analyze(R9,'r9')
try: RES=Image.Resampling.NEAREST
except AttributeError: RES=Image.NEAREST
im=Image.open(R10).convert('RGB')
im.crop((240,200,480,360)).resize((720,240),RES).save(os.path.join(CROPS,'star_zoom_r10.png'))
im.crop((240,200,480,470)).resize((480,270),RES).save(os.path.join(CROPS,'star_band_r10.png'))

with open('/home/z/my-project/download/r10_review/measurements_r10_v3.txt','w') as f: f.write('\n'.join(LOG))
P('done')
