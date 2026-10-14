# Mixagem do reel: fala do TikTok (tela dividida) + voz do Arthur nos mesmos cortes do vídeo + trilha discreta
# com ducking sob a voz + efeitos sonoros. Grava assets/media/mix_pre.wav (masterizar depois com tools/masterizar.sh).
# Uso: python3 -I tools/mixar_audio.py
import json, os, subprocess
import numpy as np

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
SR = 48000
EV = json.load(open(f"{D}/tools/eventos.json"))
TOTAL, INTRO, SEGS = EV["total"], EV["intro"], EV["segs"]
N = int(round(TOTAL * SR))


def ler(path, filtros=None, mono=True):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if filtros: cmd += ["-af", filtros]
    cmd += ["-ac", "1" if mono else "2", "-ar", str(SR), "-f", "f32le", "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return a if mono else a.reshape(-1, 2)


def db(x):
    return 10 ** (x / 20)


def fades(x, ms=6):
    n = min(len(x) // 2, int(SR * ms / 1000))
    if n > 0:
        r = np.linspace(0, 1, n); x = x.copy(); x[:n] *= r; x[-n:] *= r[::-1]
    return x


# ------------------------------------------------------------------ voz do Arthur (tratada) nos cortes
TRAT = ("highpass=f=75,afftdn=nr=10:nf=-42,"
        "equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=9000:t=q:w=1.0:g=1.5,"
        "acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3")
ar = ler(f"{D}/src/arthur.mp4", TRAT)
voz = np.zeros(N, np.float32)
for s in SEGS:
    a, b = int(s["src"] * SR), int(s["fim_src"] * SR)
    i = int(round(s["out"] * SR))
    seg = fades(ar[a:b])[: N - i]
    voz[i:i + len(seg)] += seg

# ------------------------------------------------------------------ TikTok (0 -> INTRO)
tk = ler(f"{D}/src/tiktok.mp4", "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2")
n_tk = int(INTRO * SR)
tk = tk[:n_tk].copy()
r = int(0.06 * SR); tk[-r:] *= np.linspace(1, 0, r)
# nivela a fala do TikTok com a voz do Arthur (RMS das partes ativas)
def rms_ativo(x):
    x = x[np.abs(x) > 1e-4]; e = np.sqrt(np.convolve(x ** 2, np.ones(2400) / 2400, "same"))
    return np.sqrt(np.mean(np.sort(e)[int(len(e) * 0.5):] ** 2))
tk *= rms_ativo(voz[n_tk:]) / max(rms_ativo(tk), 1e-6) * 0.95
fala = voz.copy(); fala[:len(tk)] += tk

# ------------------------------------------------------------------ trilha com ducking
INI_MUS = INTRO - 0.9
trilha_dur = TOTAL - INI_MUS
subprocess.run(["python3", "-I", f"{D}/tools/gerar_trilha.py", f"{trilha_dur:.3f}", f"{D}/assets/music/trilha_lofi.wav"], check=True)
mus = ler(f"{D}/assets/music/trilha_lofi.wav", mono=False)
musica = np.zeros((N, 2), np.float32)
i = int(INI_MUS * SR); musica[i:i + len(mus)] = mus[: N - i]
# envelope da voz (janela de 60 ms) -> ganho da trilha entre -15 dB (sob voz) e -9 dB (pausas), transições suaves
env = np.sqrt(np.convolve(fala ** 2, np.ones(2880) / 2880, "same"))
ativo = (env > db(-42)).astype(np.float32)
k = int(0.25 * SR); ker = np.hanning(2 * k + 1); ker /= ker.sum()
ativo = np.clip(np.convolve(ativo, ker, "same") * 1.6, 0, 1)
g = db(-9) + (db(-15) - db(-9)) * ativo
g[: int(INTRO * SR)] *= np.linspace(0, 1, int(INTRO * SR)) ** 2   # entra por baixo, cresce até o corte
musica *= g[:, None]
# na cartela a trilha sobe um pouco (sem voz)
c0 = int(EV["ev"]["cartela"] * SR)
musica[c0:] *= np.linspace(1, db(3), N - c0)[:, None]

# ------------------------------------------------------------------ efeitos
fx = np.zeros((N, 2), np.float32)
for nome, t, ganho in EV["sfx"]:
    s = ler(f"{D}/assets/sfx/{nome}.mp3", mono=False) * db(ganho - 2)
    i = int(round(t * SR))
    if i < 0: s = s[-i:]; i = 0
    s = s[: N - i]; fx[i:i + len(s)] += s

mix = np.stack([fala, fala], 1) * 0.92 + musica + fx
mix *= 0.5 / max(np.abs(mix).max(), 1e-6)
import wave
with wave.open(f"{D}/assets/media/mix_pre.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
# voz isolada (para QA de sincronia)
with wave.open(f"{D}/renders/voz_editada.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(fala / max(np.abs(fala).max(), 1e-6) * 0.8, -1, 1) * 32767).astype(np.int16).tobytes())
print("mix_pre.wav", round(N / SR, 2), "s")
# stems para conferência de equilíbrio (mesma escala do mix)
esc = 0.5 / max(np.abs(np.stack([fala, fala], 1) * 0.92 + musica + fx).max(), 1e-6)
for nome, x in (("stem_voz", np.stack([fala, fala], 1) * 0.92), ("stem_trilha", musica), ("stem_sfx", fx)):
    with wave.open(f"{D}/renders/{nome}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x * esc, -1, 1) * 32767).astype(np.int16).tobytes())
