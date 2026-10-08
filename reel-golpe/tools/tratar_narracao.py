"""Tratamento da narração + JSON de palavras definitivo (fonte da verdade da sincronia).

1) Ajusta os inícios de palavra depois de pausa/pontuação ao início real da fala
   (o modelo põe parte do silêncio dentro do primeiro fonema da palavra).
2) Áudio: 48 kHz mono, 0,35 s de respiro no início (o alarme da cena 1 entra
   antes da voz), tratamento "locutor" (tom ~2 semitons abaixo com rubberband,
   EQ e compressão), −14 LUFS / TP ≤ −1,5 dBTP (loudnorm em duas passadas).
   Não há mudança de andamento aqui, então os tempos continuam válidos.

Uso: python3 tools/tratar_narracao.py audio_trabalho assets/media
"""
import json
import re
import subprocess
import sys

import numpy as np
import soundfile as sf

ATRASO = 0.35
trabalho, destino = sys.argv[1], sys.argv[2]

a, sr = sf.read(f"{trabalho}/narracao_bruta.wav")
w = json.load(open(f"{trabalho}/palavras_bruto.json", encoding="utf-8"))

# 0) cortar silêncios (briefing): pausas > 0,35 s viram ~0,25 s; de 0,18 a 0,35 s viram ~0,15 s;
#    emendas com fade de 8 ms; os tempos das palavras são deslocados junto
def envelope(x):
    f = int(0.005 * sr)
    return 20 * np.log10(np.sqrt((x[: len(x) // f * f].reshape(-1, f) ** 2).mean(1)) + 1e-9)


e0 = envelope(a)
silencio = e0 < e0.max() - 45
cortes = []  # (início, fim) do trecho removido, em s
j = 0
while j < len(silencio):
    if silencio[j]:
        k = j
        while k < len(silencio) and silencio[k]:
            k += 1
        dur = (k - j) * 0.005
        alvo = 0.25 if dur > 0.35 else (0.15 if dur >= 0.18 else dur)
        if dur - alvo > 0.02 and j > 0 and k < len(silencio):
            meio = (j + k) / 2 * 0.005
            cortes.append((meio - (dur - alvo) / 2, meio + (dur - alvo) / 2))
        j = k
    else:
        j += 1
fade = int(0.008 * sr)
partes, pos = [], 0
for c0, c1 in cortes:
    seg = a[pos:int(c0 * sr)].copy()
    if partes:
        seg[:fade] *= np.linspace(0, 1, fade)
    seg[-fade:] *= np.linspace(1, 0, fade)
    partes.append(seg)
    pos = int(c1 * sr)
seg = a[pos:].copy()
if partes:
    seg[:fade] *= np.linspace(0, 1, fade)
partes.append(seg)
antes = len(a) / sr
a = np.concatenate(partes)


def mapa(t):
    tirado = 0.0
    for c0, c1 in cortes:
        if t >= c1:
            tirado += c1 - c0
        elif t > c0:
            return round(c0 - tirado, 3)
    return round(t - tirado, 3)


for x in w:
    x["inicio"], x["fim"] = mapa(x["inicio"]), mapa(x["fim"])
print(f"silêncios: {len(cortes)} encurtados, {antes:.2f}s -> {len(a) / sr:.2f}s")
bruto_cortado = f"{trabalho}/.narracao_cortada.wav"
sf.write(bruto_cortado, a, sr)

fr = int(0.005 * sr)
env = 20 * np.log10(np.sqrt((a[: len(a) // fr * fr].reshape(-1, fr) ** 2).mean(1)) + 1e-9)
limiar = env.max() - 35

ajustes = []
# início real de cada palavra que vem depois de pausa ou pontuação: fim do último trecho
# silencioso (o mais longo, >= 60 ms) perto do intervalo previsto; o fim da anterior vai para o
# começo desse silêncio
quieto = env < limiar
for i in range(1, len(w)):
    pont = re.search(r"[,.:;!?\"”]$", w[i - 1]["palavra"])
    if not pont and w[i]["inicio"] - w[i - 1]["fim"] <= 0.08:
        continue
    lo = int(max(w[i - 1]["inicio"] + 0.05, w[i - 1]["fim"] - 0.15) / 0.005)
    hi = min(int((w[i]["inicio"] + 0.12) / 0.005), len(env) - 1)
    melhor = None
    j = lo
    while j < hi:
        if quieto[j]:
            k = j
            while k < len(quieto) and quieto[k]:
                k += 1
            # o silêncio mais longo da janela é a pausa (oclusivas como o "t" duram ~40-60 ms)
            if k - j >= 12 and (melhor is None or k - j > melhor[1] - melhor[0]):
                melhor = (j, k)
            j = k
        else:
            j += 1
    if melhor is None:
        continue
    novo_fim, novo_ini = round(melhor[0] * 0.005, 3), round(melhor[1] * 0.005, 3)
    ajustes.append((w[i]["palavra"], w[i]["inicio"], novo_ini))
    if novo_ini > w[i]["inicio"]:  # palavra deslocada para frente: mantém a duração
        w[i]["fim"] = round(w[i]["fim"] + novo_ini - w[i]["inicio"], 3)
    w[i]["inicio"] = novo_ini
    w[i - 1]["fim"] = max(round(w[i - 1]["inicio"] + 0.05, 3), novo_fim)
for i in range(len(w) - 1):
    w[i]["fim"] = min(w[i]["fim"], round(w[i + 1]["inicio"] - 0.02, 3))
for x in w:
    x["fim"] = max(x["fim"], round(x["inicio"] + 0.05, 3))

pausas = [round(w[i + 1]["inicio"] - w[i]["fim"], 2) for i in range(len(w) - 1)]
print(f"{len(ajustes)} inícios ajustados; maior pausa {max(pausas)} s")

saida = [{"palavra": x["palavra"], "inicio": round(x["inicio"] + ATRASO, 3),
          "fim": round(x["fim"] + ATRASO, 3)} for x in w]
json.dump(saida, open(f"{destino}/palavras.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pre = (f"adelay={int(ATRASO * 1000)},aresample=48000,"
       # voz "locutor": ~2 semitons mais grave (timbre acompanha), graves encorpados, médios limpos, presença
       "rubberband=pitch=0.891:formant=shifted:pitchq=quality,highpass=f=60,"
       "equalizer=f=120:t=q:w=0.9:g=3.5,equalizer=f=380:t=q:w=1.2:g=-2.5,equalizer=f=3200:t=q:w=1.0:g=2.5,"
       "acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=3")
medida = subprocess.run(
    ["ffmpeg", "-hide_banner", "-nostats", "-i", bruto_cortado, "-af",
     pre + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
    capture_output=True, text=True).stderr
m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", medida).group(0))
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
      f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", bruto_cortado,
                "-af", pre + "," + ln + ",aresample=48000", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le",
                f"{destino}/narracao_tratada.wav"], check=True)
print(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                      f"{destino}/narracao_tratada.wav"], capture_output=True, text=True).stdout.strip(), "s")
