# Efeitos sonoros sintetizados (sem samples de terceiros), estéreo 48 kHz.
# Uso: python3 -I tools/gerar_sfx.py   -> assets/sfx/{papel,brilho,carimbo,tique,subida,onda,pulso,impacto}.wav
import os, wave
import numpy as np

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
SR = 48000
rng = np.random.default_rng(2410)


def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= np.clip((f - lo * 0.7) / (lo * 0.3), 0, 1) * np.clip((hi * 1.3 - f) / (hi * 0.3), 0, 1)
    return np.fft.irfft(X, len(x))


def salvar(nome, x, largura=0.25, pico=0.9):
    if x.ndim == 1:
        d = int(0.004 * SR)
        r = np.concatenate([np.zeros(d), x[:-d]]) * (1 - largura) + x * largura
        x = np.stack([x, r], 1)
    x = x / np.abs(x).max() * pico
    with wave.open(f"{D}/assets/sfx/{nome}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype("<i2").tobytes())


def t_(dur):
    return np.arange(int(dur * SR)) / SR


# papel: ingresso de papel-cartão sendo sacado — "flick" seco + farfalhar curto
t = t_(0.42)
flick = bp(rng.standard_normal(len(t)), 1800, 9000) * np.exp(-t / 0.012)
farf = np.zeros(len(t))
for p in np.cumsum(rng.exponential(0.006, 60)):
    i = int((0.02 + p) * SR); L = int(rng.uniform(0.002, 0.007) * SR)
    if i + L < len(t): farf[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 3)) * np.exp(-p / 0.08)
salvar("papel", flick * 1.2 + bp(farf, 1200, 7000) * 0.7)

# brilho: cintilar dourado (sinos agudos em arpejo, Ré maior) com cauda
t = t_(1.6); x = np.zeros(len(t))
for k, f in enumerate([1174.7, 1480.0, 1760.0, 2349.3, 2960.0]):
    s = int(k * 0.045 * SR); tt = t[: len(t) - s]
    tone = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt / 0.35)
    x[s:] += tone * (0.9 - 0.1 * k)
x += bp(rng.standard_normal(len(t)), 6000, 14000) * np.exp(-t / 0.25) * 0.15
salvar("brilho", x, 0.6, 0.8)

# carimbo: baque grave + estalo de borracha/madeira + ar
t = t_(0.55)
baque = np.sin(2 * np.pi * np.cumsum(55 + 95 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.12)
estalo = bp(rng.standard_normal(len(t)), 700, 3500) * np.exp(-t / 0.014) * 0.9
madeira = np.sin(2 * np.pi * 380 * t) * np.exp(-t / 0.035) * 0.35
salvar("carimbo", baque + estalo + madeira, 0.1)

# tique: contador mecânico (palheta) — dois cliques metálicos próximos
t = t_(0.18); x = np.zeros(len(t))
for d, g in ((0.0, 1.0), (0.028, 0.55)):
    s = int(d * SR); tt = t[: len(t) - s]
    x[s:] += g * (bp(rng.standard_normal(len(tt)), 2500, 9000) * np.exp(-tt / 0.004) + np.sin(2 * np.pi * 3100 * tt) * np.exp(-tt / 0.01) * 0.5)
salvar("tique", x, 0.3, 0.85)

# subida: riser de ar e tom ascendente (1,4 s), termina no golpe
t = t_(1.4); u = t / t[-1]
nz = rng.standard_normal(len(t))
ar = bp(nz, 400, 2000) * (1 - u) + bp(nz, 2500, 10000) * u
tom = np.sin(2 * np.pi * np.cumsum(150 + 700 * u ** 2.2) / SR) * 0.3
salvar("subida", (ar + tom) * u ** 2.4, 0.5, 0.8)

# onda: massa de água (mar da Galileia) — ruído grave que cresce e quebra com espuma
t = t_(2.2)
env = np.clip(t / 0.7, 0, 1) ** 2 * np.exp(-np.clip(t - 0.75, 0, None) / 0.5)
corpo = bp(rng.standard_normal(len(t)), 120, 900) * env
espuma = bp(rng.standard_normal(len(t)), 2500, 9000) * np.clip((t - 0.6) / 0.2, 0, 1) * np.exp(-np.clip(t - 0.8, 0, None) / 0.35) * 0.5
L = corpo + espuma; R = np.concatenate([np.zeros(int(0.011 * SR)), corpo + espuma])[: len(t)] * 0.9
salvar("onda", np.stack([L, R], 1))

# pulso: onda de choque suave (anéis "grandemente") — sub com batimento + brilho curto
t = t_(1.3)
sub = np.sin(2 * np.pi * np.cumsum(48 + 40 * np.exp(-t / 0.06)) / SR) * np.exp(-t / 0.45)
anel = np.sin(2 * np.pi * 880 * t) * np.sin(2 * np.pi * 3.0 * t) ** 2 * np.exp(-t / 0.4) * 0.12
salvar("pulso", sub + anel, 0.3)

# impacto: golpe cinematográfico curto (bumbo grave + corpo + cauda de ar)
t = t_(1.6)
bumbo = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.55)
corpo = bp(rng.standard_normal(len(t)), 80, 600) * np.exp(-t / 0.09) * 0.7
ar = bp(rng.standard_normal(len(t)), 3000, 9000) * np.exp(-t / 0.3) * 0.12
salvar("impacto", bumbo + corpo + ar, 0.2)
print("sfx ok")
