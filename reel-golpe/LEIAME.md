# Reel "Golpe do falso advogado" — projeto HyperFrames

Composição única em `index.html` (HTML + GSAP, 1080×1920, 30 fps, 111,8 s).

## Narração
A narração é **sintética** (Kokoro-82M, voz `pm_alex`, pt-BR, via `hyperframes tts`), gerada a
partir do roteiro exato (`audio_trabalho/roteiro.txt`). Para trocar pela voz gravada do Arthur:
substitua `assets/media/narracao_tratada.wav`, refaça `assets/media/palavras.json`
(transcrição por palavra) e rode `tools/gerar_legendas.py`; os tempos das cenas no script de
`index.html` seguem as frases-âncora e precisam ser conferidos.

```bash
python3 tools/gerar_narracao.py audio_trabalho/roteiro.txt audio_trabalho 1.08   # síntese + tempos por fonema
python3 tools/tratar_narracao.py audio_trabalho assets/media                     # −14 LUFS + palavras.json
python3 tools/gerar_legendas.py                                                   # assets/legendas_data.js
python3 tools/gerar_trilha.py assets/music/trilha.wav                             # trilha original (síntese)
python3 tools/gerar_sfx.py assets/sfx                                             # efeitos originais (síntese)
```

## Comandos
```bash
npx hyperframes preview --background   # editar no Studio
npx hyperframes check                  # lint + layout + contraste
npx hyperframes render --quality delivery --fps 30 --output renders/reel_golpe_falso_advogado.mp4
bash tools/qa_render.sh renders/reel_golpe_falso_advogado.mp4 qa/
python3 -I tools/qa_audio.py renders/reel_golpe_falso_advogado.mp4 assets/media/narracao_tratada.wav
```

## Onde mexer
- **Tempos das cenas**: blocos `// ===== CENA n =====` no script de `index.html` (tempos absolutos do JSON de palavras).
- **Legendas**: `assets/legendas_data.js` (gerado; palavras vermelhas/douradas definidas em `tools/gerar_legendas.py`).
- **Áudio**: voz a 100% (`#voz`); trilha `#musica` (volume 0,2 + carve contra a voz, `data-fx-carve`); efeitos no grupo `sfx`.
- **Foto oficial**: `assets/media/foto_oficial.png` (recorte de baixa resolução do print enviado; troque pelo arquivo original).
- **Logo provisório**: `assets/media/07_logo_provisorio.png` e `assets/media/icone_colunas_dourado.png`.
- **Capa**: `capa/index.html` (screenshot 1080×1920 com o Chrome headless).
