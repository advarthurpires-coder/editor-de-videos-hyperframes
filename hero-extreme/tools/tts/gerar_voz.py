"""Gera a locução do 2º HERO EXTREME frase a frase (Kokoro pm_alex, pt-br).
HERO EXTREME é forçado por fonemas para leitura natural ("Rírou Ekstrím")."""
import json, sys, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

M = os.path.expanduser('~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx')
V = os.path.expanduser('~/.cache/hyperframes/tts/voices/voices-v1.0.bin')
k = Kokoro(M, V)
voice = sys.argv[1]; speed = float(sys.argv[2]); out = sys.argv[3]
os.makedirs(out, exist_ok=True)
FRASES = [
 "E se eu te dissesse que alguns dos melhores encontros com Deus acontecem fora das quatro paredes?",
 "Vem aí o segundo HERO EXTREME, da Lagoinha Patrocínio!",
 "Serão dias de comunhão, pesca, churrasco, boas conversas, novas amizades e momentos inesquecíveis.",
 "Mas o principal vai muito além disso.",
 "Teremos louvor, adoração, Palavra e momentos especiais na presença de Deus.",
 "Um ambiente leve, para fortalecer a fé, compartilhar o amor de Jesus e lembrar que ninguém precisa caminhar sozinho.",
 "Então, convide um amigo e venha viver essa experiência com a gente!",
 "Dias vinte, vinte e um e vinte e dois de novembro.",
 "Segundo HERO EXTREME. Lagoinha Patrocínio!",
 "Muito além das quatro paredes!",
]
HERO = "xˈiɾow ekstɾˈim"
res = []
for i, f in enumerate(FRASES):
    ph = k.tokenizer.phonemize(f, 'pt-br')
    ph = ph.replace("ˈeɾw ˌestrˈemy", HERO)
    s, sr = k.create(ph, voice=voice, speed=speed, lang='pt-br', is_phonemes=True)
    p = f"{out}/f{i+1:02d}.wav"; sf.write(p, s, sr)
    res.append({"i": i+1, "texto": f, "fonemas": ph, "dur": round(len(s)/sr, 3), "sr": sr})
    print(i+1, round(len(s)/sr,2), ph)
json.dump(res, open(f"{out}/frases.json", "w"), ensure_ascii=False, indent=1)
print("total fala", round(sum(r['dur'] for r in res),2))
