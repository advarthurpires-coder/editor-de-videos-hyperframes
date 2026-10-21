# Mixagem: voz tratada nos mesmos cortes do vídeo + trilha com ducking sob a voz + efeitos sonoros.
# Grava assets/media/mix_pre.wav (masterizar depois com tools/masterizar.sh) e stems em renders/ para conferência.
# Uso: python3 -I tools/mixar_audio.py   (depois de sincronia.py e gerar_trilha.py)
import json, os, subprocess, wave
import numpy as np

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
SR = 48000
EV = json.load(open(f"{D}/tools/eventos.json"))
TOTAL, SEGS = EV["total"], EV["segs"]
N = int(round(TOTAL * SR))


def ler(path, filtros=None, mono=True):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if filtros: cmd += ["-af", filtros]
    cmd += ["-ac", "1" if mono else "2", "-ar", str(SR), "-f", "f32le", "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return a if mono else a.reshape(-1, 2)


def db(x):
    return 10 ** (x / 20)


def fades(x, ms=8):
    n = min(len(x) // 2, int(SR * ms / 1000))
    x = x.copy(); r = np.linspace(0, 1, n) ** 0.5; x[:n] *= r; x[-n:] *= r[::-1]
    return x


def conv(x, h):
    """convolução 'same' via FFT (np.convolve é lento demais para janelas longas)"""
    n = len(x) + len(h) - 1; size = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(h, size), size)[:n]
    o = (len(h) - 1) // 2
    return y[o:o + len(x)]


def salvar(path, x):
    x = np.atleast_2d(x.T).T if x.ndim == 1 else x
    with wave.open(path, "wb") as w:
        w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


# ------------------------------------------------------------------ voz (celular, sala com eco): limpeza + presença
TRAT = ("highpass=f=85,afftdn=nr=12:nf=-40:tn=1,"
        "equalizer=f=320:t=q:w=1.1:g=-3,equalizer=f=900:t=q:w=1.4:g=-1,equalizer=f=3300:t=q:w=1.0:g=3,"
        "equalizer=f=10000:t=q:w=0.9:g=2,deesser=i=0.3,"
        "acompressor=threshold=-24dB:ratio=3.2:attack=5:release=80:makeup=4")
bruto = ler(f"{D}/src/convite_original.mp4", TRAT)
voz = np.zeros(N, np.float32)
for s in SEGS:
    a, b = int(round(s["src"] * SR)), int(round(s["fim_src"] * SR))
    i = int(round(s["out"] * SR))
    seg = fades(bruto[a:b])[: N - i]
    voz[i:i + len(seg)] += seg

# ------------------------------------------------------------------ trilha com ducking
mus = ler(f"{D}/assets/music/trilha_convite_hero.wav", mono=False)[:N]
musica = np.zeros((N, 2), np.float32); musica[:len(mus)] = mus
env = np.sqrt(np.maximum(conv(voz ** 2, np.ones(2880) / 2880), 0))
ativo = (env > db(-40)).astype(np.float32)
k = int(0.22 * SR); ker = np.hanning(2 * k + 1); ker /= ker.sum()
ativo = np.clip(conv(ativo, ker) * 1.6, 0, 1)
g = db(-11) + (db(-17) - db(-11)) * ativo           # sob a voz -17 dB, nas brechas -11 dB
f0 = int(EV["ev"]["flyer"] * SR) - int(0.05 * SR)
g[f0:] = db(-1.5)                                    # sem voz: trilha em evidência no flyer/cartela
r = int(0.12 * SR); g[f0 - r:f0] = np.linspace(g[f0 - r - 1], db(-1.5), r)
musica *= g[:, None]

# ------------------------------------------------------------------ efeitos
fx = np.zeros((N, 2), np.float32)
for nome, t, ganho in EV["sfx"]:
    arq = f"{D}/assets/sfx/{nome}.wav" if os.path.exists(f"{D}/assets/sfx/{nome}.wav") else f"{D}/assets/sfx/{nome}.mp3"
    s = ler(arq, mono=False) * db(ganho)
    i = int(round(t * SR))
    if i < 0: s = s[-i:]; i = 0
    s = s[: N - i]; fx[i:i + len(s)] += s

fala = np.stack([voz, voz], 1)
mix = fala * 1.0 + musica + fx
esc = 0.5 / max(np.abs(mix).max(), 1e-6)
os.makedirs(f"{D}/renders", exist_ok=True)
salvar(f"{D}/assets/media/mix_pre.wav", mix * esc)
for nome, x in (("stem_voz", fala), ("stem_trilha", musica), ("stem_sfx", fx)):
    salvar(f"{D}/renders/{nome}.wav", x * esc)
print("mix_pre.wav", round(N / SR, 2), "s")
