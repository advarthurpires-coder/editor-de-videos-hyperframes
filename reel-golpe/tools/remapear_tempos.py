"""Reposiciona os tempos absolutos de index.html quando a narração muda.

Usa as palavras como âncoras: um tempo T da narração antiga vira o tempo
correspondente na nova, por interpolação linear entre os inícios/fins das
palavras (as duas narrações têm o mesmo texto, palavra por palavra).

Mapeia: data-start/data-duration (início e fim de cada clipe), o tempo de posição
dos tweens (`}, T)` e `}, T + ...`), e o argumento de tempo dos helpers do script
(fin, fout, swap, glitch, strike, cartela, chapter, msg, tap, voa, check).
Durações de tween não mudam.

Uso: python3 tools/remapear_tempos.py palavras_antigas.json assets/media/palavras.json index.html
"""
import json
import re
import sys

import numpy as np

antigas = json.load(open(sys.argv[1], encoding="utf-8"))
novas = json.load(open(sys.argv[2], encoding="utf-8"))
html_path = sys.argv[3]
assert [a["palavra"] for a in antigas] == [n["palavra"] for n in novas], "textos diferentes"

xa, xn = [], []
for a, n in zip(antigas, novas):
    xa += [a["inicio"], a["fim"]]
    xn += [n["inicio"], n["fim"]]
xa, xn = np.array(xa), np.array(xn)
ordem = np.argsort(xa, kind="stable")
xa, xn = xa[ordem], np.maximum.accumulate(xn[ordem])


def mapa(t):
    if t <= xa[0]:
        return t + (xn[0] - xa[0]) if t > 0 else t
    if t >= xa[-1]:
        return t + (xn[-1] - xa[-1])
    return float(np.interp(t, xa, xn))


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".") if v != int(v) else str(int(v))


s = open(html_path, encoding="utf-8").read()

# 1) clipes: data-start + data-duration (início e fim mapeados)
def clipe(m):
    ini, dur = float(m.group(2)), float(m.group(4))
    ni, nf = mapa(ini), mapa(ini + dur)
    if m.group(0).find("<audio") >= 0 and "sfx" in m.group(0):
        nf = ni + dur  # efeito sonoro: mantém a própria duração
    return f'{m.group(1)}{fmt(ni)}{m.group(3)}{fmt(round(nf - ni, 2))}"'


s = re.sub(r'(<[^>]*?data-start=")([\d.]+)("\s+data-duration=")([\d.]+)"', clipe, s)

corpo_ini = s.index("<script>", s.index("<body"))
cab, scr = s[:corpo_ini], s[corpo_ini:]

# 2) posição dos tweens
scr = re.sub(r"\}, (\d+(?:\.\d+)?)\)", lambda m: "}, " + fmt(mapa(float(m.group(1)))) + ")", scr)
scr = re.sub(r"\}, (\d+(?:\.\d+)?) \+", lambda m: "}, " + fmt(mapa(float(m.group(1)))) + " +", scr)
# 3) helpers: segundo argumento (ou terceiro em swap/tap) é tempo absoluto
pos2 = r"(\b(?:fin|fout|glitch|strike|cartela|chapter|msg|voa|check)\((?:\"[^\"]*\"|'[^']*'|\[[^\]]*\]|\d+), )(\d+(?:\.\d+)?)"
scr = re.sub(pos2, lambda m: m.group(1) + fmt(mapa(float(m.group(2)))), scr)
pos3 = r"(\b(?:swap|tap)\(\"[^\"]*\", \"[^\"]*\", )(\d+(?:\.\d+)?)"
scr = re.sub(pos3, lambda m: m.group(1) + fmt(mapa(float(m.group(2)))), scr)

open(html_path, "w", encoding="utf-8").write(cab + scr)
for t in (0.38, 10.69, 17.19, 28.95, 46.54, 59.43, 84.25, 95.61, 102.78, 108.3):
    print(f"{t:7.2f} -> {mapa(t):7.2f}")
