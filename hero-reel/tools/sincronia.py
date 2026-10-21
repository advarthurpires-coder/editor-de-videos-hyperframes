# Legendas palavra a palavra e momentos dos elementos gráficos/3D, do tempo da gravação para o tempo do reel.
# Grava assets/sincronia.js (window.SYNC) e tools/eventos.json (eventos + efeitos sonoros, para a mixagem).
# Texto: inícios de palavra do Parakeet v3, conferidos com Whisper medium e com a energia do áudio.
# Marcação: *palavra* = termo-chave (amarelo + palavra gigante atrás da pessoa) · "/" fecha um bloco de legenda.
# Estilo da palavra gigante em CHAVE: "g" = gótica (UnifrakturCook, como o H do HERO) · "a" = Anton.
# Uso: python3 -I tools/sincronia.py
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roteiro import SEGS, FIM_FALA, TOTAL, BEAT, o  # noqa: E402

D = os.path.dirname(os.path.abspath(__file__)) + "/.."

FALA = """
0.80 Meus 1.20 *irmãos,* /
1.68 a 1.84 paz 2.08 do /
2.24 Senhor /
2.64 *Jesus!* /
3.12 Deus 3.36 que /
3.52 abençoe /
4.08 a 4.16 vida 4.40 de /
4.48 vocês. /
5.08 Estou 5.36 aqui /
5.52 para 5.68 te /
5.84 fazer 6.16 um /
6.32 *convite,* /
7.52 um 7.68 convite /
8.16 muito /
8.32 *especial.* /
9.16 Deus 9.36 tem 9.52 um /
9.68 *encontro* /
10.16 com 10.32 você /
10.56 no 10.72 dia /
10.96 *24,* /
11.98 na 12.08 igreja /
12.56 Batista /
13.20 *Lagoinha.* /
14.88 Que 15.04 você /
15.36 possa 15.84 vir, /
16.48 traga 16.88 um /
17.04 *amigo,* /
17.98 traga 18.24 um /
18.40 *parente* /
19.32 e 19.44 venha /
19.84 aqui /
20.24 *adorar* /
20.64 ao 20.88 Senhor, /
21.98 falar 22.24 um /
22.40 pouco 22.72 de /
22.88 *Jesus,* /
23.44 ouvir 24.00 a /
24.08 *palavra* /
24.48 de 24.56 Deus, /
24.96 adorar 25.60 o /
25.76 *Todo-Poderoso,* /
26.80 o 26.96 *Grandão* /
27.60 da 27.68 *Galileia.* /
28.58 E 28.70 que 28.80 o /
28.86 Senhor /
29.12 possa 29.44 falar /
29.68 neste 30.08 dia /
30.40 *grandemente* /
30.88 com 31.04 você. /
31.60 Você 31.84 é /
32.00 o 32.16 nosso /
32.40 *convidado* /
32.96 *especial.* /
34.32 Deus 34.48 que /
34.64 abençoe /
35.28 você, /
35.76 esteja 36.16 com /
36.32 a 36.48 gente /
36.80 nessa /
37.20 *noite.* /
37.92 *Amém?* /
38.48 Vamos /
38.80 *junto!* /
"""

# palavra gigante atrás da pessoa: (palavra marcada, ordem da ocorrência) -> estilo, texto exibido
CHAVE = {
    ("irmãos", 0): ("a", "IRMÃOS"),
    ("jesus", 0): ("g", "Jesus"),
    ("convite", 0): ("a", "CONVITE"),
    ("especial", 0): ("g", "Especial"),
    ("encontro", 0): ("a", "ENCONTRO"),
    ("24", 0): ("n", "24"),
    ("lagoinha", 0): ("logo", ""),
    ("amigo", 0): ("a", "AMIGO"),
    ("parente", 0): ("a", "PARENTE"),
    ("adorar", 0): ("g", "Adorar"),
    ("jesus", 1): ("g", "Jesus"),
    ("palavra", 0): ("a", "PALAVRA"),
    ("todo-poderoso", 0): ("g", "Todo-Poderoso"),
    ("grandão", 0): ("a", "GRANDÃO"),
    ("galileia", 0): ("g", "Galileia"),
    ("grandemente", 0): ("o", "GRANDEMENTE"),
    ("convidado", 0): ("none", ""),
    ("especial", 1): ("none", ""),
    ("noite", 0): ("none", ""),
    ("amém", 0): ("g", "Amém"),
    ("junto", 0): ("none", ""),
}

blocos, chaves, cont = [], [], {}
for bl in FALA.split("/"):
    ws = re.findall(r"([\d.]+)\s+(\S+)", bl)
    if not ws: continue
    pal = []
    for t, w in ws:
        k = "*" in w
        txt = w.replace("*", "")
        pal.append({"t": o(float(t)), "src": float(t), "w": txt, "c": "k" if k else ""})
        if k:
            base = re.sub(r"[^\wà-úÀ-Ú-]", "", txt).lower()
            n = cont.get(base, 0); cont[base] = n + 1
            est, mostra = CHAVE.get((base, n), ("a", txt.upper()))
            if est != "none":
                chaves.append({"t": o(float(t)), "est": est, "txt": mostra, "id": f"{base}{n}"})
    blocos.append({"s": pal[0]["t"], "p": pal})

# fim de cada bloco: até o próximo começar (máx. 1,0 s parado)
for i, b in enumerate(blocos):
    prox = blocos[i + 1]["s"] if i + 1 < len(blocos) else FIM_FALA
    fim = min(prox, b["p"][-1]["t"] + 1.0)
    if prox - fim < 0.3: fim = prox
    b["e"] = round(fim, 3)
for i, c in enumerate(chaves):
    prox = chaves[i + 1]["t"] if i + 1 < len(chaves) else FIM_FALA
    c["fim"] = round(min(prox - 0.04, c["t"] + 1.6), 3)


def W(palavra, n=0):
    """tempo no reel da n-ésima ocorrência da palavra"""
    k = 0
    for b in blocos:
        for p in b["p"]:
            if re.sub(r"[^\wà-úÀ-Ú-]", "", p["w"]).lower() == palavra:
                if k == n: return p["t"]
                k += 1
    raise KeyError(palavra)


EV = {
    "seg": [s["out"] for s in SEGS],
    "irmaos": W("irmãos"), "jesus": W("jesus"), "convite": W("convite"), "convite2": W("convite", 1),
    "especial": W("especial"), "encontro": W("encontro"), "dia24": W("24"), "igreja": W("igreja"),
    "lagoinha": W("lagoinha"), "vir": W("vir"), "amigo": W("amigo"), "parente": W("parente"),
    "traga1": W("traga"), "traga2": W("traga", 1),
    "adorar": W("adorar"), "jesus2": W("jesus", 1), "ouvir": W("ouvir"), "palavra": W("palavra"),
    "adorar2": W("adorar", 1), "todo": W("todo-poderoso"), "grandao": W("grandão"), "galileia": W("galileia"),
    "senhor3": W("senhor", 2), "falar2": W("falar", 1), "grandemente": W("grandemente"), "voce_fim": W("você", 2),
    "voce_conv": W("você", 3), "convidado": W("convidado"), "especial2": W("especial", 1),
    "deus_fim": W("deus", 3), "esteja": W("esteja"), "noite": W("noite"), "amem": W("amém"),
    "vamos": W("vamos"), "junto": W("junto"),
    "fim_fala": FIM_FALA, "total": TOTAL,
}
EV["split"] = SEGS[12]["out"]          # tela dividida com o flyer: "Deus abençoe você, esteja com a gente nessa noite"
EV["split_fim"] = SEGS[14]["out"]      # volta à tela cheia no "Amém?"
EV["cartela"] = FIM_FALA

# efeitos sonoros: (arquivo, tempo no reel, ganho dB)
SFX = [
    ("whoosh", EV["seg"][1] - 0.12, -12),
    ("papel", EV["convite"] - 0.05, -8),          # ingresso entra girando
    ("whoosh", EV["convite"] + 0.10, -14),
    ("brilho", EV["especial"] - 0.02, -13),
    ("whoosh", EV["seg"][3] - 0.12, -12),
    ("carimbo", EV["dia24"] + 0.02, -6),         # carimbo 24/10 no ingresso
    ("impacto", EV["dia24"] + 0.02, -12),
    ("whoosh", EV["lagoinha"] - 0.15, -13),
    ("tique", EV["amigo"] + 0.05, -9),            # ADMITE 2
    ("papel", EV["amigo"] + 0.02, -14),
    ("tique", EV["parente"] + 0.05, -8),          # ADMITE 3
    ("papel", EV["parente"] + 0.02, -13),
    ("whoosh", EV["adorar"] - 0.10, -11),         # ingressos saem
    ("pop", EV["jesus2"], -16),
    ("pop", EV["palavra"], -16),
    ("subida", EV["todo"] - 1.4, -10),            # sobe até o Todo-Poderoso
    ("impacto", EV["todo"], -9),
    ("onda", EV["grandao"] - 0.3, -10),           # mar da Galileia
    ("impacto", EV["grandao"], -11),
    ("whoosh", EV["seg"][10] - 0.12, -13),
    ("pulso", EV["grandemente"], -9),
    ("papel", EV["convidado"] - 0.12, -9),        # ingresso VIP volta
    ("brilho", EV["especial2"], -10),
    ("whoosh", EV["split"] - 0.12, -10),          # tela dividida
    ("tique", EV["esteja"] + 0.1, -16),
    ("tique", EV["noite"], -14),
    ("whoosh", EV["split_fim"] - 0.12, -11),
    ("impacto", EV["amem"], -13),
    ("subida", EV["cartela"] - 1.0, -14),
    ("carimbo", EV["cartela"] + 0.05, -5),        # logo HERO carimbada
    ("impacto", EV["cartela"] + 0.05, -8),
    ("brilho", EV["cartela"] + 1.2, -14),
]

os.makedirs(f"{D}/assets", exist_ok=True)
with open(f"{D}/assets/sincronia.js", "w") as f:
    f.write("// gerado por tools/sincronia.py — não editar à mão\n")
    f.write("window.SYNC = " + json.dumps({"blocos": blocos, "chaves": chaves, "ev": EV}, ensure_ascii=False, separators=(",", ":")) + ";\n")
json.dump({"ev": EV, "sfx": SFX, "segs": SEGS, "total": TOTAL}, open(f"{D}/tools/eventos.json", "w"), ensure_ascii=False, indent=1)
for k, v in EV.items():
    if k != "seg": print(f"{k:12s} {v}")
print("segs", EV["seg"]); print(len(blocos), "blocos,", len(chaves), "palavras-chave")
