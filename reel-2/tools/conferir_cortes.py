# Confere cada trecho de CORTES por reconhecimento de fala (Parakeet) e imprime os tempos por palavra relativos ao trecho.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sherpa_onnx, soundfile as sf
from roteiro import CORTES
a, sr = sf.read('src/voz16k.wav', dtype='float32')
p = "/home/user/modelos/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/"
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=p+"encoder.int8.onnx", decoder=p+"decoder.int8.onnx", joiner=p+"joiner.int8.onnx", tokens=p+"tokens.txt", model_type="nemo_transducer", num_threads=4)
out = []
for i, (x, y) in enumerate(CORTES):
    s = rec.create_stream(); s.accept_waveform(sr, a[int(x*sr):int(y*sr)]); rec.decode_stream(s)
    r = s.result; ws = []
    for tok, t in zip(r.tokens, r.timestamps):
        if tok.startswith(" ") or not ws: ws.append([tok.strip(), round(x + t, 2)])
        else: ws[-1][0] += tok
    out.append(ws)
    print(i + 1, " ".join(f"{w}@{t}" for w, t in ws))
json.dump(out, open("tools/palavras_trechos.json", "w"), ensure_ascii=False)
