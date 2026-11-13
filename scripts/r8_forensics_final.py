from PIL import Image
import numpy as np
from scipy import ndimage

def load(tag, f):
    return np.asarray(Image.open(f'/home/z/my-project/critic_shots/{tag}/{f}').convert('RGB')).astype(int)

a8c = load('r8','07_clear.png')   # clear payoff shot
a8h = load('r8','01_hero.png')    # hero

gold  = ((a8c[:,:,0]>150)&(a8c[:,:,1]>110)&(a8c[:,:,2]<130)&(a8c[:,:,0]-a8c[:,:,2]>60))

# ---- 1. Connected components of gold ABOVE the band (y150-388) ----
zone = gold[150:389,:]
lab, n = ndimage.label(zone, structure=np.ones((3,3)))
sizes = ndimage.sum(zone, lab, range(1,n+1))
order = np.argsort(sizes)[::-1]
print('== gold clusters above band (top 6) ==')
for i in order[:6]:
    ys,xs = np.where(lab==i+1)
    print(f'  cluster {i+1}: area={int(sizes[i])}px2 centroid=({int(xs.mean())},{150+int(ys.mean())}) bbox x{xs.min()}-{xs.max()} y{150+ys.min()}-{150+ys.max()}')

# ---- 2. Ray thinness: contiguous gold run widths on sample rows (skip star rows 330-389) ----
print('== ray run widths (contiguous gold runs >2px) ==')
for y in [245, 255, 270, 285, 300, 315]:
    xs = np.where(gold[y])[0]
    if not len(xs): continue
    d = np.diff(xs); runs = np.split(xs, np.where(d>4)[0]+1)
    ws = [(r[-1]-r[0]+1) for r in runs if len(r)>2]
    print(f'  y{y}: {len(ws)} runs, widths={ws}')
# vertical run widths at sample columns above band
print('== vertical gold run thickness at columns ==')
for x in [60, 150, 250, 320, 480, 560, 640, 715]:
    ys = np.where(gold[150:389, x])[0]
    if not len(ys): print(f'  x{x}: none'); continue
    d = np.diff(ys); runs = np.split(ys, np.where(d>3)[0]+1)
    ws = [(150+r[-1])-(150+r[0])+1 for r in runs if len(r)>2]
    print(f'  x{x}: {len(ws)} runs thickness={ws}')

# ---- 3. Edge strips: are x0-14 / x705-719 gold in HERO too (background chrome)? ----
gh = ((a8h[:,:,0]>150)&(a8h[:,:,1]>110)&(a8h[:,:,2]<130)&(a8h[:,:,0]-a8h[:,:,2]>60))
print('== edge strips presence ==')
for tag,mask in [('clear',gold),('hero',gh)]:
    im_ = mask[150:389,:]
    print(f'  {tag}: gold px x0-14 = {im_[:,0:15].sum()}, x705-719 = {im_[:,705:720].sum()}, x350-370 = {im_[:,350:370].sum()}')

# ---- 4. Clear board truly empty? piece criterion: contiguous saturated run >=22px in cell core ----
print('== clear board piece check (8x8, core 48x48 of each cell) ==')
sat = (a8c.max(axis=2)-a8c.min(axis=2)) > 50
pieces = 0; suspicious=[]
for r in range(8):
    for c in range(8):
        y0 = int(190 + 84.5*r) + 18; x0 = 24 + 84*c + 18
        core = sat[y0:y0+48, x0:x0+48]
        cols = core.any(axis=0)
        xs = np.where(cols)[0]
        if not len(xs): continue
        d = np.diff(xs); runs = np.split(xs, np.where(d>2)[0]+1)
        w = max((r_[-1]-r_[0]+1) for r_ in runs) if runs else 0
        if w >= 22:
            pieces += 1; suspicious.append((r,c,w))
print(f'  cells with >=22px contiguous saturated blob: {pieces}/64 -> {suspicious}')

# ---- 5. HUD hierarchy loose gold scan y100-190 (hero) ----
print('== HUD hero: loose gold rows ==')
gl = ((a8h[:,:,0]>140)&(a8h[:,:,1]>90)&(a8h[:,:,2]<130)&(a8h[:,:,0]-a8h[:,:,2]>50))
prev=None; start=None
for y in range(100,190):
    row = gl[y]
    n = row[24:700].sum()
    hit = n>8
    if hit and start is None: start=y
    if (not hit) and start is not None:
        if y-start>3: print(f'  gold text block y{start}-{y-1} h={y-start}')
        start=None
if start is not None: print(f'  gold text block y{start}-189 h={190-start}')
# PONTOS white value bbox precise
wh = ((a8h[:,:,0]>210)&(a8h[:,:,1]>210)&(a8h[:,:,2]>210))
sub = wh[120:190, 24:700]
ys,xs = np.where(sub)
print(f'  HUD white value bbox y{120+ys.min()}-{120+ys.max()} h={ys.max()-ys.min()+1} x{24+xs.min()}-{24+xs.max()}')
# wordmark
sub2 = wh[0:60, 24:700]
ys2,xs2 = np.where(sub2)
print(f'  wordmark bbox y{ys2.min()}-{ys2.max()} h={ys2.max()-ys2.min()+1} x{24+xs2.min()}-{24+xs2.max()}')

# ---- 6. Banner text size ratio + baseline placement ----
print('== banner geometry (r8 clear) ==')
# band: hairlines found y389-394 and y499-504, x58-661
band_top, band_bot = 389, 504
band_c = (band_top+band_bot)/2
print(f'  band y{band_top}-{band_bot} h={band_bot-band_top+1}px, center y={band_c}')
print(f'  text glyphs y446-485 h=39px cap-height, text center y={(446+485)/2}, offset from band center = {(446+485)/2-band_c:+.0f}px')
print(f'  text width 548px vs band width 603px -> fill ratio {548/603*100:.0f}%')
print(f'  cap-height/band-height = {39/115*100:.0f}%')

# ---- 7. Below-band rays extent ----
bel = gold[505:880,:]
ys,xs = np.where(bel)
if len(ys): print(f'== below-band gold bbox y{505+ys.min()}-{505+ys.max()} x{xs.min()}-{xs.max()} px={len(ys)}')

# ---- 8. r7 banner band geometry for delta ----
a7c = load('r7','07_clear.png')
g7 = ((a7c[:,:,0]>150)&(a7c[:,:,1]>110)&(a7c[:,:,2]<130)&(a7c[:,:,0]-a7c[:,:,2]>60))
row = g7[430]; xs=np.where(row)[0]
print(f'== r7 band row y430 x{xs.min()}-{xs.max()} width={xs.max()-xs.min()+1} (screen=720)')
