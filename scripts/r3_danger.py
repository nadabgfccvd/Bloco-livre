from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
calm=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
full=np.array(Image.open(base+'06_full.png').convert('RGB')).astype(int)

# Danger claim: trigger 55% fill, mean diff full-vs-calm 77.92/channel, border warms toward red.
# 06_full vs 02_skin0: both presumably same skin (classic) but different board state.
# 1) board bg / gutter color comparison
def zone_means(a,label):
    gutter=a[833:880,100:694]  # below board? actually board ends 833. take gutter strips inside board
    # take actual gutter pixels: the (24,32,46) color. sample gutter columns at x=186-193 etc
    g=a[200:830,186:194].reshape(-1,3).mean(0)
    print(f'{label} gutter(186-194,y200-830)=({g[0]:.1f},{g[1]:.1f},{g[2]:.1f})')
    # board outer frame: vertical strip x694-700 & x24? Actually board frame = around x100? we saw page bg at x0-24 (31,36,52) and (24,32,46) board panel from x36
    frame=a[200:830, 36:100].reshape(-1,3)
    fm=frame.mean(0)
    print(f'{label} board panel left rail mean=({fm[0]:.1f},{fm[1]:.1f},{fm[2]:.1f})')
    # page bg y1240-1280
    pbg=a[1240:1280, 300:400].reshape(-1,3).mean(0)
    print(f'{label} page bg=({pbg[0]:.1f},{pbg[1]:.1f},{pbg[2]:.1f})')
zone_means(calm,'CALM(02)')
zone_means(full,'FULL(06)')
print()
# 2) occupied ratio in 06_full
# board grid: x cells start 24+85*i? cells: 112..177 etc. cell r,c box: x0=24+85*i+12, y0=193+85*j+8? we saw gutters at y=271-280 etc. row j box y=193+85*j... rows: 193,271(?), let's compute: row gutters seen at y271-280,356-364,440-449,525-533,610-618,694-703,778-787 and board ends 833. So row boxes: 193-270 (row0), 280-355 (row1), 364-439, 449-524, 533-609, 618-693, 703-777, 787-833.
rows=[(193,270),(280,355),(364,439),(449,524),(533,609),(618,693),(703,777),(787,833)]
cols=[(112,184),(197,269),(282,353),(366,437),(451,522),(536,607),(620,689),(693,?) ]
# cell 8: gutter at 693? cell8 box: x620-689 based on col edges 608-620 gutter, 620-689 cell, 689-693 gutter. So:
cols=[(112,184),(197,269),(282,353),(366,437),(451,522),(536,607),(620,689),(620,689)]
# fix: derive from gutter x positions: gutters at 100-112,184-197,269-282,353-366,438-451,523-536,608-620,693-707(board edge)
cols=[(112,184),(197,269),(282,353),(366,437),(451,522),(536,607),(620,689),(693,693)]
# last col seems clipped: col edges 608-620 gutter then 620-689 cell, then 689-693 edge? but 8 cells need 8 boxes: x620-689 is col7; col8?
# Actually board x: 100(board edge) .. 112 cell0 start ... 693 end. 8 cells of ~73px + 7 gutters of 13px = 584+91=675. 112+675=787>693. Hmm.
# From scanline: cells at y600: gutter 100-112, cell 112-177 (65px), gutter 184-197(13), cell 197-262, gutter 269-282, cell 282-347, gutter 354-366, cell 366-431, gutter 438-451, cell 451-516, gutter 523-536, cell 536-601, gutter 608-620, cell 620-689? wait that's 69px, then 693 board edge.
# So last cell truncated? No—cells are ~65px with 17px gutter: 112-177(65),197-262(65),282-347(65),366-431(65),451-516(65),536-601(65),620-685? we saw 620-689 (66). And col8: gutter at 693-707? no, 693 is board edge (page bg from 707).
# Board inner region 112..689 = 577px. 8 cells → 72px each incl gutter: cell 65 + gutter 7? But gutter runs showed 13px. 65*8=520 + 7*13=91 → 611. Too much. So last column partially clipped? scanline at y600 showed 8th cell = x620-689 with gutter 608-620 then board edge at 693. So only 7.5 cells? No: count cells in scanline: x112,197,282,366,451,536,620 = 7 cells, then 689-693 edge. But vscan x=650 showed cells too...
# Better: count cell starts: 112,197,282,366,451,536,620 — that's 7. The 8th may start at 704?? No board ends 693.
# Hmm: 85px pitch * 7 = 595; 112+595=707 > 693. So actually pitch might be 79-80px. Let's not overfit; count cells by scanning the center row of each row band for gutter runs.
y=482  # from vscan, row band 451-524 → mid 482
row=full[y]
runs=[];prev=None;start=100
for x in range(100,700):
    t=tuple(row[x])
    if prev is None: prev=t;continue
    if max(abs(t[i]-prev[i]) for i in range(3))>6:
        runs.append((start,x))
        start=x;prev=t
print('row y482 gutter/cell runs x:',[r for r in runs])
