"""Tempo de fim de cada palavra: sintetiza prefixos da frase e mede a duração
(Kokoro é não autorregressivo; o prefixo aproxima a fronteira real). Normaliza pela frase inteira."""
import json, os, sys
from kokoro_onnx import Kokoro
k = Kokoro(os.path.expanduser('~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx'), os.path.expanduser('~/.cache/hyperframes/tts/voices/voices-v1.0.bin'))
voice, speed, d = sys.argv[1], float(sys.argv[2]), sys.argv[3]
fr = json.load(open(f"{d}/frases.json"))
HERO = "xˈiɾow ekstɾˈim"
for f in fr:
    words = f["texto"].split()
    ends = []
    for n in range(1, len(words)+1):
        pre = " ".join(words[:n])
        ph = k.tokenizer.phonemize(pre, 'pt-br').replace("ˈeɾw ˌestrˈemy", HERO).replace("ˈeɾw", "xˈiɾow")
        s, sr = k.create(ph, voice=voice, speed=speed, lang='pt-br', is_phonemes=True)
        ends.append(len(s)/sr)
    # monotônico + escala para a duração real
    for i in range(1, len(ends)): ends[i] = max(ends[i], ends[i-1]+0.05)
    sc = f["dur"]/ends[-1]
    ends = [round(e*sc, 3) for e in ends]
    f["palavras"] = [{"w": w, "fim": e} for w, e in zip(words, ends)]
    print(f["i"], [(w, e) for w, e in zip(words, ends)])
json.dump(fr, open(f"{d}/frases.json", "w"), ensure_ascii=False, indent=1)
