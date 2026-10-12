"""Texturas procedurais determinísticas: grão de filme (tile 512 px, alfa) e papel (1080x1920).
Uso: python3 -I tools/gerar_texturas.py assets/media"""
import sys
import numpy as np
from PIL import Image, ImageFilter

out = sys.argv[1]
rng = np.random.default_rng(3)
# grão: ruído gaussiano em cinza médio com alfa — usado em mix-blend overlay
g = np.clip(128 + rng.standard_normal((512, 512)) * 46, 0, 255).astype(np.uint8)
Image.fromarray(np.dstack([g, g, g, np.full_like(g, 255)]), "RGBA").save(f"{out}/grao.png", optimize=True)
# papel: fibras + manchas suaves, tons quentes em torno de #EEEAE2
h, w = 1920, 1080
base = rng.standard_normal((h // 8, w // 8))
manchas = np.array(Image.fromarray(((base - base.min()) / np.ptp(base) * 255).astype(np.uint8))
                   .resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40)), dtype=float) / 255
fibra = rng.standard_normal((h, w))
fibra = np.array(Image.fromarray(np.clip(128 + fibra * 60, 0, 255).astype(np.uint8))
                 .filter(ImageFilter.BoxBlur(1)), dtype=float) / 255
lum = 0.5 + (manchas - 0.5) * 0.5 + (fibra - 0.5) * 0.35
a = np.clip(np.abs(lum - 0.5) * 2 * 255 * 0.9, 0, 255).astype(np.uint8)
escuro = (lum < 0.5)
r = np.where(escuro, 120, 255); gg = np.where(escuro, 104, 252); b = np.where(escuro, 80, 244)
Image.fromarray(np.dstack([r, gg, b, a]).astype(np.uint8), "RGBA").save(f"{out}/papel.png", optimize=True)
print("ok")
