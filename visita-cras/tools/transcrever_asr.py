# Uso: python3 -I tools/transcrever_asr.py <audio16k.wav> <saida.json> <pasta_modelos> '[[ini,fim],...]'
# Modelos (GitHub k2-fsa/sherpa-onnx, release asr-models): sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8 e sherpa-onnx-whisper-medium.
# Transcreve com Whisper medium (texto) + Parakeet v3 (tempos por token), em blocos entre silêncios.
import sys, json, wave, numpy as np, sherpa_onnx
M = sys.argv[3]
wav, out = sys.argv[1], sys.argv[2]
chunks = json.loads(sys.argv[4])  # [[ini,fim],...]
w = wave.open(wav); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768
pk = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{M}/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/encoder.int8.onnx",
    decoder=f"{M}/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/decoder.int8.onnx",
    joiner=f"{M}/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/joiner.int8.onnx",
    tokens=f"{M}/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/tokens.txt", model_type="nemo_transducer", num_threads=4)
wh = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{M}/sherpa-onnx-whisper-medium/medium-encoder.int8.onnx",
    decoder=f"{M}/sherpa-onnx-whisper-medium/medium-decoder.int8.onnx",
    tokens=f"{M}/sherpa-onnx-whisper-medium/medium-tokens.txt", language="pt", task="transcribe", num_threads=4)
res = []
for ini, fim in chunks:
    seg = a[int(ini*sr):int(fim*sr)]
    r = {}
    for nome, rec in (("pk", pk), ("wh", wh)):
        s = rec.create_stream(); s.accept_waveform(sr, seg); rec.decode_stream(s)
        r[nome] = s.result
    toks = [(t, round(ini+ts, 3)) for t, ts in zip(r["pk"].tokens, r["pk"].timestamps)]
    # junta tokens em palavras (sentencepiece: '▁' ou espaço inicial marca palavra nova)
    words = []
    for t, ts in toks:
        if t.startswith("▁") or t.startswith(" ") or not words:
            words.append([t.lstrip("▁ "), ts])
        else:
            words[-1][0] += t
    item = {"ini": ini, "fim": fim, "whisper": r["wh"].text.strip(), "parakeet": r["pk"].text.strip(), "words": words}
    res.append(item)
    print(f"[{ini:6.2f}-{fim:6.2f}] W: {item['whisper']}\n                 P: {item['parakeet']}", flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
