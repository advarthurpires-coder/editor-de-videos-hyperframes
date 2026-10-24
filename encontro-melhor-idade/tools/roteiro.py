"""Grade de tempo compartilhada entre a trilha e a edição (index.html usa os mesmos números).

Ré maior, 72 bpm: tempo = 0,8333 s; compasso (4 tempos) = 3,3333 s. Os cortes caem em tempos da trilha.
"""
SR = 48000
BPM = 72
BEAT = 60 / BPM
BAR = 4 * BEAT
TOTAL = 49.0          # duração do reel (s)

# seções (em compassos, começando do 0)
SECOES = {
    "preparo": (0, 3),     # 0,00–10,00  piano sozinho + pad
    "chegada": (3, 4),     # 10,00–13,33 entra o baixo
    "palavra": (4, 8),     # 13,33–26,67 verso (Salmos 92:14), batida de coração
    "comunhao": (8, 11),   # 26,67–36,67 refrão cheio (drop no 1º tempo do compasso 9)
    "rostos": (11, 13),    # 36,67–43,33 refrão segue, polaroides
    "final": (13, 15),     # 43,33–49,00 acorde final de Ré
}
