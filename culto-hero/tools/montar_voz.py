"""Posiciona as 20 frases da locução nos tempos de roteiro.py -> assets/media/voz_master.wav (48 kHz, estéreo).
EQ leve: passa-altas 75 Hz, presença 2–5 kHz e um pouco de corpo em 120–250 Hz (voz de "aviso", grave).
Uso: python3 -I tools/montar_voz.py assets/media/voz
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_util import hp, load, lp, put, wav  # noqa: E402
from roteiro import INICIO, SR, TOTAL  # noqa: E402
import numpy as np  # noqa: E402

VOZ_DIR = sys.argv[1]
N = int(TOTAL * SR)
frases = json.load(open(f"{VOZ_DIR}/frases.json"))
voz = np.zeros((N, 2))
for f, t0 in zip(frases, INICIO):
    s = load(f"{VOZ_DIR}/f{f['i']:02d}.wav")[:, 0]
    s = hp(s, 75)
    pres = hp(lp(s, 5000), 2000)
    corpo = hp(lp(s, 250), 120)
    s = s + 0.2 * pres + 0.35 * corpo
    put(voz, s, t0)
voz = voz / np.abs(voz).max() * 0.5
wav("assets/media/voz_master.wav", voz)
for f, t0 in zip(frases, INICIO):
    print(f"frase {f['i']:2d}: {t0:6.2f} -> {t0 + f['dur']:6.2f}  {f['texto']}")
