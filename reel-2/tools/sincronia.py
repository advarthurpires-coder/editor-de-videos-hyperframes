# Legendas (tarjas de telejornal com marca-texto na palavra falada) e momentos dos elementos gráficos/3D,
# do tempo da gravação para o tempo do reel. Grava assets/sincronia.js (window.SYNC) e tools/eventos.json.
# Tempos: inícios de palavra do Parakeet v3 rodado trecho a trecho (tools/conferir_cortes.py), conferidos com Whisper.
# Marcação: *palavra* = termo-chave (Bebas Neue amarela, maior) · "/" fecha uma tarja.
# Uso: python3 -I tools/sincronia.py
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roteiro import SEGS, FIM_FALA, TOTAL, o  # noqa: E402

D = os.path.dirname(os.path.abspath(__file__)) + "/.."

FALA = """
0.44 Meus 0.60 *irmãos,* 0.92 tudo 1.08 bem? /
1.50 Estou 1.82 passando 2.06 aqui /
2.22 neste 2.46 momento /
2.70 para 2.94 te 3.10 *convidar* /
4.32 que 4.64 nesse /
4.88 *sábado,* /
5.44 dia 5.68 *24* /
6.08 de 6.16 *outubro,* /
6.56 às 6.72 *7* 6.96 *e* 7.04 *meia,* /
7.44 será 7.84 promovido /
8.32 o 8.40 nosso 8.88 *primeiro* /
9.20 culto 9.60 *HERO* /
10.08 da 10.24 Igreja 10.56 Batista /
11.04 *Lagoinha,* 11.84 tá? /
12.08 Te 12.24 convido 12.56 a /
12.72 fazer 12.96 *presente* /
13.36 neste 13.60 momento, /
14.26 *venha,* /
15.12 traga 15.52 *mais* 15.68 *um,* /
16.16 que 16.32 será /
16.64 *tremendo,* /
17.52 a 17.76 *unção* 18.24 de 18.32 *Deus,* /
19.26 momento 19.66 de /
19.82 *adoração* /
20.54 e 20.70 *comunhão* /
21.26 com 21.42 os 21.58 *irmãos.* /
22.62 *Venha,* /
24.02 não 24.18 fica /
24.42 *fora* 24.66 dessa, /
24.90 não, 25.20 tá 25.36 bom? /
"""

blocos = []
for bl in FALA.split("/"):
    ws = re.findall(r"([\d.]+)\s+(\S+)", bl)
    if not ws: continue
    pal = [{"t": o(float(t)), "w": w.replace("*", ""), "c": "k" if "*" in w else ""} for t, w in ws]
    blocos.append({"s": pal[0]["t"], "p": pal})
for i, b in enumerate(blocos):
    prox = blocos[i + 1]["s"] if i + 1 < len(blocos) else FIM_FALA
    fim = min(prox, b["p"][-1]["t"] + 1.0)
    if prox - fim < 0.3: fim = prox
    b["e"] = round(fim, 3)


def W(palavra, n=0):
    k = 0
    for b in blocos:
        for p in b["p"]:
            if re.sub(r"[^\wà-úÀ-Ú-]", "", p["w"]).lower() == palavra:
                if k == n: return p["t"]
                k += 1
    raise KeyError(palavra)


EV = {
    "seg": [s["out"] for s in SEGS],
    "irmaos": W("irmãos"), "estou": W("estou"), "convidar": W("convidar"), "que": W("que"),
    "sabado": W("sábado"), "dia": W("dia"), "dia24": W("24"), "outubro": W("outubro"), "as7": W("7"), "meia": W("meia"),
    "sera": W("será"), "primeiro": W("primeiro"), "culto": W("culto"), "hero": W("hero"), "igreja": W("igreja"),
    "lagoinha": W("lagoinha"), "ta1": W("tá"), "te": W("te", 1), "presente": W("presente"), "neste2": W("neste", 1),
    "venha1": W("venha"), "traga": W("traga"), "mais": W("mais"), "um": W("um"), "que3": W("que", 1),
    "tremendo": W("tremendo"), "uncao": W("unção"), "deus": W("deus"), "momento3": W("momento", 2),
    "adoracao": W("adoração"), "comunhao": W("comunhão"), "irmaos2": W("irmãos", 1), "venha2": W("venha", 1),
    "nao": W("não"), "fora": W("fora"), "dessa": W("dessa"), "nao2": W("não", 1), "tabom": W("tá", 1),
    "fim_fala": FIM_FALA, "total": TOTAL,
}
EV["cartela"] = FIM_FALA

SFX = [
    ("liga_tv", 0.0, -8),                      # TV liga
    ("vinheta", 0.05, -10),                    # vinheta de plantão
    ("whoosh", EV["convidar"] - 0.15, -12),
    ("impacto", EV["convidar"], -11),          # janela + "CONVIDAR" saltando
    ("papel", EV["sabado"] - 0.05, -9),        # calendário entra
    ("folhas", EV["dia24"] - 0.25, -8),        # páginas arrancadas até o 24
    ("tique", EV["dia24"] + 0.02, -8),
    ("tique", EV["outubro"], -12),
    ("relogio", EV["as7"] - 0.1, -8),          # ponteiros girando
    ("ding", EV["meia"] + 0.15, -10),
    ("whoosh", EV["sera"] - 0.1, -13),
    ("whoosh", EV["culto"] - 0.12, -11),       # tela dividida com o flyer
    ("impacto", EV["hero"], -9),
    ("pop", EV["lagoinha"], -13),
    ("whoosh", EV["te"] - 0.1, -13),
    ("impacto", EV["presente"], -12),
    ("impacto", EV["venha1"], -10),
    ("clone", EV["mais"] - 0.05, -9),          # clone desliza
    ("clone", EV["um"] + 0.05, -11),
    ("terremoto", EV["tremendo"] - 0.05, -7),  # sismógrafo + tremor
    ("brilho", EV["uncao"] - 0.05, -10),       # gotas de ouro
    ("gota", EV["uncao"] + 0.25, -12),
    ("gota", EV["uncao"] + 0.75, -14),
    ("whoosh", EV["momento3"] - 0.15, -11),    # carrossel de fotos
    ("obturador", EV["adoracao"] + 0.05, -12),
    ("obturador", EV["comunhao"] + 0.05, -12),
    ("whoosh", EV["irmaos2"] + 0.1, -11),
    ("impacto", EV["venha2"], -9),
    ("whoosh", EV["fora"] - 0.2, -12),         # a janela encolhe: "FORA"
    ("carimbo", EV["nao2"], -7),               # carimbo "NÃO"
    ("vinheta", EV["cartela"] - 0.1, -9),
    ("impacto", EV["cartela"] + 0.05, -8),
]

with open(f"{D}/assets/sincronia.js", "w") as f:
    f.write("// gerado por tools/sincronia.py — não editar à mão\n")
    f.write("window.SYNC = " + json.dumps({"blocos": blocos, "ev": EV}, ensure_ascii=False, separators=(",", ":")) + ";\n")
json.dump({"ev": EV, "sfx": SFX, "segs": SEGS, "total": TOTAL}, open(f"{D}/tools/eventos.json", "w"), ensure_ascii=False, indent=1)
for k, v in EV.items():
    if k != "seg": print(f"{k:10s} {v}", end="   ")
print(); print("segs", EV["seg"]); print(len(blocos), "tarjas")
