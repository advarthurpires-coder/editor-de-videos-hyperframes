# Sintetiza efeitos (thud, whoosh, tic, shimmer) e a cama sonora; tudo gerado aqui, sem bibliotecas de terceiros.
import json, wave, numpy as np, re
SR = 48000
TOTAL = 87.95 + 0.8
W = json.load(open('src/data/words.json'))
def at(word, nth=1, after=0):
    n = 0
    for w in W:
        if w['start'] >= after and re.sub(r'[.,?!]', '', w['word'].lower()) == word:
            n += 1
            if n == nth: return w['start']
    raise SystemExit('palavra ' + word)
LEAD = 3 / 30
rng = np.random.default_rng(7)
N = int(TOTAL * SR) + SR
sfx = np.zeros(N)
def db(x): return 10 ** (x / 20)
def put(sig, t, gain_db):
    i = int(t * SR); sig = sig / (np.max(np.abs(sig)) + 1e-9) * db(gain_db)
    sfx[i:i + len(sig)] += sig[:max(0, N - i)]
def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)
def thud():
    n = int(0.6 * SR); t = np.arange(n) / SR
    f = 95 * np.exp(-t * 6) + 42
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.14)
    click = rng.standard_normal(n) * env(n, 0.0005, 0.012)
    k = np.ones(40) / 40; click = np.convolve(click, k, 'same')
    return body + 0.5 * click
def whoosh(dur=0.7):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n); y = 0.0
    fc = 300 + 2600 * np.sin(np.pi * t / dur) ** 2
    for i in range(n):  # passa-baixa com corte variável
        a = 1 - np.exp(-2 * np.pi * fc[i] / SR); y += a * (noise[i] - y); out[i] = y
    return out * np.sin(np.pi * t / dur) ** 1.5
def tic():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * t) + 0.5 * np.sin(2 * np.pi * 3700 * t)) * env(n, 0.0003, 0.006)
def shimmer(dur=1.1):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for k, f in enumerate([1318.5, 1760, 2217.5, 2637, 3520]):
        s += np.sin(2 * np.pi * f * t + k) * np.exp(-((t - 0.12 * k - 0.15) ** 2) / 0.05) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t))
    return s * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.3)

# carimbos
put(thud(), 0.08, -20)
put(thud(), at('promulga') - 0.03 - 0.02, -21)
put(thud(), at('hoje') - 0.03 - 0.02, -21)
# whoosh nas trocas de capítulo (e no dolly-out inicial)
for tt in [0.7, 11.6, 24.2, 35.3, 43.3, 61.5, 74.5, 83.3]:
    put(whoosh(), tt - 0.35, -24)
# tic-tic: 6 dias
for i in range(6): put(tic(), at('6') - LEAD + i * 0.085, -24)
# placar 0→75 (contador mecânico desacelerando)
p0 = at('75') + 0.65
for k in range(16):
    x = k / 15; put(tic(), p0 + (1 - (1 - x) ** 0.5) * 0.8, -25)
# 44 → 42 → 40
put(tic(), at('44') - LEAD, -24)
for base in [at('42'), at('40')]:
    for k in range(3): put(tic(), base - LEAD + k * 0.15, -24)
# shimmer: colunas viram o símbolo
put(shimmer(), 87.0 + 0.8, -22)

def write(path, x):
    x = np.clip(x, -1, 1); d = (x * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
write('out/sfx.wav', sfx[:int(TOTAL * SR)])

# cama sonora: pad grave sustentado (Ré + Lá), sem melodia, com respiração lenta
n = int(TOTAL * SR); t = np.arange(n) / SR
pad = np.zeros(n)
for f, g in [(73.42, 1.0), (110.0, 0.7), (146.83, 0.45), (220.0, 0.22)]:
    for det in (-0.6, 0.6):
        pad += g * np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
pad *= 0.75 + 0.25 * np.sin(2 * np.pi * t / 9.0)
pad *= np.minimum(1, t / 1.5) * np.minimum(1, (TOTAL - t) / 1.2)
pad = pad / np.sqrt(np.mean(pad ** 2)) * db(-26) * db(-14 + 14)  # RMS ≈ −26 dBFS
write('out/pad.wav', pad)
print('ok')
