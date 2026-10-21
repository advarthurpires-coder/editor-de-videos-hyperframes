# Reel "Convite HERO — Deus tem um encontro com você" — projeto HyperFrames + Three.js

Convite gravado no celular, na rua à noite (464×832, 60 fps, 39,9 s), transformado em reel 1080×1920, 30 fps, 37,4 s
(33,8 s de fala depois do corte dos silêncios + 3,6 s de cartela).

**Conceito: o ingresso.** O "convite" da fala vira um ingresso 3D de papel-cartão que costura o vídeo inteiro:
nasce na palavra "convite", gira em volta da cabeça (passa por trás dele e volta pela frente), recebe o carimbo
"24 OUT · SÁBADO · 19H30" no "dia 24", conta "ADMITE 1 → 2 → 3" em leque no "traga um amigo / traga um parente",
sobe girando e some no "adorar", volta pelo verso "CONVIDADO ESPECIAL · NOME: VOCÊ · ADMITE VOCÊ +2" e pousa na cartela
("SEU CONVITE ESTÁ FEITO.").

## Estrutura (tempo do reel)
| s | fala | o que acontece |
|---|---|---|
| 0,0 | Meus irmãos, a paz do Senhor Jesus… | abertura em cortina, "IRMÃOS" e "Jesus" gigantes atrás dele, logo Lagoinha |
| 4,2 | Estou aqui para te fazer um convite… | chicote; "CONVITE" letra a letra; ingresso 3D entra por trás da cabeça |
| 6,2 | …muito especial | "Especial" gótico; brilho dourado e faíscas no ingresso |
| 7,8 | Deus tem um encontro… no dia 24 | "ENCONTRO"; "2" e "4" partidos em volta da cabeça; carimbo + tremor + flash |
| 10,5 | na igreja Batista Lagoinha | logo da Lagoinha revelada atrás dele |
| 12,4 | Que você possa vir, traga um amigo, traga um parente | contador ADMITE 1→2→3, ingressos abrem em leque |
| 16,0 | e venha aqui adorar ao Senhor | ingressos sobem girando e somem por trás; "Adorar" |
| 18,0 | …Jesus, a palavra, o Todo-Poderoso, o Grandão da Galileia | raios no "Todo-Poderoso"; mar de partículas douradas (Galileia) sobe atrás dele |
| 24,4 | …falar neste dia grandemente com você | "GRANDEMENTE" vazado que se preenche; anéis de onda 3D saindo de trás da cabeça |
| 27,2 | Você é o nosso convidado especial | ingresso volta pelo verso VIP "CONVIDADO ESPECIAL · VOCÊ" |
| 29,1 | Deus abençoe você, esteja com a gente nessa noite | **tela dividida**: ele à esquerda, flyer do evento à direita + data e endereço |
| 32,3 | Amém? Vamos junto! | "Amém" gótico; o ingresso sobe para a cartela |
| 33,8 | — | cartela: logo HERO carimbada, ingresso 3D, data, endereço, logo Lagoinha |

Legendas: palavra a palavra (Barlow Condensed); termos-chave em amarelo, maiores e com outra fonte
(Anton ou a gótica UnifrakturCook, a mesma família do "H" do HERO) + a versão gigante **atrás da pessoa**
(recorte com alfa, `assets/media/pessoa.webm`, sobre o vídeo-base).
Logos e flyer: arquivos ORIGINAIS enviados (`assets/brand/*_original.png`, `assets/fotos/flyer_original.png`).

## Pipeline
```bash
# dependências: pip install sherpa-onnx soundfile opencv-python-headless mediapipe onnx ; apt install libegl1 ; ffmpeg ; Node 22
# modelos (fora do repositório): Parakeet TDT v3 + Whisper medium (sherpa-onnx), selfie_multiclass_256x256 (MediaPipe),
#   realesr-general-x4v3.pth (Real-ESRGAN, convertido com tools/pth2onnx.py)
# 0) bruto (não versionado): src/original.mp4 ; src/voz16k.wav = ffmpeg -i src/original.mp4 -ac 1 -ar 16000
python3 -I tools/transcrever.py src/voz16k.wav tools/transcricao.json        # tempos por palavra
python3 -I tools/upscale.py src/original.mp4 realesr-general-x4v3.onnx src/original_sr.mp4   # ~70 min em CPU
python3 -I tools/segmentar.py src/original.mp4 selfie_multiclass.tflite    # máscara da pessoa + rastreio da cabeça
python3 -I tools/sincronia.py                 # legendas/palavras-chave/eventos -> assets/sincronia.js, tools/eventos.json
python3 -I tools/montar_video.py              # -> assets/media/base.mp4 + assets/media/pessoa.webm + assets/linha_tempo.js
python3 -I tools/gerar_trilha.py assets/music/trilha.wav
python3 -I tools/gerar_sfx.py
python3 -I tools/mixar_audio.py && bash tools/masterizar.sh   # -14 LUFS -> assets/media/mix_master.wav
npx hyperframes@0.8.149 check
npx hyperframes@0.8.149 render --quality high --fps 30 --output renders/convite_hero_reel.mp4
```

## Onde mexer
- **Cortes (silêncios removidos)**: `CORTES` em `tools/roteiro.py` — legendas, 3D, efeitos e trilha se reposicionam.
- **Texto das legendas / termos-chave**: `FALA` (`*palavra*` = termo-chave, `/` fecha o bloco) e `CHAVE` (fonte da palavra
  gigante: `a` Anton, `g` gótica, `n` número partido, `o` vazado, `logo`, `none`) em `tools/sincronia.py`.
- **Efeitos sonoros**: `SFX` em `tools/sincronia.py`. **Zoom / punch-ins**: `ZOOM` e `PUNCH` em `tools/montar_video.py`.
- **Ingresso 3D, mar, anéis**: `assets/cena3d.js` (arte do ingresso desenhada em canvas: `frente()`, `verso()`, `carimbo()`).
- **Volume da trilha**: `tools/mixar_audio.py` (−18 dB sob a voz, −12 dB nas brechas, −2 dB na cartela).
- **Trilha**: `tools/gerar_trilha.py` (síntese original, Ré maior, ~100 bpm; golpes presos ao "Todo-Poderoso" e à cartela).
