"""Gera a locução do reel "Golpe do falso advogado" frase a frase (Kokoro, pt-br).
Uso: python3 -I tools/tts/gerar_voz.py <voz> <velocidade> <pasta_saida>
Grava fNN.wav + frases.json (texto, fonemas, duração)."""
import json, os, sys
import soundfile as sf
from kokoro_onnx import Kokoro

M = os.path.expanduser('~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx')
V = os.path.expanduser('~/.cache/hyperframes/tts/voices/voices-v1.0.bin')
FRASES = [
    "Alerta: criminosos estão usando o nome do seu advogado para aplicar golpes.",
    "A mensagem chega pelo WhatsApp, com a foto e o nome dele.",
    "Cita o número do seu processo e diz que você ganhou a causa.",
    "Mas, para liberar o dinheiro, pede um Pix urgente de taxa.",
    "É golpe! Os dados do processo são públicos, e o criminoso usa isso.",
    "Não pague nada. Ligue para o seu advogado, no número que você já conhece.",
    "Já pagou? Registre boletim de ocorrência e avise seu banco na hora.",
    "Fraude eletrônica é crime: pena de quatro a oito anos.",
    "Compartilhe e proteja quem você ama.",
]
# correções de pronúncia aplicadas sobre os fonemas do espeak (pt-br)
TROCAS = {
    "ˌalˈɛɾətæ": "alˈɛɾtæ",
    "ˌuɾəʒˈeɪŋtʃy": "uɾʒˈeɪŋtʃy",
    "wˈatz ˈap": "wˌɔtsˈapi",
    "kˌompaɾətʃˈiljj": "kˌõpaɾtʃˈiʎy",
}


def fonemas(k, texto):
    ph = k.tokenizer.phonemize(texto, 'pt-br')
    for a, b in TROCAS.items():
        ph = ph.replace(a, b)
    return ph


if __name__ == "__main__":
    voice, speed, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    k = Kokoro(M, V)
    os.makedirs(out, exist_ok=True)
    res = []
    for i, f in enumerate(FRASES):
        ph = fonemas(k, f)
        s, sr = k.create(ph, voice=voice, speed=speed, lang='pt-br', is_phonemes=True)
        sf.write(f"{out}/f{i+1:02d}.wav", s, sr)
        res.append({"i": i + 1, "texto": f, "fonemas": ph, "dur": round(len(s) / sr, 3), "sr": sr})
        print(i + 1, round(len(s) / sr, 2), ph)
    json.dump(res, open(f"{out}/frases.json", "w"), ensure_ascii=False, indent=1)
    print("total fala", round(sum(r['dur'] for r in res), 2))
