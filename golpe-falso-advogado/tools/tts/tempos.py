"""Apara silêncios de cada frase e estima o fim de cada palavra.
Kokoro não é autorregressivo: sintetiza prefixos da frase e mede onde a fala termina
(fim do último trecho acima do limiar), normalizando pela frase inteira.
Uso: python3 -I tools/tts/tempos.py <voz> <velocidade> <pasta_frases>"""
import json, os, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerar_voz import M, V, fonemas

LIM = 0.012  # limiar de silêncio (amplitude)


def borda(s, sr):
    a = np.abs(s)
    win = int(0.01 * sr)
    env = np.convolve(a, np.ones(win) / win, mode="same")
    idx = np.where(env > LIM)[0]
    return (idx[0], idx[-1]) if len(idx) else (0, len(s) - 1)


voice, speed, d = sys.argv[1], float(sys.argv[2]), sys.argv[3]
k = Kokoro(M, V)
fr = json.load(open(f"{d}/frases.json"))
for f in fr:
    s, sr = sf.read(f"{d}/f{f['i']:02d}.wav")
    a, b = borda(s, sr)
    a = max(0, a - int(0.03 * sr)); b = min(len(s), b + int(0.06 * sr))
    sf.write(f"{d}/f{f['i']:02d}.wav", s[a:b], sr)
    f["dur"] = round((b - a) / sr, 3)
    words = f["texto"].split()
    ends = []
    for n in range(1, len(words) + 1):
        ps, _ = k.create(fonemas(k, " ".join(words[:n])), voice=voice, speed=speed, lang='pt-br', is_phonemes=True)
        pa, pb = borda(ps, sr)
        ends.append((pb - a) / sr)
    for i in range(1, len(ends)):
        ends[i] = max(ends[i], ends[i - 1] + 0.06)
    sc = (f["dur"] - 0.06) / ends[-1]
    ends = [round(e * sc, 3) for e in ends]
    f["palavras"] = [{"w": w, "fim": e} for w, e in zip(words, ends)]
    print(f["i"], f["dur"], [(w, e) for w, e in zip(words, ends)])
json.dump(fr, open(f"{d}/frases.json", "w"), ensure_ascii=False, indent=1)
print("total", round(sum(x["dur"] for x in fr), 2))
