# Reel "Promessa não é garantia" — projeto HyperFrames

Composição única em `index.html` (HTML + GSAP, 1080×1920, 30 fps, 90,8 s).

## Comandos
```bash
npx hyperframes preview --background   # editar no Studio
npx hyperframes check                  # lint + layout + contraste
npx hyperframes render --quality delivery --fps 30 --output renders/reel_eleicao_final.mp4
bash tools/qa_render.sh renders/reel_eleicao_final.mp4 qa/              # folha de contato, sincronia, loudness
python3 -I tools/qa_audio.py renders/reel_eleicao_final.mp4 assets/media/03_trilha_voz_master.wav
python3 -I tools/qa_cores.py renders/reel_eleicao_final.mp4
```

## Onde mexer
- **Legendas**: `assets/legendas_data.js` (gerado de `assets/media/05_cronograma_e_legendas.json`; tempos absolutos da trilha mestre).
- **Tempos das cenas**: bloco `// ===== CENA n =====` no script de `index.html`.
- **Áudio**: voz mestre a 100% (`#voz`); trilha `#musica` (volume 0,401 + carve 0,35 contra a voz);
  fader master `hf-audio-group#master` (0,767) leva o mix a −14 LUFS.
- **Trilha**: `tools/gerar_trilha.py` (síntese original, piano + cordas, determinística).
- **Logo provisório**: troque `assets/media/07_logo_provisorio.png` e `assets/media/icone_colunas_dourado.png`.
- **Capa**: `capa/index.html` (screenshot 1080×1920 com o Chrome headless).
