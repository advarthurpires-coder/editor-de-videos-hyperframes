"""Procura cores proibidas (vermelho, verde, azul saturado) nos quadros do render.

Amostra 1 quadro por segundo. Para 0–14,56 s (recortes dos candidatos) ignora a
área dos cards, cujo conteúdo é o vídeo original e não pode ser alterado.
Uso: python3 -I tools/qa_cores.py renders/reel.mp4
"""
import subprocess
import sys

import numpy as np

W, H = 270, 480
raw = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", sys.argv[1], "-vf", f"fps=1,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
    check=True, capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)

rgb = frames.astype(np.float32) / 255.0
mx, mn = rgb.max(-1), rgb.min(-1)
s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
v = mx
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
d = np.maximum(mx - mn, 1e-6)
h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
strong = (s > 0.55) & (v > 0.35)
red = strong & ((h < 15) | (h > 340))
green = strong & (h > 75) & (h < 165)
blue = strong & (h > 200) & (h < 250) & (v > 0.55)

ok = True
for i in range(len(frames)):
    mask = np.ones((H, W), bool)
    if i <= 14:  # área dos cards com os recortes originais
        mask[90:330, :] = False
    fr, fg, fb = ((x[i] & mask).mean() * 100 for x in (red, green, blue))
    if max(fr, fg, fb) > 0.05:
        ok = False
        print(f"t={i}s vermelho {fr:.2f}% verde {fg:.2f}% azul {fb:.2f}%")
print("nenhuma cor proibida fora dos recortes" if ok else "ATENÇÃO: cores proibidas encontradas")
