# Reel "A visita do CRAS vai virar regra" — projeto HyperFrames

Reação + explicação: 1080×1920, 30 fps, 100,7 s. Composição em `index.html` (HTML + SVG + GSAP) sobre um
vídeo-base montado em Python (`assets/media/base.mp4`) e um áudio único já mixado e masterizado (`assets/media/mix_master.wav`).

## Estrutura do reel
| Tempo | Bloco |
|---|---|
| 0 – 14,3 s | Tela dividida: TikTok (@peraimash) em cima, reação do Arthur embaixo; título fixo "A partir de **JULHO DE 2027**, isso vai ser de verdade 👀"; falas do TikTok legendadas |
| 14,3 – 97,5 s | Corte seco para o Arthur em tela cheia; pausas removidas (39 trechos), zoom/punch-in alternado a cada corte, legendas dinâmicas palavra a palavra, elementos 3D/motion |
| 97,5 – 100,7 s | Cartela final (emblema, nome, "Compartilhe com quem recebe Bolsa Família ou BPC/LOAS", @) |

Elementos gráficos (todos sincronizados com a fala; os marcados com ✋ seguem a mão rastreada):
calendário 3D que vira de 2026 para **2027** · casa "mora só você?" ✋ · cartões Bolsa Família / BPC-LOAS ·
lupa do pente-fino · vapor e "cafezinho" saindo da xícara real · miniatura do TikTok "como no vídeo" ✋ ·
"2" dourado no gesto em V ✋ · lista "O que o CRAS vai conferir" com ✓ · alerta vermelho em "tome muito cuidado" ·
chip "vale a partir de JUL/2027" · INSS / Justiça (escudo e balança em 3D) · avião de papel em "encaminhe" ✋.

## Pipeline
Brutos (não versionados): `src/tiktok.mp4` (recorte 0–21,8 s) e `src/arthur.mp4` (gravação do WhatsApp, 108 s).
```bash
python3 -I tools/transcrever_asr.py audio16k.wav tools/asr_arthur.json <modelos> "<blocos>"  # (feito uma vez) -> tools/asr_arthur.json, tools/asr_tiktok.json
python3 -I tools/rastrear.py src/arthur.mp4 tools/rastreio.json <modelos>   # rosto e mãos (MediaPipe)
python3 -I tools/cortes.py src/arthur.mp4      # trechos com fala -> tools/cortes.json
python3 -I tools/montar_video.py               # vídeo-base + tools/linha_tempo.json (~30 min; "mapa" = só o mapa)
python3 -I tools/sincronia.py                  # legendas e eventos -> assets/sincronia.js, tools/eventos.json
python3 -I tools/mixar_audio.py && bash tools/masterizar.sh    # voz + TikTok + trilha + efeitos -> -14 LUFS
npx hyperframes@0.8.149 check
npx hyperframes@0.8.149 render --quality high --fps 30 --output renders/visita_cras_reel.mp4
```
Transcrição: Parakeet TDT v3 (tempos por palavra) + Whisper medium (grafia), via sherpa-onnx; texto revisado à mão em `tools/texto.py`.

## Onde mexer
- **Texto e cores das legendas**: `tools/texto.py` (`*palavra*` dourado, `!palavra!` vermelho, `palavra|` quebra). Rode `tools/sincronia.py`.
- **Momento de cada elemento gráfico / efeitos sonoros**: `EV_SRC` e `SFX` em `tools/sincronia.py` (tempos da gravação original).
- **Zoom por trecho e punch-ins**: `FIXO` e `PUNCH` em `tools/montar_video.py` (exige re-renderizar o vídeo-base).
- **Volume da trilha**: ganho sob a voz/pausas em `tools/mixar_audio.py` (hoje −15/−9 dB; trilha ~12 dB abaixo da voz).
- **Trilha**: `tools/gerar_trilha.py` (lo-fi original por síntese, 86 BPM, determinística).
