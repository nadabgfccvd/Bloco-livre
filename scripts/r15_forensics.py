import numpy as np, os
from PIL import Image
from matplotlib.colors import rgb_to_hsv

R15='/home/z/my-project/critic_shots/r15'; R14='/home/z/my-project/critic_shots/r14'
OUT='/tmp/critic_crops_r15'; os.makedirs(OUT,exist_ok=True)

def load(d,f):
    return Image.open(os.path.join(d,f)).convert('RGB')

def arr(im):
    return np.asarray(im).astype(np.float32)/255.0

def lum(a):
    return (0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2])*255.0

def hsv(a):
    return rgb_to_hsv(a)

def cell_stats(im):
    """per occupied cell: interior luminance std. returns list of (std, col,row, meanL) for occupied + count"""
    a=arr(im); L=lum(a); H=hsv(a); s=H[...,1]; v=H[...,2]
    res=[]; occ=[]
    for col in range(8):
        for row in range(8):
            x0=24+col*84; y0=190+row*84
            xs=slice(x0+6,x0+78); ys=slice(y0+6,y0+78)
            sv=s[ys,xs]; vv=v[ys,xs]; lv=L[ys,xs]
            frac=float(((sv>0.35)&(vv>0.22)).mean())
            if frac>0.45:
                res.append((float(lv.std()), col,row,float(lv.mean())))
                occ.append((col,row))
    return res,occ

def board_mask_empty_cells(im):
    """return list of empty cell coords"""
    a=arr(im); H=hsv(a); s=H[...,1]; v=H[...,2]
    empty=[]
    for col in range(8):
        for row in range(8):
            x0=24+col*84; y0=190+row*84
            xs=slice(x0+6,x0+78); ys=slice(y0+6,y0+78)
            frac=float(((s[ys,xs]>0.35)&(v[ys,xs]>0.22)).mean())
            if frac<=0.45: empty.append((col,row))
    return empty

def faces_report(tag, path):
    im=load(*path) if isinstance(path,tuple) else Image.open(path).convert('RGB')
    res,occ=cell_stats(im)
    stds=[r[0] for r in res]
    print(f"[{tag}] occupied faces={len(stds)}  face-internal L std: mean={np.mean(stds):.1f} min={np.min(stds):.1f} max={np.max(stds):.1f} median={np.median(stds):.1f}")
    return stds

def confetti(tag, path):
    im=Image.open(path).convert('RGB'); a=arr(im); H=hsv(a)
    s=H[...,1]; v=H[...,2]; h=H[...,0]
    sat=(s>0.45)&(v>0.50)
    gold=(h>=0.08)&(h<=0.20)&(s>0.40)&(v>0.60)
    nongold=sat&~((h>=0.08)&(h<=0.20))
    print(f"[{tag}] sat px total={int(sat.sum())}  non-gold sat={int(nongold.sum())}  gold px={int(gold.sum())}")
    # connected components (4-conn) on non-gold sat mask, downscaled 2x for speed
    m=(nongold[::2,::2])
    lab=np.zeros(m.shape,np.int32); cur=0
    import collections
    idx=np.argwhere(m)
    seen=set()
    sizes=[]
    for (y,x) in map(tuple,idx):
        if (y,x) in seen: continue
        cur+=1; q=collections.deque([(y,x)]); seen.add((y,x)); n=0
        while q:
            cy,cx=q.popleft(); n+=1
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny,nx=cy+dy,cx+dx
                if 0<=ny<m.shape[0] and 0<=nx<m.shape[1] and m[ny,nx] and (ny,nx) not in seen:
                    seen.add((ny,nx)); q.append((ny,nx))
        sizes.append(n)
    big=[sz for sz in sizes if sz>=3]
    print(f"    components>=3px(2x-downscaled): {len(sizes)} total, {len(big)} substantive")
    return int(nongold.sum()), int(gold.sum())

def star_find(tag, path):
    im=Image.open(path).convert('RGB'); a=arr(im); H=hsv(a)
    s=H[...,1]; v=H[...,2]; h=H[...,0]
    # bright, near-white or gold
    m=((v>0.82)&(s<0.28))|((v>0.75)&(h>=0.09)&(h<=0.19)&(s>0.3))
    m[:190,:]=False  # only at/above board? no -> search whole, then filter
    m2=((v>0.82)&(s<0.28))|((v>0.75)&(h>=0.09)&(h<=0.19)&(s>0.3))
    ys,xs=np.where(m2)
    if len(ys)==0: print(f"[{tag}] star: none"); return
    # cluster by y<190 (above board)
    sel=ys<190
    if sel.sum()>20:
        yy,xx=ys[sel],xs[sel]
        print(f"[{tag}] star-ish cluster ABOVE board: x{xx.min()}-{xx.max()} y{yy.min()}-{yy.max()} px={int(sel.sum())} -> gap to board top(190) = {190-yy.max()}px")
    else:
        print(f"[{tag}] no cluster above board; bright px total={len(ys)}")

def streak(tag, path):
    im=Image.open(path).convert('RGB'); a=arr(im); H=hsv(a)
    s=H[...,1]; v=H[...,2]
    band=slice(1228,1262)
    white=(v[band,:]>0.86)&(s[band,:]<0.20)
    cols=np.where(white.any(0))[0]
    # cluster columns into ticks
    ticks=[]; run=None
    for c in cols:
        if run is None: run=[c,c]
        elif c-run[1]<=3: run[1]=c
        else: ticks.append(tuple(run)); run=[c,c]
    if run: ticks.append(tuple(run))
    print(f"[{tag}] streak band y1228-1262 white px={int(white.sum())} distinct tick clusters={len(ticks)}")

def radial(tag,path):
    im=Image.open(path).convert('RGB'); a=arr(im); L=lum(a)
    cy,cx=528,360
    yy,xx=np.mgrid[190:866,24:696]
    d=np.sqrt((yy-cy)**2+(xx-cx)**2)
    inner=d<80; outer=d>330
    print(f"[{tag}] radial well: center L={L[190:866,24:696][inner].mean():.1f} rim L={L[190:866,24:696][outer].mean():.1f} delta={L[190:866,24:696][inner].mean()-L[190:866,24:696][outer].mean():.1f}")

print("=== image sizes ===")
for f in ['01_hero.png','07_clear.png','06_full.png']:
    print(f, Image.open(os.path.join(R15,f)).size)

print("\n=== FACE INTERNAL CONTRAST (L std inside 72px cell core) ===")
h15=faces_report("R15 hero",(R15,'01_hero.png')) if False else faces_report("R15 hero",os.path.join(R15,'01_hero.png'))
h14=faces_report("R14 hero",os.path.join(R14,'01_hero.png'))
for i,name in enumerate(['Clássico','Neon','Gema','Pixel']):
    s15=faces_report(f"R15 skin{i} {name}",os.path.join(R15,f'0{i+2}_skin{i}.png'))
    s14=faces_report(f"R14 skin{i} {name}",os.path.join(R14,f'0{i+2}_skin{i}.png'))

print("\n=== CELEBRATION (07_clear) ===")
confetti("R15 clear",os.path.join(R15,'07_clear.png'))
confetti("R14 clear",os.path.join(R14,'07_clear.png'))

print("\n=== STAR / DANGER (06_full) ===")
star_find("R15 full",os.path.join(R15,'06_full.png'))
star_find("R15 clear",os.path.join(R15,'07_clear.png'))

print("\n=== STREAK BAND ===")
streak("R15 hero",os.path.join(R15,'01_hero.png'))
streak("R15 full",os.path.join(R15,'06_full.png'))

print("\n=== RADIAL WELL ===")
radial("R15 skin0",os.path.join(R15,'02_skin0.png'))
radial("R14 skin0",os.path.join(R14,'02_skin0.png'))

print("\n=== CROPS ===")
def crop_scale(im, box, scale, name):
    c=im.crop(box)
    c=c.resize((c.width*scale,c.height*scale), Image.NEAREST if scale>=3 else Image.LANCZOS)
    p=os.path.join(OUT,name); c.save(p)
    print("saved",p,c.size)

hero=load(R15,'01_hero.png')
# find an occupied 3x4 block region on hero for context crop
a=arr(hero); H=hsv(a); s=H[...,1]; v=H[...,2]
occ=np.zeros((8,8),bool)
for col in range(8):
    for row in range(8):
        x0=24+col*84; y0=190+row*84
        frac=float(((s[y0+6:y0+78,x0+6:x0+78]>0.35)&(v[y0+6:y0+78,x0+6:x0+78]>0.22)).mean())
        occ[row,col]=frac>0.45
print("hero occupancy grid (rows top->bottom):")
for r in range(8): print('   ',''.join('#' if occ[r,c] else '.' for c in range(8)))

# pick densest 4x3 window
best=None
for r in range(0,5):
    for c in range(0,5):
        sc=occ[r:r+4,c:c+4].sum()
        if best is None or sc>best[0]: best=(sc,r,c)
sc,r0,c0=best
crop_scale(hero,(24+c0*84,190+r0*84,24+(c0+4)*84,190+(r0+4)*84),2,f"crop1_hero_block_r{r0}c{c0}.png")
crop_scale(hero,(24,860,696,1142),1,"crop2_tray.png")

for i,name in enumerate(['classico','neon','gema','pixel']):
    im=load(R15,f'0{i+2}_skin{i}.png')
    # find first occupied cell in middle rows
    found=False
    for row in range(1,7):
        for col in range(8):
            x0=24+col*84; y0=190+row*84
            frac=float(((s if False else 0)) if False else 0)
        # recompute properly
    a2=arr(im); H2=hsv(a2); s2=H2[...,1]; v2=H2[...,2]
    for row in range(1,7):
        for col in range(8):
            x0=24+col*84; y0=190+row*84
            frac=float(((s2[y0+6:y0+78,x0+6:x0+78]>0.35)&(v2[y0+6:y0+78,x0+6:x0+78]>0.22)).mean())
            if frac>0.6:
                crop_scale(im,(x0,y0,x0+84,y0+84),4,f"crop3_skin{i}_{name}_cell_r{row}c{col}.png")
                found=True; break
        if found: break

clear=load(R15,'07_clear.png')
crop_scale(clear,(24,190,696,530),1,"crop4_clear_confetti_top.png")
crop_scale(clear,(24,530,696,866),1,"crop5_clear_confetti_bot.png")
crop_scale(clear,(120,1160,600,1290),1,"crop6_clear_footer.png")
full=load(R15,'06_full.png')
crop_scale(full,(200,60,520,260),2,"crop7_full_star.png")
crop_scale(full,(24,1220,696,1270),1,"crop8_streak.png")
