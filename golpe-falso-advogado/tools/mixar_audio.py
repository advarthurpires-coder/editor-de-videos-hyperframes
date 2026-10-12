"""Mixagem do reel "Golpe do falso advogado" + dados de sincronia palavra a palavra.

- Posiciona as 9 frases da locução (Kokoro pm_alex, pt-BR, 1,12x) nos tempos de INICIO.
- Trilha original (tools/gerar_trilha.py) com ducking guiado pela voz (até -10 dB).
- Efeitos sonoros nos cortes, batidas e destaques (CORTES / SFX abaixo).
- Saídas: assets/media/mix_pre.wav (sem normalizar) e assets/sincronia.js
  (window.SYNC = frases com início absoluto de cada palavra; usado pelo index.html).
Uso: python3 -I tools/mixar_audio.py
"""
import json, subprocess, wave
import numpy as np

SR = 48000
TOTAL = 33.0
N = int(TOTAL * SR)
VOZ = "assets/media/voz"
INICIO = [0.20, 4.46, 7.65, 10.72, 14.07, 17.88, 21.90, 25.52, 28.91]
CORTES = [4.36, 7.55, 10.62, 14.0, 17.78, 21.80, 25.42, 28.70]   # trocas de cena
DROP1, DROP2 = 14.0, 28.70


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<f4").reshape(-1, 2).astype(np.float64)


def put(buf, sig, t, g=1.0):
    i = int(round(t * SR)); j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * g


frases = json.load(open(f"{VOZ}/frases.json"))
voz = np.zeros((N, 2))
for f, t0 in zip(frases, INICIO):
    put(voz, load(f"{VOZ}/f{f['i']:02d}.wav"), t0)
voz = voz / np.abs(voz).max() * 0.5

subprocess.run(["python3", "-I", "tools/gerar_trilha.py", "assets/music/trilha_alerta.wav",
                str(DROP1), str(DROP2), str(TOTAL)], check=True)
mus = load("assets/music/trilha_alerta.wav")[:N]
mus = np.pad(mus, ((0, N - len(mus)), (0, 0)))
# ducking: seguidor de envelope em blocos de 10 ms (ataque rápido, liberação 350 ms)
blk = int(0.01 * SR); nb = N // blk
e = np.abs(voz[: nb * blk, 0]).reshape(nb, blk).max(1)
g = np.zeros(nb); cur = 0.0
for k in range(nb):
    cur += (0.35 if e[k] > cur else 0.03) * (e[k] - cur); g[k] = cur
duck = np.repeat(10 ** (-10.0 * np.clip(g / 0.12, 0, 1) / 20), blk)
duck = np.pad(duck, (0, N - len(duck)), constant_values=1)
mus *= duck[:, None]

SFX = [("impact-bass-1.mp3", 0.02, 0.45)]
for c in CORTES:
    if c not in (DROP1, DROP2):
        SFX.append(("whoosh.mp3", c - 0.22, 0.28))
SFX += [
    ("impact-bass-2.mp3", 3.0, 0.32),     # carimbo FALSO
    ("pop.mp3", 5.0, 0.22),               # balão da mensagem
    ("click-soft.mp3", 6.55, 0.25), ("click-soft.mp3", 7.2, 0.25),   # setas foto / nome
    ("click.mp3", 8.15, 0.18),            # número do processo
    ("sparkle.mp3", 9.75, 0.20),          # "ganhou a causa"
    ("click.mp3", 12.55, 0.2), ("click.mp3", 13.05, 0.2),             # cronômetro
    ("impact-bass-1.mp3", DROP1, 0.62),   # É GOLPE!
    ("whoosh.mp3", 15.2, 0.2),
    ("impact-bass-2.mp3", 17.9, 0.36),    # NÃO PAGUE
    ("pop.mp3", 19.3, 0.18), ("pop.mp3", 21.0, 0.18),
    ("pop.mp3", 23.1, 0.18), ("pop.mp3", 24.6, 0.18),
    ("impact-bass-2.mp3", 27.0, 0.3),     # 4 a 8 anos
    ("impact-bass-1.mp3", DROP2, 0.42),   # cartela
    ("sparkle.mp3", 29.6, 0.16),
]
sfx = np.zeros((N, 2))
for arq, tc, gv in SFX:
    put(sfx, load(f"assets/sfx/{arq}"), tc, gv)

t = np.arange(N) / SR
mix = voz + mus * 0.36 + sfx * 0.55
mix *= np.clip((TOTAL - t) / 0.5, 0, 1)[:, None]
with wave.open("assets/media/mix_pre.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    x = np.clip(mix / max(1.0, np.abs(mix).max() / 0.95), -1, 1)
    w.writeframes((x * 32767).astype("<i2").tobytes())

sync = []
for f, t0 in zip(frases, INICIO):
    pal, ini = [], t0
    for p in f["palavras"]:
        pal.append({"w": p["w"], "s": round(ini, 3), "e": round(t0 + p["fim"], 3)})
        ini = t0 + p["fim"]
    sync.append({"s": t0, "e": round(t0 + f["dur"], 3), "texto": f["texto"], "p": pal})
with open("assets/sincronia.js", "w") as fh:
    fh.write("window.SYNC = " + json.dumps(sync, ensure_ascii=False) + ";\n")
for s in sync:
    print(f"{s['s']:6.2f} -> {s['e']:6.2f}  {s['texto']}")
