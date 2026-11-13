from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
full=np.array(Image.open(base+'06_full.png').convert('RGB')).astype(int)
calm=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
# Where does "breathing red tint" live in 06_full? Diff whole images where colors differ beyond block layout
# Focus on page bg + board panel + HUD, not cells (layout differs).
# 1) page bg far corner y1400-1440 x0-720
for y0,y1,x0,x1,lab in [(1400,1440,0,720,'bottom strip'),(1160,1280,0,720,'dead zone'),(880,1120,0,720,'tray zone'),(0,100,0,720,'top HUD')]:
    fc=full[y0:y1,x0:x1].reshape(-1,3); cc=calm[y0:y1,x0:x1].reshape(-1,3)
    print(f'{lab}: full=({fc[:,0].mean():.1f},{fc[:,1].mean():.1f},{fc[:,2].mean():.1f}) calm=({cc[:,0].mean():.1f},{cc[:,1].mean():.1f},{cc[:,2].mean():.1f})')
print()
# 2) Board frame: the (31,36,52)→(56,72,97) ring around board — sample ring x704-716 and x0-24
for lab,(x0,x1) in [('right of board',(704,716)),('left of board',(0,24))]:
    f=full[190:840,x0:x1].reshape(-1,3).mean(0); c=calm[190:840,x0:x1].reshape(-1,3).mean(0)
    print(f'{lab}: full=({f[0]:.1f},{f[1]:.1f},{f[2]:.1f}) calm=({c[0]:.1f},{c[1]:.1f},{c[2]:.1f})')
# 3) top of board y180-193 x100-690
f=full[180:193,100:690].reshape(-1,3).mean(0); c=calm[180:193,100:690].reshape(-1,3).mean(0)
print(f'board top edge: full=({f[0]:.1f},{f[1]:.1f},{f[2]:.1f}) calm=({c[0]:.1f},{c[1]:.1f},{c[2]:.1f})')
# 4) tray bg between pieces y840-880
f=full[840:880,100:690].reshape(-1,3).mean(0); c=calm[840:880,100:690].reshape(-1,3).mean(0)
print(f'tray top gap: full=({f[0]:.1f},{f[1]:.1f},{f[2]:.1f}) calm=({c[0]:.1f},{c[1]:.1f},{c[2]:.1f})')
# 5) HUD numerals: find text px in 06 vs 02 y108-170
for arr,lab in [(full,'full'),(calm,'calm')]:
    zone=arr[108:170,120:640]
    bright=(zone.sum(2)>450)
    ys,xs=np.nonzero(bright)
    print(f'{lab}: bright text px={len(ys)} bbox y{108+ys.min()}-{108+ys.max()} x{120+xs.min()}-{120+xs.max()}')
# 6) Check tray piece colors in both — is the "danger" shot maybe pulsing pieces?
