# Reel "Golpe do falso advogado" — projeto HyperFrames

Composição única em `index.html` (HTML + SVG + GSAP), 1080×1920, 30 fps, 33,0 s. Roteiro e cenas: `STORYBOARD.md`.
Toda a tipografia é sincronizada palavra a palavra com a locução via `assets/sincronia.js` (gerado pela mixagem).

## Pipeline (ordem)
```bash
# 1. Locução (Kokoro pm_alex, pt-BR, 1,12x) e tempos de cada palavra
python3 -I tools/tts/gerar_voz.py pm_alex 1.12 assets/media/voz
python3 -I tools/tts/tempos.py   pm_alex 1.12 assets/media/voz
# 2. Texturas, trilha + mixagem (gera sincronia.js), masterização (-14 LUFS)
python3 -I tools/gerar_texturas.py assets/media
python3 -I tools/mixar_audio.py
bash tools/masterizar.sh
# 3. Verificar e renderizar
npx hyperframes@0.8.149 check
npx hyperframes@0.8.149 render --quality high --fps 30 --output renders/golpe_falso_advogado_reel.mp4
```

## Onde mexer
- **Texto da locução / pronúncia**: `FRASES` e `TROCAS` em `tools/tts/gerar_voz.py`.
- **Início de cada frase, cortes de cena, efeitos sonoros**: `INICIO`, `CORTES`, `SFX` em `tools/mixar_audio.py`.
  Se mudar `CORTES`, ajuste também `data-start`/`data-duration` das `<section>` e a lista `CENAS` no script do `index.html`.
- **Cenas**: blocos `CENA n` no HTML e `// ===== CENA n =====` no script.
- **Trocar por voz humana**: grave as 9 frases como `assets/media/voz/fNN.wav`, rode `tools/tts/tempos.py`
  (ou ajuste os tempos em `frases.json`) e repita o passo 2.
- **Cores**: variáveis `:root` (vermelho só em GOLPE, FALSO e NÃO PAGUE).
