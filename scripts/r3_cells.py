from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'

def analyze(name, x0,y0, pitch, label):
    im=Image.open(base+name).convert('RGB')
    a=np.array(im).astype(int)
    print(f'=== {label} ({name}) grid x0={x0} y0={y0} pitch={pitch} ===')
    # sample cell centers (empty ones) — take center 30x30 of each cell
    empt=[]
    for r in range(8):
        row=[]
        for c in range(8):
            cy=y0+int(pitch*(r+0.5)); cx=x0+int(pitch*(c+0.5))
            patch=a[cy-15:cy+15, cx-15:cx+15]
            m=patch.reshape(-1,3).mean(0); s=patch.reshape(-1,3).std(0)
            row.append((m,s))
        empt.append(row)
    # print corner-ish cells to inspect
    for (r,c) in [(0,0),(0,1),(0,2),(1,1),(3,3),(4,4)]:
        m,s=empt[r][c]
        print(f'  cell({r},{c}) mean=({m[0]:5.1f},{m[1]:5.1f},{m[2]:5.1f}) std=({s[0]:4.1f},{s[1]:4.1f},{s[2]:4.1f})')
    # parity check: average even (r+c) vs odd
    even=[];odd=[]
    for r in range(8):
        for c in range(8):
            (even if (r+c)%2==0 else odd).append(empt[r][c][0])
    even=np.array(even); odd=np.array(odd)
    # only cells with low std = empty
    em=[empt[r][c] for r in range(8) for c in range(8) if empt[r][c][1].mean()<12]
    if em:
        e=np.array([m for m,s in em])
        print(f'  EMPTY cells n={len(em)} mean=({e[:,0].mean():.1f},{e[:,1].mean():.1f},{e[:,2].mean():.1f}) minstd={min(s.mean() for m,s in em):.1f}')
    print(f'  parity even=({even[:,0].mean():.1f},{even[:,1].mean():.1f},{even[:,2].mean():.1f}) odd=({odd[:,0].mean():.1f},{odd[:,1].mean():.1f},{odd[:,2].mean():.1f}) diff={np.abs(even-odd).mean():.1f}')
    # vertical structure inside a cell: top vs bottom 12px band at cell center columns
    r,c=0,0
    cy=y0+int(pitch*(r+0.5)); cx=x0+int(pitch*(c+0.5))
    top=a[cy-20:cy-8, cx-15:cx+15].reshape(-1,3).mean(0)
    mid=a[cy-6:cy+6, cx-15:cx+15].reshape(-1,3).mean(0)
    bot=a[cy+8:cy+20, cx-15:cx+15].reshape(-1,3).mean(0)
    print(f'  cell(0,0) top20px=({top[0]:.1f},{top[1]:.1f},{top[2]:.1f}) mid=({mid[0]:.1f},{mid[1]:.1f},{mid[2]:.1f}) bot20px=({bot[0]:.1f},{bot[1]:.1f},{bot[2]:.1f})')

analyze('02_skin0.png',100,205,85,'SKIN0 Clássico')
analyze('03_skin1.png',100,205,85,'SKIN1 Neon')
analyze('04_skin2.png',100,205,85,'SKIN2 Gema')
analyze('05_skin3.png',100,205,85,'SKIN3 Pixel')
