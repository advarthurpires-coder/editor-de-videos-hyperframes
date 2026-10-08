"""Mixagem do reel 2º HERO EXTREME + dados de legenda.

- Posiciona as 10 frases da locução (Kokoro pm_alex, pt-BR) nos tempos do roteiro.
- Ambiências sintetizadas (vento/pássaros, água, brasa/churrasqueira) e efeitos do projeto.
- Trilha com ducking guiado pela voz (sidechain); voz sempre inteligível.
- Saídas: assets/media/voz_master.wav, assets/media/mix_pre.wav (sem normalizar),
  assets/legendas_data.js (frases com tempo absoluto de cada palavra).
Uso: python3 -I tools/mixar_audio.py <pasta_frases_tts>
"""
import json
import subprocess
import sys
import wave

import numpy as np

SR = 48000
TOTAL = 59.0
N = int(TOTAL * SR)
rng = np.random.default_rng(7)
VOZ_DIR = sys.argv[1]

# início (s) de cada frase no vídeo
INICIO = [1.00, 8.60, 13.60, 21.20, 24.60, 31.20, 39.40, 45.80, 49.80, 53.40]

# blocos de legenda por frase (None = sem legenda: a cartela mostra o texto falado)
BLOCOS = {
    1: ["E se eu te dissesse", "que alguns dos melhores", "encontros com Deus", "acontecem fora", "das quatro paredes?"],
    2: None,
    3: ["Serão dias de comunhão,", "pesca, churrasco,", "boas conversas,", "novas amizades", "e momentos inesquecíveis."],
    4: ["Mas o principal", "vai muito além disso."],
    5: ["Teremos louvor,", "adoração, Palavra", "e momentos especiais", "na presença de Deus."],
    6: ["Um ambiente leve,", "para fortalecer a fé,", "compartilhar o amor de Jesus", "e lembrar que ninguém", "precisa caminhar sozinho."],
    7: ["Então, convide um amigo", "e venha viver essa experiência", "com a gente!"],
    8: None, 9: None, 10: None,
}
DESTAQUE = {"Deus", "Deus.", "quatro", "paredes?", "comunhão,", "pesca,", "churrasco,", "louvor,", "adoração,",
            "Palavra", "fé,", "Jesus", "ninguém", "sozinho.", "amigo", "experiência", "além", "amizades"}


def load(path, sr=SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<f4").reshape(-1, 2).astype(np.float64)


def fftconv(x, h):
    n = len(x) + len(h) - 1
    size = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(h, size), size)[:n]


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    h = (1 - a) * a ** np.arange(int(np.log(1e-4) / np.log(a)) + 1)
    return fftconv(fftconv(x, h)[: len(x)], h)[: len(x)]


def hp(x, fc):
    return x - lp(x, fc)


def put(buf, sig, t, gain=1.0):
    i = int(round(t * SR))
    if sig.ndim == 1:
        sig = np.stack([sig, sig], 1)
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


# ------------------------------------------------------------------ voz
frases = json.load(open(f"{VOZ_DIR}/frases.json"))
voz = np.zeros((N, 2))
for f, t0 in zip(frases, INICIO):
    s = load(f"{VOZ_DIR}/f{f['i']:02d}.wav")[:, 0]
    s = hp(s, 75)
    # leve presença (2–5 kHz) e calor (200 Hz) — EQ suave por mistura de bandas
    pres = hp(lp(s, 5000), 2000)
    s = s + 0.18 * pres
    put(voz, s, t0)
pk = np.abs(voz).max()
voz = voz / pk * 0.5

# ------------------------------------------------------------------ trilha + ducking
mus = load("assets/music/trilha_hero_extreme.wav")[:N]
mus = np.pad(mus, ((0, N - len(mus)), (0, 0)))
env = np.abs(voz[:, 0])
# seguidor de envelope (ataque 25 ms, liberação 400 ms) em blocos de 10 ms
blk = int(0.01 * SR)
nb = N // blk
e = env[: nb * blk].reshape(nb, blk).max(1)
g = np.zeros(nb)
cur = 0.0
for k in range(nb):
    a = 0.33 if e[k] > cur else 0.025
    cur += a * (e[k] - cur)
    g[k] = cur
g = np.clip(g / 0.12, 0, 1)
duck_db = -9.0 * g  # até -9 dB sob a voz
duck = np.repeat(10 ** (duck_db / 20), blk)
duck = np.pad(duck, (0, N - len(duck)), constant_values=1)
mus = mus * duck[:, None]

# ------------------------------------------------------------------ ambiências sintetizadas
amb = np.zeros((N, 2))
t = np.arange(N) / SR


def janela(a, b, fi=0.6, fo=0.6):
    w = np.clip((t - a) / fi, 0, 1) * np.clip((b - t) / fo, 0, 1)
    return w


# vento (0–8,3 s): ruído grave modulado, estéreo descorrelacionado
wl = lp(rng.standard_normal(N), 420); wr = lp(rng.standard_normal(N), 420)
mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.17 * t) * np.sin(2 * np.pi * 0.05 * t + 1)
w = janela(0.2, 8.3, 1.5, 0.6) * mod
amb[:, 0] += wl * w * 0.35; amb[:, 1] += wr * w * 0.35
# pássaros (gorjeios FM curtos)
for tc, f0, pan in [(1.6, 3200, -0.5), (1.85, 3600, -0.5), (3.1, 2800, 0.6), (4.3, 3900, -0.2), (4.5, 4200, -0.2), (5.9, 3000, 0.5), (6.15, 3400, 0.5)]:
    d = 0.11
    tt = np.arange(int(d * SR)) / SR
    fr = f0 * (1 + 0.25 * np.sin(2 * np.pi * 28 * tt)) * (1 + 0.3 * tt / d)
    ch = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * tt / d) ** 2 * 0.05
    put(amb, np.stack([ch * (1 - pan) / 2, ch * (1 + pan) / 2], 1), tc)
# água na margem (13,3–16,0 s)
wa = lp(rng.standard_normal(N), 700)
lap = (0.5 + 0.5 * np.sin(2 * np.pi * 0.45 * t)) ** 3
w = janela(13.3, 15.9, 0.4, 0.5) * lap
amb[:, 0] += wa * w * 0.28; amb[:, 1] += np.roll(wa, 900) * w * 0.28


def crepitar(a, b, dens, ganho, chiado=0.0):
    n = int((b - a) * dens)
    for k in range(n):
        tc = a + rng.random() * (b - a)
        d = 0.004 + rng.random() * 0.01
        tt = np.arange(int(d * SR)) / SR
        c = hp(rng.standard_normal(len(tt)), 1500) * np.exp(-tt / (d / 3)) * (0.3 + rng.random()) * ganho
        pan = rng.uniform(-0.6, 0.6)
        put(amb, np.stack([c * (1 - pan) / 2, c * (1 + pan) / 2], 1), tc)
    if chiado:
        sz = hp(rng.standard_normal(N), 3000) * janela(a, b, 0.4, 0.5) * chiado
        amb[:, 0] += sz; amb[:, 1] += np.roll(sz, 400)


crepitar(7.9, 13.3, 9, 0.25)                 # fogueira da abertura do título
crepitar(15.6, 18.3, 16, 0.3, chiado=0.035)   # churrasqueira (brasa + chiado)
crepitar(18.1, 20.8, 6, 0.18)                # fogueira da roda de conversa
crepitar(45.0, 58.5, 5, 0.18)                # brasas da cartela final

# ------------------------------------------------------------------ efeitos do projeto
sfx = np.zeros((N, 2))
for arq, tc, gv in [
    ("assets/sfx/impact-bass-1.mp3", 7.88, 0.55),
    ("assets/sfx/impact-bass-2.mp3", 9.95, 0.32),   # entrada da logomarca (HERO)
    ("assets/sfx/whoosh.mp3", 13.05, 0.30),
    ("assets/sfx/whoosh.mp3", 15.35, 0.22),
    ("assets/sfx/whoosh.mp3", 17.85, 0.22),
    ("assets/sfx/whoosh.mp3", 20.65, 0.20),
    ("assets/sfx/sparkle.mp3", 24.35, 0.16),
    ("assets/sfx/whoosh.mp3", 30.35, 0.22),
    ("assets/sfx/whoosh.mp3", 38.75, 0.26),
    ("assets/sfx/impact-bass-2.mp3", 44.98, 0.55),
    ("assets/sfx/sparkle.mp3", 55.6, 0.14),
]:
    put(sfx, load(arq), tc, gv)

# ------------------------------------------------------------------ soma
mix = voz * 1.0 + mus * 0.42 + amb * 0.5 + sfx * 0.6
fade = np.clip((TOTAL - t) / 0.4, 0, 1)
mix *= fade[:, None]


def wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


wav("assets/media/voz_master.wav", voz)
wav("assets/media/mix_pre.wav", mix / max(1.0, np.abs(mix).max() / 0.95))

# ------------------------------------------------------------------ legendas
leg = []
for f, t0 in zip(frases, INICIO):
    bl = BLOCOS[f["i"]]
    if not bl:
        continue
    pal = f["palavras"]
    k = 0
    for bi, txt in enumerate(bl):
        ws = txt.split()
        item = {"w": []}
        for wtxt in ws:
            p = pal[k]
            assert p["w"] == wtxt, (p["w"], wtxt)
            ini = t0 + (pal[k - 1]["fim"] if k > 0 else 0.0)
            item["w"].append({"t": wtxt, "s": round(ini, 3), "h": wtxt in DESTAQUE})
            k += 1
        item["s"] = item["w"][0]["s"]
        leg.append(item)
    assert k == len(pal)
    # fim de cada bloco: início do próximo bloco da mesma frase; último = fim da frase + 0,35 s
    fim_frase = t0 + f["dur"] + 0.35
    blocos_frase = leg[-len(bl):]
    for a, b in zip(blocos_frase, blocos_frase[1:]):
        a["e"] = b["s"]
    blocos_frase[-1]["e"] = round(fim_frase, 3)
with open("assets/legendas_data.js", "w") as fh:
    fh.write("window.LEGENDAS = " + json.dumps(leg, ensure_ascii=False) + ";\n")
print("legendas:", len(leg), "blocos")
for f, t0 in zip(frases, INICIO):
    print(f"frase {f['i']:2d}: {t0:6.2f} -> {t0 + f['dur']:6.2f}")
