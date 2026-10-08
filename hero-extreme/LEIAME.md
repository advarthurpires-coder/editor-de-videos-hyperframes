# Reel "2º HERO EXTREME" — projeto HyperFrames

Composição única em `index.html` (HTML + SVG + GSAP), 1080×1920, 30 fps, 59,0 s.
Motion design 100% vetorial/procedural: nenhuma foto de pessoa real; silhuetas ilustradas.
Logomarca: arquivo ORIGINAL `assets/brand/logo_hero_patrocinio.png` (apenas aparado, sem redesenho).

## Pipeline (ordem)
```bash
# 1. Locução (Kokoro pm_alex, pt-BR, 0,9x) — frases em assets/media/voz/ (já geradas)
# 2. Texturas, trilha, mixagem, masterização
python3 -I tools/gerar_texturas.py assets/media
python3 -I tools/gerar_trilha.py assets/music/trilha_hero_extreme.wav
python3 -I tools/mixar_audio.py assets/media/voz      # gera mix_pre.wav, voz_master.wav e assets/legendas_data.js
bash tools/masterizar.sh                               # -14 LUFS, limitador -1,5 dBTP -> mix_master.wav
# 3. Verificar e renderizar
npx hyperframes@0.8.140 check
npx hyperframes@0.8.140 render --quality high --fps 30 --output renders/hero_extreme_reel.mp4
```

## Onde mexer
- **Tempos da locução / blocos de legenda / destaques**: `INICIO`, `BLOCOS`, `DESTAQUE` em `tools/mixar_audio.py`.
- **Cenas**: blocos `// ===== CENA n =====` no script de `index.html` (cortes: 0 · 7,9 · 13,3 · 20,9 · 30,6 · 39,0 · 45,0 · 59,0).
- **Trilha**: seções A–G em `tools/gerar_trilha.py` (síntese original, sem samples de terceiros).
- **Pronúncia de "HERO EXTREME"**: forçada por fonemas ("xˈiɾow ekstɾˈim") em `gerar_voz.py`/`tempos.py` (`tools/tts/`).
- **Trocar a locução por voz humana**: grave as 10 frases, salve como `assets/media/voz/fNN.wav`,
  ajuste `frases.json` (durações/tempos de palavra) e rode os passos 2–3.
