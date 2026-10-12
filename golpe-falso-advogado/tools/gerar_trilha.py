"""Trilha original do reel (síntese determinística, sem samples de terceiros).
Tensão contida: drone grave em Ré menor, pulso de sub a 100 BPM, tique de relógio,
riser antes de "É golpe!" (drop em DROP1) e resolução maior na cartela final (DROP2).
Uso: python3 -I tools/gerar_trilha.py <saida.wav> <drop1> <drop2> <total>"""
import sys, wave
import numpy as np

SR = 48000
out, DROP1, DROP2, TOTAL = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
N = int(TOTAL * SR); t = np.arange(N) / SR
rng = np.random.default_rng(11)
BPM = 100.0; BEAT = 60 / BPM
L = np.zeros(N); R = np.zeros(N)


def env_ar(n, a, r):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / (r * SR)); return e


def lowpass(x, fc):
    # passa-baixa de 1 polo aplicado por convolução com a resposta ao impulso exponencial
    a = np.exp(-2 * np.pi * fc / SR)
    h = (1 - a) * a ** np.arange(int(np.log(1e-4) / np.log(a)) + 1)
    n = len(x) + len(h) - 1; size = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(h, size), size)[:len(x)]


def add(sig, t0, gl=1.0, gr=1.0):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if j <= i: return
    L[i:j] += sig[:j - i] * gl; R[i:j] += sig[:j - i] * gr


# --- drone (Ré menor -> Ré maior na cartela) ---------------------------------------
def nota(f, n_seg, det=0.0):
    tt = np.arange(int(n_seg * SR)) / SR
    return (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * 2 * f * (1 + det) * tt + 1)
            + 0.25 * np.sin(2 * np.pi * 3 * f * tt + 2))


fade_in = np.clip(t / 1.2, 0, 1)
dr = np.zeros(N)
for f, g in [(36.71, 0.5), (73.42, 0.35), (110.0, 0.12), (87.31, 0.10)]:  # D1 D2 A2 F2
    dr += g * nota(f, TOTAL, 0.002)
lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t)
mask_min = (t < DROP2).astype(float)
maj = np.zeros(N)
for f, g in [(73.42, 0.3), (92.5, 0.12), (110.0, 0.14), (146.83, 0.08)]:  # D F# A D
    maj += g * nota(f, TOTAL)
xf = np.clip((t - DROP2 + 0.05) / 0.4, 0, 1)
drone = (dr * (1 - xf) + maj * xf) * lfo * fade_in * 0.16
# respiração: abre levemente após o primeiro drop
drone *= np.where(t < DROP1, 0.85, 1.0)
L += drone; R += np.roll(drone, 240)

# --- pulso de sub (batida cardíaca contida) ----------------------------------------
k = 0
while k * BEAT < TOTAL - 0.2:
    tb = k * BEAT
    if tb > 0.5 and not (DROP1 - 1.6 < tb < DROP1):
        n = int(0.35 * SR); tt = np.arange(n) / SR
        f = 55 * np.exp(-tt * 9) + 38
        kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ar(n, 0.003, 0.11)
        g = 0.55 if tb > DROP1 else 0.4
        if tb > DROP2: g = 0.3
        add(kick * g, tb)
        # contratempo leve (duplo) depois do drop
        if tb > DROP1 and tb < DROP2:
            add(kick * g * 0.45, tb + BEAT * 0.5)
    k += 1

# --- tique de relógio (urgência) -------------------------------------------------------
k = 0
while k * BEAT / 2 < DROP2:
    tb = k * BEAT / 2
    if tb > 3.0:
        n = int(0.03 * SR)
        tick = rng.standard_normal(n) * env_ar(n, 0.0005, 0.006)
        tick = tick - lowpass(tick, 3500)
        pan = 0.3 if k % 2 else -0.3
        add(tick * 0.09, tb, 1 - pan, 1 + pan)
    k += 1

# --- riser antes do drop 1 e do drop 2 ---------------------------------------------
for D, dur, g in [(DROP1, 1.6, 0.22), (DROP2, 1.2, 0.16)]:
    n = int(dur * SR); tt = np.arange(n) / SR
    nz = rng.standard_normal(n)
    x = (tt / dur) ** 2
    hp = nz - (lowpass(nz, 600) * (1 - x) + lowpass(nz, 3000) * x)  # filtro varrendo para o agudo
    rise = hp * (tt / dur) ** 2.2 * g
    sw = np.sin(2 * np.pi * np.cumsum(200 + 900 * (tt / dur) ** 2) / SR) * (tt / dur) ** 3 * g * 0.35
    add(rise + sw, D - dur, 0.9, 1.0)
    # golpe grave no drop
    n2 = int(1.8 * SR); t2 = np.arange(n2) / SR
    boom = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-t2 * 3) + 30) / SR) * env_ar(n2, 0.002, 0.5)
    add(boom * 0.8, D)

# --- pad agudo na cartela ----------------------------------------------------------
n = N - int(DROP2 * SR); tt = np.arange(n) / SR
pad = sum(np.sin(2 * np.pi * f * tt + p) for f, p in [(293.66, 0), (369.99, 1), (440.0, 2), (587.33, 3)])
pad *= np.clip(tt / 0.8, 0, 1) * 0.035
add(pad, DROP2, 1.0, 0.0); add(np.roll(pad, 600), DROP2, 0.0, 1.0)

fade = np.clip((TOTAL - t) / 1.0, 0, 1)
mix = np.stack([L, R], 1) * fade[:, None]
mix = mix / np.abs(mix).max() * 0.85
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("trilha", out, TOTAL, "s")
