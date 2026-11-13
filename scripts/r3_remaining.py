from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
# 1. Empty cell values: parity A=(50,64,90), B=(41,52,73). Claim: empty=(40,50,70) vs bg(24,32,47)=+25% luminance
bg=(24,32,46)
A=(50,64,90); B=(41,52,73)
lum=lambda c:0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
print(f'lum bg={lum(bg):.1f}  A={lum(A):.1f} (+{(lum(A)/lum(bg)-1)*100:.0f}%)  B={lum(B):.1f} (+{(lum(B)/lum(bg)-1)*100:.0f}%)')
print(f'claim (40,50,70) vs measured A={A} B={B}')
print()
# 2. Danger: 06_full vs 02 calm — but different board states. Compare page bg + gutter + panel + HUD numerals.
for name in ['02_skin0.png','06_full.png']:
    a=np.array(Image.open(base+name).convert('RGB')).astype(int)
    pbg=a[1160:1280,300:420].reshape(-1,3)
    print(f'{name}: page-bg mean=({pbg[:,0].mean():.1f},{pbg[:,1].mean():.1f},{pbg[:,2].mean():.1f})')
# Board filled ratio 06_full
a=np.array(Image.open(base+'06_full.png').convert('RGB')).astype(int)
colx=[(26,102),(110,187),(195,271),(280,356),(364,440),(449,525),(533,610),(618,694)]
rowy=[(193,267),(281,352),(365,436),(449,522),(533,605),(618,690),(703,774),(787,833)]
occ=0; tot=0; empt=[]
for j,(x0,x1) in enumerate(colx):
    for i,(y0,y1) in enumerate(rowy):
        cx=(x0+x1)//2; cy=(y0+y1)//2
        m=a[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).mean(0)
        s=a[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).std(0).mean()
        tot+=1
        if m.mean()>70: occ+=1
        else: empt.append((i,j,m))
print(f'06_full occupied-ish (mean>70): {occ}/{tot} = {occ/tot*100:.0f}%')
print('06_full empty-ish cells:',[(i,j,tuple(np.round(m,1))) for i,j,m in empt])
