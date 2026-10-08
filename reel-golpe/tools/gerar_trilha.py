"""Trilha instrumental original para o reel "Golpe do falso advogado".

Síntese pura (sem samples de terceiros, sem vocal), determinística.
- 0 a 58,7 s (cenas 1-5): Ré menor, pulsos graves de cordas e um "batimento"
  grave a 84 bpm, discreto -> tensão sem susto.
- 58,7 a 59,4 s: quase silêncio (o "vácuo" do R$ 0,00).
- 59,4 s em diante ("Então grava isso"): Ré maior, piano em arpejos + colchão
  de cordas -> calmo e confiante, resolve no fim.
Uso: python3 tools/gerar_trilha.py assets/music/trilha.wav
"""
import sys
import wave

import numpy as np

SR = 48000
TOTAL = 111.8
CALM_AT = 59.4
VACUO = 58.7
rng = np.random.default_rng(20261009)

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


# ---------------------------------------------------------------- tensão (Ré menor)
beat = 60 / 84
tense_chords = [
    [50, 57, 62, 65],  # Dm
    [46, 53, 58, 62],  # Bb
    [43, 50, 55, 58],  # Gm
    [45, 52, 57, 61],  # A (dominante, tensão)
]
t0, i = 0.0, 0
CH = 4 * beat * 2  # 5,71 s por acorde
while t0 < VACUO:
    notes = tense_chords[i % 4]
    d = min(CH, VACUO - t0)
    g = 0.75 + 0.25 * min(1, t0 / 40)  # cresce devagar até a cena 5
    add(strings(notes[1:], d + 0.1, att=0.5, relt=0.5, gain=0.8 * g, tremolo=(84 / 60 * 2, 0.5)), t0, pan=-0.15)
    add(strings([notes[0] - 12], d + 0.1, att=0.7, relt=0.5, gain=1.25 * g), t0, pan=0.1)
    add(piano(notes[0] - 24, 2.4, 0.5), t0, pan=-0.1)
    t0 += CH
    i += 1
# batimento grave (pulso), discreto
k = 0
tb = 0.0
while tb < VACUO - 0.3:
    tt = np.arange(int(0.35 * SR)) / SR
    f = 52 * np.exp(-tt * 6) + 38
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 11)
    add(thump * (0.20 if k % 2 == 0 else 0.12), tb, pan=0.0)
    tb += beat
    k += 1
# notas agudas esparsas (inquietação)
for tt_, m in [(3.0, 74), (9.0, 73), (15.2, 74), (21.0, 77), (27.4, 76), (33.0, 73), (39.1, 74), (45.0, 77), (51.3, 76), (55.0, 73)]:
    add(piano(m, 1.0, 0.26), tt_, pan=0.35)

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
end_music = TOTAL - 4.2
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
# trecho tenso 4 dB abaixo do calmo (o calmo é mais esparso e some mais sob a voz)
tenso = np.where(t < CALM_AT - 0.3, 10 ** (-4 / 20), np.where(t > CALM_AT + 0.3, 1.0, 10 ** (-4 / 20 * (CALM_AT + 0.3 - t) / 0.6)))
outL *= fade * fade_in * tenso
outR *= fade * fade_in * tenso
peak = max(np.abs(outL).max(), np.abs(outR).max())
outL, outR = outL / peak * 0.7, outR / peak * 0.7

pcm = (np.stack([outL, outR], axis=1) * 32767).astype("<i2")
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("ok", sys.argv[1], f"{n_out / SR:.2f}s")
