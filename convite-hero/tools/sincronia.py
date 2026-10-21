# Legendas palavra a palavra e momentos dos elementos gráficos, do tempo da gravação para o tempo do reel.
# Grava assets/sincronia.js (window.SYNC) e tools/eventos.json (eventos + efeitos sonoros, para a mixagem).
# Texto: tempos de início por palavra (Parakeet v3, conferidos com Whisper medium e com a energia do áudio).
# Marcação: *palavra* = amarelo (termo-chave) · "/" fecha um bloco de legenda (1 ou 2 palavras, como na referência).
# Uso: python3 -I tools/sincronia.py
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roteiro import SEGS, FIM_FALA, FLYER, CARTELA, TOTAL, BEAT, o  # noqa: E402

D = os.path.dirname(os.path.abspath(__file__)) + "/.."

FALA = """
2.10 Fala, /
2.80 meus 3.08 irmãos, /
3.58 *graça* /
3.98 e 4.18 *paz!* /
5.14 Que 5.30 *Deus* /
5.46 abençoe /
6.02 vocês! /
6.88 Irmãos, /
7.26 venho 7.50 aqui /
7.66 fazer 7.88 um /
7.98 *convite* /
8.46 muito /
8.70 *especial* /
9.26 para 9.50 vocês, /
9.96 *HOMENS!* /
11.20 Vai /
11.42 acontecer /
11.90 aqui 12.12 em /
12.28 *Patrocínio* /
13.46 na 13.66 Batista /
16.08 o 16.30 nosso /
16.78 *primeiro* /
17.18 culto /
17.64 do /
19.00 Eu 19.12 quero /
19.30 fazer 19.46 um /
19.54 *convite* /
19.90 muito /
20.06 *especial* /
20.44 para 20.60 vocês. /
21.26 Dia 21.56 *24* /
22.12 de 22.28 *outubro* /
23.10 às 23.48 *19h30* /
25.68 *VEM!* /
"""

blocos = []
for bl in FALA.split("/"):
    ws = re.findall(r"([\d.]+)\s+(\S+)", bl)
    if not ws: continue
    pal = []
    for t, w in ws:
        pal.append({"t": o(float(t)), "w": w.replace("*", ""), "c": "k" if "*" in w else ""})
    blocos.append({"s": pal[0]["t"], "p": pal})

# momentos (tempo da gravação), convertidos para o reel
EV_SRC = {
    "homens": 9.96, "pin": 12.28, "batista": 13.66, "lagoinha": 14.28,
    "hero": 17.80, "dia": 21.26, "outubro": 22.28, "hora": 23.48, "vem": 25.68,
}
EV = {k: o(v) for k, v in EV_SRC.items()}
EV["seg"] = [s["out"] for s in SEGS]          # início de cada trecho
EV["papel"] = SEGS[5]["out"]                  # colagem: Lagoinha -> "primeiro culto do HERO"
EV["cartao"] = SEGS[7]["out"]                 # vídeo vira cartão + flyer (data)
EV["cartao_fim"] = SEGS[8]["out"]             # volta à tela cheia no "Vem!"
EV["flyer"] = FLYER
EV["cartela"] = CARTELA
EV["total"] = TOTAL
# o "na Batista" sai quando a logo entra; nenhum bloco fica na tela durante logo/HERO/flyer
OCULTA = [(EV["lagoinha"] - 0.02, SEGS[5]["out"] + 0.02), (EV["hero"] - 0.02, SEGS[6]["out"] + 0.02)]

# fim de cada bloco: até o próximo começar (máx. 0,9 s parado), cortado pelos intervalos ocultos
for i, b in enumerate(blocos):
    prox = blocos[i + 1]["s"] if i + 1 < len(blocos) else FIM_FALA
    fim = min(prox, b["p"][-1]["t"] + 0.9)
    if prox - fim < 0.25: fim = prox
    for a, z in OCULTA:
        if b["s"] < a < fim: fim = a
    b["e"] = round(min(fim, FIM_FALA), 3)
    b["modo"] = "cartao" if EV["cartao"] <= b["s"] < EV["cartao_fim"] else ""

# efeitos sonoros: (arquivo em assets/sfx, tempo no reel, ganho dB)
SFX = [
    ("whoosh", 0.00, -20),
] + [("whoosh", EV["seg"][i] - 0.08, -24) for i in (1, 2, 3, 4, 6)] + [
    ("pop", EV["homens"] - 0.02, -15), ("impact-bass-1", EV["homens"] - 0.03, -17),
    ("pop", EV["pin"] + 0.05, -14), ("click-soft", EV["pin"] + 0.30, -16),
    ("whoosh", EV["lagoinha"] - 0.12, -17), ("sparkle", EV["lagoinha"] + 0.05, -16),
    ("rasgo", EV["papel"] - 0.30, -10), ("whoosh", EV["papel"] - 0.25, -16), ("rasgo", EV["papel"] + 0.08, -12),
    ("impact-bass-2", EV["hero"] - 0.03, -12), ("carimbo", EV["hero"] - 0.01, -12),
    ("whoosh", EV["cartao"] - 0.10, -15), ("rasgo", EV["cartao"] + 0.02, -15), ("pop", EV["cartao"] + 0.18, -14),
    ("click", EV["dia"] + 0.0, -16), ("click", EV["outubro"], -16), ("pop", EV["hora"], -13), ("sparkle", EV["hora"] + 0.04, -18),
    ("whoosh", EV["cartao_fim"] - 0.12, -14),
    ("impact-bass-1", EV["vem"] - 0.03, -11),
    ("rasgo", FLYER - 0.22, -9), ("whoosh", FLYER - 0.2, -14),
    ("sparkle", FLYER + 0.6, -18),
    ("whoosh", CARTELA - 0.15, -15), ("carimbo", CARTELA + 0.18, -11),
    ("click", CARTELA + 1.00, -20), ("click-soft", CARTELA + 1.10, -20), ("click", CARTELA + 1.22, -20), ("click-soft", CARTELA + 1.33, -21),
    ("click", CARTELA + 1.45, -20), ("click-soft", CARTELA + 1.58, -21), ("pop", CARTELA + 2.05, -15),
]

# rosto em coordenadas de saída (para posicionar a legenda acima da cabeça e o pino)
LT = json.load(open(f"{D}/tools/linha_tempo.json"))
SYNC = {"total": TOTAL, "fim_fala": FIM_FALA, "leg": blocos, "ev": EV, "rosto": LT["rosto"], "beat": BEAT}
with open(f"{D}/assets/sincronia.js", "w") as fh:
    fh.write("// gerado por tools/sincronia.py — não editar à mão\nwindow.SYNC = ")
    json.dump(SYNC, fh, ensure_ascii=False, separators=(",", ":"))
    fh.write(";\n")
json.dump({"total": TOTAL, "segs": SEGS, "ev": EV, "sfx": SFX}, open(f"{D}/tools/eventos.json", "w"), indent=1)
print("blocos", len(blocos), "| total", TOTAL)
for b in blocos: print(f"  {b['s']:6.2f}-{b['e']:6.2f} {b['modo']:7s}", " ".join(p["w"] for p in b["p"]))
for k, v in EV.items():
    if not isinstance(v, list): print(f"  {k:12s} {v}")
