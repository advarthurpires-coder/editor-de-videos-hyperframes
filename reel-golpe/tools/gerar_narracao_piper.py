"""Narração com a voz Piper "cadu" (pt-BR, dataset CC0) e marcação de tempo por palavra.

O modelo VITS do Piper calcula a duração de cada fonema (tensor "w_ceil", em
quadros de 256 amostras); este script o expõe como saída extra do ONNX e usa
esses tempos para saber exatamente quando cada palavra é dita.

Cada frase é sintetizada inteira (entonação natural) e as frases são unidas
com 0,25 s de pausa. O tratamento "locutor" (tom mais grave, EQ, compressão)
fica em tools/tratar_narracao.py e não altera os tempos.

Modelo: github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-cadu-medium.tar.bz2
Saídas: <saida>/narracao_bruta.wav (22,05 kHz) e <saida>/palavras_bruto.json
Uso: python3 tools/gerar_narracao_piper.py <roteiro.txt> <pasta_saida> [length_scale]
"""
import json
import os
import re
import sys
import unicodedata

import numpy as np
import onnx
import onnxruntime as ort
import phonemizer
import soundfile as sf
from kokoro_onnx.tokenizer import Tokenizer  # só para registrar a biblioteca do espeak-ng

MODELO = os.path.expanduser("~/.cache/tts-piper/vits-piper-pt_BR-cadu-medium/pt_BR-cadu-medium")
FRASE = 0.25
HOP = 256

# Pronúncia: grafias que o espeak lê melhor; o texto exibido não muda.
FALA = {"WhatsApp.": "uótsápi.", "link": "línqui", "link,": "línqui,", "Arthur": "Ártur"}


def sessao(destino):
    if not os.path.exists(destino):
        m = onnx.load(MODELO + ".onnx")
        m.graph.output.append(onnx.helper.make_tensor_value_info("w_ceil", onnx.TensorProto.FLOAT, None))
        onnx.save(m, destino)
    return ort.InferenceSession(destino, providers=["CPUExecutionProvider"])


def main():
    roteiro, saida = sys.argv[1], sys.argv[2]
    escala = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    os.makedirs(saida, exist_ok=True)
    Tokenizer()
    cfg = json.load(open(MODELO + ".onnx.json", encoding="utf-8"))
    ids_de = {k: v[0] for k, v in cfg["phoneme_id_map"].items()}
    sr = cfg["audio"]["sample_rate"]
    inf = cfg["inference"]
    s = sessao(os.path.join(saida, ".piper-dur.onnx"))

    paragrafos = [p.strip() for p in open(roteiro, encoding="utf-8").read().split("\n\n") if p.strip()]
    pedacos, palavras, t0 = [], [], 0.0
    for pi, par in enumerate(paragrafos):
        frases = re.findall(r"[^.!?]+[.!?]+[\"”]?", par.replace("\n", " "))
        for fi, frase in enumerate(frases):
            exibidas = frase.split()
            # fonemas palavra a palavra: cada token sabe a que palavra pertence
            ids, dono = [ids_de["^"], ids_de["_"]], [-1, -1]
            for k, w in enumerate(exibidas):
                fal = re.sub(r"[\"“”]", "", FALA.get(w, w))
                fon = phonemizer.phonemize(fal, language="pt-br", backend="espeak", preserve_punctuation=True,
                                           with_stress=True, strip=True)
                fon = unicodedata.normalize("NFD", fon.strip())
                if k:
                    ids += [ids_de[" "], ids_de["_"]]
                    dono += [-1, -1]
                for ch in fon:
                    if ch in ids_de:
                        ids += [ids_de[ch], ids_de["_"]]
                        dono += [k, k]
            ids.append(ids_de["$"])
            dono.append(-1)
            audio, dur = s.run(None, {
                "input": np.array([ids], dtype=np.int64),
                "input_lengths": np.array([len(ids)], dtype=np.int64),
                "scales": np.array([inf["noise_scale"], escala, inf["noise_w"]], dtype=np.float32)})
            audio = audio.squeeze()
            fr = dur.squeeze()
            borda = np.concatenate([[0], np.cumsum(fr)]) * HOP / sr  # início de cada token, em s
            esc = len(audio) / sr / borda[-1]  # ajuste fino (o vocoder pode diferir 1 quadro)
            ini = {}
            fim = {}
            for j, k in enumerate(dono):
                if k < 0 or fr[j] == 0:
                    continue
                ini.setdefault(k, borda[j] * esc)
                fim[k] = borda[j + 1] * esc
            if len(ini) != len(exibidas):
                raise SystemExit(f"palavras sem fonemas em: {frase}")
            corte_ini = max(0.0, ini[0] - 0.03)
            corte_fim = min(len(audio) / sr, fim[len(exibidas) - 1] + 0.06)
            trecho = audio[int(corte_ini * sr):int(corte_fim * sr)].astype(np.float32)
            for k, w in enumerate(exibidas):
                palavras.append({"palavra": w, "inicio": round(t0 + ini[k] - corte_ini, 3),
                                 "fim": round(t0 + fim[k] - corte_ini, 3), "paragrafo": pi + 1})
            ultima = pi == len(paragrafos) - 1 and fi == len(frases) - 1
            pausa = 0.0 if ultima else FRASE
            pedacos += [trecho, np.zeros(int(pausa * sr), dtype=np.float32)]
            t0 += len(trecho) / sr + pausa
            print(f"{t0:7.2f}s  {frase.strip()[:70]}")
    sf.write(os.path.join(saida, "narracao_bruta.wav"), np.concatenate(pedacos), sr)
    json.dump(palavras, open(os.path.join(saida, "palavras_bruto.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"total {t0:.2f}s, {len(palavras)} palavras")


if __name__ == "__main__":
    main()
