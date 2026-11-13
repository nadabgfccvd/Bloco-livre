from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
calm=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
full=np.array(Image.open(base+'06_full.png').convert('RGB')).astype(int)

# Compare EMPTY cells (same parity) between calm and full: cells empty in both.
colx=[(26,102),(110,187),(195,271),(280,356),(364,440),(449,525),(533,610),(618,694)]
rowy=[(193,267),(281,352),(365,436),(449,522),(533,605),(618,690),(703,774),(787,833)]
# 06_full empty list from prior: cells empty in 06 (col j, row i)
empty06={(0,0),(1,0),(5,0),(0,1),(5,1),(2,2),(5,2),(7,2),(0,3),(5,3),(0,4),(5,4),(0,5),(5,5),(7,5),(0,6),(1,6),(2,6),(3,6),(0,7),(1,7),(4,7),(5,7),(6,7),(7,7)}
empty02=set()
# recompute empties in 02
for j,(x0,x1) in enumerate(colx):
    for i,(y0,y1) in enumerate(rowy):
        cx=(x0+x1)//2; cy=(y0+y1)//2
        m=calm[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).mean(0)
        if m.mean()<=70: empty02.add((j,i))  # (col,row)
common=empty06 & {(j,i) for (i,j) in [(a,b) for (b,a) in empty06]}  # normalize
print('empty cells in 06 (col,row):',sorted(empty06))
print('empty cells in 02 (col,row):',sorted(empty02))
both=empty06 & empty02
print('both empty:',sorted(both))
diffs=[]
for (j,i) in sorted(both):
    x0,x1=colx[j]; y0,y1=rowy[i]
    cx=(x0+x1)//2; cy=(y0+y1)//2
    mc=calm[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).mean(0)
    mf=full[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).mean(0)
    diffs.append(np.abs(mf-mc))
if diffs:
    d=np.array(diffs)
    print('per-channel |calm-full| on shared empty cells: mean=',d.mean(0).round(2),'max=',d.max(0))
# Danger tint should tint EMPTY cells red: check hue shift: R-G difference
for (j,i) in sorted(both)[:8]:
    x0,x1=colx[j]; y0,y1=rowy[i]
    cx=(x0+x1)//2; cy=(y0+y1)//2
    mc=calm[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).mean(0)
    mf=full[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).mean(0)
    print(f'cell col{j} row{i}: calm=({mc[0]:.0f},{mc[1]:.0f},{mc[2]:.0f}) full=({mf[0]:.0f},{mf[1]:.0f},{mf[2]:.0f}) dR-dG={(mf[0]-mf[1])-(mc[0]-mc[1]):.1f}')
# board border / panel warm check: compare panel colors
print()
print('board panel (x36-100) calm vs full already done: calm warm-goldish(141,108,90) vs full cool(87,115,122)?')
# That looks like different content. Compare the gutter BETWEEN cells (same bg) — done: nearly same.
# Check the star/trophy colors right side HUD
print('trophy zone y124-152: calm x670=',calm[140,670],'full x670=',full[140,670])
