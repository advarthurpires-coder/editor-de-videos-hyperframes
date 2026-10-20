"""Gera a locução do reel "Culto Hero" frase a frase (Kokoro pm_alex, pt-br) e o tempo de cada palavra.
"Hero" é forçado por fonemas para a leitura usada na igreja ("Rírou").
O fim de cada palavra vem da síntese de prefixos da frase (Kokoro é não autorregressivo), escalada
para a duração real da frase.
Uso: python3 -I tools/tts/gerar_voz.py pm_alex 0.9 assets/media/voz
"""
import json
import os
import sys

import soundfile as sf
from kokoro_onnx import Kokoro

M = os.path.expanduser("~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx")
V = os.path.expanduser("~/.cache/hyperframes/tts/voices/voices-v1.0.bin")
k = Kokoro(M, V)
voice, speed, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
os.makedirs(out, exist_ok=True)

# (texto exibido/legendado, texto falado quando difere)
FRASES = [
    ("Três motivos pra você não ir ao Culto Hero.", None),
    ("Primeiro: lá vai ter homem de tudo quanto é tipo.", None),
    ("Peão, empresário, motorista, estudante, aposentado…", "Peão, empresário, motorista, estudante, aposentado."),
    ("e você vai descobrir que não é tão diferente deles assim.", None),
    ("Isso incomoda.", None),
    ("Segundo: você vai sair de lá com vontade de mudar umas coisas em casa.", None),
    ("E sua esposa vai estranhar.", None),
    ("Terceiro, e esse é o mais perigoso:", "Terceiro, e esse é o mais perigoso."),
    ("você pode acabar fazendo amigo.", None),
    ("Amigo de verdade.", None),
    ("Daqueles que te ligam pra saber como você tá.", None),
    ("Aí já era.", None),
    ("Não tem mais como sumir.", None),
    ("Então, se você quer continuar exatamente do jeito que tá…", "Então, se você quer continuar exatamente do jeito que tá."),
    ("não vai.", None),
    ("Agora, se você topa o risco…", "Agora, se você topa o risco."),
    ("Culto Hero.", None),
    ("Sábado, dia 24, às sete e meia.", "Sábado, dia vinte e quatro, às sete e meia."),
    ("Avenida Faria Pereira, 3083.", "Avenida Faria Pereira, três mil e oitenta e três."),
    ("Depois não diz que eu não avisei.", None),
]
HERO = "xˈiɾow"


def fon(txt):
    return k.tokenizer.phonemize(txt, "pt-br").replace("ˈeɾʊ", HERO)


def sint(txt):
    s, sr = k.create(fon(txt), voice=voice, speed=speed, lang="pt-br", is_phonemes=True)
    return s, sr


res = []
for i, (vis, fal) in enumerate(FRASES):
    fal = fal or vis
    s, sr = sint(fal)
    sf.write(f"{out}/f{i + 1:02d}.wav", s, sr)
    dur = len(s) / sr
    pal_f = fal.split()
    ends = []
    for n in range(1, len(pal_f) + 1):
        p, _ = sint(" ".join(pal_f[:n]))
        ends.append(len(p) / sr)
    for j in range(1, len(ends)):
        ends[j] = max(ends[j], ends[j - 1] + 0.05)
    sc = dur / ends[-1]
    ends = [round(e * sc, 3) for e in ends]
    # palavras exibidas: quando o texto falado expande números, os números exibidos herdam o fim do grupo falado
    pal_v = vis.split()
    if len(pal_v) == len(pal_f):
        fins = ends
    else:
        fins = []
        mapa = {"24,": ["vinte", "e", "quatro,"], "3083.": ["três", "mil", "e", "oitenta", "e", "três."]}
        j = 0
        for w in pal_v:
            j += len(mapa.get(w, [w]))
            fins.append(ends[j - 1])
        assert j == len(pal_f), (vis, fal)
    res.append({"i": i + 1, "texto": vis, "falado": fal, "dur": round(dur, 3), "sr": sr,
                "palavras": [{"w": w, "fim": e} for w, e in zip(pal_v, fins)]})
    print(f"{i + 1:2d} {dur:5.2f}s  {vis}")
json.dump(res, open(f"{out}/frases.json", "w"), ensure_ascii=False, indent=1)
print("total fala", round(sum(r["dur"] for r in res), 2))
