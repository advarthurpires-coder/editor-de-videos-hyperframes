"""Gera assets/legendas_data.js a partir de assets/media/palavras.json.

Grupos de até 4 palavras: frases quebradas na pontuação e divididas em blocos
escolhidos por custo (prefere 3 palavras, evita terminar em palavra funcional
e passar de 1,6 s).
Palavras-chave: vermelho (golpe) e dourado (oficial), conforme o briefing.
Uso: python3 tools/gerar_legendas.py
"""
import json
import re

w = json.load(open("assets/media/palavras.json", encoding="utf-8"))

VERMELHO = r"^(urgente|golpe|falsos?|link|empr[eé]stimos?|transfer[eê]ncias?|sumiu|pressa)$"
DOURADO = r"^(advogado|desligue|pessoalmente|oficial|agenda|banco|boletim|proteger)$"


def limpa(p):
    return re.sub(r"[\"“”,.;]", "", p).upper()


def cor(p):
    b = re.sub(r"[^\wÀ-ú]", "", p).lower()
    if re.match(VERMELHO, b):
        return "r"
    if re.match(DOURADO, b):
        return "d"
    return ""


FUNCAO = set("a o e é as os do da dos das de com pra pros por no na nos nas num numa um uma meu seu sua minha "
             "ao em para pelo pela que ou se te me seus suas meus nosso nossa pro pros não esse essa".split())
FIM = r"[,.:;!?\"”]$"


def custo(bl, fim_da_frase=False):
    """Custo de um bloco: prefere 3 palavras, evita fim em palavra funcional e blocos longos/curtos."""
    n = len(bl)
    dur = bl[-1]["fim"] - bl[0]["inicio"]
    c = {1: 5.0, 2: 0.3, 3: 0.0, 4: 0.2}[n]
    if n > 1 and not fim_da_frase and limpa(bl[-1]["palavra"]).lower() in FUNCAO:
        c += 4
    if dur > 1.6:
        c += (dur - 1.6) * 6
    if dur < 0.5:
        c += 1.5
    return c


def divide(f):
    """Divisão ótima (programação dinâmica) de uma frase em blocos de 1 a 4 palavras."""
    melhor = [(0.0, [])] + [(1e9, None)] * len(f)
    for i in range(1, len(f) + 1):
        for k in range(1, 5):
            if i - k < 0:
                break
            c = melhor[i - k][0] + custo(f[i - k:i], i == len(f))
            if c < melhor[i][0]:
                melhor[i] = (c, melhor[i - k][1] + [f[i - k:i]])
    return melhor[-1][1]


# 1) frases pela pontuação (ou pausa longa)
frases, atual = [], []
for x in w:
    if atual and (re.search(FIM, atual[-1]["palavra"]) or x["inicio"] - atual[-1]["fim"] > 0.35):
        frases.append(atual)
        atual = []
    atual.append(x)
frases.append(atual)
# 2) frase de uma palavra que dura menos de 0,4 s até a próxima ("Um:") vai junto com a seguinte
f2 = []
for i, f in enumerate(frases):
    if f2 and f2[-1] is not None and len(f2[-1]) == 1 and f[0]["inicio"] - f2[-1][0]["inicio"] < 0.4:
        f2[-1] = f2[-1] + f
    else:
        f2.append(f)
# 3) blocos
fund = [bl for f in f2 for bl in divide(f)]

out = []
for k, g in enumerate(fund):
    s = g[0]["inicio"]
    prox = fund[k + 1][0]["inicio"] if k + 1 < len(fund) else None
    e = g[-1]["fim"] + 0.35
    if prox is not None:
        e = min(e, prox - 0.02)
    out.append({"s": round(s, 3), "e": round(e, 3),
                "w": [{"w": limpa(x["palavra"]), "s": round(x["inicio"], 3), "c": cor(x["palavra"])} for x in g]})

open("assets/legendas_data.js", "w", encoding="utf-8").write(
    "window.LEGENDAS = " + json.dumps(out, ensure_ascii=False) + ";\n")
tam = [len(g["w"]) for g in out]
print(len(out), "grupos; tamanhos", {n: tam.count(n) for n in sorted(set(tam))})
for g in out:
    print(f'{g["s"]:7.2f}-{g["e"]:7.2f}', " ".join(x["w"] + ("*" + x["c"] if x["c"] else "") for x in g["w"]))
