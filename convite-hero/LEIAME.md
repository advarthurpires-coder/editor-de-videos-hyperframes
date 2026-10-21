# Reel "Convite HERO" — projeto HyperFrames

Convite gravado no celular (480×1068, 29 s) transformado em reel 1080×1920, 30 fps, 26,5 s.
Edição inspirada na referência enviada (`src/referencia_edicao.mp4`): legenda palavra a palavra grande no topo
com rastro de movimento, transições de colagem (papel rasgado + recorte em retícula), foto "colada" ao lado do flyer,
logo da igreja discreta na base e final com o flyer + cartela de perfil.

## Estrutura
| Reel (s) | Bloco |
|---|---|
| 0 – 9,5 | "Fala, meus irmãos…" → "…vocês, HOMENS!" (cortes secos, zoom alternado, punch-in + tremor em "HOMENS") · pino em "Patrocínio" |
| 9,5 – 11,1 | "na Batista **Lagoinha**": fundo desfocado + logo da igreja com brilho → colagem (folha amarela, dupla do flyer em retícula, faixas "Hero" e "24 DE OUTUBRO • 19H30") |
| 11,1 – 13,4 | "o nosso primeiro culto do **HERO**": carimbo da logo HERO com impacto, flash e tremor |
| 13,4 – 15,4 | "Eu quero fazer um convite muito especial…" |
| 15,4 – 19,4 | "Dia 24 de outubro, às 19h30": o vídeo vira foto colada sobre fundo amarelo, o flyer entra ao lado, círculo laranja desenhado na data, endereço |
| 19,4 – 20,1 | "VEM!" (punch-in, flash, tremor) |
| 20,1 – 23,7 | papel rasga e revela o flyer em tela cheia (zoom lento, brilho, selo "VEM PRO HERO!") — drop da trilha |
| 23,7 – 26,5 | cartela: HERO + pincelada, data, logo Lagoinha, busca digitando "@lagoinhapatrocinio" |

Logos e flyer: arquivos ORIGINAIS enviados (`assets/brand/*_original.png`, `assets/fotos/flyer_original.jpg`); versões aparadas sem redesenho.

## Pipeline
```bash
# 0) brutos (não versionados): src/convite_original.mp4 e src/referencia_edicao.mp4
# 1) upscale com IA (Real-ESRGAN realesr-general-x4v3 convertido para ONNX, sem torch) -> src/convite_sr.mp4 (1080x2404)
python3 -I tools/pth2onnx.py realesr-general-x4v3.pth realesr-general-x4v3.onnx
python3 -I tools/upscale.py src/convite_original.mp4 realesr-general-x4v3.onnx src/convite_sr.mp4 26.6   # ~40 min em CPU
# 2) rosto, vídeo-base, texturas, legendas/eventos, trilha, efeitos, mixagem
python3 -I tools/rastrear.py src/convite_original.mp4      # OpenCV Haar (opencv-python-headless < 5)
python3 -I tools/montar_video.py                           # -> assets/media/base.mp4 + tools/linha_tempo.json
python3 -I tools/gerar_texturas.py
python3 -I tools/sincronia.py                              # -> assets/sincronia.js + tools/eventos.json
python3 -I tools/gerar_trilha.py assets/music/trilha_convite_hero.wav
python3 -I tools/gerar_sfx.py
python3 -I tools/mixar_audio.py && bash tools/masterizar.sh # -14 LUFS, -1,5 dBTP -> assets/media/mix_master.wav
# 3) verificar e renderizar
npx hyperframes@0.8.149 check
npx hyperframes@0.8.149 render --quality high --fps 30 --output renders/convite_hero_reel.mp4
```
Transcrição: Parakeet TDT v3 (tempos por palavra) + Whisper medium (grafia), via sherpa-onnx; texto revisado à mão.

## Onde mexer
- **Cortes (pausas removidas)**: `CORTES` em `tools/roteiro.py` — tudo (legendas, efeitos, trilha) se reposiciona.
- **Texto/destaques das legendas**: `FALA` em `tools/sincronia.py` (`*palavra*` = amarelo, `/` fecha o bloco).
- **Efeitos sonoros**: `SFX` em `tools/sincronia.py`. **Zoom e punch-ins**: `ZOOM`/`PUNCH` em `tools/montar_video.py`.
- **Volume da trilha**: ganhos em `tools/mixar_audio.py` (−17 dB sob a voz, −11 dB nas brechas, cheia no flyer/cartela).
- **Trilha**: `tools/gerar_trilha.py` (síntese original, Ré maior, 100 bpm; drop preso ao flyer).
