from PIL import Image
import os

base='/home/z/my-project/critic_shots/r3/'
out='/tmp/critic_crops_r3/'
os.makedirs(out,exist_ok=True)
def crop(src,name,box):
    im=Image.open(base+src).convert('RGB')
    c=im.crop(box)
    c.save(out+name)
    print(name,c.size)
# board close-ups per skin
crop('02_skin0.png','board_skin0.png',(24,190,700,840))
crop('03_skin1.png','board_skin1.png',(24,190,700,840))
crop('04_skin2.png','board_skin2.png',(24,190,700,840))
crop('05_skin3.png','board_skin3.png',(24,190,700,840))
# empty cell macro (skin0)
crop('02_skin0.png','emptycell_macro_skin0.png',(110,280,290,440))
# tray crop incl long piece
crop('02_skin0.png','tray_skin0.png',(0,840,720,1120))
crop('06_full.png','tray_full.png',(0,840,720,1120))
# streak strip zone (claimed)
crop('01_main_classic.png','streakstrip_claimed.png',(0,1120,720,1290))
# footer crop
crop('01_main_classic.png','footer.png',(0,1280,720,1360))
# celebration macro
crop('07_clear.png','celebration_full.png',(0,0,720,1440))
crop('07_clear.png','celebration_board.png',(0,190,720,840))
# danger diff
crop('06_full.png','danger_full_board.png',(0,190,720,840))
