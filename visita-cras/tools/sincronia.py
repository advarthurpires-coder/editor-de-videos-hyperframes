# Converte o texto revisado (tools/texto.py) e os momentos dos elementos gráficos do tempo da gravação
# para o tempo do reel (após os cortes), usando tools/linha_tempo.json. Grava:
#   assets/sincronia.js  -> window.SYNC (legendas palavra a palavra, falas do TikTok, eventos, âncoras das mãos)
#   tools/eventos.json   -> mesmos eventos + efeitos sonoros, para a mixagem
# Uso: python3 -I tools/sincronia.py
import json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__)) + "/.."
sys.path.insert(0, D + "/tools")
from texto import FALA, TIKTOK

LT = json.load(open(f"{D}/tools/linha_tempo.json"))
SEGS, FPS, Q = LT["segs"], LT["fps"], LT["quadros"]
TOTAL, INTRO, CARTELA = LT["total"], LT["intro"], LT["cartela"]


def o(ts):
    """tempo da gravação -> tempo do reel (pausas cortadas colapsam no início do trecho seguinte)."""
    for s in SEGS:
        if s["src"] <= ts < s["fim_src"]:
            return round(s["out"] + ts - s["src"], 3)
        if ts < s["src"]:
            return round(s["out"], 3)
    return round(SEGS[-1]["out"] + SEGS[-1]["fim_src"] - SEGS[-1]["src"], 3)


# ------------------------------------------------------------------ legendas
toks = []
for m in re.finditer(r"([\d.]+)\s+([^\s|]+)(\|?)", FALA):
    t, w, br = float(m.group(1)), m.group(2), m.group(3) == "|"
    cls = ""
    if "*" in w: cls = "g"
    if "!" in w: cls = "r"
    w = w.replace("*", "").replace("!", "")
    toks.append({"src": t, "t": o(t), "w": w, "c": cls, "br": br})
grupos, cur = [], []
for k in toks:
    cur.append(k)
    chars = sum(len(x["w"]) for x in cur) + len(cur) - 1
    nxt = toks[toks.index(k) + 1] if k is not toks[-1] else None
    quebra = k["br"] or len(cur) >= 3 or (nxt and chars + 1 + len(nxt["w"]) > 18)
    if quebra:
        grupos.append(cur); cur = []
if cur: grupos.append(cur)
leg = []
for gi, g in enumerate(grupos):
    prox = grupos[gi + 1][0]["t"] if gi + 1 < len(grupos) else TOTAL - CARTELA
    fim = min(prox, g[-1]["t"] + 0.75)
    if prox - fim < 0.35: fim = prox
    pal = []
    for j, k in enumerate(g):
        e = g[j + 1]["t"] if j + 1 < len(g) else fim
        pal.append({"t": k["t"], "e": round(e, 3), "w": k["w"], "c": k["c"]})
    leg.append({"s": g[0]["t"], "e": round(fim, 3), "p": pal})


def palavra(src_t):
    """tempo de saída da palavra cujo início na gravação é src_t"""
    return min(toks, key=lambda k: abs(k["src"] - src_t))["t"]


# ------------------------------------------------------------------ eventos (tempo da gravação -> reel)
EV_SRC = {
    "nome_in": 13.55,
    "cal_in": 16.30, "cal_2027": 17.86, "cal_out": 18.75,
    "casa_in": 29.12, "casa_out": 31.05,
    "bf_in": 34.07, "bpc_in": 34.79, "cartoes_out": 36.62,
    "lupa_in": 37.45,
    "cafe_in": 46.30, "cafe_out": 49.30,
    "porta_in": 54.10, "porta_out": 56.30,
    "dois_in": 57.62, "lista_in": 58.58, "item1_in": 58.74, "check1": 60.02, "lista_out": 62.20,
    "lista2_in": 72.12, "item2_in": 74.27, "check2": 76.43, "lista2_out": 77.80,
    "cuidado1": 78.27, "omita": 83.47, "cuidado2": 85.02,
    "jul_chip_in": 91.42, "jul_chip_out": 97.30,
    "inss_in": 99.79, "justica_in": 100.59, "inss_out": 102.45,
    "aviao_in": 104.02,
}
EV = {k: (palavra(v) if any(abs(v - x["src"]) < 0.02 for x in toks) else o(v)) for k, v in EV_SRC.items()}
EV["corte"] = INTRO
EV["cartela"] = round(TOTAL - CARTELA, 3)
EV["total"] = TOTAL


# ------------------------------------------------------------------ âncoras (mão que gesticula, rosto)
def ancora(nome, t0, t1, tipo="palma", modo="alta"):
    i0, i1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    pts, last = [], None
    for i in range(i0, min(i1, len(Q))):
        q = Q[i]
        if q is None: pts.append(last); continue
        if tipo in ("nariz", "xicara"):
            p = q[tipo]
        else:
            hs = q["maos"]
            if hs:
                h = min(hs, key=lambda h: h["palma"][1]) if modo == "alta" else min(hs, key=lambda h: h["palma"][0])
                p = h["ind"] if tipo == "ind" else h["palma"]
            else:
                p = last
        if p is None: p = last or [540, 1100]
        if last is not None:   # suavização exponencial (evita tremor do rastreio)
            p = [last[0] * 0.55 + p[0] * 0.45, last[1] * 0.55 + p[1] * 0.45]
        last = p; pts.append([round(p[0]), round(p[1])])
    pts = [p if p is not None else pts[-1] for p in pts]
    return {"t0": round(i0 / FPS, 3), "pts": pts}


ANC = {
    "nariz_cal": ancora("nariz_cal", EV["cal_in"], EV["cal_out"] + 0.6, "nariz"),
    "mao_casa": ancora("mao_casa", EV["casa_in"] - 0.3, EV["casa_out"] + 0.5, "palma"),
    "mao_porta": ancora("mao_porta", EV["porta_in"] - 0.4, EV["porta_in"] + 0.6, "palma"),
    "dedos_dois": ancora("dedos_dois", EV["dois_in"] - 0.2, EV["lista_in"] + 0.2, "ind"),
    "mao_aviao": ancora("mao_aviao", EV["aviao_in"] - 0.2, EV["aviao_in"] + 0.5, "palma", "esq"),
    "xicara": ancora("xicara", EV["cafe_in"] - 0.2, EV["cafe_out"] + 0.5, "xicara"),
    "nariz_cuidado": ancora("nariz_cuidado", EV["cuidado1"], EV["cuidado2"] + 1.0, "nariz"),
}

# cortes (início de cada trecho no reel) para pequenos acentos visuais
CORTES = [s["out"] for s in SEGS]

# ------------------------------------------------------------------ efeitos sonoros (arquivo, tempo, ganho dB)
SFX = [
    ("click-soft", 0.35, -14), ("click-soft", 0.75, -16),               # título da tela dividida
    ("impact-bass-1", INTRO - 0.02, -13), ("whoosh", INTRO - 0.20, -17),  # corte seco para tela cheia
    ("whoosh", EV["nome_in"], -20),
    ("whoosh", EV["cal_in"], -16), ("click", EV["cal_2027"], -11), ("sparkle", EV["cal_2027"] + 0.02, -17),
    ("pop", EV["casa_in"], -14),
    ("pop", EV["bf_in"], -14), ("pop", EV["bpc_in"], -13),
    ("whoosh", EV["lupa_in"], -13),
    ("sparkle", EV["cafe_in"], -16),
    ("whoosh", EV["porta_in"] - 0.05, -15), ("pop", EV["porta_in"] + 0.30, -16),
    ("pop", EV["dois_in"], -12),
    ("whoosh", EV["lista_in"], -18), ("click", EV["item1_in"], -14), ("click-soft", EV["check1"], -12),
    ("whoosh", EV["lista2_in"], -18), ("click", EV["item2_in"], -14), ("click-soft", EV["check2"], -12),
    ("impact-bass-2", EV["cuidado1"] - 0.03, -15), ("impact-bass-1", EV["omita"] - 0.03, -18),
    ("impact-bass-2", EV["cuidado2"] - 0.03, -14),
    ("click", EV["jul_chip_in"], -15),
    ("pop", EV["inss_in"], -13), ("pop", EV["justica_in"], -12), ("sparkle", EV["justica_in"] + 0.05, -19),
    ("whoosh", EV["aviao_in"], -13),
    ("whoosh", EV["cartela"] - 0.15, -15), ("sparkle", EV["cartela"] + 0.25, -14), ("impact-bass-1", EV["cartela"] + 0.05, -19),
]

SYNC = {"total": TOTAL, "intro": INTRO, "cartela": CARTELA, "fps": FPS, "leg": leg,
        "tiktok": [{"s": a, "e": b, "txt": t} for a, b, t in TIKTOK], "ev": EV, "anc": ANC, "cortes": CORTES}
with open(f"{D}/assets/sincronia.js", "w") as fh:
    fh.write("// gerado por tools/sincronia.py — não editar à mão\nwindow.SYNC = ")
    json.dump(SYNC, fh, ensure_ascii=False, separators=(",", ":"))
    fh.write(";\n")
json.dump({"total": TOTAL, "intro": INTRO, "segs": SEGS, "ev": EV, "sfx": SFX}, open(f"{D}/tools/eventos.json", "w"), indent=1)
print("legendas", len(leg), "| total", TOTAL)
for k in sorted(EV, key=EV.get): print(f"  {EV[k]:7.2f}  {k}")
