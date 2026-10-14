"""Trilha original e discreta (lo-fi leve, 86 BPM, Fá maior) para o reel "A visita do CRAS vai virar regra".

Síntese pura (sem samples de terceiros, sem vocal): piano elétrico suave, baixo redondo, bumbo e chimbal
abafados. Deterministica (semente fixa). Termina com acorde final sustentado.
Uso: python3 -I tools/gerar_trilha.py <duracao_s> assets/music/trilha_lofi.wav
"""
import sys, wave
import numpy as np

SR = 48000
DUR = float(sys.argv[1]); OUT = sys.argv[2]
BPM = 86.0; BEAT = 60 / BPM; BAR = 4 * BEAT
rng = np.random.default_rng(20261014)
N = int((DUR + 4) * SR)
L = np.zeros(N); R = np.zeros(N)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, t, pan=0.0, g=1.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * np.cos((pan + 1) * np.pi / 4) * g
    R[i:i + len(sig)] += sig * np.sin((pan + 1) * np.pi / 4) * g


def epiano(m, dur, vel=0.5):
    """Piano elétrico (FM leve: portadora + modulador 1:1 que decai rápido) com tremolo sutil."""
    f = hz(m); ln = dur + 1.2
    t = np.arange(int(ln * SR)) / SR
    idx = 1.6 * vel * np.exp(-t * 7)
    mod = np.sin(2 * np.pi * f * t) * idx
    car = np.sin(2 * np.pi * f * t + mod) + 0.18 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
    env = np.minimum(1, t / 0.006) * np.exp(-t * (1.1 + f / 2500))
    rel = np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.25))
    trem = 1 - 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * 4.2 * t))
    return car * env * rel * trem * vel * 0.10


def bass(m, dur, vel=0.6):
    f = hz(m); t = np.arange(int((dur + 0.3) * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    env = np.minimum(1, t / 0.01) * np.where(t < dur, np.exp(-t * 0.9), np.exp(-dur * 0.9) * np.exp(-(t - dur) / 0.08))
    return s * env * vel * 0.16


def kick(vel=0.5):
    t = np.arange(int(0.35 * SR)) / SR
    f = 48 + 70 * np.exp(-t * 32)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * vel * 0.32


def hat(vel=0.3, ln=0.05):
    n = rng.standard_normal(int(ln * SR))
    n = n - np.convolve(n, np.ones(8) / 8, "same")          # passa-altas simples
    return n * np.exp(-np.arange(len(n)) / (0.012 * SR)) * vel * 0.05


def snap(vel=0.3):
    n = rng.standard_normal(int(0.18 * SR)); n = np.convolve(n, np.ones(5) / 5, "same")
    t = np.arange(len(n)) / SR
    return (n * 0.6 + np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 26) * vel * 0.07


# Fmaj9 - Em7 - Dm9 - Cmaj7(/E)  (voicings fechados, região média)
PROG = [(41, [57, 60, 64, 67]), (40, [55, 59, 62, 67]), (38, [53, 57, 60, 64]), (36, [52, 55, 59, 64])]
FIM_MUS = DUR - 1.2
t0, b = 0.0, 0
while t0 < FIM_MUS - 0.01:
    root, ch = PROG[b % 4]
    ultimo = t0 + BAR >= FIM_MUS
    d = BAR if not ultimo else (DUR - t0)
    # acordes: ataque no 1 e "empurrão" sincopado no 2e
    for k, n in enumerate(ch):
        add(epiano(n, BEAT * 1.4, 0.42), t0 + 0.008 * k, pan=-0.25 + 0.15 * k)
        if not ultimo:
            add(epiano(n, BEAT * 1.6, 0.30), t0 + BEAT * 1.5 + 0.008 * k, pan=-0.2 + 0.13 * k)
    if ultimo:
        for k, n in enumerate(ch + [ch[-1] + 5]):
            add(epiano(n, d, 0.38), t0 + 0.02 * k, pan=-0.3 + 0.12 * k)
        add(bass(root, d, 0.6), t0)
        break
    # melodia curta e esparsa a cada 2 compassos
    if b % 2 == 1:
        for (dt, m) in [(2.5, ch[-1] + 5), (3.0, ch[-1] + 3), (3.5, ch[-1])]:
            add(epiano(m, BEAT * 0.5, 0.22), t0 + dt * BEAT, pan=0.35)
    add(bass(root, BEAT * 1.8, 0.55), t0)
    add(bass(root + 7, BEAT * 0.9, 0.40), t0 + BEAT * 2.5)
    add(bass(root, BEAT * 0.9, 0.42), t0 + BEAT * 3.25)
    if b >= 1:   # bateria entra no 2º compasso
        add(kick(0.55), t0); add(kick(0.35), t0 + BEAT * 2.5)
        add(snap(0.5), t0 + BEAT); add(snap(0.5), t0 + BEAT * 3)
        for k in range(8):
            add(hat(0.35 if k % 2 == 0 else 0.22), t0 + k * BEAT / 2 + (0.018 if k % 2 else 0), pan=0.2)
    t0 += BAR; b += 1

mix = np.stack([L, R], 1)[: int(DUR * SR)]
# entrada suave (2 s) e saída natural
fi = np.minimum(1, np.arange(len(mix)) / (2.0 * SR))[:, None]
mix = mix * fi
# filtro passa-baixas leve (som "abafado", não compete com a voz)
a = np.exp(-2 * np.pi * 5200 / SR)
for c in range(2):
    y = np.zeros(len(mix)); acc = 0.0
    x = mix[:, c]
    # IIR 1 polo vetorizado por blocos via lfilter manual
    from itertools import accumulate
    y = np.array(list(accumulate(x * (1 - a), lambda p, v: a * p + v)))
    mix[:, c] = y
mix = mix / (np.abs(mix).max() + 1e-9) * 0.7
with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("trilha", OUT, round(len(mix) / SR, 2), "s")
