"""Trilha instrumental original do reel 2º HERO EXTREME (síntese, sem samples de terceiros).

Ré maior, 100 bpm (compasso = 2,4 s). Seções presas aos cortes do vídeo:
  0,0–7,9   atmosfera: drone grave, cordas aéreas, riser e prato reverso até o impacto
  7,9       IMPACTO (entrada de HERO EXTREME): subgrave + taiko + prato
  7,9–13,3  pulso cinematográfico: taikos, metais curtos, cordas cheias
  13,3–20,9 convivência: violão dedilhado (Karplus-Strong), palmas, chocalho, bumbo leve
  20,9–30,6 espiritual: sem bateria; piano e cordas, progressão inspiradora
  30,6–39,0 calor humano: violão + piano + bumbo suave
  39,0–45,0 crescendo: tons em colcheias, rufo de caixa, riser
  45,0      IMPACTO da cartela; 45–55,6 tema cheio; 55,6 batida final e sustentação até 59,0

Uso: python3 -I tools/gerar_trilha.py assets/music/trilha_hero_extreme.wav
Determinística (semente fixa).
"""
import sys
import wave

import numpy as np

SR = 48000
TOTAL = 59.0
N = int((TOTAL + 3) * SR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(20261120)
BEAT = 0.6
BAR = 2.4


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, start, pan=0.0, gain=1.0):
    i = int(round(start * SR))
    if i >= N or i < 0:
        return
    sig = sig[: N - i]
    lg = np.cos((pan + 1) * np.pi / 4) * gain
    rg = np.sin((pan + 1) * np.pi / 4) * gain
    L[i: i + len(sig)] += sig * lg
    R[i: i + len(sig)] += sig * rg


def fftconv(x, h):
    n = len(x) + len(h) - 1
    size = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(h, size), size)[:n]


def lp(x, fc):
    """Passa-baixas de 1 polo (duas passadas)."""
    a = np.exp(-2 * np.pi * fc / SR)
    h = (1 - a) * a ** np.arange(int(np.log(1e-4) / np.log(a)) + 1)
    y = fftconv(x, h)[: len(x)]
    return fftconv(y, h)[: len(x)]


def hp(x, fc):
    return x - lp(x, fc)


def piano(m, dur, vel=0.6):
    f = midi_hz(m)
    ring = min(dur + 1.6, 6.0)
    t = np.arange(int(ring * SR)) / SR
    out = np.zeros_like(t)
    B = 0.00035
    bright = 0.6 + 0.8 * vel
    for n in range(1, 13):
        fn = f * n * np.sqrt(1 + B * n * n)
        if fn > 9000:
            break
        amp = (1.0 / n ** (2.1 - 0.6 * bright)) * (1.0 if n > 1 else 1.2)
        k = 0.9 + 0.55 * n + f / 900.0
        env = 0.72 * np.exp(-k * t) + 0.28 * np.exp(-k * t / 5.0)
        det = 1 + 0.0004 * (n % 2 - 0.5)
        out += amp * env * (np.sin(2 * np.pi * fn * t) + 0.6 * np.sin(2 * np.pi * fn * det * t + 0.3))
    att = np.minimum(1, t / 0.004)
    rel = np.ones_like(t)
    off = int(dur * SR)
    if off < len(t):
        rel[off:] = np.exp(-(t[off:] - dur) / 0.35)
    return out * att * rel * vel * 0.22


def strings(notes, dur, att=1.2, relt=1.6, gain=1.0, bright=3800):
    ln = dur + relt
    t = np.arange(int(ln * SR)) / SR
    out = np.zeros_like(t)
    for m in notes:
        f = midi_hz(m)
        for d in (-0.07, -0.025, 0.0, 0.03, 0.065):
            fd = f * 2 ** (d / 12)
            vib = 1 + 0.0018 * np.sin(2 * np.pi * (4.8 + d * 8) * t + d * 40)
            ph = 2 * np.pi * fd * np.cumsum(vib) / SR + rng.uniform(0, 6.28)
            nmax = int(min(14, bright / fd))
            for n in range(1, max(2, nmax)):
                out += np.sin(n * ph) / (n ** 1.35)
    env = np.minimum(1, t / att) * np.where(t < dur, 1.0, np.exp(-(t - dur) / (relt / 3)))
    return lp(out * env, 2400) * 0.012 * gain


def brass(notes, dur, gain=1.0):
    """Metal curto (staccato), serra filtrada com envelope de brilho."""
    ln = dur + 0.25
    t = np.arange(int(ln * SR)) / SR
    out = np.zeros_like(t)
    for m in notes:
        f = midi_hz(m)
        for d in (-0.04, 0.04):
            ph = 2 * np.pi * f * 2 ** (d / 12) * t
            for n in range(1, int(min(18, 5000 / f))):
                out += np.sin(n * ph) / n * np.exp(-n * 0.09 * (1 + 3 * t))
    env = np.minimum(1, t / 0.025) * np.where(t < dur, np.exp(-t * 1.2), np.exp(-dur * 1.2) * np.exp(-(t - dur) / 0.06))
    return lp(out * env, 1800) * 0.03 * gain


def guitar(m, dur=2.5, vel=0.6, bright=0.5):
    """Violão por Karplus-Strong."""
    f = midi_hz(m)
    p = int(SR / f)
    n = int(dur * SR)
    buf = rng.uniform(-1, 1, p) * vel
    buf = lp(np.concatenate([buf, np.zeros(64)]), 2500 + 5000 * bright)[:p]
    out = np.zeros(n)
    out[:p] = buf
    decay = 0.996
    for i in range(p, n, p):
        seg = out[i - p: i]
        nxt = decay * 0.5 * (seg + np.roll(seg, 1))
        j = min(p, n - i)
        out[i: i + j] = nxt[:j]
    env = np.minimum(1, np.arange(n) / (0.002 * SR))
    return out * env * 0.16


def strum(chord, start, down=True, vel=0.55, spread=0.018, dur=2.4, pan=0.2):
    notes = chord if down else chord[::-1]
    for k, m in enumerate(notes):
        add(guitar(m, dur, vel * (0.85 + 0.15 * rng.random())), start + k * spread, pan=pan)


def kick(gain=1.0, f0=110, f1=42, dec=0.35):
    t = np.arange(int(0.6 * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.045)
    ph = 2 * np.pi * np.cumsum(f) / SR
    click = rng.standard_normal(len(t)) * np.exp(-t / 0.003) * 0.15
    return (np.sin(ph) * np.exp(-t / dec) + click) * 0.5 * gain


def taiko(gain=1.0, f0=95, size=1.0):
    t = np.arange(int(1.4 * SR)) / SR
    f = f0 * (1 + 0.35 * np.exp(-t / 0.03))
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / (0.32 * size)) + 0.35 * np.sin(ph * 1.58) * np.exp(-t / 0.12)
    skin = lp(rng.standard_normal(len(t)), 900) * np.exp(-t / 0.05) * 0.9
    return (body + skin) * 0.45 * gain


def tom(f0=140, gain=1.0):
    t = np.arange(int(0.6 * SR)) / SR
    f = f0 * (1 + 0.25 * np.exp(-t / 0.04))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t / 0.16) + lp(rng.standard_normal(len(t)), 1500) * np.exp(-t / 0.03) * 0.4) * 0.35 * gain


def snare(gain=1.0, dec=0.12):
    t = np.arange(int(0.4 * SR)) / SR
    nz = hp(rng.standard_normal(len(t)), 900) * np.exp(-t / dec)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05) * 0.5
    return (nz * 0.6 + body) * 0.3 * gain


def clap(gain=1.0):
    t = np.arange(int(0.35 * SR)) / SR
    env = np.zeros_like(t)
    for d in (0.0, 0.011, 0.022):
        env += np.where(t >= d, np.exp(-(t - d) / 0.008), 0)
    env += np.exp(-t / 0.09) * 0.5
    return hp(lp(rng.standard_normal(len(t)), 3500), 900) * env * 0.22 * gain


def shaker(gain=1.0):
    t = np.arange(int(0.12 * SR)) / SR
    env = np.minimum(1, t / 0.015) * np.exp(-t / 0.03)
    return hp(rng.standard_normal(len(t)), 5000) * env * 0.12 * gain


def crash(gain=1.0, dec=1.6):
    t = np.arange(int(3.5 * SR)) / SR
    return hp(rng.standard_normal(len(t)), 4000) * np.exp(-t / dec) * 0.16 * gain


def reverse_cymbal(length, gain=1.0):
    t = np.arange(int(length * SR)) / SR
    env = (t / length) ** 2.6
    return hp(rng.standard_normal(len(t)), 3500) * env * 0.2 * gain


def riser(length, gain=1.0):
    t = np.arange(int(length * SR)) / SR
    x = t / length
    nz = rng.standard_normal(len(t))
    lo = lp(nz, 600)
    hi = hp(nz, 2500)
    sweep = lo * (1 - x) + hi * x
    tone = np.sin(2 * np.pi * np.cumsum(180 + 900 * x ** 2) / SR) * 0.25
    return (sweep + tone) * x ** 2.2 * 0.2 * gain


def boom(gain=1.0, dur=3.0):
    t = np.arange(int(dur * SR)) / SR
    f = 36 + 50 * np.exp(-t / 0.08)
    ph = 2 * np.pi * np.cumsum(f) / SR
    nz = lp(rng.standard_normal(len(t)), 400) * np.exp(-t / 0.25) * 0.6
    return (np.sin(ph) * np.exp(-t / 0.9) + nz) * 0.55 * gain


def drone(m, dur, gain=1.0, att=2.5):
    t = np.arange(int((dur + 2) * SR)) / SR
    f = midi_hz(m)
    out = np.zeros_like(t)
    for n, a in [(1, 1), (2, 0.5), (3, 0.25), (4, 0.12)]:
        out += a * np.sin(2 * np.pi * f * n * t * (1 + 0.0007 * np.sin(2 * np.pi * 0.11 * t)))
    env = np.minimum(1, t / att) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.7))
    return out * env * 0.05 * gain


# acordes (Ré maior)
D = [50, 57, 62, 66]
Bm = [47, 54, 59, 62]
G = [43, 55, 59, 62]
A = [45, 52, 57, 61]
Em = [40, 52, 55, 59]
DF = [42, 54, 57, 62]
Asus = [45, 52, 57, 62]
AC = [49, 57, 61, 64]
GTR = {  # vozes de violão (6 cordas, região média)
    "D": [50, 57, 62, 66], "G": [43, 47, 50, 55, 59, 67], "Bm": [47, 54, 59, 62, 66],
    "A": [45, 52, 57, 61, 64], "Em": [40, 47, 52, 55, 59, 64], "DF": [42, 50, 57, 62, 66],
    "AC": [49, 52, 57, 61, 64],
}

# ===================================================== A) 0–7,9 atmosfera
add(drone(26, 7.6, 1.3, 3.0), 0.0)                      # Ré grave
add(drone(33, 7.4, 0.6, 3.5), 0.6, pan=0.2)             # quinta
add(strings([62, 69], 6.0, att=3.0, relt=1.2, gain=0.55, bright=5000), 1.6, pan=-0.3)
add(strings([74, 78], 4.0, att=2.5, relt=0.8, gain=0.35, bright=6000), 3.6, pan=0.35)
for tt, m, v in [(1.3, 74, 0.22), (2.9, 69, 0.2), (4.4, 76, 0.22), (5.6, 78, 0.24)]:
    add(piano(m, 1.4, v), tt, pan=0.3)
for tt, g in [(3.4, 0.35), (4.0, 0.3), (5.8, 0.45), (6.4, 0.4)]:   # pulso de "coração"
    add(kick(g, 80, 38, 0.3), tt)
add(riser(2.6, 1.0), 7.9 - 2.6)
add(reverse_cymbal(1.6, 1.0), 7.9 - 1.6, pan=0.1)

# ===================================================== B) 7,9–13,3 impacto + pulso
add(boom(1.4), 7.9)
add(taiko(1.4, 70, 1.6), 7.9)
add(crash(1.2), 7.9, pan=-0.2)
for i, ch in enumerate([D, Bm, G, A]):
    t0 = 7.9 + i * 1.2 + (0.0 if i == 0 else 0.0)
    add(strings(ch[1:] + [ch[1] + 12], 1.25, att=0.15, relt=0.9, gain=1.0), t0, pan=-0.15)
    add(strings([ch[0] - 12], 1.25, att=0.15, relt=0.9, gain=1.3), t0, pan=0.15)
    for k in range(4):  # metais em colcheias pontuadas
        if k in (0, 3) or i == 3:
            add(brass([ch[0], ch[1]], 0.18, 0.9), t0 + k * 0.3, pan=0.05)
add(strings([57, 62, 64], 0.8, att=0.4, relt=0.6, gain=0.9), 12.7)  # Asus suspenso
add(strings([33], 0.8, att=0.3, relt=0.6, gain=1.2), 12.7)
pat = [0.0, 0.9, 1.2, 1.8, 2.1]
for b in range(3):
    for p in pat:
        tt = 7.9 + BAR * b + p
        if 8.0 < tt < 13.1:
            add(taiko(0.9 if p == 0 else 0.6, 95 if p in (0, 1.2) else 120), tt, pan=0.0 if p == 0 else (0.25 if p > 1.5 else -0.25))
for k, tt in enumerate(np.arange(12.4, 13.25, 0.15)):  # virada
    add(tom(150 - k * 8, 0.8 + k * 0.05), tt, pan=-0.3 + k * 0.1)

# ===================================================== C) 13,3–20,9 convivência
prog_c = [("D", D, 13.3), ("G", G, 15.7), ("Bm", Bm, 18.1), ("A", A, 19.3)]
for name, ch, t0 in prog_c:
    dur = 2.4 if t0 < 19 else 1.6
    add(strings(ch[1:], dur, att=0.8, relt=1.0, gain=0.5), t0, pan=-0.2)
    add(strings([ch[0] - 12], dur, att=0.6, relt=1.0, gain=0.8), t0, pan=0.2)
    # dedilhado / batida: B . B . C B . B (colcheias de 0,3 s)
    steps = int(round(dur / 0.3))
    for k in range(steps):
        if k % 8 in (0, 2, 3, 5, 6):
            strum(GTR[name], t0 + k * 0.3, down=(k % 2 == 0), vel=0.5 if k % 8 == 0 else 0.36, dur=1.2, pan=0.25)
for tt in np.arange(13.3, 20.6, 0.3):
    add(shaker(0.8 if int(round((tt - 13.3) / 0.3)) % 2 else 0.5), tt, pan=0.45)
for tt in np.arange(13.3, 20.6, BEAT):
    k = int(round((tt - 13.3) / BEAT))
    if k % 2 == 0:
        add(kick(0.55), tt)
    else:
        add(clap(0.8), tt, pan=-0.1)
for k, tt in enumerate(np.arange(20.3, 20.85, 0.15)):
    add(tom(170 - k * 12, 0.5), tt)

# ===================================================== D) 20,9–30,6 espiritual
add(strings([50, 57, 62], 3.5, att=1.4, relt=1.6, gain=0.55), 20.9, pan=-0.1)
add(strings([38], 3.5, att=1.4, relt=1.6, gain=0.8), 20.9, pan=0.1)
add(piano(66, 2.0, 0.28), 21.1, pan=0.2)
add(piano(64, 1.6, 0.25), 22.3, pan=0.25)
add(piano(62, 2.2, 0.26), 23.1, pan=0.2)
prog_d = [(G, 24.4), (DF, 26.8), (Em, 29.2)]
arp = [0, 1, 2, 3, 2, 1, 2, 3]
for ch, t0 in prog_d:
    dur = 2.4 if t0 < 29 else 1.6
    add(strings(ch[1:] + [ch[2] + 12], dur + 0.2, att=1.0, relt=1.6, gain=0.7), t0, pan=-0.2)
    add(strings([ch[0] - 12], dur + 0.2, att=1.0, relt=1.6, gain=0.9), t0, pan=0.2)
    add(piano(ch[0] - 12, dur, 0.4), t0)
    for k in range(int(dur / 0.3)):
        add(piano(ch[arp[k % 8]] + 12, 0.5, 0.24 + 0.06 * (k % 4 == 0)), t0 + k * 0.3, pan=0.25 * np.sin(k))
add(piano(74, 2.0, 0.3), 25.6, pan=0.3)
add(piano(73, 1.6, 0.28), 28.0, pan=0.3)
add(reverse_cymbal(1.2, 0.5), 30.6 - 1.2)

# ===================================================== E) 30,6–39,0 calor humano
prog_e = [("D", D, 30.6), ("AC", AC, 33.0), ("Bm", Bm, 35.4), ("G", G, 37.8)]
for name, ch, t0 in prog_e:
    dur = 2.4 if t0 < 37 else 1.2
    add(strings(ch[1:], dur + 0.2, att=0.9, relt=1.4, gain=0.6), t0, pan=-0.2)
    add(strings([ch[0] - 12], dur + 0.2, att=0.9, relt=1.4, gain=0.85), t0, pan=0.2)
    gv = GTR[name]
    for k in range(int(round(dur / 0.3))):
        m = gv[[0, 2, 1, 3, 2, 4 % len(gv), 3, 2][k % 8] % len(gv)]
        add(guitar(m + 12 if k % 8 == 5 else m, 1.4, 0.5), t0 + k * 0.3, pan=0.3)
    add(piano(ch[0] - 12, dur, 0.36), t0)
for tt in np.arange(30.6, 38.95, BEAT * 2):
    add(kick(0.42, 95, 42, 0.3), tt)
for tt in np.arange(31.2, 38.95, BEAT * 2):
    add(clap(0.45), tt, pan=-0.1)
for tt in np.arange(30.6, 38.95, 0.3):
    add(shaker(0.45), tt, pan=0.45)

# ===================================================== F) 39,0–45,0 crescendo
prog_f = [(G, 39.0, 2.4), (A, 41.4, 2.4), (Asus, 43.8, 1.2)]
for ch, t0, dur in prog_f:
    add(strings(ch[1:] + [ch[1] + 12], dur + 0.1, att=0.5, relt=0.6, gain=0.8 + 0.15 * (t0 > 41)), t0, pan=-0.2)
    add(strings([ch[0] - 12], dur + 0.1, att=0.5, relt=0.6, gain=1.0), t0, pan=0.2)
    for k in range(int(round(dur / 0.3))):
        strum(GTR["G" if ch is G else "A"], t0 + k * 0.3, down=(k % 2 == 0), vel=0.42, dur=0.8, pan=0.25)
for tt in np.arange(39.0, 44.95, BEAT):
    add(kick(0.55), tt)
for k, tt in enumerate(np.arange(41.4, 43.8, 0.3)):
    add(tom(120 + (k % 2) * 30, 0.5 + 0.04 * k), tt, pan=-0.2 + 0.4 * (k % 2))
for k, tt in enumerate(np.arange(43.8, 44.98, 0.075)):
    add(snare(0.3 + 0.6 * k / 16, 0.08), tt, pan=0.05)
add(riser(3.0, 1.1), 45.0 - 3.0)
add(reverse_cymbal(1.8, 1.0), 45.0 - 1.8, pan=-0.1)

# ===================================================== G) 45,0–59,0 cartela final
add(boom(1.5), 45.0)
add(taiko(1.4, 68, 1.7), 45.0)
add(crash(1.3, 2.0), 45.0, pan=0.2)
prog_g = [(D, 45.0), (Bm, 47.4), (G, 49.8), (A, 52.2)]
for ch, t0 in prog_g:
    dur = 2.4 if t0 < 52 else 3.4
    add(strings(ch[1:] + [ch[1] + 12, ch[3] + 12], dur + 0.1, att=0.3, relt=0.8, gain=0.95), t0, pan=-0.2)
    add(strings([ch[0] - 12, ch[0] - 24], dur + 0.1, att=0.3, relt=0.8, gain=1.1), t0, pan=0.2)
    for k in range(int(round(dur / 0.3))):
        if k % 8 in (0, 3, 6):
            add(brass([ch[0], ch[1]], 0.16, 0.7), t0 + k * 0.3)
    for p in [0.0, 0.9, 1.2, 1.8, 2.1]:
        if t0 + p < 55.4:
            add(taiko(0.75 if p == 0 else 0.5, 92 if p in (0, 1.2) else 118), t0 + p, pan=0.0)
for k, tt in enumerate(np.arange(54.8, 55.55, 0.125)):
    add(tom(160 - k * 10, 0.7 + k * 0.05), tt, pan=-0.3 + 0.1 * k)
# batida final (fim de "paredes!") e acorde de Ré sustentado
FIN = 55.65
add(boom(1.6, 3.4), FIN)
add(taiko(1.5, 66, 2.0), FIN)
add(crash(1.2, 2.4), FIN, pan=-0.2)
add(strings([50, 57, 62, 66, 69, 74], 2.0, att=0.08, relt=1.8, gain=1.1), FIN, pan=-0.1)
add(strings([26, 38], 2.0, att=0.08, relt=1.8, gain=1.3), FIN, pan=0.1)
add(brass([50, 57, 62], 0.9, 1.0), FIN)
for k, m in enumerate([62, 66, 69, 74, 78]):
    add(piano(m, 3.0, 0.32), FIN + 0.35 + k * 0.12, pan=0.25)

# ===================================================== reverb + master
ir_len = int(2.4 * SR)
tt = np.arange(ir_len) / SR
irL = lp(rng.standard_normal(ir_len) * np.exp(-tt / 0.5), 3500)
irR = lp(rng.standard_normal(ir_len) * np.exp(-tt / 0.5), 3500)
irL /= np.sqrt(np.sum(irL ** 2))
irR /= np.sqrt(np.sum(irR ** 2))
wetL = fftconv(L, irL)[:N]
wetR = fftconv(R, irR)[:N]
outL = 0.8 * L + 0.35 * wetL
outR = 0.8 * R + 0.35 * wetR
n_out = int(TOTAL * SR)
outL, outR = outL[:n_out], outR[:n_out]
t = np.arange(n_out) / SR
fade = np.clip((TOTAL - t) / 2.6, 0, 1) ** 1.3
outL *= fade
outR *= fade
# compressão suave (soft clip) e normalização de pico
peak = max(np.abs(outL).max(), np.abs(outR).max())
outL, outR = np.tanh(outL / peak * 1.4) / np.tanh(1.4), np.tanh(outR / peak * 1.4) / np.tanh(1.4)
outL, outR = outL * 0.85, outR * 0.85
pcm = (np.stack([outL, outR], axis=1) * 32767).astype("<i2")
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("ok", sys.argv[1], f"{n_out / SR:.2f}s")
