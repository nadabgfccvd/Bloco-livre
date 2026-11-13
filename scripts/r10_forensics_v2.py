import os
from PIL import Image
import numpy as np

R9='/home/z/my-project/critic_shots/r9/07_clear.png'
R10='/home/z/my-project/critic_shots/r10/07_clear.png'
CROPS='/tmp/critic_crops_r10'
OUT='/home/z/my-project/download/r10_review'
os.makedirs(CROPS,exist_ok=True); os.makedirs(OUT,exist_ok=True)
LOG=[]
def P(s=''):
    print(s); LOG.append(str(s))

CX_EXPC, CY_EXPC = 360.0, 528-2.42*84  # 324.7

def analyze(path, tag):
    a=np.asarray(Image.open(path).convert('RGB')).astype(int)
    H,W=a.shape[:2]
    R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
    yy,xx=np.ogrid[0:H,0:W]
    P('\n=== STAR v2 %s ===' % tag)
    # star neighborhood only: above gold band (band y355-466), around diff bbox
    reg=(yy>=100)&(yy<352)&(xx>=180)&(xx<540)
    yellow=(R>165)&(G>115)&(B<115)&((R-B)>70)&reg
    ys,xs=np.nonzero(yellow)
    cx,cy=float(xs.mean()),float(ys.mean())
    dist=np.sqrt((xx-cx)**2+(yy-cy)**2)
    P('star center=(%.1f,%.1f) vs expected (%.1f,%.1f) -> off %+.1f,%+.1f px' % (cx,cy,CX_EXPC,CY_EXPC,cx-CX_EXPC,cy-CY_EXPC))
    dy=dist[yellow]
    body=dist<60
    n_body=int((yellow&body).sum()); r_body=float(np.sqrt(n_body/np.pi))
    P('yellow body (r<60) px=%d (claim 3904) r_equiv=%.1f' % (n_body,r_body))
    # outline: dark 0xFF3A2A08=(58,42,8), ring around body
    dark=(abs(R-58)<=32)&(abs(G-42)<=32)&(abs(B-8)<=38)&(R>=G)&(G>B)
    ring=dark&(dist>=r_body*0.9)&(dist<=r_body*1.45)&(yy<356)
    n_ring=int(ring.sum())
    if n_ring:
        rys,rxs=np.nonzero(ring); rd=np.sqrt((rxs-cx)**2+(rys-cy)**2)
        P('outline ring px=%d (claim 1608) median_r=%.1f ratio=%.2f (claim 1.10r)' % (n_ring,np.median(rd),np.median(rd)/r_body))
    else:
        P('outline ring px=0 (claim 1608)')
    # white-hot core
    white=(R>222)&(G>222)&(B>205)&(dist<r_body*1.2)
    n_white=int(white.sum())
    if n_white:
        wys,wxs=np.nonzero(white); wd=np.sqrt((wxs-cx)**2+(wys-cy)**2)
        P('white core px=%d max_r=%.1f ratio=%.2f (claim 0.45r) peak RGB=%s' % (n_white,wd.max(),wd.max()/r_body,tuple(a[wys[np.argmax(wd)],wxs[np.argmax(wd)]])))
    else:
        P('white core px=0')
    # glow halo falloff (upper hemi), bg lum ~64
    lum=(R+G+B)/3.0
    P('glow annuli (upper hemi): lum vs bg64')
    row=[]
    for r0 in range(0,200,20):
        m=(dist>=r0)&(dist<r0+20)&(yy<cy)&reg
        if m.sum()>20: row.append('r%d:%.0f'%(r0,lum[m].mean()))
    P('  '+' '.join(row))
    # spokes: yellowish outside outline, upper hemisphere, above band
    spokes=(R>140)&(G>90)&((R-B)>55)&(dist>r_body*1.5)&(yy<cy+6)&(yy<353)&reg
    n_sp=int(spokes.sum())
    sys_,sxs=np.nonzero(spokes)
    P('spoke px=%d' % n_sp)
    if n_sp:
        t=np.arctan2(cy-sys_, sxs-cx)/np.pi  # 0=right, .5=up, 1=left
        hist,_=np.histogram(t,bins=100,range=(0,1))
        runs=[];inrun=False
        for i,c in enumerate(hist):
            if c>=2 and not inrun: s_=i;inrun=True
            elif c<2 and inrun: runs.append((s_,i));inrun=False
        if inrun: runs.append((s_,100))
        merged=[]
        for s_,e in runs:
            if merged and s_-merged[-1][1]<=4: merged[-1]=(merged[-1][0],e)
            else: merged.append((s_,e))
        P('distinct spokes=%d (claim 8)' % len(merged))
        for s_,e in merged:
            sel=(t>=s_/100)&(t<e/100)
            dd=np.sqrt((sxs[sel]-cx)**2+(sys_[sel]-cy)**2)
            P('   t=%.3f pi (%.0f deg) px=%d len=%.0f end_y=%d' % ((s_+e)/200,(s_+e)/100*180,int(sel.sum()),dd.max(),sys_[sel].max()))
        P('spoke t-range [%.3f,%.3f] pi (claim 0.08-0.92); max spoke y=%d (band top=355, must stay <355)' % (t.min(),t.max(),sys_.max()))
    else:
        P('NO SPOKES above horizon')
    # lower-hemisphere spokes / band crossing
    low=(R>140)&(G>90)&((R-B)>55)&(dist>r_body*1.5)&(yy>cy+10)&(yy<353)&reg
    P('below-horizon spoke px (cy<y<353): %d' % int(low.sum()))
    # strip between star bottom and band top, and below band
    for (ya,yb,lab) in [(340,354,'gap star->band'),(467,560,'below band')]:
        m=(R>140)&(G>90)&((R-B)>55)&(yy>=ya)&(yy<yb)&(xx>=200)&(xx<520)
        P('%s y%d-%d yellowish px=%d' % (lab,ya,yb,int(m.sum())))
    # crop 2x zoom of star region
    try: RES=Image.Resampling.NEAREST
    except AttributeError: RES=Image.NEAREST
    im=Image.open(path).convert('RGB')
    box=(200,110,520,360)
    im.crop(box).resize((640,500),RES).save(os.path.join(CROPS,'star_%s.png'%tag))
    return dict(a=a,cx=cx,cy=cy,r_body=r_body,dist=dist,reg=reg)

d10=analyze(R10,'r10')
d9=analyze(R9,'r9')

# R9 vs R10 side-by-side star crop
try: RES=Image.Resampling.NEAREST
except AttributeError: RES=Image.NEAREST
i9=Image.open(R9).convert('RGB').crop((200,110,520,470)).resize((480,288),RES)
i10=Image.open(R10).convert('RGB').crop((200,110,520,470)).resize((480,288),RES)
canvas=Image.new('RGB',(980,300),(20,20,20))
canvas.paste(i9,(5,5)); canvas.paste(i10,(495,5))
canvas.save(os.path.join(CROPS,'star_r9_vs_r10.png'))

open(os.path.join(OUT,'measurements_r10_v2.txt'),'w').write('\n'.join(LOG))
P('\nOK')
