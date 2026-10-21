"""Transcrição com tempos por token (Parakeet TDT v3, sherpa-onnx) + texto do Whisper medium para conferir grafia."""
import json, sys
import sherpa_onnx, soundfile as sf

M = "/home/user/modelos"
wav, saida = sys.argv[1], sys.argv[2]
audio, sr = sf.read(wav, dtype="float32")

p = M + "/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/"
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=p + "encoder.int8.onnx", decoder=p + "decoder.int8.onnx", joiner=p + "joiner.int8.onnx",
    tokens=p + "tokens.txt", model_type="nemo_transducer", num_threads=4)
s = rec.create_stream(); s.accept_waveform(sr, audio); rec.decode_stream(s)
r = s.result
# junta tokens em palavras (token iniciado por espaço "▁" abre palavra nova)
palavras = []
for tok, t in zip(r.tokens, r.timestamps):
    if tok.startswith(" ") or tok.startswith("▁") or not palavras:
        palavras.append({"w": tok.strip().replace("▁", ""), "t": round(t, 3)})
    else:
        palavras[-1]["w"] += tok
w = M + "/sherpa-onnx-whisper-medium/"
rw = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=w + "medium-encoder.int8.onnx", decoder=w + "medium-decoder.int8.onnx",
                                                tokens=w + "medium-tokens.txt", language="pt", task="transcribe", num_threads=4)
texto_w = []
for i in range(0, len(audio), sr * 28):
    sw = rw.create_stream(); sw.accept_waveform(sr, audio[i:i + sr * 28]); rw.decode_stream(sw); texto_w.append(sw.result.text)
json.dump({"parakeet": r.text, "whisper": " ".join(texto_w), "palavras": palavras}, open(saida, "w"), ensure_ascii=False, indent=1)
print(r.text); print("---"); print(" ".join(texto_w))
