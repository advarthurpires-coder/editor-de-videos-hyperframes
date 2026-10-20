# Reel "Culto Hero" — projeto HyperFrames + Three.js

Composição em `index.html` (HTML + GSAP) com um mundo 3D em `assets/cena3d.js` (Three.js r169, local em
`assets/vendor/three/`), 1080×1920, 30 fps, 63,5 s. Conceito: **comunicado oficial de risco**. Tom sério do início
ao fim; o único "sorriso" é a última frase, com o acorde em Ré **maior** no carimbo "AVISADO".

Logomarcas e fotos: arquivos ORIGINAIS enviados (`assets/brand/*_original.png`, `assets/fotos/flyer_original.jpg`).
O "H" 3D e o adesivo 3D da logo HERO são extrudados a partir dos contornos da própria arte, sem redesenho.

## Cenas (cortes em `tools/roteiro.py` → `CENAS`)
| s | cena | 3D |
|---|---|---|
| 0,0 | Gancho: "AVISO" | fitas zebradas, placa "!" |
| 3,85 | Motivo 1 | numeral gótico 1, carrossel (capacete, maleta, volante, capelo, óculos), 7 peões |
| 15,1 | "Isso incomoda." | glitch (trilha corta) |
| 17,0 | Motivo 2 | numeral 2, casa com janelas acendendo, "?" |
| 24,4 | Motivo 3 | numeral 3, giroflex, celular tocando, cadeado, placa SAÍDA apagando |
| 38,6 | Virada (sem cor) | objetos congelados, placa "NÃO VÁ" |
| 45,4 | O risco (a cor volta) | medalhão "H" girando |
| 48,0 | Convite (drop) | logo HERO 3D, calendário, relógio 19h30, pin |
| 56,35 | Final (no seco) | dupla do flyer, carimbo 3D → "AVISADO." e cartão final |
| 62,5 | Loop | as fitas voltam e fecham igual ao 1º quadro |

## Pipeline
```bash
# dependências: pip install kokoro-onnx soundfile opencv-python-headless ; ffmpeg ; Node 22
python3 -I tools/preparar_assets.py                      # recorte da dupla, contornos do H e da logo
node tools/gerar_fontes3d.mjs <node_modules com opentype.js e @fontsource/{unifrakturcook,anton}>
python3 -I tools/tts/gerar_voz.py pm_alex 0.9 assets/media/voz   # locução Kokoro (20 frases)
python3 -I tools/montar_voz.py assets/media/voz          # -> assets/media/voz_master.wav
python3 -I tools/legendas.py assets/media/voz            # tempos de palavra -> tempos_data.js / legendas_data.js
python3 -I tools/gerar_trilha.py assets/music/trilha_culto_hero.wav
python3 -I tools/mixar_audio.py && bash tools/masterizar.sh   # -14 LUFS -> mix_master.wav
npx hyperframes@0.8.140 check
npx hyperframes@0.8.140 render --quality high --fps 30 --output renders/culto_hero_reel.mp4
```

## Trocar a locução pela voz do pastor (recomendado)
Grave as 20 frases de `tools/tts/gerar_voz.py` (uma por arquivo, `assets/media/voz/fNN.wav`), com tom de alerta,
quase sem sorrir, e o **meio sorriso só em "avisei"**. Rode `legendas.py` (ele mede pausas e energia do áudio real),
depois `montar_voz.py`, `mixar_audio.py`, `masterizar.sh` e o render. Se alguma frase ficar mais longa, ajuste
`INICIO` em `tools/roteiro.py`: legendas, efeitos sonoros e animações 3D presas às palavras se reposicionam sozinhos.
