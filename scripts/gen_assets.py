#!/usr/bin/env python3
"""Gera ícone (PNGs em 6 densidades) e sons WAV sintetizados do Bloco Livre."""
import math, os, struct, wave

BASE = "/home/z/my-project/app/res"
OUT = "/home/z/my-project/app/gen"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- ícone
def icon(size):
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # fundo arredondado azul-escuro
    r = size * 0.22
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=(16, 20, 28, 255))
    # grade sutil
    g = size * 0.04
    d.rectangle([g, g, size - 1 - g, size - 1 - g], outline=(42, 54, 72, 255))
    # blocos vivos (2x2 + peça L) — cores da paleta do jogo
    cols = [(79, 195, 247), (255, 183, 77), (186, 104, 200), (129, 199, 132), (255, 213, 79)]
    cell = size / 5.2
    ox = (size - cell * 4) / 2
    oy = (size - cell * 4) / 2
    def block(x, y, c, s=0.94):
        p = cell * (1 - s) / 2
        x0 = ox + x * cell + p; y0 = oy + y * cell + p
        d.rounded_rectangle([x0, y0, x0 + cell * s, y0 + cell * s], radius=cell * 0.2, fill=c + (255,))
    block(0, 0, cols[0]); block(1, 0, cols[1]); block(2, 0, cols[2]); block(3, 0, cols[3])
    block(0, 1, cols[1]); block(1, 1, cols[4]); block(2, 1, cols[0]); block(3, 1, cols[1])
    block(0, 2, cols[2]); block(1, 2, cols[3]); block(2, 2, cols[4]); block(3, 2, cols[2])
    block(0, 3, cols[3]); block(1, 3, cols[2]); block(2, 3, cols[1]); block(3, 3, cols[0])
    return img

for dpi, size in [("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)]:
    p = f"{BASE}/mipmap-{dpi}"
    os.makedirs(p, exist_ok=True)
    icon(size).save(f"{p}/ic_launcher.png")

# ---------------------------------------------------------------- sons (WAV 16-bit mono 22050 Hz, sintetizados)
SR = 22050
def write_wav(name, samples):
    with wave.open(f"{OUT}/{name}.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples))

def env(t, dur, a=0.005, r=0.06):
    at = min(1.0, t / a) if a > 0 else 1.0
    rel = max(0.0, 1.0 - max(0.0, t - (dur - r)) / r) if t < dur else 0.0
    return at * rel

def tone(dur, f0, f1=None, vol=0.5, shape="sine"):
    n = int(SR * dur)
    f1 = f0 if f1 is None else f1
    out = []
    ph = 0.0
    for i in range(n):
        t = i / SR
        f = f0 + (f1 - f0) * (t / dur)
        ph += 2 * math.pi * f / SR
        s = math.sin(ph)
        if shape == "tri":
            s = 2 / math.pi * math.asin(math.sin(ph))
        out.append(s * env(t, dur) * vol)
    return out

# place: "toc" curto de madeira (duas senoides rápidas + decaimento)
place = [0.0] * 0
for f, v in [(660, 0.35), (990, 0.18)]:
    place += tone(0.09, f, f * 0.82, v)
place = place[:int(SR * 0.09)]
write_wav("place", place)

# clear: arpejo alegre curto (C-E-G) 
clear = []
for i, f in enumerate([523, 659, 784]):
    clear += tone(0.07, f, f, 0.4, "tri")
clear += tone(0.12, 1046, 1046, 0.35, "tri")
write_wav("clear", clear)

# combo: fanfarra pequena
combo = []
for i, (f, d) in enumerate([(587, 0.08), (740, 0.08), (880, 0.08), (1175, 0.16)]):
    combo += tone(d, f, f, 0.42, "tri")
write_wav("combo", combo)

# over: descida suave (não punitiva)
over = tone(0.5, 440, 220, 0.4) + tone(0.4, 330, 165, 0.3)
write_wav("over", over)

# bad: blip grave curto
bad = tone(0.12, 200, 160, 0.3)
write_wav("bad", bad)

print("icones + sons gerados em", OUT)
for f in sorted(os.listdir(OUT)):
    print(" ", f, os.path.getsize(f"{OUT}/{f}"), "bytes")
for dpi in ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]:
    p = f"{BASE}/mipmap-{dpi}/ic_launcher.png"
    print(" ", p, os.path.getsize(p), "bytes")
