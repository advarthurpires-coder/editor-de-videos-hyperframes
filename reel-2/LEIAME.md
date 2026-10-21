# Reel 2 "Plantão HERO" — projeto HyperFrames + Three.js

Selfie de convite (576×1008 após a rotação, 30 fps, 25,7 s) transformada em reel 1080×1920, 30 fps, 27,3 s
(23,9 s de fala depois do corte dos silêncios + 3,4 s de cartela).

**Conceito: boletim ao vivo.** O convite vira um "plantão" de telejornal: TV ligando, selo **AO VIVO** piscando,
GC "URGENTE", letreiro correndo com data/horário/endereço, legendas em **tarja com marca-texto** (a linha inteira
aparece apagada e o marcador amarelo acompanha a palavra falada). Identidade diferente do reel 1 (que era noturno,
gótico, palavras soltas): aqui as fontes são Archivo Black (tarjas), Bebas Neue (destaques) e Space Mono (letreiro).

## Estrutura (tempo do reel)
| s | fala | o que acontece |
|---|---|---|
| 0,0 | Meus irmãos, tudo bem? | TV liga (linha que abre), AO VIVO, GC "URGENTE · 1º CULTO HERO · NESTE SÁBADO" |
| 0,9 | …para **te convidar** | o vídeo vira uma **janela** e ele salta para fora dela; "TE CONVIDAR" gigante atrás dele |
| 3,0 | que nesse **sábado, dia 24 de outubro, às 7 e meia** | janela estreita; **calendário 3D** arranca as folhas 20→23 e para no 24; **relógio 3D** gira até 7:30 |
| 7,8 | o nosso primeiro **culto HERO** da Igreja Batista **Lagoinha** | **tela dividida**: flyer no alto, ele embaixo; selo da Lagoinha na divisa |
| 11,0 | te convido a fazer **presente**… **venha** | janela + palavras atrás dele (eco empilhado) |
| 13,8 | traga **mais um** | um **clone** amarelo dele desliza para o lado + selo "+1" |
| 15,4 | que será **tremendo** | sismógrafo, letreiro com fenda RGB, tremor forte, estrondo |
| 16,5 | a **unção** de Deus | luz dourada e **gotas de ouro 3D** caindo |
| 17,4 | momento de **adoração** e **comunhão** com os irmãos | **carrossel 3D** com fotos reais dos cultos da Lagoinha Patrocínio orbitando atrás dele |
| 20,9 | **Venha!** | janela + "VENHA!" atrás dele |
| 22,3 | não fica **fora** dessa, **não** | ele fica preso numa janelinha, "FORA" do lado de fora; carimbo "NÃO FIQUE DE FORA!" |
| 23,9 | — | cartela: logo HERO, "VOCÊ ESTÁ CONVOCADO.", calendário e relógio 3D voltam, "TRAGA MAIS UM!", endereço, Lagoinha |

Logos e flyer: arquivos ORIGINAIS enviados. Fotos dos cultos: `fotos-igreja/lagoinha-deus-do-impossivel/saida/individuais`.

## Pipeline
```bash
# dependências: pip install sherpa-onnx soundfile opencv-python-headless mediapipe onnx ; apt install libegl1 ; ffmpeg ; Node 22
# 0) bruto (não versionado): src/original.mov ; src/voz16k.wav = ffmpeg -i src/original.mov -ac 1 -ar 16000
python3 -I tools/transcrever.py src/voz16k.wav tools/transcricao.json
python3 -I tools/conferir_cortes.py          # confere cada trecho de CORTES e dá os tempos por palavra
python3 -I tools/upscale.py src/original.mov realesr-general-x4v3.onnx src/original_sr.mp4   # ~60 min em CPU
python3 -I tools/segmentar.py src/original.mov selfie_multiclass.tflite
python3 -I tools/sincronia.py
python3 -I tools/montar_video.py              # -> base.mp4 + pessoa.webm + assets/linha_tempo.js
python3 -I tools/gerar_trilha.py assets/music/trilha.wav
python3 -I tools/gerar_sfx.py
python3 -I tools/mixar_audio.py && bash tools/masterizar.sh
npx hyperframes@0.8.149 check
npx hyperframes@0.8.149 render --quality high --fps 30 --output renders/plantao_hero_reel.mp4
```

## Onde mexer
- **Cortes**: `CORTES` em `tools/roteiro.py`. **Texto das tarjas**: `FALA` em `tools/sincronia.py` (`*palavra*` = destaque).
- **Efeitos sonoros**: `SFX` em `tools/sincronia.py`. **Zoom / punch-ins**: `ZOOM` e `PUNCH` em `tools/montar_video.py`.
- **Janelas e palavras atrás dele**: `MODO` e `KWS` em `index.html`. **Letreiro**: `frase` em `index.html`.
- **Calendário, relógio, gotas, carrossel**: `assets/cena3d.js`.
