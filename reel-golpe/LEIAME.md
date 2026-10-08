# Reel "Golpe do falso advogado" — projeto HyperFrames

Composição única em `index.html` (HTML + GSAP, 1080×1920, 30 fps, 110,3 s).

## Narração
A narração é **sintética**: voz Piper "cadu" (pt-BR, modelo do sherpa-onnx, dataset CC0) com
tratamento de locutor (~2 semitons mais grave, EQ e compressão), gerada a partir do roteiro exato
(`audio_trabalho/roteiro.txt`). Amostras das vozes avaliadas em `amostras_voz/`.
A versão anterior (Kokoro) continua reproduzível com `tools/gerar_narracao.py`.

Para trocar pela voz gravada do Arthur: substitua `audio_trabalho/narracao_bruta.wav`, refaça
`audio_trabalho/palavras_bruto.json` (transcrição por palavra) e rode a sequência abaixo a partir
do tratamento. `tools/remapear_tempos.py` reposiciona as cenas pelas palavras-âncora.

```bash
python3 tools/gerar_narracao_piper.py audio_trabalho/roteiro.txt audio_trabalho 1.0  # síntese + tempos por fonema
python3 tools/tratar_narracao.py audio_trabalho assets/media                        # corta silêncios, locutor, −14 LUFS
python3 tools/remapear_tempos.py <palavras_antigas.json> assets/media/palavras.json index.html
python3 tools/gerar_legendas.py                                                      # assets/legendas_data.js
python3 tools/gerar_trilha.py assets/music/trilha.wav                                # ajustar TOTAL/CALM_AT/VACUO
python3 tools/gerar_sfx.py assets/sfx
node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed musica --voice voz --strength 0.6
```

## Comandos
```bash
npx hyperframes preview --background   # editar no Studio
npx hyperframes check                  # lint + layout + contraste
npx hyperframes render --quality delivery --fps 30 --output renders/reel_golpe_falso_advogado.mp4
tools/master_final.sh renders/reel_golpe_falso_advogado.mp4 entregas/reel_golpe_falso_advogado.mp4  # −14 LUFS
bash tools/qa_render.sh entregas/reel_golpe_falso_advogado.mp4 qa/
python3 -I tools/qa_audio.py renders/reel_golpe_falso_advogado.mp4 assets/media/narracao_tratada.wav
```

## Onde mexer
- **Tempos das cenas**: blocos `// ===== CENA n =====` no script de `index.html` (tempos absolutos do JSON de palavras).
- **Legendas**: `assets/legendas_data.js` (gerado; palavras vermelhas/douradas definidas em `tools/gerar_legendas.py`).
- **Áudio**: voz (`#voz`); trilha `#musica` (carve contra a voz, `data-fx-carve`); efeitos no grupo `sfx`. O loudness final é feito por `tools/master_final.sh`.
- **Foto oficial**: `assets/media/foto_oficial.png` (recorte de baixa resolução do print enviado; troque pelo arquivo original).
- **Logo provisório**: `assets/media/07_logo_provisorio.png` e `assets/media/icone_colunas_dourado.png`.
- **Capa**: `capa/index.html` (screenshot 1080×1920 com o Chrome headless).
