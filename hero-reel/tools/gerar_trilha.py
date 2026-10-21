"""Trilha instrumental original do reel "Convite HERO — Deus tem um encontro com você" (síntese, sem samples).

Ré maior, ~100 bpm. A grade é calculada para que dois tempos fortes caiam exatamente no "Todo-Poderoso"
(golpe principal) e na cartela final; o "Grandão" cai dois tempos depois do golpe. Seções (tempo do reel):
  0 – 4,2     abertura: pad, piano em colcheias, batida de coração
  4,2 – 7,8   o convite: violão dedilhado + brilho no "especial"
  7,8 – 12,4  encontro: bumbo leve, palmas; golpe no "24"
  12,4 – 16   traga um amigo / parente: chocalho e baixo pulsando
  16 – 21,8   subida: cordas crescendo, tons, riser
  21,8 – 24,4 TODO-PODEROSO / GRANDÃO: golpes, acordes cheios
  24,4 – 32,3 groove quente sob a voz (convidado especial, tela dividida)
  32,3 – 33,8 "Amém?": respiro e virada
  33,8 – fim  cartela: golpe final e Ré sustentado
Instrumentos: os mesmos sintetizadores das trilhas anteriores do HERO (convite-hero/tools/gerar_trilha.py).
Uso: python3 -I tools/gerar_trilha.py assets/music/trilha.wav   (rodar sincronia.py antes)
Determinística (semente fixa).
"""
import json
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roteiro import TOTAL, SR  # noqa: E402
EV = json.load(open(os.path.dirname(os.path.abspath(__file__)) + "/eventos.json"))["ev"]

TODO, CARTELA = EV["todo"], EV["cartela"]
BAR = (CARTELA - TODO) / 5
BEAT = BAR / 4
G0 = TODO - 9 * BAR           # 1º tempo forte da grade (~0,16 s)
N = int((TOTAL + 3) * SR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(20261024)


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
Asus = [45, 52, 57, 62]
GTR = {"D": [50, 57, 62, 66], "G": [43, 47, 50, 55, 59, 67], "Bm": [47, 54, 59, 62, 66], "A": [45, 52, 57, 61, 64],
       "Em": [40, 47, 52, 55, 59, 64]}
PROG = [("D", D), ("Bm", Bm), ("G", G), ("A", A)]


def bar(i):
    return G0 + i * BAR


def quando(t):
    """índice do compasso que contém t"""
    return int(np.floor((t - G0) / BAR))


SEG = EV["seg"]
SPLIT, SPLIT_FIM, AMEM = EV["split"], EV["split_fim"], EV["amem"]
S2, S4, S6, S9, S11 = SEG[1], SEG[3], SEG[5], SEG[8], SEG[10]

# ===================================================== pad contínuo + piano em colcheias (compassos 0 .. 13)
for i in range(0, 14):
    if bar(i) >= CARTELA - 0.05: break
    nome, ch = PROG[i % 4]
    t0 = bar(i)
    dur = min(BAR, CARTELA - t0)
    forte = TODO - 0.01 <= t0 < S11 - 0.01
    add(strings(ch[1:], dur, att=0.9 if i == 0 else 0.4, relt=1.0, gain=0.34 if not forte else 0.85), t0, pan=-0.25)
    add(strings([ch[0] - 12], dur, att=0.6, relt=1.0, gain=0.55 if not forte else 1.0), t0, pan=0.25)
    if AMEM - 0.3 < t0 < CARTELA: continue
    # piano: arpejo em colcheias (acompanha a fala, sem disputar com ela)
    arp = [ch[0] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 12, ch[1] + 24, ch[2] + 12, ch[3] + 12, ch[2] + 12]
    for k, m in enumerate(arp):
        tt = t0 + k * BEAT / 2
        if tt >= CARTELA - 0.05 or (AMEM - 0.2 < tt < CARTELA): continue
        add(piano(m, 0.35, 0.13 if k % 2 else 0.17), tt, pan=0.3 if k % 2 else -0.05)

# ===================================================== batida de coração (abertura)
for i in range(0, 2):
    for p in (0, 2):
        tt = bar(i) + p * BEAT
        if tt < S2: add(kick(0.42, 90, 40, 0.25), tt); add(kick(0.25, 90, 40, 0.2), tt + 0.16)

# ===================================================== o convite: violão dedilhado
for i in range(quando(S2), quando(S4) + 1):
    nome, ch = PROG[i % 4]
    for k in range(8):
        tt = bar(i) + k * BEAT / 2
        if S2 - 0.05 <= tt < S4 + 1.2:
            m = GTR[nome][[0, 2, 3, 4, 2, 3, 1, 3][k] % len(GTR[nome])]
            add(guitar(m, 1.4, 0.32 if k else 0.42), tt, pan=0.35)

# ===================================================== encontro + traga: bumbo, palmas, chocalho, baixo
for tt in np.arange(bar(quando(S4)), TODO - 0.01, BEAT):
    if tt < S4 - 0.01: continue
    k = int(round((tt - G0) / BEAT))
    add(kick(0.5 if tt < S6 else 0.62), tt)
    if k % 2 == 1: add(clap(0.55 if tt < S6 else 0.7), tt, pan=-0.1)
for tt in np.arange(bar(quando(S6)), TODO - 0.01, BEAT / 2):
    if tt >= S6 - 0.01: add(shaker(0.55), tt, pan=0.45)
for tt in np.arange(bar(quando(S6)), TODO - 0.01, BEAT / 2):
    if tt >= S6 - 0.01:
        nome, ch = PROG[quando(tt) % 4]
        add(strings([ch[0] - 12], 0.18, att=0.01, relt=0.15, gain=0.9), tt, pan=0.0)

# golpe no "24"
add(boom(0.6, 1.4), EV["dia24"])
add(taiko(0.7, 80, 1.2), EV["dia24"])

# ===================================================== subida até o TODO-PODEROSO
for k, tt in enumerate(np.arange(bar(quando(S9)), TODO - 0.01, BEAT)):
    if tt >= S9: add(taiko(0.35 + 0.02 * k, 100 if k % 2 == 0 else 125), tt, pan=-0.2 + 0.4 * (k % 2))
add(strings([57, 62, 64, 69], TODO - S9, att=TODO - S9, relt=0.2, gain=0.7), S9, pan=-0.1)
for k, tt in enumerate(np.arange(TODO - BAR / 2, TODO - 0.01, BEAT / 4)):
    add(snare(0.2 + 0.06 * k, 0.07), tt)
add(riser(1.8, 0.9), TODO - 1.8)
add(reverse_cymbal(1.2, 0.8), TODO - 1.2, pan=-0.1)

# ===================================================== TODO-PODEROSO / GRANDÃO
for t0, gg in ((TODO, 1.4), (EV["grandao"], 1.2)):
    add(boom(gg), t0)
    add(taiko(gg, 68, 1.6), t0)
    add(crash(0.9 * gg / 1.4), t0, pan=-0.2)
    add(brass([50, 57, 62], 0.5, 0.9), t0)
for tt in np.arange(TODO, S11 - 0.01, BEAT):
    k = int(round((tt - TODO) / BEAT))
    if k % 2 == 0 and tt not in (TODO,): add(taiko(0.55, 95), tt, pan=0.1)
    add(shaker(0.5), tt, pan=0.45)

# ===================================================== groove quente (24,4 – 32,3)
for tt in np.arange(bar(quando(S11)), AMEM - 0.2, BEAT):
    if tt < S11 - 0.01: continue
    k = int(round((tt - G0) / BEAT))
    cheio = tt >= SPLIT - 0.01
    add(kick(0.5 if not cheio else 0.6), tt)
    if k % 2 == 1: add(clap(0.5 if not cheio else 0.65), tt, pan=-0.1)
    add(shaker(0.35), tt + BEAT / 2, pan=0.45)
for i in range(quando(S11), quando(AMEM) + 1):
    nome, ch = PROG[i % 4]
    for k in range(8):
        tt = bar(i) + k * BEAT / 2
        if S11 <= tt < AMEM - 0.2:
            add(guitar(GTR[nome][[0, 2, 3, 4, 2, 3, 1, 3][k] % len(GTR[nome])], 1.2, 0.28), tt, pan=0.35)
add(strings([74, 78, 81], 1.6, att=0.05, relt=1.2, gain=0.35), EV["especial2"], pan=0.3)

# ===================================================== "Amém?" — respiro e virada
add(strings([62, 66, 69], 0.5, att=0.02, relt=0.6, gain=0.5), AMEM)
for k, tt in enumerate(np.arange(CARTELA - BAR / 2, CARTELA - 0.01, BEAT / 4)):
    add(tom(170 - k * 9, 0.55 + 0.05 * k), tt, pan=-0.3 + 0.08 * k)
add(riser(1.0, 0.6), CARTELA - 1.0)

# ===================================================== cartela: golpe final e Ré sustentado
FIN = CARTELA
add(boom(1.6, 3.4), FIN)
add(taiko(1.5, 66, 2.0), FIN)
add(crash(1.2, 2.4), FIN, pan=-0.2)
add(strings([50, 57, 62, 66, 69, 74], 3.0, att=0.08, relt=1.8, gain=1.1), FIN, pan=-0.1)
add(strings([26, 38], 3.0, att=0.08, relt=1.8, gain=1.3), FIN, pan=0.1)
add(brass([50, 57, 62], 0.9, 1.0), FIN)
for k, m in enumerate([62, 66, 69, 74, 78]):
    add(piano(m, 2.4, 0.3), FIN + 0.35 + k * 0.12, pan=0.25)

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
fade = np.clip((TOTAL - t) / 1.6, 0, 1) ** 1.3
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
