"""Efeitos sonoros originais por síntese (determinísticos), 48 kHz mono.

alarme, glitch, digitacao, notificacao, tictac, tictac_acelera, toque, papel, ding, vacuo,
desligar, contador
Uso: python3 tools/gerar_sfx.py assets/sfx
"""
import os
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(77)
out = sys.argv[1]


def t(d):
    return np.arange(int(d * SR)) / SR


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def env(x, att=0.005, rel=0.05):
    n = len(x)
    e = np.ones(n)
    a, r = int(att * SR), int(rel * SR)
    e[:a] = np.linspace(0, 1, a)
    e[n - r:] *= np.linspace(1, 0, r)
    return x * e


def save(name, x, peak=0.8):
    x = x / (np.abs(x).max() + 1e-9) * peak
    with wave.open(os.path.join(out, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


# alarme grave curto: duas varreduras de sirene, abafadas
tt = t(1.3)
f = 330 + 140 * (0.5 - 0.5 * np.cos(2 * np.pi * tt / 0.65))
s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + np.sin(2 * np.pi * np.cumsum(f) / SR)
save("alarme", env(lp(s, 1400), 0.02, 0.25))

# glitch digital: rajadas de ruído/onda quadrada picotadas
tt = t(0.42)
g = np.zeros_like(tt)
for k in range(9):
    a0 = int(rng.uniform(0, 0.38) * SR)
    ln = int(rng.uniform(0.012, 0.05) * SR)
    fr = rng.uniform(300, 2400)
    seg = np.sign(np.sin(2 * np.pi * fr * np.arange(ln) / SR)) * 0.6 + rng.standard_normal(ln) * 0.5
    g[a0:a0 + ln] += seg[: len(g[a0:a0 + ln])]
save("glitch", env(g, 0.001, 0.03), 0.7)

# digitação: cliques curtos irregulares
tt = t(1.4)
d = np.zeros_like(tt)
tk = 0.03
while tk < 1.3:
    i = int(tk * SR)
    ln = int(0.012 * SR)
    clk = rng.standard_normal(ln) * np.exp(-np.arange(ln) / (0.0025 * SR))
    d[i:i + ln] += clk * rng.uniform(0.5, 1.0)
    tk += rng.uniform(0.06, 0.14)
save("digitacao", lp(d, 5000), 0.7)

# notificação: dois tons curtos (genérica)
tt = t(0.32)
n1 = np.sin(2 * np.pi * 988 * tt) * np.exp(-tt * 18)
n2 = np.zeros_like(tt)
o = int(0.11 * SR)
n2[o:] = np.sin(2 * np.pi * 1319 * tt[: len(tt) - o]) * np.exp(-tt[: len(tt) - o] * 14)
save("notificacao", env(n1 + n2, 0.002, 0.05), 0.6)

# tique-taque: um "tic" seco
tt = t(0.08)
save("tictac", env(rng.standard_normal(len(tt)) * np.exp(-tt * 120) + np.sin(2 * np.pi * 2200 * tt) * np.exp(-tt * 90), 0.0005, 0.01), 0.6)

# toque de chamada: trinado genérico 2 x 0,4 s
tt = t(1.5)
r = np.zeros_like(tt)
for st in (0.0, 0.5):
    i0 = int(st * SR)
    ln = int(0.4 * SR)
    x = np.arange(ln) / SR
    tone = (np.sin(2 * np.pi * 740 * x) + np.sin(2 * np.pi * 880 * x)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 20 * x)))
    r[i0:i0 + ln] += env(tone, 0.005, 0.03)
save("toque", lp(r, 3000), 0.55)

# papel deslizando: ruído filtrado com envelope
tt = t(0.7)
p = lp(rng.standard_normal(len(tt)), 2500) - lp(rng.standard_normal(len(tt)), 300) * 0.3
save("papel", env(p * np.sin(np.pi * tt / 0.7) ** 1.5, 0.01, 0.1), 0.5)

# ding grave (revelação)
tt = t(1.6)
dg = sum(np.sin(2 * np.pi * 220 * h * tt) / h ** 1.4 * np.exp(-tt * (2 + h)) for h in (1, 2, 3, 4.2))
save("ding", env(dg, 0.003, 0.2), 0.7)

# vácuo: varredura descendente de ruído
tt = t(0.9)
v = np.zeros_like(tt)
x = rng.standard_normal(len(tt))
for k, fc in enumerate((3200, 1600, 700)):
    v += lp(x, fc) * np.clip(1 - tt / 0.9 * (1 + k * 0.3), 0, 1)
save("vacuo", env(v * (tt / 0.9) ** 0.2, 0.05, 0.3), 0.55)

# desligar: clique + tom descendente curto
tt = t(0.35)
dl = np.sin(2 * np.pi * np.cumsum(620 - 300 * tt / 0.35) / SR) * np.exp(-tt * 9)
dl[: int(0.01 * SR)] += rng.standard_normal(int(0.01 * SR)) * 0.8
save("desligar", env(dl, 0.001, 0.05), 0.6)
# tique-taque acelerando (6,8 s): intervalo de 0,5 s até 0,13 s
tt = t(6.8)
ta = np.zeros_like(tt)
tick = rng.standard_normal(int(0.03 * SR)) * np.exp(-np.arange(int(0.03 * SR)) / (0.003 * SR))
pos, k = 0.0, 0
while pos < 6.7:
    i = int(pos * SR)
    ta[i:i + len(tick)] += tick[: len(ta[i:i + len(tick)])] * (0.6 if k % 2 else 1.0)
    pos += 0.5 - 0.37 * (pos / 6.8) ** 0.8
    k += 1
save("tictac_acelera", lp(ta, 4500) * np.clip(0.4 + tt / 6.8, 0, 1), 0.6)

# contador descendo (0,7 s): cliques rápidos subindo de tom
tt = t(0.7)
ct = np.zeros_like(tt)
for j in range(16):
    i = int(j * 0.04 * SR)
    x = np.arange(int(0.02 * SR)) / SR
    ct[i:i + len(x)] += np.sin(2 * np.pi * (1500 - 40 * j) * x) * np.exp(-x * 220)
save("contador", ct, 0.5)
print("ok")
