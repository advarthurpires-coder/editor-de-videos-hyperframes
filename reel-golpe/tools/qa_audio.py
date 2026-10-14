"""Verifica o áudio do render contra a narração tratada.

1) Alinha a narração ao mix e estima o ganho dela (deve ser ~1,0 = 100%).
2) Subtrai a voz: o resíduo é trilha + efeitos. Mede quanto a trilha fica
   abaixo da voz nos trechos falados (meta: ~20 dB).
Uso: python3 -I tools/qa_audio.py renders/reel_golpe_falso_advogado.mp4 assets/media/narracao_tratada.wav
"""
import json
import subprocess
import sys

import numpy as np

SR = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


mix, voz = load(sys.argv[1]), load(sys.argv[2])
n = min(len(mix), len(voz))
mix, voz = mix[:n], voz[:n]
seg = slice(int(1 * SR), int(30 * SR))
best = (0, -1)
for lag in range(-2400, 2401, 4):
    c = np.dot(mix[seg], np.roll(voz, lag)[seg])
    if c > best[1]:
        best = (lag, c)
lag = best[0]
v = np.roll(voz, lag)
g = np.dot(mix[seg], v[seg]) / np.dot(v[seg], v[seg])
res = mix - g * v


def db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


w = json.load(open("assets/media/palavras.json", encoding="utf-8"))
fala = np.zeros(n, bool)
for x in w:
    fala[int(x["inicio"] * SR):int(x["fim"] * SR)] = True
print(f"atraso voz->mix: {lag / SR * 1000:.2f} ms | ganho da voz no mix: {g:.3f} ({20 * np.log10(g):+.2f} dB)")
for a, b, nome in [(0, 59.4, "cenas 1-5 (tensa)"), (59.4, 108.3, "cenas 6-9 (calma)")]:
    m = fala.copy()
    m[: int(a * SR)] = False
    m[int(b * SR):] = False
    print(f"{nome}: voz {db(g * v[m]):.1f} dBFS | trilha+efeitos durante a fala {db(res[m]):.1f} dBFS | abaixo da voz {db(g * v[m]) - db(res[m]):.1f} dB")
