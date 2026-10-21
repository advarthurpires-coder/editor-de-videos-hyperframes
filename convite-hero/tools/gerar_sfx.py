# Efeitos sonoros sintetizados (sem samples de terceiros): papel rasgando e carimbo/batida seca.
# Uso: python3 -I tools/gerar_sfx.py   -> assets/sfx/rasgo.wav, assets/sfx/carimbo.wav
import os, wave
import numpy as np

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
SR = 48000
rng = np.random.default_rng(77)


def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= np.clip((f - lo * 0.7) / (lo * 0.3), 0, 1) * np.clip((hi * 1.3 - f) / (hi * 0.3), 0, 1)
    return np.fft.irfft(X, len(x))


def salvar(nome, x, stereo_w=0.25):
    x = x / np.abs(x).max() * 0.9
    d = int(0.004 * SR)
    l = x; r = np.concatenate([np.zeros(d), x[:-d]]) * (1 - stereo_w) + x * stereo_w
    pcm = (np.stack([l, r], 1) * 32767).astype("<i2")
    with wave.open(f"{D}/assets/sfx/{nome}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


# papel rasgando: grãos de estalo (fibras) com envelope que cresce e some, brilho subindo
n = int(0.55 * SR); t = np.arange(n) / SR
graos = np.zeros(n)
pos = np.cumsum(rng.exponential(0.0045, 400)); pos = pos[pos < 0.5]
for p in pos:
    i = int(p * SR); L = int(rng.uniform(0.002, 0.009) * SR)
    if i + L < n: graos[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 3)) * rng.uniform(0.3, 1.0)
corpo = rng.standard_normal(n) * 0.35
env = np.clip(t / 0.06, 0, 1) * np.exp(-np.clip(t - 0.30, 0, None) / 0.07)
rasgo = (bp(graos, 1500, 7500) + bp(corpo, 800, 5000)) * env
salvar("rasgo", rasgo)

# carimbo: baque grave + estalo de madeira + ar
n = int(0.5 * SR); t = np.arange(n) / SR
baque = np.sin(2 * np.pi * np.cumsum(60 + 90 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.11)
estalo = bp(rng.standard_normal(n), 900, 4000) * np.exp(-t / 0.012) * 0.8
madeira = np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.03) * 0.35
salvar("carimbo", baque + estalo + madeira, 0.1)
print("sfx ok")
