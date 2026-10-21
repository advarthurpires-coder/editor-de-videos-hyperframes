# Efeitos sonoros sintetizados (sem samples de terceiros), estéreo 48 kHz — os novos do reel "Plantão HERO".
# (papel, tique, impacto, brilho e carimbo vêm de hero-reel/tools/gerar_sfx.py)
# Uso: python3 -I tools/gerar_sfx.py -> assets/sfx/{liga_tv,vinheta,folhas,relogio,ding,clone,terremoto,gota,obturador}.wav
import os, wave
import numpy as np

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
SR = 48000
rng = np.random.default_rng(1930)


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


def t_(d):
    return np.arange(int(d * SR)) / SR


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def metal(f, d, brilho=1.0):
    """metal sintético (serra filtrada) com ataque curto"""
    t = t_(d); x = np.zeros(len(t))
    for det in (-0.06, 0.0, 0.06):
        for n in range(1, int(5000 / f)):
            x += np.sin(2 * np.pi * f * 2 ** (det / 12) * n * t) / n * np.exp(-n * 0.12 / brilho * (1 + 2 * t))
    return x * np.minimum(1, t / 0.012) * np.exp(-t * 1.6)


# liga_tv: estalo de tubo + chiado que some + zumbido de linha
t = t_(0.7)
chiado = bp(rng.standard_normal(len(t)), 2000, 12000) * np.exp(-t / 0.18) * 0.5
estalo = bp(rng.standard_normal(len(t)), 300, 5000) * np.exp(-t / 0.01)
zumbido = np.sin(2 * np.pi * 15734 / 100 * t) * 0.06 * np.exp(-t / 0.4)
salvar("liga_tv", estalo + chiado + zumbido)

# vinheta: assinatura de "plantão" — três metais (Ré, Lá, Ré') + tímpano
t = t_(1.9); x = np.zeros(len(t))
for k, (m, d) in enumerate(((62, 0.16), (69, 0.16), (74, 1.2))):
    s = int(k * 0.17 * SR); m_ = metal(hz(m), d + 0.4) + 0.6 * metal(hz(m - 12), d + 0.4)
    x[s:s + len(m_)] += m_[: len(x) - s]
tim = np.sin(2 * np.pi * np.cumsum(70 + 40 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.5)
s = int(0.34 * SR); x[s:] += tim[: len(x) - s] * 1.6
salvar("vinheta", x, 0.35)

# folhas: páginas arrancadas em sequência (5 rasgos curtos e secos)
t = t_(0.7); x = np.zeros(len(t))
for k in range(5):
    s = int(k * 0.065 * SR); L = int(0.09 * SR); tt = np.arange(L) / SR
    g = bp(rng.standard_normal(L), 1500, 9000) * np.minimum(1, tt / 0.01) * np.exp(-tt / 0.03)
    x[s:s + L] += g * (0.7 + 0.3 * k / 4)
salvar("folhas", x, 0.5)

# relogio: catraca rápida que desacelera (ponteiros girando) e trava
t = t_(0.9); x = np.zeros(len(t)); p = 0.0; dt = 0.022
while p < 0.75:
    s = int(p * SR); L = int(0.012 * SR); tt = np.arange(L) / SR
    x[s:s + L] += (bp(rng.standard_normal(L), 3000, 10000) * np.exp(-tt / 0.002) + np.sin(2 * np.pi * 2600 * tt) * np.exp(-tt / 0.004) * 0.4)
    p += dt; dt *= 1.09
s = int(0.8 * SR); tt = t[: len(x) - s]
x[s:] += np.sin(2 * np.pi * 900 * tt) * np.exp(-tt / 0.03) * 1.2
salvar("relogio", x, 0.3, 0.8)

# ding: sineta (campainha de recepção)
t = t_(1.6)
x = sum(a * np.sin(2 * np.pi * 1318.5 * r * t) * np.exp(-t / dcy) for r, a, dcy in ((1, 1, 0.6), (2.76, 0.4, 0.25), (5.4, 0.2, 0.1)))
salvar("ding", x * np.minimum(1, t / 0.002), 0.4, 0.75)

# clone: deslize com efeito de fase (cópia "duplicando")
t = t_(0.55); u = t / t[-1]
nz = rng.standard_normal(len(t))
x = bp(nz, 500, 6000) * np.sin(np.pi * u) ** 1.5
pha = np.sin(2 * np.pi * np.cumsum(300 + 2200 * u) / SR) * np.sin(np.pi * u) * 0.25
salvar("clone", x + pha, 0.6)

# terremoto: estrondo grave, tremor de 7 Hz e chacoalhar de vidro
t = t_(1.6)
rum = bp(rng.standard_normal(len(t)), 25, 160) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)) * np.minimum(1, t / 0.05) * np.exp(-t / 0.7)
bum = np.sin(2 * np.pi * np.cumsum(32 + 60 * np.exp(-t / 0.06)) / SR) * np.exp(-t / 0.6)
vid = bp(rng.standard_normal(len(t)), 4000, 11000) * (np.sin(2 * np.pi * 7 * t) > 0.6) * np.exp(-t / 0.4) * 0.12
salvar("terremoto", rum * 1.4 + bum + vid, 0.3)

# gota: pingo grave em líquido (tom que sobe rápido) + leve eco
t = t_(0.7)
x = np.sin(2 * np.pi * np.cumsum(500 + 1300 * np.clip(t / 0.03, 0, 1)) / SR) * np.exp(-t / 0.05)
x += np.concatenate([np.zeros(int(0.16 * SR)), x[: -int(0.16 * SR)]]) * 0.3
salvar("gota", x, 0.5, 0.7)

# obturador: clique duplo de câmera (cortina abrindo/fechando)
t = t_(0.22); x = np.zeros(len(t))
for d, g in ((0.0, 1.0), (0.07, 0.8)):
    s = int(d * SR); tt = t[: len(t) - s]
    x[s:] += g * (bp(rng.standard_normal(len(tt)), 1500, 8000) * np.exp(-tt / 0.006) + np.sin(2 * np.pi * 180 * tt) * np.exp(-tt / 0.015) * 0.5)
salvar("obturador", x, 0.2, 0.8)
print("sfx ok")
