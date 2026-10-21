"""Linha do tempo do reel 2 "Plantão HERO" (fonte única de tempos para vídeo, legendas, efeitos, trilha e mixagem).

Fonte: src/original.mov (selfie 576x1008 após a rotação, 30 fps, 25,7 s). Tempos em segundos da gravação.
Cada trecho de CORTES é uma fala; as pausas entre eles são removidas (corte seco).
"""
FPS = 30
SR = 48000

CORTES = [
    (0.42, 1.36),    # 1 Meus irmãos, tudo bem?
    (1.50, 3.60),    # 2 Estou passando aqui neste momento para te convidar
    (4.00, 8.74),    # 3 que nesse sábado, dia 24 de outubro, às 7 e meia, será promovido
    (8.80, 14.12),   # 4 o nosso primeiro culto Hero da Igreja Batista Lagoinha, tá? Te convido a fazer presente neste momento,
    (14.18, 14.88),  # 5 venha,
    (15.04, 18.68),  # 6 traga mais um, que será tremendo, a unção de Deus,
    (18.86, 22.34),  # 7 momento de adoração e comunhão com os irmãos.
    (22.58, 25.10),  # 8 Venha, não fica fora dessa, não,
    (25.20, 25.70),  # 9 tá bom?
]
CAUDA = 3.4           # cartela final depois da última fala


def _q(t):
    return round(round(t * FPS) / FPS, 4)


SEGS = []
_t = 0.0
for _a, _b in CORTES:
    _n = int(round((_b - _a) * FPS))
    SEGS.append({"src": _a, "fim_src": round(_a + _n / FPS, 4), "out": _q(_t), "n": _n})
    _t += _n / FPS
FIM_FALA = _q(_t)
TOTAL = _q(FIM_FALA + CAUDA)


def o(ts):
    """tempo da gravação -> tempo do reel (pausa cortada colapsa no início do trecho seguinte)."""
    for s in SEGS:
        if s["src"] <= ts < s["fim_src"]:
            return round(s["out"] + ts - s["src"], 3)
        if ts < s["src"]:
            return s["out"]
    return FIM_FALA


if __name__ == "__main__":
    for i, s in enumerate(SEGS):
        print(i + 1, s)
    print("fim fala", FIM_FALA, "total", TOTAL)
