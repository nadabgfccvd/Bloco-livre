#!/usr/bin/env python3
"""Preview fiel da tela do Bloco Livre: mesma paleta/proporções do GameView.
Lê /tmp/midstate.txt (estado real do motor) e desenha tabuleiro+bandeja+HUD."""
from PIL import Image, ImageDraw, ImageFont
import sys

W, H = 720, 1560
CELL_INT = lambda v: int(round(v))  # proporção de celular 9:19.5

BG = (16, 20, 28)
BOARD_BG = (27, 35, 48)
BOARD_BORDER = (42, 54, 72)
COLORS = {
    1: (79, 195, 247), 2: (255, 183, 77), 3: (186, 104, 200), 4: (129, 199, 132),
    5: (229, 115, 115), 6: (255, 213, 79), 7: (77, 182, 172),
}

state = open('/tmp/midstate.txt').read().strip().split(';')
# v1;seed;score;best;combo;comboBest;pieces;lines;games;over;draws;revive; 64 grid; 3 tray
grid = [int(v) for v in state[12:12 + 64]]
tray = [int(v) for v in state[12 + 64:12 + 67]]
score = state[2]; best = state[3]; combo = int(state[4])

# ----- peças (idêntico ao Piece.java)
def shapes():
    S = []
    S.append([(0, 0)])
    S += [[(0, 0), (1, 0)], [(0, 0), (1, 0), (2, 0)], [(0, 0), (1, 0), (2, 0), (3, 0)], [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]]
    S += [[(0, 0), (0, 1)], [(0, 0), (0, 1), (0, 2)], [(0, 0), (0, 1), (0, 2), (0, 3)], [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]]
    S.append([(0, 0), (1, 0), (0, 1), (1, 1)])
    S.append([(x, y) for y in range(3) for x in range(3)])
    S.append([(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)])
    S.append([(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)])
    S += [[(0, 0), (1, 0), (0, 1)], [(0, 0), (1, 0), (1, 1)], [(0, 0), (0, 1), (1, 1)], [(1, 0), (0, 1), (1, 1)]]
    S += [[(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)], [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
          [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2)], [(2, 0), (2, 1), (2, 2), (0, 2), (1, 2)]]
    S += [[(0, 0), (1, 0), (2, 0), (1, 1)], [(1, 0), (0, 1), (1, 1), (1, 2)],
          [(1, 0), (0, 1), (1, 1), (2, 1)], [(0, 0), (0, 1), (0, 2), (1, 1)]]
    S += [[(1, 0), (2, 0), (0, 1), (1, 1)], [(0, 0), (1, 0), (1, 1), (2, 1)],
          [(0, 0), (0, 1), (1, 1), (1, 2)], [(1, 0), (1, 1), (0, 1), (0, 2)]]
    S += [[(0, 0), (0, 1), (0, 2), (1, 2)], [(0, 0), (1, 0), (2, 0), (0, 1)],
          [(0, 0), (1, 0), (1, 1), (1, 2)], [(2, 0), (0, 1), (1, 1), (2, 1)]]
    return S
SHAPES = shapes()

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
try:
    f_big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 64)
    f_med = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
    f_sml = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
except Exception:
    f_big = f_med = f_sml = ImageFont.load_default()

# HUD (igual MainActivity: score à esquerda, recorde à direita)
d.text((24, 28), score, font=f_big, fill=(255, 255, 255))
d.text((24, 108), ("combo x%d" % combo) if combo >= 2 else "sem combo", font=f_sml, fill=(143, 163, 191))
bw = d.textlength(best, font=f_med)
d.text((W - 24 - d.textlength("RECORDE", font=f_sml), 28), "RECORDE", font=f_sml, fill=(143, 163, 191))
d.text((W - 24 - d.textlength(best, font=f_med), 54), best, font=f_med, fill=(255, 213, 79))

# layout (espelha computeLayout)
pad = max(8, W * 0.02)
top_reserve = H * 0.10
avail_h = H - top_reserve - pad * 4
cell = min((W - pad * 2) / 8, avail_h / 11.2, W / 9)
bs = cell * 8
bl = (W - bs) / 2
bt = top_reserve + pad

def block(x, y, s, color, sh=0.10):
    x, y, s = int(x), int(y), int(s)
    shh = s * sh
    d.rounded_rectangle([x, y, x + s, y + s], radius=s * 0.22, fill=tuple(c // 3 for c in color))
    d.rounded_rectangle([x, y, x + s, y + s - shh], radius=s * 0.22, fill=color)
    d.rounded_rectangle([x + s * 0.10, y + s * 0.08, x + s * 0.90, y + s * 0.38], radius=s * 0.12,
                        fill=tuple(min(255, c + 70) for c in color))

# tabuleiro
d.rounded_rectangle([int(bl), int(bt), int(bl+bs), int(bt+bs)], radius=int(cell*0.3), fill=BOARD_BG, outline=BOARD_BORDER, width=max(2, int(cell*0.06)))
for y in range(8):
    for x in range(8):
        v = grid[y * 8 + x]
        l = int(bl + x * cell + cell * 0.06)
        t = int(bt + y * cell + cell * 0.06)
        s = int(cell * 0.88)
        if v:
            block(l, t, s, COLORS[v])
        else:
            d.rounded_rectangle([l, t, l + s, t + s], radius=s * 0.18, fill=(35, 47, 62))

# bandeja
tray_y = bt + bs + pad * 1.5
tc = cell * 0.8
for i, pid in enumerate(tray):
    cx = W / 2 + (i - 1) * (W / 3.4)
    if pid < 0:
        s = tc
        d.rounded_rectangle([cx - s / 2, tray_y - s / 2, cx + s / 2, tray_y + s / 2], radius=s * 0.2, fill=BOARD_BG)
        continue
    pc = SHAPES[pid]
    col = COLORS[1 + (pid % 7)]
    off = (pc and max(p[0] for p in pc)) * tc / 2
    maxx = max(p[0] for p in pc); maxy = max(p[1] for p in pc)
    for (px, py) in pc:
        l = cx - maxx * tc / 2 + px * tc
        t = tray_y - maxy * tc / 2 + py * tc
        block(l, t, tc, col)

# rodapé de botões
fy = tray_y + tc * 2.4
for i, (label, w) in enumerate([("Novo jogo", 200), ("Trocar bandeja", 240), ("?", 60)]):
    x0 = (W - (200 + 240 + 60 + 40)) / 2 + sum([0, 220, 470][:i])
    d.rounded_rectangle([x0, fy, x0 + w, fy + 74], radius=18, fill=(35, 48, 74))
    tw = d.textlength(label, font=f_med)
    d.text((x0 + (w - tw) / 2, fy + 22), label, font=f_med, fill=(234, 240, 248))

out = '/home/z/my-project/download/preview_tela.png'
img.save(out)
print('salvo', out, img.size)
