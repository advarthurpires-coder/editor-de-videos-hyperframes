"""Linha do tempo do reel "Convite HERO" (fonte única de tempos para vídeo, legendas, trilha e mixagem).

Fonte: src/convite_original.mp4 (480x1068, ~30 fps, 29,1 s). Tempos em segundos da gravação.
Cada trecho de CORTES é uma fala; as pausas entre eles são removidas (corte seco).
"""
FPS = 30
SR = 48000
BEAT = 0.6            # trilha a 100 bpm
BAR = 4 * BEAT

CORTES = [
    (2.05, 4.62),    # Fala, meus irmãos, graça e paz!
    (5.10, 6.45),    # Que Deus abençoe vocês.
    (6.84, 10.32),   # Irmãos, venho aqui fazer um convite muito especial para vocês, homens.
    (11.14, 13.24),  # Vai acontecer aqui em Patrocínio,
    (13.44, 15.02),  # na Batista Lagoinha
    (16.05, 18.36),  # o nosso primeiro culto do HERO.
    (18.94, 20.93),  # Eu quero fazer um convite muito especial para vocês.
    (21.22, 25.25),  # Dia 24 de outubro, às 19h30.
    (25.62, 26.32),  # Vem!
]


def _q(t):
    return round(round(t * FPS) / FPS, 4)


# início de cada trecho no reel (quantizado em quadros)
SEGS = []
_t = 0.0
for _a, _b in CORTES:
    _n = int(round((_b - _a) * FPS))
    SEGS.append({"src": _a, "fim_src": round(_a + _n / FPS, 4), "out": _q(_t), "n": _n})
    _t += _n / FPS
FIM_FALA = _q(_t)               # fim da última fala no reel
FLYER = FIM_FALA                # flyer em tela cheia
CARTELA = _q(FLYER + 1.5 * BAR) # cartela final (logos + @), no tempo da trilha
TOTAL = _q(CARTELA + 2.8)


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
    print("fim fala", FIM_FALA, "flyer", FLYER, "cartela", CARTELA, "total", TOTAL)
