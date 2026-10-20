"""Trilha instrumental original do reel "Culto Hero" (síntese, sem samples de terceiros).

Ré menor, 100 bpm (tempo = 0,6 s; compasso = 2,4 s). Seções presas aos cortes de roteiro.py:
  0,0–15,1   ALERTA: impacto, drone grave, batida de coração, ostinato de cordas graves
  15,1–17,0  CORTE SECO ("Isso incomoda.")
  17,0–23,2  motivo 2: pulso retoma, pizzicato curioso; "estranhar" -> parada de fita
  24,4–38,5  motivo 3: semicolcheias, tons, metais; o mais tenso; impactos em "Aí já era" / "Não tem mais"
  38,6–45,4  VIRADA: quase silêncio, só relógio (tique-taque) e drone; impacto em "não VAI"
  45,4–48,0  riser + rufo
  48,0–56,35 DROP: tema heroico Dm–B♭–F–C, bateria de trailer
  56,35–59,2 silêncio (a última frase é dita no seco)
  59,25      CARIMBO: acorde de Ré MAIOR (o "meio sorriso" da trilha) e sustentação até 63,5

Uso: python3 -I tools/gerar_trilha.py assets/music/trilha_culto_hero.wav
Determinística (semente fixa).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_util import fftconv, hp, lp, wav  # noqa: E402
from roteiro import BEAT, SR, TOTAL  # noqa: E402

N = int((TOTAL + 3) * SR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(20261024)
BAR = 4 * BEAT


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, start, pan=0.0, gain=1.0):
    i = int(round(start * SR))
    if i >= N or i < 0:
        return
    sig = sig[: N - i]
    L[i: i + len(sig)] += sig * np.cos((pan + 1) * np.pi / 4) * gain
    R[i: i + len(sig)] += sig * np.sin((pan + 1) * np.pi / 4) * gain


def env_ar(n, att, rel_from, rel):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(att, 1e-4)) * np.where(t < rel_from, 1.0, np.exp(-(t - rel_from) / rel))


# ------------------------------------------------------------------ instrumentos
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
            for n in range(1, max(2, int(min(14, bright / fd)))):
                out += np.sin(n * ph) / (n ** 1.35)
    env = np.minimum(1, t / att) * np.where(t < dur, 1.0, np.exp(-(t - dur) / (relt / 3)))
    return lp(out * env, 2400) * 0.012 * gain


def stacc(m, dur=0.22, gain=1.0, bright=2600):
    """Cordas graves em staccato (spiccato): serra com envelope curto."""
    t = np.arange(int((dur + 0.15) * SR)) / SR
    out = np.zeros_like(t)
    f = midi_hz(m)
    for d in (-0.05, 0.0, 0.05):
        ph = 2 * np.pi * f * 2 ** (d / 12) * t + rng.uniform(0, 6.28)
        for n in range(1, int(min(24, bright / f))):
            out += np.sin(n * ph) / n
    env = np.minimum(1, t / 0.008) * np.exp(-t / (dur * 0.55))
    return lp(out * env, bright) * 0.05 * gain


def pizz(m, gain=1.0):
    t = np.arange(int(0.6 * SR)) / SR
    f = midi_hz(m)
    out = sum(np.sin(2 * np.pi * f * n * t) * np.exp(-t * (6 + 3 * n)) / n for n in range(1, 7))
    return out * np.minimum(1, t / 0.003) * 0.12 * gain


def brass(notes, dur, gain=1.0):
    ln = dur + 0.3
    t = np.arange(int(ln * SR)) / SR
    out = np.zeros_like(t)
    for m in notes:
        f = midi_hz(m)
        for d in (-0.05, 0.05):
            ph = 2 * np.pi * f * 2 ** (d / 12) * t
            for n in range(1, int(min(18, 5000 / f))):
                out += np.sin(n * ph) / n * np.exp(-n * 0.08 * (1 + 3 * t))
    env = np.minimum(1, t / 0.03) * np.where(t < dur, np.exp(-t * 0.9), np.exp(-dur * 0.9) * np.exp(-(t - dur) / 0.08))
    return lp(out * env, 1900) * 0.03 * gain


def piano(m, dur, vel=0.6):
    f = midi_hz(m)
    ring = min(dur + 1.6, 6.0)
    t = np.arange(int(ring * SR)) / SR
    out = np.zeros_like(t)
    for n in range(1, 12):
        fn = f * n * np.sqrt(1 + 0.00035 * n * n)
        if fn > 9000:
            break
        k = 0.9 + 0.55 * n + f / 900.0
        out += (1.0 / n ** 1.6) * (0.72 * np.exp(-k * t) + 0.28 * np.exp(-k * t / 5.0)) * np.sin(2 * np.pi * fn * t)
    rel = np.ones_like(t)
    off = int(dur * SR)
    if off < len(t):
        rel[off:] = np.exp(-(t[off:] - dur) / 0.35)
    return out * np.minimum(1, t / 0.004) * rel * vel * 0.22


def kick(gain=1.0, f0=110, f1=42, dec=0.35):
    t = np.arange(int(0.6 * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.045)
    click = rng.standard_normal(len(t)) * np.exp(-t / 0.003) * 0.15
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / dec) + click) * 0.5 * gain


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
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
            + lp(rng.standard_normal(len(t)), 1500) * np.exp(-t / 0.03) * 0.4) * 0.35 * gain


def snare(gain=1.0, dec=0.12):
    t = np.arange(int(0.5 * SR)) / SR
    nz = hp(rng.standard_normal(len(t)), 900) * np.exp(-t / dec)
    return (nz * 0.6 + np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05) * 0.5) * 0.3 * gain


def crash(gain=1.0, dec=1.6):
    t = np.arange(int(3.5 * SR)) / SR
    return hp(rng.standard_normal(len(t)), 4000) * np.exp(-t / dec) * 0.16 * gain


def reverse_cymbal(length, gain=1.0):
    t = np.arange(int(length * SR)) / SR
    return hp(rng.standard_normal(len(t)), 3500) * (t / length) ** 2.6 * 0.2 * gain


def riser(length, gain=1.0):
    t = np.arange(int(length * SR)) / SR
    x = t / length
    nz = rng.standard_normal(len(t))
    sweep = lp(nz, 600) * (1 - x) + hp(nz, 2500) * x
    tone = np.sin(2 * np.pi * np.cumsum(140 + 1100 * x ** 2) / SR) * 0.3
    return (sweep + tone) * x ** 2.2 * 0.2 * gain


def boom(gain=1.0, dur=3.0):
    t = np.arange(int(dur * SR)) / SR
    f = 34 + 52 * np.exp(-t / 0.08)
    nz = lp(rng.standard_normal(len(t)), 400) * np.exp(-t / 0.25) * 0.6
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9) + nz) * 0.55 * gain


def drone(m, dur, gain=1.0, att=2.5):
    t = np.arange(int((dur + 2) * SR)) / SR
    f = midi_hz(m)
    out = np.zeros_like(t)
    for n, a in [(1, 1), (2, 0.5), (3, 0.3), (4, 0.15), (5, 0.08)]:
        out += a * np.sin(2 * np.pi * f * n * t * (1 + 0.0007 * np.sin(2 * np.pi * 0.11 * t)))
    env = np.minimum(1, t / att) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.7))
    return out * env * 0.05 * gain


def tique(alto=True, gain=1.0):
    """Relógio: clique de madeira ressonante (tique agudo / taque grave)."""
    t = np.arange(int(0.12 * SR)) / SR
    f = 2300 if alto else 1650
    body = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012) + 0.5 * np.sin(2 * np.pi * f * 2.7 * t) * np.exp(-t / 0.006)
    clk = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.002)
    return (body * 0.5 + clk * 0.4) * 0.25 * gain


def coracao(t0, gain=1.0):
    add(kick(0.75 * gain, 70, 34, 0.22), t0)
    add(kick(0.5 * gain, 64, 32, 0.2), t0 + 0.2)


# ------------------------------------------------------------------ harmonia (Ré menor)
Dm = [50, 53, 57]
Bb = [46, 50, 53]
F = [41, 48, 53, 57]
C = [48, 52, 55]
Gm = [43, 50, 55]
A = [45, 49, 52]
DM = [50, 54, 57]

# ===================================================== A) 0–15,1 ALERTA
add(boom(1.5, 3.4), 0.0)
add(taiko(1.4, 66, 1.8), 0.0)
add(crash(0.9, 1.4), 0.02, pan=-0.2)
add(drone(26, 14.6, 1.3, 1.5), 0.0)
add(drone(33, 14.0, 0.55, 3.0), 0.8, pan=0.25)
for tt in np.arange(1.2, 15.0, 2 * BEAT):
    coracao(tt, 0.7 + 0.3 * (tt / 15))
for k, tt in enumerate(np.arange(0.6, 15.05, BEAT)):
    add(tique(k % 2 == 0, 0.45), tt, pan=0.3)
# numeral 1
add(taiko(1.2, 72, 1.4), 3.85)
add(boom(0.9, 2.2), 3.85)
fig = [38, 38, 38, 41, 38, 38, 40, 36]
for k, tt in enumerate(np.arange(3.85, 15.05, 0.3)):
    m = fig[k % 8] + (0 if tt < 10.9 else 0)
    add(stacc(m, 0.2, 0.85 + 0.25 * ((k % 4) == 0)), tt, pan=-0.15)
    if tt > 10.9:
        add(stacc(m + 12, 0.18, 0.45), tt, pan=0.2)
add(strings(Dm, 3.6, att=1.5, relt=0.4, gain=0.55), 7.2, pan=-0.2)
add(strings(Bb, 3.6, att=1.0, relt=0.3, gain=0.6), 10.8, pan=-0.2)
add(strings([62, 63], 3.0, att=2.0, relt=0.2, gain=0.35, bright=6000), 11.9, pan=0.3)  # semitom: incômodo
add(reverse_cymbal(1.2, 0.6), 15.1 - 1.2)

# ===================================================== B) 17,0–23,2 motivo 2
add(taiko(1.3, 70, 1.5), 17.0)
add(boom(1.0, 2.4), 17.0)
add(drone(26, 6.0, 1.0, 0.4), 17.0)
for tt in np.arange(17.6, 23.0, 2 * BEAT):
    coracao(tt, 0.75)
pz = [62, 65, 69, 65, 62, 64, 65, 60]
for k, tt in enumerate(np.arange(17.6, 23.0, 0.3)):
    if k % 8 not in (3, 7):
        add(pizz(pz[k % 8] - 12 * (k % 2), 0.9), tt, pan=0.25 * np.sin(k))
for k, tt in enumerate(np.arange(17.0, 23.0, 0.3)):
    add(stacc([38, 38, 41, 38][k % 4], 0.18, 0.6), tt, pan=-0.15)
add(strings(Dm, 2.4, att=0.8, relt=0.3, gain=0.45), 18.1, pan=-0.2)
add(strings(Gm, 2.4, att=0.8, relt=0.3, gain=0.45), 20.5, pan=-0.2)
add(strings([57, 61, 64], 1.0, att=0.3, relt=0.2, gain=0.45), 22.2, pan=-0.2)  # A (dominante) suspensa

# ===================================================== C) 24,4–38,5 motivo 3 (o mais perigoso)
add(taiko(1.5, 64, 1.9), 24.4)
add(boom(1.3, 3.0), 24.4)
add(crash(0.8, 1.6), 24.42, pan=0.2)
add(drone(26, 10.5, 1.2, 0.6), 24.4)
prog = [(Dm, 24.4), (Bb, 26.8), (Gm, 29.2), (A, 31.6), (Dm, 32.8)]
for ch, t0 in prog:
    d = 2.4 if t0 < 31 else 1.2
    if t0 > 32:
        d = 2.2
    add(strings(ch + [ch[0] + 12], d + 0.1, att=0.4, relt=0.4, gain=0.7), t0, pan=-0.2)
    add(strings([ch[0] - 12], d + 0.1, att=0.4, relt=0.4, gain=0.9), t0, pan=0.2)
for k, tt in enumerate(np.arange(25.0, 34.95, 0.15)):
    base = 38 if tt < 26.8 else (34 if tt < 29.2 else (31 if tt < 31.6 else (33 if tt < 32.8 else 38)))
    add(stacc(base + (12 if k % 4 == 2 else 0), 0.12, 0.55 + 0.35 * (tt - 25) / 10), tt, pan=-0.1)
for tt in np.arange(25.0, 34.95, BEAT):
    k = int(round((tt - 25.0) / BEAT))
    add(kick(0.6) if k % 2 == 0 else tom(115, 0.7), tt, pan=0.0 if k % 2 == 0 else 0.2)
for tt in [29.84, 31.74, 32.67]:
    add(brass([38, 50, 53], 0.3, 0.9), tt)
for k, tt in enumerate(np.arange(33.6, 34.95, 0.15)):
    add(snare(0.25 + 0.5 * k / 9, 0.07), tt, pan=0.05)
add(reverse_cymbal(1.0, 0.8), 35.06 - 1.0)
# "Aí já era." / "Não tem mais como sumir."
for tt, g in [(35.06, 1.4), (35.63, 1.0), (36.44, 1.2), (37.67, 1.3)]:
    add(taiko(g, 66, 1.4), tt)
    add(boom(0.6 * g, 2.0), tt)
add(brass([38, 45, 50], 0.6, 1.0), 35.63)
add(strings([38, 50], 2.4, att=0.1, relt=1.2, gain=0.8), 35.06, pan=0.1)
add(strings([37, 49], 1.2, att=0.1, relt=1.0, gain=0.7), 37.67, pan=0.1)

# ===================================================== D) 38,6–45,4 VIRADA (relógio)
add(drone(26, 5.6, 0.7, 1.0), 38.6)
for k, tt in enumerate(np.arange(38.4, 44.3, BEAT)):
    add(tique(k % 2 == 0, 1.1), tt, pan=0.15 * (1 if k % 2 else -1))
for tt in np.arange(39.0, 43.6, 4 * BEAT):
    coracao(tt, 0.55)
add(reverse_cymbal(0.6, 0.7), 44.40 - 0.6)
add(boom(1.6, 3.2), 44.40)
add(taiko(1.5, 60, 2.0), 44.40)
add(brass([26, 38, 45], 0.9, 1.1), 44.40)

# ===================================================== E) 45,4–48,0 o risco (riser)
add(riser(2.55, 1.2), 48.0 - 2.55)
add(reverse_cymbal(1.8, 1.1), 48.0 - 1.8, pan=-0.1)
for k, tt in enumerate(np.arange(46.6, 47.9, 0.1)):
    add(snare(0.2 + 0.7 * (k / 13) ** 1.5, 0.06), tt, pan=0.05)
add(strings([50, 57, 62], 2.5, att=2.2, relt=0.05, gain=0.7), 45.45, pan=-0.1)

# ===================================================== F) 48,0–56,35 DROP heroico
add(boom(1.7, 3.0), 48.0)
add(taiko(1.6, 64, 2.0), 48.0)
add(crash(1.3, 2.0), 48.0, pan=0.2)
progF = [(Dm, 48.0), (Bb, 50.4), (F, 52.8), (C, 55.2)]
for ch, t0 in progF:
    d = 2.4 if t0 < 55 else 1.15
    add(strings(ch + [ch[1] + 12, ch[0] + 24], d + 0.05, att=0.2, relt=0.2, gain=1.0), t0, pan=-0.2)
    add(strings([ch[0] - 12, ch[0] - 24], d + 0.05, att=0.2, relt=0.2, gain=1.1), t0, pan=0.2)
    for k in range(int(round(d / 0.3))):
        add(stacc(ch[0] - 12 + (12 if k % 2 else 0), 0.16, 0.8), t0 + k * 0.3, pan=-0.1)
        if k % 8 in (0, 3, 6):
            add(brass([ch[0], ch[1], ch[2]], 0.16, 0.75), t0 + k * 0.3)
for tt in np.arange(48.0, 56.3, BAR):
    for p, kind in [(0.0, "k"), (0.9, "k"), (1.2, "s"), (1.8, "k"), (2.1, "t")]:
        x = tt + p
        if x < 56.3:
            if kind == "k":
                add(kick(0.85), x)
            elif kind == "s":
                add(snare(1.3, 0.2), x)
                add(taiko(0.6, 110), x)
            else:
                add(tom(120, 0.7), x, pan=0.2)
for k, tt in enumerate(np.arange(55.2, 56.3, 0.15)):
    add(tom(170 - k * 9, 0.6 + 0.05 * k), tt, pan=-0.3 + 0.08 * k)
for tt, m in [(48.6, 74), (49.2, 77), (50.4, 74), (51.0, 70), (52.8, 72), (53.4, 77), (55.2, 76)]:
    add(piano(m, 0.9, 0.35), tt, pan=0.3)

# ===================================================== G) 59,25 carimbo: Ré MAIOR
FIN = 59.25
add(boom(1.4, 2.8), FIN)
add(taiko(1.5, 64, 2.0), FIN)
add(crash(1.0, 2.2), FIN, pan=-0.2)
add(strings(DM + [62, 66, 69], 2.6, att=0.06, relt=2.2, gain=1.0), FIN, pan=-0.1)
add(strings([26, 38], 2.6, att=0.06, relt=2.2, gain=1.2), FIN, pan=0.1)
add(brass([50, 54, 57], 0.8, 1.0), FIN)
for k, m in enumerate([66, 69, 74, 78]):
    add(piano(m, 2.2, 0.3), FIN + 0.3 + k * 0.11, pan=0.25)

# ===================================================== reverb, cortes secos e master
ir_len = int(2.2 * SR)
tt = np.arange(ir_len) / SR
irL = lp(rng.standard_normal(ir_len) * np.exp(-tt / 0.45), 3500)
irR = lp(rng.standard_normal(ir_len) * np.exp(-tt / 0.45), 3500)
irL /= np.sqrt(np.sum(irL ** 2))
irR /= np.sqrt(np.sum(irR ** 2))
outL = 0.8 * L + 0.3 * fftconv(L, irL)[:N]
outR = 0.8 * R + 0.3 * fftconv(R, irR)[:N]
n_out = int(TOTAL * SR)
outL, outR = outL[:n_out], outR[:n_out]
t = np.arange(n_out) / SR


def corte(a, b, fo=0.02, fi=0.02):
    """Silêncio entre a e b (corte seco)."""
    return 1 - np.clip((t - a) / fo, 0, 1) * np.clip((b - t) / fi, 0, 1)


def fita(a, d=0.35):
    """Parada de fita a partir de a: reamostra com velocidade caindo a zero."""
    i0, n = int(a * SR), int(d * SR)
    vel = np.linspace(1, 0, n) ** 1.3
    pos = i0 + np.cumsum(vel)
    for ch in (outL, outR):
        seg = np.interp(pos, np.arange(len(ch)), ch) * np.linspace(1, 0.2, n)
        ch[i0: i0 + n] = seg


fita(23.05, 0.4)
g = corte(15.12, 16.98) * corte(23.45, 24.38) * corte(47.92, 47.995, 0.01, 0.005) * corte(56.35, 59.24, 0.03, 0.005)
outL *= g
outR *= g
fade = np.clip((TOTAL - t) / 3.0, 0, 1) ** 1.3
outL *= fade
outR *= fade
peak = max(np.abs(outL).max(), np.abs(outR).max())
outL, outR = np.tanh(outL / peak * 1.4) / np.tanh(1.4), np.tanh(outR / peak * 1.4) / np.tanh(1.4)
wav(sys.argv[1], np.stack([outL, outR], 1) * 0.85)
print("ok", sys.argv[1], f"{n_out / SR:.2f}s")
