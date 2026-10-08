"""Tratamento da narração + JSON de palavras definitivo (fonte da verdade da sincronia).

1) Ajusta os inícios de palavra depois de pausa ao início real da energia
   (o kokoro-onnx acrescenta as pausas de vírgula depois de calcular os tempos,
   e o início da palavra seguinte pode ficar até ~0,15 s fora).
2) Áudio: 48 kHz mono, 0,35 s de respiro no início (o alarme da cena 1 entra
   antes da voz), passa-alta 80 Hz, compressão suave, −14 LUFS / TP ≤ −1,5 dBTP
   (loudnorm em duas passadas). Não há mudança de andamento aqui: a aceleração
   de 8 % foi feita na síntese (velocidade 1,08), então os tempos continuam válidos.

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

fr = int(0.005 * sr)
env = 20 * np.log10(np.sqrt((a[: len(a) // fr * fr].reshape(-1, fr) ** 2).mean(1)) + 1e-9)
limiar = env.max() - 35

ajustes = []
for i in range(1, len(w)):
    if w[i]["inicio"] - w[i - 1]["fim"] > 0.08:
        j = int((w[i - 1]["fim"] + 0.03) / 0.005)
        while j < len(env) and env[j] < limiar:
            j += 1
        novo = round(j * 0.005, 3)
        if abs(novo - w[i]["inicio"]) > 0.02 and abs(novo - w[i]["inicio"]) < 0.25:
            ajustes.append((w[i]["palavra"], w[i]["inicio"], novo))
            if novo > w[i]["inicio"]:  # palavra deslocada para frente: mantém a duração
                w[i]["fim"] = round(w[i]["fim"] + novo - w[i]["inicio"], 3)
            w[i]["inicio"] = novo
            w[i - 1]["fim"] = min(w[i - 1]["fim"], round(novo - 0.03, 3))
for x in w:
    x["fim"] = max(x["fim"], round(x["inicio"] + 0.05, 3))

pausas = [round(w[i + 1]["inicio"] - w[i]["fim"], 2) for i in range(len(w) - 1)]
print(f"{len(ajustes)} inícios ajustados; maior pausa {max(pausas)} s")

saida = [{"palavra": x["palavra"], "inicio": round(x["inicio"] + ATRASO, 3),
          "fim": round(x["fim"] + ATRASO, 3)} for x in w]
json.dump(saida, open(f"{destino}/palavras.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pre = f"adelay={int(ATRASO * 1000)},aresample=48000,highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2"
medida = subprocess.run(
    ["ffmpeg", "-hide_banner", "-nostats", "-i", f"{trabalho}/narracao_bruta.wav", "-af",
     pre + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
    capture_output=True, text=True).stderr
m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", medida).group(0))
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
      f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", f"{trabalho}/narracao_bruta.wav",
                "-af", pre + "," + ln + ",aresample=48000", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le",
                f"{destino}/narracao_tratada.wav"], check=True)
print(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                      f"{destino}/narracao_tratada.wav"], capture_output=True, text=True).stdout.strip(), "s")
