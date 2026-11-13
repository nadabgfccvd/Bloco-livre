import os, hashlib
from PIL import Image
import numpy as np

R9='/home/z/my-project/critic_shots/r9'
R10='/home/z/my-project/critic_shots/r10'
CROPS='/tmp/critic_crops_r10'
OUT='/home/z/my-project/download/r10_review'
os.makedirs(CROPS, exist_ok=True); os.makedirs(OUT, exist_ok=True)
try: RES=Image.Resampling.NEAREST
except AttributeError: RES=Image.NEAREST

LOG=[]
def P(s=''):
    print(s); LOG.append(str(s))

FILES=['01_hero.png','02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png','06_full.png','07_clear.png']
CELL=84; BX0,BX1,BY0,BY1=24,696,190,866
CY=(BY0+BY1)/2.0  # 528

P('=== CLAIM 4: R9 vs R10 HASH COMPARE ===')
for f in FILES:
    b9=open(os.path.join(R9,f),'rb').read(); b10=open(os.path.join(R10,f),'rb').read()
    same = b9==b10
    P('%s: %s (r10 md5 %s, r9 md5 %s)' % (f, 'BYTE-IDENTICAL' if same else 'DIFFERS',
        hashlib.md5(b10).hexdigest()[:10], hashlib.md5(b9).hexdigest()[:10]))

def star_metrics(path, tag, cropname):
    img=Image.open(path).convert('RGB')
    a=np.asarray(img).astype(int)
    H,W=a.shape[:2]
    R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
    P('\n=== STAR FORENSICS %s (%dx%d) ===' % (tag,W,H))
    yellow=(R>165)&(G>115)&(B<115)&((R-B)>70)
    if yellow.sum()<50:
        P('no yellow star found'); return
    ys,xs=np.nonzero(yellow)
    cx,cy=float(xs.mean()),float(ys.mean())
    ny=int(yellow.sum()); r_area=float(np.sqrt(ny/np.pi))
    d_y=np.sqrt((xs-cx)**2+(ys-cy)**2); r_tip=float(d_y.max())
    P('yellow body px=%d (claim 3904) centroid=(%.1f,%.1f) r_equiv=%.1f r_tip=%.1f' % (ny,cx,cy,r_area,r_tip))
    P('expected center cy-2.42*cell=%.1f -> measured offset %+.1f px' % (CY-2.42*CELL, cy-(CY-2.42*CELL)))
    # dark outline 0xFF3A2A08 = (58,42,8)
    x0,y0=max(0,int(xs.min())-80),max(0,int(ys.min())-80)
    x1,y1=min(W,int(xs.max())+80),min(H,int(ys.max())+80)
    sub=a[y0:y1,x0:x1]
    oR,oG,oB=sub[:,:,0],sub[:,:,1],sub[:,:,2]
    outline=(abs(oR-58)<=30)&(abs(oG-42)<=30)&(abs(oB-8)<=36)&(oR>oG)&(oG>oB)
    oys,oxs=np.nonzero(outline)
    if len(oxs):
        oxs=oxs+x0; oys=oys+y0
        d_o=np.sqrt((oxs-cx)**2+(oys-cy)**2)
        P('outline px=%d (claim 1608) dist p5/p50/p95/max=%.1f/%.1f/%.1f/%.1f  p50/r_equiv=%.2f (claim 1.10) p50/r_tip=%.2f' % (
            len(oxs), np.percentile(d_o,5), np.percentile(d_o,50), np.percentile(d_o,95), d_o.max(),
            np.percentile(d_o,50)/r_area, np.percentile(d_o,50)/r_tip))
        star_bot=max(ys.max(),oys.max()); star_top=min(ys.min(),oys.min())
    else:
        P('outline px=0 (claim 1608) -> NO DARK RING'); star_bot=ys.max(); star_top=ys.min()
    P('star vertical extent y%d-%d, star bottom y=%d vs gold band top y=355' % (star_top,star_bot,star_bot))
    # white-hot core
    yy,xx=np.ogrid[0:H,0:W]
    dist=np.sqrt((xx-cx)**2+(yy-cy)**2)
    white=(R>222)&(G>222)&(B>210)&(dist<0.8*r_tip)
    wys,wxs=np.nonzero(white)
    if len(wxs):
        d_w=np.sqrt((wxs-cx)**2+(wys-cy)**2)
        P('white core px=%d core_max_r=%.1f core_r/r_tip=%.2f core_r/r_equiv=%.2f (claim 0.45r)' % (
            len(wxs), d_w.max(), d_w.max()/r_tip, d_w.max()/r_area))
    else:
        P('white core px=0 -> NO WHITE-HOT CORE')
    # glow annuli (upper hemisphere)
    lum=(R+G+B)/3.0
    P('glow falloff (upper hemisphere, mean lum / mean R per annulus):')
    for r0 in range(0,280,20):
        m=(dist>=r0)&(dist<r0+20)&(yy<cy)
        if m.sum()>25:
            P('  r%3d-%3d: lum=%5.0f R=%5.0f px=%d' % (r0,r0+20,lum[m].mean(),R[m].mean(),int(m.sum())))
    # spokes
    strict=(R>185)&(G>120)&(B<160)&((R-B)>50)&(dist>r_tip*1.12)
    loose =(R>140)&(G>95)&(B<150)&((R-B)>55)&(dist>r_tip*1.12)
    m_up=strict&(yy<cy+8)&(yy<352)
    m_dn=strict&(yy>cy+12)&(yy<353)
    P('spoke px strict: upper=%d below-horizon(y>cy+12,y<353)=%d ; loose upper=%d' % (
        int(m_up.sum()), int(m_dn.sum()), int((loose&(yy<cy+8)&(yy<352)).sum())))
    ys2,xs2=np.nonzero(m_up)
    if len(ys2):
        t=np.arctan2(cy-ys2, xs2-cx)/np.pi  # 0=right 0.5=up 1=left
        hist,_=np.histogram(t,bins=90,range=(0,1))
        runs=[];inrun=False
        for i,c in enumerate(hist):
            if c>=2 and not inrun: start=i;inrun=True
            elif c<2 and inrun: runs.append((start,i));inrun=False
        if inrun: runs.append((start,90))
        merged=[]
        for s,e in runs:
            if merged and s-merged[-1][1]<=3: merged[-1]=(merged[-1][0],e)
            else: merged.append((s,e))
        P('distinct spokes=%d (claim 8); per-spoke (angle/pi, px, tip_r):' % len(merged))
        for s,e in merged:
            sel=(t>=s/90)&(t<e/90)
            dd=np.sqrt((xs2[sel]-cx)**2+(ys2[sel]-cy)**2)
            P('   t=%.3f (%.1f deg) px=%d tip_r=%.0f' % ((s+e)/2/90, (s+e)/2*2, int(sel.sum()), dd.max()))
        P('t range=[%.3f,%.3f] -> [%.3f pi, %.3f pi] (claim 0.08pi-0.92pi); max spoke y=%d vs band top 355' % (
            t.min(),t.max(),t.min(),t.max(),ys2.max()))
    else:
        P('NO spokes detected with strict mask')
    # gold band + board rows
    gold=(R>140)&(G>100)&(B<130)&((R-B)>50)
    band=[y for y in range(300,520) if gold[y,24:696].mean()>0.55]
    if band: P('gold band rows y%d-%d (claim 355-466) n=%d' % (min(band),max(band),len(band)))
    else: P('no gold band rows found (claim 355-466)')
    for r in range(8):
        ya,yb=190+84*r,190+84*(r+1)
        P('board row %d (y%d-%d): gold frac=%.2f' % (r,ya,yb,gold[ya:yb,24:696].mean()))
    for r in range(4,8):
        P('row %d cell-center colors x-col0/3/7: %s' % (r, [tuple(a[190+84*r+42,24+84*c+42]) for c in (0,3,7)]))
    # tray & streak
    P('tray y880-1110 mean color=%s ; streak y1240-1250 mean color=%s' % (
        tuple(a[880:1110].reshape(-1,3).mean(axis=0).astype(int)),
        tuple(a[1240:1250].reshape(-1,3).mean(axis=0).astype(int))))
    # crops
    box=(max(0,int(xs.min())-150),max(0,int(ys.min())-150),min(W,int(xs.max())+150),min(H,int(ys.max())+150))
    img.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2),RES).save(os.path.join(CROPS,cropname))
    return img,a,cx,cy

im10,a10,cx,cy=star_metrics(os.path.join(R10,'07_clear.png'),'R10 07_clear','c1_star_r10.png')
star_metrics(os.path.join(R9,'07_clear.png'),'R9 07_clear (baseline)','c2_star_r9.png')

# diff r9->r10 on 07_clear
a9=np.asarray(Image.open(os.path.join(R9,'07_clear.png')).convert('RGB')).astype(int)
d=np.abs(a10-a9).sum(axis=2); ch=d>12
P('\n=== 07_clear R9->R10 DIFF ===')
P('changed px=%d' % int(ch.sum()))
if ch.sum():
    ys,xs=np.nonzero(ch)
    P('change bbox x%d-%d y%d-%d (everything else in all 7 shots byte-identical)' % (xs.min(),xs.max(),ys.min(),ys.max()))
    vis=np.where(ch[:,:,None],np.array([255,0,0],dtype=np.int64),a9).astype(np.uint8)
    Image.fromarray(vis).save(os.path.join(CROPS,'c9_diff_r9r10.png'))

# overview crops
im=Image.open(os.path.join(R10,'07_clear.png')).convert('RGB')
im.crop((0,0,720,420)).save(os.path.join(CROPS,'c3_upper_r10.png'))
im.crop((0,330,720,880)).save(os.path.join(CROPS,'c4_band_rows_r10.png'))
im.crop((0,870,720,im.size[1])).save(os.path.join(CROPS,'c5_tray_streak_r10.png'))
for src,name in (('01_hero.png','c6_hero_half.png'),('03_skin1.png','c7_skin1_half.png'),('06_full.png','c8_full_half.png')):
    h=Image.open(os.path.join(R10,src)).convert('RGB')
    h.resize((h.size[0]//2,h.size[1]//2),RES).save(os.path.join(CROPS,name))

open(os.path.join(OUT,'measurements_r10.txt'),'w').write('\n'.join(LOG))
P('\nsaved log to %s and %d crops to %s' % (OUT, len(os.listdir(CROPS)), CROPS))
