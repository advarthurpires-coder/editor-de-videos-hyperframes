"""Trilha instrumental original (piano + cordas) para o reel "Promessa não é garantia".

Gerada por síntese (sem samples de terceiros, sem vocal, sem batida eletrônica).
- 0,00–14,04 s da trilha (14,56–28,60 s do vídeo): Si menor, pulso de cordas
  em colcheias e notas graves de piano -> levemente tensa.
- 14,04 s em diante (a partir de "calma"): Ré maior, arpejos suaves de piano
  sobre colchão de cordas -> leve, acolhedora.
- Fade-out final até 76,24 s (fim do vídeo em 90,80 s).

Uso: python3 tools/gerar_trilha.py assets/music/trilha_piano_cordas.wav
Determinística (semente fixa).
"""
import sys
import wave

import numpy as np

SR = 48000
TOTAL = 76.24  # 90.80 - 14.56
CALM_AT = 14.04  # 28.60 - 14.56
rng = np.random.default_rng(20261008)

N = int(TOTAL * SR) + SR
L = np.zeros(N)
R = np.zeros(N)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    lg = np.cos((pan + 1) * np.pi / 4) * gain
    rg = np.sin((pan + 1) * np.pi / 4) * gain
    L[i : i + len(sig)] += sig * lg
    R[i : i + len(sig)] += sig * rg


def piano(m, dur, vel=0.6):
    """Piano por síntese aditiva com inarmonicidade e decaimento em dois estágios."""
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
    # liberação ao soltar a tecla
    rel = np.ones_like(t)
    off = int(dur * SR)
    if off < len(t):
        rel[off:] = np.exp(-(t[off:] - dur) / 0.35)
    # martelo: ruído curto filtrado
    hn = rng.standard_normal(int(0.012 * SR))
    hn = np.convolve(hn, np.ones(6) / 6, mode="same") * np.exp(-np.arange(len(hn)) / (0.003 * SR))
    out[: len(hn)] += hn * 0.08 * vel
    return out * att * rel * vel * 0.22


def strings(notes, dur, att=1.2, relt=1.6, gain=1.0, tremolo=None):
    """Cordas: serras detunadas (aditivas, limitadas em banda) com ataque lento."""
    ln = dur + relt
    t = np.arange(int(ln * SR)) / SR
    out = np.zeros_like(t)
    for m in notes:
        f = midi_hz(m)
        for d in (-0.07, -0.025, 0.0, 0.03, 0.065):
            fd = f * 2 ** (d / 12)
            vib = 1 + 0.0018 * np.sin(2 * np.pi * (4.8 + d * 8) * t + d * 40)
            ph = 2 * np.pi * fd * np.cumsum(vib) / SR + rng.uniform(0, 6.28)
            nmax = int(min(14, 3800 / fd))
            for n in range(1, max(2, nmax)):
                out += np.sin(n * ph) / (n ** 1.35)
    env = np.minimum(1, t / att) * np.where(t < dur, 1.0, np.exp(-(t - dur) / (relt / 3)))
    if tremolo is not None:
        rate, depth = tremolo
        env = env * (1 - depth * (0.5 + 0.5 * np.cos(2 * np.pi * rate * t)))
    out *= env
    # suavização (passa-baixas simples de 1 polo, duas vezes)
    a = np.exp(-2 * np.pi * 2200 / SR)
    for _ in range(2):
        out = lfilter1(out, a)
    return out * 0.012 * gain


def lfilter1(x, a):
    """y[n] = (1-a) x[n] + a y[n-1] via convolução com resposta exponencial truncada."""
    h = (1 - a) * a ** np.arange(int(np.log(1e-4) / np.log(a)) + 1)
    return fftconv(x, h)[: len(x)]


def fftconv(x, h):
    n = len(x) + len(h) - 1
    size = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(h, size), size)[:n]


# ---------------------------------------------------------------- tensão (Si menor)
beat8 = 60 / 80 / 2  # colcheia a 80 bpm
tense_chords = [
    (0.0, [47, 54, 59, 62]),  # Bm
    (3.5, [43, 50, 55, 59]),  # G
    (7.0, [40, 47, 55, 59, 66]),  # Em9-ish
    (10.5, [42, 49, 54, 59, 61]),  # F#sus4 -> tensão
]
for start, notes in tense_chords:
    d = 3.5 if start < 10.5 else CALM_AT - start
    add(strings(notes[1:], d + 0.2, att=0.6, relt=1.2, gain=0.9, tremolo=(80 / 60 * 2, 0.45)), start, pan=-0.15)
    add(strings([notes[0] - 12], d + 0.2, att=0.8, relt=1.2, gain=1.3), start, pan=0.1)
    add(piano(notes[0] - 12, 2.8, 0.55), start, pan=-0.1)
    add(piano(notes[0], 2.4, 0.4), start + 0.02, pan=-0.05)
# notas agudas esparsas (inquietação)
for tt, m in [(1.5, 74), (3.0, 73), (5.25, 74), (8.4, 78), (9.9, 76), (12.0, 73), (13.1, 71)]:
    add(piano(m, 1.0, 0.30), tt, pan=0.35)

# ---------------------------------------------------------------- calma (Ré maior)
bar = 60 / 72 * 4  # 3,333 s
eighth = bar / 8
calm_prog = [
    [50, 57, 62, 66, 69],  # D
    [49, 57, 61, 64, 69],  # A/C#
    [47, 54, 62, 66, 69],  # Bm7
    [43, 55, 59, 62, 66],  # Gmaj7
]
arp_shapes = [0, 2, 3, 4, 3, 2, 1, 2]
t0 = CALM_AT
i = 0
end_music = TOTAL - 4.6
while t0 < end_music:
    ch = calm_prog[i % 4]
    last = t0 + bar >= end_music
    d = bar if not last else (TOTAL - t0 - 0.6)
    add(strings(ch[1:4], d + 0.3, att=1.6 if i == 0 else 1.0, relt=2.2, gain=0.85), t0, pan=-0.2)
    add(strings([ch[0] - 12], d + 0.3, att=1.4, relt=2.2, gain=1.0), t0, pan=0.15)
    add(piano(ch[0] - 12, bar * 0.95, 0.42), t0, pan=-0.05)
    if not last:
        for k in range(8):
            m = ch[arp_shapes[k]] + 12
            v = 0.30 + 0.08 * (k == 0) + 0.03 * rng.standard_normal()
            add(piano(m, eighth * 1.6, max(0.18, v)), t0 + k * eighth + 0.004 * rng.standard_normal(), pan=0.25 * np.sin(k))
        # melodia simples a cada dois compassos
        if i % 2 == 1:
            add(piano(ch[4] + 12, bar * 0.5, 0.33), t0 + bar * 0.5, pan=0.3)
    else:
        for k, m in enumerate([62, 66, 69, 74]):
            add(piano(m + 12 - 12, 4.0, 0.32), t0 + k * 0.18, pan=0.2)
        break
    t0 += bar
    i += 1

# ---------------------------------------------------------------- reverb (convolução)
ir_len = int(2.6 * SR)
tt = np.arange(ir_len) / SR
irL = rng.standard_normal(ir_len) * np.exp(-tt / 0.55)
irR = rng.standard_normal(ir_len) * np.exp(-tt / 0.55)
irL = lfilter1(irL, np.exp(-2 * np.pi * 3500 / SR))
irR = lfilter1(irR, np.exp(-2 * np.pi * 3500 / SR))
irL /= np.sqrt(np.sum(irL ** 2))
irR /= np.sqrt(np.sum(irR ** 2))
wetL = fftconv(L, irL)[:N]
wetR = fftconv(R, irR)[:N]
outL = 0.78 * L + 0.42 * wetL
outR = 0.78 * R + 0.42 * wetR

n_out = int(TOTAL * SR)
outL, outR = outL[:n_out], outR[:n_out]
t = np.arange(n_out) / SR
fade = np.clip((TOTAL - t) / 4.0, 0, 1) ** 1.5  # fade-out nos 4 s finais
fade_in = np.clip(t / 0.8, 0, 1)
outL *= fade * fade_in
outR *= fade * fade_in
peak = max(np.abs(outL).max(), np.abs(outR).max())
outL, outR = outL / peak * 0.7, outR / peak * 0.7

pcm = (np.stack([outL, outR], axis=1) * 32767).astype("<i2")
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("ok", sys.argv[1], f"{n_out / SR:.2f}s")
