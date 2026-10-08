"""Texturas procedurais (determinísticas) do reel 2º HERO EXTREME.
Uso: python3 -I tools/gerar_texturas.py assets/media"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(2026_11_20)


def fbm(h, w, octaves=6, base=4, seed=0):
    r = np.random.default_rng(seed)
    acc = np.zeros((h, w)); amp = 1.0; tot = 0
    for o in range(octaves):
        n = base * 2 ** o
        g = r.random((n + 1, int(n * w / h) + 2))
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += amp * np.asarray(im, float) / 255; tot += amp; amp *= 0.5
    return acc / tot


def save_rgba(rgb, a, path):
    a = np.clip(a, 0, 1)
    arr = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), (a * 255).astype(np.uint8)])
    Image.fromarray(arr, "RGBA").save(path, optimize=True)

# 1) grão de película (tile 1024, cinza neutro com alpha)
g = rng.normal(0, 1, (1024, 1024))
g = np.asarray(Image.fromarray(((g * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), float)
d = (g - 128) / 128
rgb = np.where(d[..., None] > 0, 255, 0) * np.ones(3)
save_rgba(rgb, np.abs(d) * 0.9, f"{out}/grao.png")

# 2) pincelada laranja seca (faixa da cartela)
H, W = 420, 1400
y = np.linspace(-1, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
edge = fbm(H, W, 6, 3, 11)
top = -0.62 + 0.16 * (fbm(1, W, 5, 6, 12)[0] - 0.5) * 2
bot = 0.62 + 0.16 * (fbm(1, W, 5, 6, 13)[0] - 0.5) * 2
band = ((y > top) & (y < bot)).astype(float)
# fibras da cerda (riscos horizontais)
fib = np.asarray(Image.fromarray((rng.random((H, 60)) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), float) / 255
dry = (fib * 0.55 + edge * 0.6) > 0.42
# bordas esfarrapadas nas pontas
ends = np.clip(np.minimum(x / 0.06, (1 - x) / 0.07), 0, 1)
ragged = (edge + 0.35 * fib) > (1 - ends) * 0.95
alpha = band * dry * ragged
# dentro da faixa, quase sólido; falhas mais nas bordas
inner = (np.abs(y) < 0.42).astype(float)
alpha = np.maximum(alpha, inner * (fib * 0.4 + edge * 0.7 > 0.33) * ragged)
alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), float) / 255
c1 = np.array([214, 91, 22]); c2 = np.array([244, 122, 22]); c3 = np.array([245, 160, 20])
t = (fbm(H, W, 5, 2, 14))[..., None]
rgb = c1 * (1 - t) + c2 * t
rgb = rgb + (c3 - c2) * np.clip((x[..., None] - 0.55) * 1.2, 0, 1) * 0.6
rgb = rgb * (0.82 + 0.25 * fib[..., None])
save_rgba(rgb, alpha, f"{out}/pincelada_laranja.png")

# 3) sujeira grunge (manchas + arranhões) para sobreposição, preto com alpha
H, W = 1920, 1080
n = fbm(H, W, 7, 3, 21)
spots = np.clip((n - 0.58) * 4, 0, 1) * 0.55
specks = (rng.random((H, W)) > 0.9993).astype(float)
specks = np.asarray(Image.fromarray((specks * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.7)), float) / 255
scr = np.zeros((H, W))
for _ in range(38):
    x0 = rng.integers(0, W); y0 = rng.integers(0, H); L = rng.integers(80, 520); ang = rng.normal(1.5708, 0.12)
    for s in range(L):
        xx = int(x0 + np.cos(ang) * s); yy = int(y0 + np.sin(ang) * s)
        if 0 <= xx < W and 0 <= yy < H: scr[yy, xx] = 0.5 + 0.5 * rng.random()
scr = np.asarray(Image.fromarray((scr * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), float) / 255
a = np.clip(spots + specks * 0.8, 0, 1)
save_rgba(np.zeros((H, W, 3)), a, f"{out}/sujeira.png")
save_rgba(np.full((H, W, 3), 245), np.clip(scr * 0.7 + specks * 0.5, 0, 1), f"{out}/arranhoes.png")

# 4) fumaça/névoa macia (branco com alpha)
H, W = 1200, 1200
n = fbm(H, W, 7, 2, 37)
yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
a = np.clip((n - 0.38) * 2.2, 0, 1) * np.clip(1 - r, 0, 1) ** 1.2
save_rgba(np.full((H, W, 3), 255), a, f"{out}/fumaca.png")

# 5) textura de tinta desgastada para letreiro (máscara branca com falhas)
H, W = 600, 1400
n = fbm(H, W, 7, 4, 41)
fib = np.asarray(Image.fromarray((rng.random((H, 90)) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), float) / 255
holes = ((n * 0.8 + fib * 0.3) > 0.36).astype(float)
holes = np.asarray(Image.fromarray((holes * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), float) / 255
save_rgba(np.full((H, W, 3), 255), holes, f"{out}/tinta_desgastada.png")
print("ok")
