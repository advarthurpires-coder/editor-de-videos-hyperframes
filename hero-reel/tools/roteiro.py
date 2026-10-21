"""Linha do tempo do reel (fonte única de tempos para vídeo, legendas, efeitos, trilha e mixagem).

Fonte: src/original.mp4 (464x832, 60 fps, 39,9 s). Tempos em segundos da gravação.
Cada trecho de CORTES é uma fala; as pausas entre eles são removidas (corte seco).
"""
FPS = 30
SR = 48000
BEAT = 60 / 96        # trilha a 96 bpm
BAR = 4 * BEAT

CORTES = [
    (0.70, 4.92),    # 1  Meus irmãos, a paz do Senhor Jesus, Deus que abençoe a vida de vocês.
    (5.06, 6.98),    # 2  Estou aqui para te fazer um convite,
    (7.28, 8.94),    # 3  um convite muito especial.
    (9.12, 11.76),   # 4  Deus tem um encontro com você no dia 24,
    (11.94, 13.92),  # 5  na igreja Batista Lagoinha.
    (14.84, 16.18),  # 6  Que você possa vir,
    (16.46, 17.56),  # 7  traga um amigo,
    (17.88, 19.02),  # 8  traga um parente
    (19.30, 21.28),  # 9  e venha aqui adorar ao Senhor,
    (21.92, 28.34),  # 10 falar um pouco de Jesus, ouvir a palavra de Deus, adorar o Todo-Poderoso, o Grandão da Galileia.
    (28.54, 31.38),  # 11 E que o Senhor possa falar neste dia grandemente com você.
    (31.56, 33.46),  # 12 Você é o nosso convidado especial.
    (34.24, 35.58),  # 13 Deus abençoe você,
    (35.72, 37.52),  # 14 esteja com a gente nessa noite.
    (37.84, 39.40),  # 15 Amém? Vamos junto.
]
CAUDA = 3.6           # cartela final depois da última fala


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
