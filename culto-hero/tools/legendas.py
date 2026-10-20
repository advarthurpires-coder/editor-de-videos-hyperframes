"""Tempo de cada palavra da locução + dados de legenda para a composição.

Alinhamento sem rede (o ASR exigiria baixar modelos):
  1. por frase, envelope RMS (10 ms) do arquivo da frase; início/fim da voz;
  2. pausas internas (vírgula, dois-pontos, ponto) = os maiores silêncios detectados, em ordem;
  3. dentro de cada trecho, fronteiras proporcionais ao número de fonemas de cada palavra,
     ajustadas para o vale de energia mais próximo (±90 ms).
Saídas: assets/legendas_data.js (window.LEGENDAS = blocos com tempo de cada palavra)
        assets/tempos_data.js   (window.TEMPOS = início/fim absoluto de cada palavra de cada frase)
Uso: python3 -I tools/legendas.py assets/media/voz
"""
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roteiro import BLOCOS, DESTAQUE, INICIO  # noqa: E402
from kokoro_onnx import Kokoro  # noqa: E402

VOZ_DIR = sys.argv[1]
k = Kokoro(os.path.expanduser("~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx"),
           os.path.expanduser("~/.cache/hyperframes/tts/voices/voices-v1.0.bin"))
NUM = {"24,": "vinte e quatro,", "3083.": "três mil e oitenta e três."}


def n_fonemas(w):
    ph = k.tokenizer.phonemize(NUM.get(w, w), "pt-br")
    return max(1, len(re.sub(r"[ˈˌ.,:;!?…\s]", "", ph)))


frases = json.load(open(f"{VOZ_DIR}/frases.json"))
tempos = []
for f, t0 in zip(frases, INICIO):
    s, sr = sf.read(f"{VOZ_DIR}/f{f['i']:02d}.wav")
    hop = sr // 100
    env = np.sqrt(np.convolve(s ** 2, np.ones(hop) / hop, "same"))[::hop]
    lim = max(0.012, env.max() * 0.06)
    voz = env > lim
    a, b = np.argmax(voz), len(voz) - np.argmax(voz[::-1])
    # silêncios internos (>= 60 ms)
    gaps = []
    i = a
    while i < b:
        if not voz[i]:
            j = i
            while j < b and not voz[j]:
                j += 1
            if j - i >= 6:
                gaps.append((j - i, i, j))
            i = j
        else:
            i += 1
    words = f["texto"].split()
    quebras = [ix for ix, w in enumerate(words[:-1]) if re.search(r"[,:.;…]$", w)]
    # posição esperada de cada pausa (fonemas + peso da pausa) e escolha da maior pausa por perto
    pw = np.array([n_fonemas(w) + (4 if ix in quebras else 0) for ix, w in enumerate(words)], float)
    esper = a + np.cumsum(pw) / pw.sum() * (b - a)
    usadas, q_ok = [], []
    for q in quebras:
        cand = [g for g in gaps if abs((g[1] + g[2]) / 2 - esper[q]) < 45 and g not in usadas
                and (not usadas or g[1] > usadas[-1][2])]
        if cand:
            g = max(cand, key=lambda g: g[0] - 0.05 * abs((g[1] + g[2]) / 2 - esper[q]))
            usadas.append(g)
            q_ok.append(q)
    quebras, gaps = q_ok, usadas
    # trechos (índices de palavras) e janelas de tempo correspondentes
    lims_w = [0] + [q + 1 for q in quebras] + [len(words)]
    lims_t = [a] + [x for g in gaps for x in (g[1], g[2])] + [b]
    ini = [0.0] * len(words)
    fim = [0.0] * len(words)
    for seg in range(len(lims_w) - 1):
        ws = list(range(lims_w[seg], lims_w[seg + 1]))
        ta, tb = lims_t[2 * seg], lims_t[2 * seg + 1]
        pesos = np.array([n_fonemas(words[w]) for w in ws], float)
        cum = np.concatenate([[0], np.cumsum(pesos)]) / pesos.sum()
        bord = ta + cum * (tb - ta)
        for q in range(1, len(bord) - 1):  # encaixa no vale de energia mais próximo
            c = int(round(bord[q]))
            lo, hi = max(ta + 1, c - 9), min(tb - 1, c + 9)
            if hi > lo:
                bord[q] = lo + np.argmin(env[lo:hi])
        for q, w in enumerate(ws):
            ini[w] = bord[q] / 100
            fim[w] = bord[q + 1] / 100
    tempos.append({"i": f["i"], "texto": f["texto"], "ini": round(t0 + a / 100, 3), "fim": round(t0 + b / 100, 3),
                   "palavras": [{"w": w, "s": round(t0 + x, 3), "e": round(t0 + y, 3)} for w, x, y in zip(words, ini, fim)]})

with open("assets/tempos_data.js", "w") as fh:
    fh.write("window.TEMPOS = " + json.dumps(tempos, ensure_ascii=False) + ";\n")

leg = []
for tf in tempos:
    bl = BLOCOS[tf["i"]]
    if not bl:
        continue
    pal = tf["palavras"]
    kk = 0
    blocos = []
    for txt in bl:
        item = {"w": []}
        for wtxt in txt.split():
            assert pal[kk]["w"] == wtxt, (pal[kk]["w"], wtxt)
            item["w"].append({"t": wtxt, "s": pal[kk]["s"], "h": wtxt in DESTAQUE})
            kk += 1
        item["s"] = item["w"][0]["s"]
        blocos.append(item)
    assert kk == len(pal)
    for x, y in zip(blocos, blocos[1:]):
        x["e"] = y["s"]
    blocos[-1]["e"] = round(tf["fim"] + 0.3, 3)
    leg += blocos
with open("assets/legendas_data.js", "w") as fh:
    fh.write("window.LEGENDAS = " + json.dumps(leg, ensure_ascii=False) + ";\n")

for tf in tempos:
    print(tf["i"], " ".join(f"{p['w']}@{p['s']:.2f}" for p in tf["palavras"]))
print("legendas:", len(leg), "blocos")
