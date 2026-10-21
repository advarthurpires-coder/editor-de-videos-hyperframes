# Texturas da colagem (transições no estilo da referência): papel rasgado, folha amarela rasgada,
# recorte da dupla do flyer em retícula (halftone) e fundo amarelo com sujeira. Determinístico.
# Uso: python3 -I tools/gerar_texturas.py
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
M = f"{D}/assets/media"
rng = np.random.default_rng(2410)
AMARELO = (233, 167, 27)
CREME = (241, 233, 214)


def ruido(w, h, sigma, seed):
    r = np.random.default_rng(seed).standard_normal((h // 4 + 2, w // 4 + 2)).astype(np.float32)
    im = Image.fromarray(((r - r.min()) / (r.ptp() if hasattr(r, "ptp") else (r.max() - r.min())) * 255).astype(np.uint8))
    return np.asarray(im.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sigma)), np.float32) / 255


def borda_rasgada(n, amp, seed):
    """perfil de rasgo: soma de senoides + ruído em várias escalas"""
    r = np.random.default_rng(seed)
    x = np.arange(n)
    y = np.zeros(n)
    for f, a in [(0.004, 1.0), (0.013, 0.45), (0.05, 0.22), (0.17, 0.12)]:
        y += a * np.sin(2 * np.pi * f * x + r.uniform(0, 6.28))
    y += np.convolve(r.standard_normal(n), np.ones(3) / 3, "same") * 0.18
    return (y - y.min()) / (y.max() - y.min()) * amp


def papel(w, h, cor, rasgos=("top", "bottom"), amp=34, seed=1, fibras=True):
    """folha com bordas rasgadas (faixa branca de fibra na borda) e textura de papel; RGBA"""
    a = np.zeros((h, w), np.float32)
    top = borda_rasgada(w, amp, seed) if "top" in rasgos else np.zeros(w)
    bot = borda_rasgada(w, amp, seed + 7) if "bottom" in rasgos else np.zeros(w)
    yy = np.arange(h)[:, None]
    a = ((yy >= top[None, :]) & (yy <= h - 1 - bot[None, :])).astype(np.float32)
    # borda de fibra (papel branco aparecendo no rasgo)
    fib = ((yy >= top[None, :] - 0) & (yy < top[None, :] + 7 + 6 * ruido(w, 1, 0, seed)[0][None, :])) if "top" in rasgos else np.zeros((h, w), bool)
    fib2 = ((yy <= h - 1 - bot[None, :]) & (yy > h - 1 - bot[None, :] - 7 - 6 * ruido(w, 1, 0, seed + 3)[0][None, :])) if "bottom" in rasgos else np.zeros((h, w), bool)
    tex = ruido(w, h, 1.2, seed + 11)
    fine = np.random.default_rng(seed + 5).standard_normal((h, w)).astype(np.float32) * 0.025
    base = np.array(cor, np.float32)[None, None, :] / 255 * (0.92 + 0.12 * tex[..., None]) + fine[..., None]
    if fibras:
        base[fib | fib2] = np.array([0.97, 0.96, 0.93])
    rgba = np.dstack([np.clip(base, 0, 1) * 255, a * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    # sombra projetada leve
    sh = Image.new("RGBA", (w, h + 30), (0, 0, 0, 0))
    m = im.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.45))
    sh.paste(Image.new("RGBA", (w, h), (0, 0, 0, 255)), (0, 14), m)
    sh.alpha_composite(im, (0, 0))
    return sh


os.makedirs(M, exist_ok=True)
papel(1300, 330, CREME, seed=3).save(f"{M}/papel_faixa_a.png")
papel(1300, 280, (24, 22, 20), seed=9).save(f"{M}/papel_faixa_b.png")
papel(1200, 2300, AMARELO, rasgos=("top",), amp=60, seed=21).save(f"{M}/papel_amarelo.png")
papel(1200, 2300, CREME, rasgos=("top",), amp=60, seed=33).save(f"{M}/papel_creme.png")

# fundo amarelo do cartão (data): amarelo do flyer + sujeira + leve vinheta
W, H = 1080, 1920
t = ruido(W, H, 6, 41)
fundo = np.array(AMARELO, np.float32)[None, None, :] * (0.9 + 0.16 * t[..., None])
suj = np.asarray(Image.open(f"{M}/sujeira.png").convert("L").resize((W, H)), np.float32) / 255
fundo *= (0.84 + 0.16 * suj[..., None])
yy, xx = np.mgrid[0:H, 0:W]
v = 1 - 0.18 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2, 0, 1)
fundo *= v[..., None]
Image.fromarray(np.clip(fundo, 0, 255).astype(np.uint8)).save(f"{M}/fundo_amarelo.jpg", quality=92)

# dupla do flyer em retícula (pontos pretos sobre transparente), estilo recorte de jornal
duo = Image.open(f"{D}/assets/fotos/duo_recorte.png").convert("RGBA")
duo = duo.resize((duo.width * 3 // 2, duo.height * 3 // 2), Image.LANCZOS)
g = np.asarray(duo.convert("L"), np.float32) / 255
al = np.asarray(duo.split()[3], np.float32) / 255
g = np.clip((g - 0.5) * 1.35 + 0.5, 0, 1)
cel = 9
h2, w2 = g.shape
out = Image.new("L", (w2, h2), 0)
dr = ImageDraw.Draw(out)
ang = np.deg2rad(45)
for yy0 in range(-h2, 2 * h2, cel):
    for xx0 in range(-w2, 2 * w2, cel):
        x = xx0 * np.cos(ang) - yy0 * np.sin(ang) + w2 / 2
        y = xx0 * np.sin(ang) + yy0 * np.cos(ang) + h2 / 2
        if 0 <= x < w2 and 0 <= y < h2 and al[int(y), int(x)] > 0.5:
            r = (1 - g[int(y), int(x)]) ** 0.9 * cel * 0.72
            if r > 0.6: dr.ellipse([x - r, y - r, x + r, y + r], fill=255)
ht = Image.new("RGBA", (w2, h2), (20, 18, 16, 0)); ht.putalpha(ImageChops.multiply(out, duo.split()[3]))
# contorno de recorte (papel branco em volta)
borda = duo.split()[3].filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.GaussianBlur(1.5))
rec = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
rec.paste(Image.new("RGBA", (w2, h2), CREME + (255,)), (0, 0), borda)
rec.alpha_composite(ht)
rec.save(f"{M}/duo_reticula.png")
print("texturas ok")
