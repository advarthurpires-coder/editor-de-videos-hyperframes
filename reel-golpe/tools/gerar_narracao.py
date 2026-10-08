"""Narração sintética (Kokoro-82M, voz pm_alex, pt-BR) com marcação de tempo por palavra.

O modelo Kokoro em ONNX não expõe as durações por fonema; este script copia o
modelo do cache do HyperFrames e acrescenta a saída "duration" (o tensor
/encoder/Clip, em quadros por token). Com ela o kokoro-onnx devolve o tempo de
cada fonema, e as palavras saem da fala sintetizada, não de uma transcrição.

Cada frase é sintetizada inteira (entonação natural) e as frases são unidas
com pausas fixas: 0,25 s entre frases, 0,25 s também entre parágrafos,
0,15 s nas vírgulas/dois-pontos (feito pelo próprio kokoro-onnx).

Saídas: <saida>/narracao_bruta.wav (24 kHz) e <saida>/palavras_bruto.json
Uso: python3 tools/gerar_narracao.py <roteiro.txt> <pasta_saida> [velocidade]
"""
import json
import os
import re
import sys

import numpy as np
import onnx
import soundfile as sf
from kokoro_onnx import Kokoro

CACHE = os.path.expanduser("~/.cache/hyperframes/tts")
VOZ = "pm_alex"
FRASE = 0.25
PARAGRAFO = 0.25
VIRGULA = 0.15

# Pronúncia: o espeak lê "WhatsApp" em inglês truncado; o texto exibido não muda.
FALA = {"WhatsApp": "uótsápi", "WhatsApp.": "uótsápi.", "link": "línki", "link,": "línki,"}
# O espeak insere um "ə" depois do r em "Arthur" e "logomarca"; fonemas fixados à mão.
FONEMAS = {"Arthur": "ˈaɾtur", "logomarca": "lˌoɡomˈaɾkæ"}


def modelo_com_duracao(destino):
    if os.path.exists(destino):
        return destino
    m = onnx.load(os.path.join(CACHE, "models/kokoro-v1.0.onnx"))
    cast = onnx.helper.make_node("Cast", ["/encoder/Clip_output_0"], ["duration"], to=onnx.TensorProto.INT64)
    m.graph.node.append(cast)
    m.graph.output.append(onnx.helper.make_tensor_value_info("duration", onnx.TensorProto.INT64, None))
    onnx.save(m, destino)
    return destino


def main():
    roteiro, saida = sys.argv[1], sys.argv[2]
    velocidade = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    os.makedirs(saida, exist_ok=True)
    k = Kokoro(modelo_com_duracao(os.path.join(saida, ".kokoro-dur.onnx")), os.path.join(CACHE, "voices/voices-v1.0.bin"))
    assert k.has_timings

    paragrafos = [p.strip() for p in open(roteiro, encoding="utf-8").read().split("\n\n") if p.strip()]
    sr = 24000
    pedacos, palavras, t0 = [], [], 0.0
    for pi, par in enumerate(paragrafos):
        frases = re.findall(r"[^.!?]+[.!?]+[\"”]?", par.replace("\n", " "))
        for fi, frase in enumerate(frases):
            exibidas = frase.split()
            faladas = [FALA.get(w, w) for w in exibidas]
            # fonemas palavra a palavra, para saber exatamente a que palavra cada fonema pertence
            fon = [FONEMAS.get(w) or k.tokenizer.phonemize(re.sub(r"[\"“”]", "", w), "pt-br") for w in faladas]
            audio, sr, tim = k.create_timed(" ".join(fon), VOZ, velocidade, "pt-br", is_phonemes=True,
                                            sentence_pause=0.0, clause_pause=VIRGULA)
            # percorre os fonemas: espaço separa palavras
            idx, atual = 0, []
            limites = []
            for t in tim:
                if t.phoneme == " ":
                    if atual:
                        limites.append(atual)
                        atual = []
                    continue
                atual.append(t)
            if atual:
                limites.append(atual)
            if len(limites) != len(exibidas):
                raise SystemExit(f"palavras {len(exibidas)} != grupos {len(limites)} em: {frase}")
            for w, grupo in zip(exibidas, limites):
                sons = [t for t in grupo if t.phoneme not in ",.;:!?—…\"“” "] or grupo
                palavras.append({"palavra": w, "inicio": round(t0 + sons[0].start, 3),
                                 "fim": round(t0 + sons[-1].end, 3), "paragrafo": pi + 1})
            fala = np.asarray(audio, dtype=np.float32)
            # remove o silêncio final que sobrar além do fim da última palavra
            fim_ult = int((limites[-1][-1].end + 0.04) * sr)
            fala = fala[:max(fim_ult, 1)]
            pausa = PARAGRAFO if fi == len(frases) - 1 and pi < len(paragrafos) - 1 else FRASE
            if pi == len(paragrafos) - 1 and fi == len(frases) - 1:
                pausa = 0.0
            pedacos += [fala, np.zeros(int(pausa * sr), dtype=np.float32)]
            t0 += len(fala) / sr + pausa
            print(f"{t0:7.2f}s  {frase.strip()[:70]}")
    sf.write(os.path.join(saida, "narracao_bruta.wav"), np.concatenate(pedacos), sr)
    json.dump(palavras, open(os.path.join(saida, "palavras_bruto.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"total {t0:.2f}s, {len(palavras)} palavras")


if __name__ == "__main__":
    main()
