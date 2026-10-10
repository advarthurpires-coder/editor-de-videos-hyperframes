# Trilha original 120 BPM (pop/house), sintetizada em numpy. Duração exata = argv[2] s.
import numpy as np, wave, sys
SR = 44100; BPM = 120; BEAT = 60 / BPM
out = sys.argv[1]; DUR = float(sys.argv[2])
N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    s = sig[: N - i] * gain
    L[i:i+len(s)] += s * (1 - max(pan, 0)); R[i:i+len(s)] += s * (1 + min(pan, 0))
def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)
def lp(x, k):  # moving-average lowpass
    k = max(int(k), 1); return np.convolve(x, np.ones(k) / k, mode='same')
def note(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, n, det=0.0):
    t = np.arange(n) / SR; ph = (f * (1 + det)) * t
    return 2 * (ph - np.floor(ph + 0.5))
# --- sons ---
n = int(0.35 * SR); t = np.arange(n) / SR
kick = np.sin(2 * np.pi * (45 * t + (110 / 18) * (1 - np.exp(-18 * t)))) * np.exp(-t / 0.13)
kick += 0.3 * np.sin(2 * np.pi * 60 * t) * np.exp(-t / 0.25)
nz = rng.standard_normal(int(0.25 * SR))
clap = lp(nz - lp(nz, 30), 3) * env(len(nz), 0.001, 0.07)
hn = rng.standard_normal(int(0.06 * SR)); hat = (hn - lp(hn, 6)) * env(len(hn), 0.0005, 0.015)
on = rng.standard_normal(int(0.25 * SR)); ohat = (on - lp(on, 6)) * env(len(on), 0.001, 0.09)
# progressão I–V–vi–IV em Lá maior (A E F#m D), 1 compasso cada
prog = [[57, 61, 64, 69], [52, 56, 59, 64], [54, 57, 61, 66], [50, 54, 57, 62]]
roots = [45, 40, 42, 38]
bars = int((DUR - 1.0) // (4 * BEAT)) + 1  # último compasso = acorde final soando até o fim
end_hit = (bars - 1) * 4 * BEAT  # downbeat do último compasso: acorde final
for b in range(bars):
    t0 = b * 4 * BEAT; ch = prog[b % 4]; rt = roots[b % 4]
    final = t0 >= end_hit - 1e-6
    build = (bars - 4) <= b < bars - 1  # ultimos compassos antes do fim: mais brilho
    if final:
        # acorde final sustentado + kick, decaindo até o fim exato
        n = N - int(t0 * SR); pad = sum(saw(note(m), n, d) for m in ch for d in (-0.004, 0.004))
        pad = lp(pad, 6) * np.exp(-np.arange(n) / SR / 0.7) * 0.05
        add(pad, t0, 1.0, 0.0); add(kick, t0, 0.9)
        add(saw(note(rt), n) * np.exp(-np.arange(n) / SR / 0.5), t0, 0.12)
        break
    for k in range(4):
        tb = t0 + k * BEAT
        add(kick, tb, 0.9)
        if k in (1, 3): add(clap, tb, 0.35, 0.05)
        add(hat, tb + BEAT / 2, 0.22, -0.3)
        if b >= 2: add(hat, tb + BEAT / 4, 0.08, 0.3); add(hat, tb + 3 * BEAT / 4, 0.08, 0.3)
        if k == 3: add(ohat, tb + BEAT / 2, 0.12, -0.2)
        # baixo no contratempo (bombeado)
        n = int(BEAT / 2 * SR); bs = lp(saw(note(rt), n) + 0.5 * saw(note(rt + 12), n), 18)
        add(bs * env(n, 0.005, 0.18), tb + BEAT / 2, 0.30)
    # pad com sidechain
    n = int(4 * BEAT * SR); tt = np.arange(n) / SR
    pad = sum(saw(note(m + 12), n, d) for m in ch for d in (-0.006, 0.0, 0.006))
    pad = lp(pad, 10 if not build else 5)
    duck = 1 - 0.75 * np.exp(-((tt % BEAT) / 0.09))
    add(pad * duck * 0.018, t0, 1.0, 0.0)
    # arpejo pluck em semicolcheias (entra no compasso 2)
    if b >= 1:
        seq = ch + ch[::-1]
        for s in range(16):
            m = seq[s % 8] + 12; n = int(0.22 * SR)
            pl = lp(saw(note(m), n) + 0.5 * np.sin(2 * np.pi * note(m) * np.arange(n) / SR), 4)
            add(pl * env(n, 0.002, 0.07), t0 + s * BEAT / 4, 0.07, 0.35 if s % 2 else -0.35)
    # riser antes do último compasso
    if b == bars - 2:
        n = int(4 * BEAT * SR); rz = rng.standard_normal(n); rz = rz - lp(rz, 8)
        add(rz * np.linspace(0, 1, n) ** 2 * 0.05, t0)
mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
fade = int(0.04 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix /= np.abs(mix).max() / 0.89
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', out, DUR, 's, bars', bars, 'final hit at', end_hit)
