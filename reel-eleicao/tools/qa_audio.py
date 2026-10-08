"""Verifica o áudio do render contra a trilha de voz mestre.

1) Alinha a voz mestre ao mix e estima o ganho dela (deve ser ~1,0 = 100%).
2) Subtrai a voz: o resíduo é trilha + efeitos (+ ruído do AAC).
   - Em 0–14,4 s (recortes dos candidatos) o resíduo deve ser quase silêncio:
     prova de que os vídeos estão mudos (sem eco/duplicação).
   - De 14,9 a 86,3 s mede a trilha+efeitos em relação à voz.
Uso: python3 -I tools/qa_audio.py renders/reel.mp4 assets/media/03_trilha_voz_master.wav
"""
import subprocess
import sys

import numpy as np

SR = 48000


def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


mix = load(sys.argv[1])
voz = load(sys.argv[2])
n = min(len(mix), len(voz))
mix, voz = mix[:n], voz[:n]

# atraso (busca em ±50 ms) por correlação cruzada nos primeiros 12 s
seg = slice(int(1 * SR), int(12 * SR))
best = (0, -1)
for lag in range(-2400, 2401, 4):
    c = np.dot(mix[seg], np.roll(voz, lag)[seg])
    if c > best[1]:
        best = (lag, c)
lag = best[0]
for l2 in range(lag - 4, lag + 5):
    c = np.dot(mix[seg], np.roll(voz, l2)[seg])
    if c > best[1]:
        best = (l2, c)
lag = best[0]
v = np.roll(voz, lag)
g = np.dot(mix[seg], v[seg]) / np.dot(v[seg], v[seg])
res = mix - g * v


def db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def win(a, b):
    return slice(int(a * SR), int(b * SR))


print(f"atraso voz->mix: {lag / SR * 1000:.2f} ms | ganho estimado da voz no mix: {g:.3f} ({20 * np.log10(g):+.2f} dB)")
a = win(0.2, 14.4)
v = g * v
print(f"0–14,4 s  voz {db(v[a]):.1f} dBFS | resíduo {db(res[a]):.1f} dBFS | diferença {db(v[a]) - db(res[a]):.1f} dB (alto = sem eco)")
b = win(14.9, 86.3)
print(f"14,9–86,3 s voz {db(v[b]):.1f} dBFS | trilha+efeitos {db(res[b]):.1f} dBFS | trilha abaixo da voz {db(v[b]) - db(res[b]):.1f} dB")
