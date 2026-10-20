"""Mixagem do reel "Culto Hero": locução + trilha (com ducking) + efeitos sonoros sincronizados às palavras.

Efeitos: sintetizados aqui (determinísticos) + whoosh/impactos de assets/sfx (os mesmos do reel Hero Extreme).
Os tempos vêm de assets/tempos_data.js (gerado por tools/legendas.py), então mudar INICIO em roteiro.py
reposiciona tudo.
Saída: assets/media/mix_pre.wav (sem normalizar; depois tools/masterizar.sh -> mix_master.wav)
Uso: python3 -I tools/mixar_audio.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_util import bp, hp, load, lp, put, wav  # noqa: E402
from roteiro import CENAS, SR, TOTAL  # noqa: E402

N = int(TOTAL * SR)
rng = np.random.default_rng(1024)
TEMPOS = json.loads(open("assets/tempos_data.js").read().split("=", 1)[1].rstrip().rstrip(";"))


def W(frase, palavra, n=0):
    """Início absoluto da n-ésima ocorrência de `palavra` (prefixo) na frase `frase` (1-based)."""
    hits = [p for p in TEMPOS[frase - 1]["palavras"] if p["w"].lower().startswith(palavra.lower())]
    return hits[n]["s"]


def T(d):
    return np.arange(int(d * SR)) / SR


# ------------------------------------------------------------------ efeitos sintetizados
def clunk(g=1.0):
    """Peça metálica travando: parciais inarmônicos + baque."""
    t = T(0.9)
    out = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in
              [(420, 0.5, 0.18), (1130, 0.35, 0.12), (1870, 0.25, 0.08), (2950, 0.15, 0.05)])
    thud = lp(rng.standard_normal(len(t)), 300) * np.exp(-t / 0.04) * 1.2
    return (out + thud) * 0.45 * g


def pop(f0=520, g=1.0):
    t = T(0.25)
    f = f0 * (1 + 1.2 * np.exp(-t / 0.012))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.05)
            + hp(rng.standard_normal(len(t)), 2000) * np.exp(-t / 0.003) * 0.4) * 0.35 * g


def clack(g=1.0, f=900):
    t = T(0.2)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.02) + 0.6 * np.sin(2 * np.pi * f * 2.3 * t) * np.exp(-t / 0.01)
            + lp(rng.standard_normal(len(t)), 1200) * np.exp(-t / 0.01)) * 0.25 * g


def glitch(d=1.1, g=1.0):
    """Interferência digital: rajadas de zumbido quadrado + ruído reduzido a 8 kHz / 4 bits."""
    t = T(d)
    out = np.zeros_like(t)
    pos = 0.0
    while pos < d - 0.03:
        ln = 0.03 + rng.random() * 0.11
        i, j = int(pos * SR), int(min(d, pos + ln) * SR)
        f = rng.choice([110, 220, 330, 880, 1760, 60])
        seg = np.sign(np.sin(2 * np.pi * f * t[i:j])) * 0.5 + rng.standard_normal(j - i) * rng.random() * 0.6
        if rng.random() < 0.3:
            seg *= 0
        out[i:j] = seg
        pos += ln + rng.random() * 0.04
    hold = np.repeat(out[::6], 6)[: len(out)]
    return np.round(hold * 8) / 8 * 0.22 * g


def interruptor(g=1.0):
    t = T(0.08)
    return (hp(rng.standard_normal(len(t)), 2500) * np.exp(-t / 0.004) + np.sin(2 * np.pi * 3100 * t) * np.exp(-t / 0.006) * 0.5) * 0.45 * g


def scratch(g=1.0):
    """Arranhão de disco: ruído filtrado com tom que sobe e desce (mão no vinil)."""
    d = 0.55
    t = T(d)
    vel = np.concatenate([np.linspace(0, 1, len(t) // 3), np.linspace(1, -0.8, len(t) // 3), np.linspace(-0.8, 0.2, len(t) - 2 * (len(t) // 3))])
    f = 300 + 1600 * np.abs(vel)
    tone = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.35
    nz = bp(rng.standard_normal(len(t)), 600, 4000) * (0.4 + 0.6 * np.abs(vel))
    return lp(tone + nz, 5000) * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.05) * 0.3 * g


def sirene(d, g=1.0):
    t = T(d)
    f = 520 + 180 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.55 * t - np.pi / 2))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    s = s + 0.3 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.8)
    return lp(s, 1800) * env * 0.12 * g


def vibra(d=0.42, g=1.0):
    """Celular vibrando na mesa: 165 Hz com chocalho."""
    t = T(d)
    m = np.sin(2 * np.pi * 165 * t) + 0.5 * np.sign(np.sin(2 * np.pi * 165 * t))
    rattle = hp(rng.standard_normal(len(t)), 1500) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 82 * t))) * 0.25
    env = np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.03)
    return lp(m + rattle, 2500) * env * 0.22 * g


def cadeado(g=1.0):
    """Trava do cadeado: clique duplo metálico + ressonância curta."""
    out = np.zeros(int(0.7 * SR))
    for dt, a in [(0.0, 1.0), (0.045, 0.7)]:
        c = clunk(a * 0.8)[: len(out) - int(dt * SR)]
        out[int(dt * SR):] += c
    t = T(0.7)
    out += hp(rng.standard_normal(len(t)), 4000) * np.exp(-t / 0.006) * 0.6
    return out * g


def zumbido(d, g=1.0):
    """Placa luminosa: zumbido de reator 120 Hz + estalos."""
    t = T(d)
    hum = (np.sin(2 * np.pi * 120 * t) + 0.4 * np.sin(2 * np.pi * 240 * t) + 0.2 * np.sign(np.sin(2 * np.pi * 120 * t))) * 0.12
    est = np.zeros_like(t)
    for c in rng.uniform(0, d, 9):
        i = int(c * SR)
        ln = min(len(t) - i, int(0.03 * SR))
        est[i:i + ln] += hp(rng.standard_normal(ln), 2000) * np.exp(-np.arange(ln) / SR / 0.008) * 0.5
    return (hum + est) * np.minimum(1, t / 0.1) * g


def bzzt_off(g=1.0):
    t = T(0.6)
    f = 120 * np.exp(-t / 0.25)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t / 0.18) * 0.3
    return (s + clunk(0.5)[: len(t)]) * g


def whoomp(g=1.0):
    """Tudo perde a cor: queda de tom grave."""
    t = T(1.4)
    f = 180 * np.exp(-t / 0.35) + 30
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.6)
    return (s + lp(rng.standard_normal(len(t)), 500) * np.exp(-t / 0.3) * 0.3) * 0.5 * g


def clang(g=1.0):
    """Placa de aço caindo e travando."""
    t = T(1.6)
    out = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in
              [(180, 0.6, 0.5), (473, 0.45, 0.35), (811, 0.35, 0.3), (1290, 0.25, 0.2), (2120, 0.15, 0.12)])
    return (out + lp(rng.standard_normal(len(t)), 400) * np.exp(-t / 0.05)) * 0.4 * g


def shing(g=1.0):
    """Moeda girando: anel metálico com batimento."""
    t = T(1.8)
    out = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.7) for f in (3150, 3172, 4720)) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t))
    return out * np.minimum(1, t / 0.01) * 0.06 * g


def papel(g=1.0):
    t = T(0.16)
    return bp(rng.standard_normal(len(t)), 1200, 7000) * np.sin(np.pi * t / 0.16) ** 2 * 0.35 * g


def ding(f=1760, g=1.0):
    t = T(1.4)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.2)) * np.exp(-t / 0.5) * 0.12 * g


def thud(g=1.0, f0=90):
    t = T(0.5)
    f = f0 * (1 + 0.8 * np.exp(-t / 0.02))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09) + lp(rng.standard_normal(len(t)), 700) * np.exp(-t / 0.02) * 0.6) * 0.55 * g


def carimbo(g=1.0):
    """Carimbo de borracha batendo no papel: baque surdo + estalo de papel."""
    t = T(0.8)
    body = thud(1.4, 70)
    body = np.pad(body, (0, len(t) - len(body)))
    crack = bp(rng.standard_normal(len(t)), 800, 6000) * np.exp(-t / 0.025) * 0.5
    return (body + crack) * g


# ------------------------------------------------------------------ montagem
sfx = np.zeros((N, 2))
WH = load("assets/sfx/whoosh.mp3")
# os impactos originais sustentam ~2,5 s de grave cheio: encurtados para não cobrir a voz
_dec = lambda x, d: x * np.exp(-np.arange(len(x)) / SR / d)[:, None]
IMP1 = _dec(load("assets/sfx/impact-bass-1.mp3"), 0.45) * 0.55
IMP2 = _dec(load("assets/sfx/impact-bass-2.mp3"), 0.45) * 0.55
SPK = load("assets/sfx/sparkle.mp3")

# gancho: fitas cruzando + placa travando
put(sfx, WH, 0.0, 0.5)
put(sfx, WH, 0.14, 0.4)
put(sfx, clunk(1.0), 1.18, 0.9, pan=0.1)
# motivo 1
put(sfx, WH, CENAS["motivo1"] - 0.25, 0.35)
put(sfx, IMP2, CENAS["motivo1"], 0.45)
for k, w in enumerate(["Peão", "empresário", "motorista", "estudante", "aposentado"]):
    put(sfx, WH, W(3, w) - 0.22, 0.12, pan=0.0)
    put(sfx, pop(480 + 70 * k, 1.0), W(3, w) + 0.02, 0.8, pan=-0.3 + 0.15 * k)
for k in range(7):
    put(sfx, clack(0.9, 760 + 40 * (k % 3)), 10.95 + 0.085 * k, 0.8, pan=-0.6 + 0.2 * k)
put(sfx, ding(1318, 1.0), W(4, "diferente") + 0.05, 0.6)
put(sfx, glitch(1.2, 1.0), CENAS["incomoda"] + 0.15, 0.6)
# motivo 2
put(sfx, IMP1, CENAS["motivo2"], 0.5)
put(sfx, WH, 17.95, 0.25)
for k, tt in enumerate([19.13, 19.68, 20.04, 20.52, 21.15]):
    put(sfx, interruptor(1.0), tt + 0.05, 0.75, pan=-0.4 + 0.2 * k)
put(sfx, pop(380, 1.2), W(7, "esposa"), 0.9)
put(sfx, scratch(1.0), W(7, "estranhar") + 0.08, 0.95)
# motivo 3
put(sfx, IMP2, CENAS["motivo3"], 0.55)
put(sfx, sirene(3.0, 1.0), CENAS["motivo3"] + 0.1, 0.5)
put(sfx, WH, W(9, "você") - 0.2, 0.25)
for a in np.arange(27.75, 29.6, 0.7):
    put(sfx, vibra(0.42, 1.0), a, 0.4, pan=0.1)
put(sfx, SPK, W(10, "Amigo"), 0.25)
for a in np.arange(31.75, 34.6, 0.7):
    put(sfx, vibra(0.42, 1.1), a, 0.42, pan=0.1)
put(sfx, WH, W(12, "Aí") - 0.15, 0.3)
put(sfx, cadeado(1.0), W(12, "era") + 0.05, 1.0)
put(sfx, zumbido(1.25, 1.0), W(13, "Não"), 0.35)
put(sfx, bzzt_off(1.0), W(13, "sumir") + 0.05, 0.9)
# virada
put(sfx, whoomp(1.0), CENAS["virada"], 0.8)
put(sfx, WH, W(15, "vai") - 0.3, 0.35)
put(sfx, clang(1.0), W(15, "vai") + 0.02, 0.9)
put(sfx, IMP1, W(15, "vai"), 0.45)
# o risco
put(sfx, WH, CENAS["risco"] + 0.05, 0.4)
put(sfx, SPK, CENAS["risco"] + 0.1, 0.3)
put(sfx, shing(1.0), CENAS["risco"] + 0.3, 0.8)
put(sfx, clunk(0.6), 47.25, 0.5)
# convite
put(sfx, WH, CENAS["convite"] - 0.25, 0.4)
put(sfx, IMP2, CENAS["convite"] + 0.05, 0.6)
for k in range(4):
    put(sfx, papel(1.0), W(18, "Sábado") + 0.05 + 0.13 * k, 0.8, pan=-0.3)
put(sfx, thud(0.7, 140), W(18, "24") + 0.05, 0.7, pan=-0.2)
for k, a in enumerate(np.arange(W(18, "às"), W(18, "meia"), 0.07)):
    put(sfx, clack(0.35, 2400), a, 0.5, pan=0.2)
put(sfx, ding(1568, 1.0), W(18, "meia") + 0.15, 0.7, pan=0.2)
put(sfx, WH, W(19, "Avenida") - 0.25, 0.25)
put(sfx, thud(1.0, 85), W(19, "Avenida") + 0.12, 0.9)
put(sfx, thud(0.45, 95), W(19, "Avenida") + 0.42, 0.7)
# final
put(sfx, WH, CENAS["final"] + 0.05, 0.18)
put(sfx, WH, CENAS["carimbo"] - 0.3, 0.2)
put(sfx, carimbo(1.0), CENAS["carimbo"], 1.0)
put(sfx, WH, 62.55, 0.45)
put(sfx, WH, 62.7, 0.4)

# ------------------------------------------------------------------ voz + trilha com ducking
voz = load("assets/media/voz_master.wav")[:N]
voz = np.pad(voz, ((0, N - len(voz)), (0, 0)))
mus = load("assets/music/trilha_culto_hero.wav")[:N]
mus = np.pad(mus, ((0, N - len(mus)), (0, 0)))
blk = int(0.01 * SR)
nb = N // blk
e = np.abs(voz[: nb * blk, 0]).reshape(nb, blk).max(1)
g = np.zeros(nb)
cur = 0.0
for kk in range(nb):
    cur += (0.33 if e[kk] > cur else 0.02) * (e[kk] - cur)
    g[kk] = cur
g = np.clip(g / 0.1, 0, 1)
duck = np.repeat(10 ** (-10.0 * g / 20), blk)
duck = np.pad(duck, (0, N - len(duck)), constant_values=1)
mus *= duck[:, None]

t = np.arange(N) / SR
mix = voz * 1.0 + mus * 0.3 + sfx * 0.42
mix *= np.clip((TOTAL - t) / 0.3, 0, 1)[:, None]
wav("assets/media/mix_pre.wav", mix / max(1.0, np.abs(mix).max() / 0.95))
print("mix ok")
