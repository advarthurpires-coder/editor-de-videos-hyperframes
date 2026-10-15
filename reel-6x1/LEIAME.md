# Reel "Fim da escala 6x1" — Arthur Pires Nascimento Advocacia

Motion design 3D (Remotion + @remotion/three / three.js) sobre a narração versão B (87,95 s).
Conceito "As sete colunas": um único mundo 3D com 7 colunas de mármore (SEG–DOM); 6x1 → 5x2 → símbolo do escritório.

## Estrutura
- `src/World.tsx` — mundo 3D (colunas caneladas, piso, trilho/linha do tempo, placa + carimbo, partículas, frontão final)
- `src/HeroProps.tsx` — objetos 3D de cena presos à câmera (triângulo, ampulheta, carimbo, holerite + cadeado, calendário, selo ≤40h, check, emblemas, lojinha)
- `src/camera.ts` — plano-sequência (keyframes) + projeção 3D→tela para rótulos
- `src/Scenes.tsx` — tipografia e cartões em CSS 3D, cena a cena
- `src/timeline.ts` — âncoras de tempo lidas de `src/data/words.json` (fonte da verdade)
- `src/Captions.tsx` + `src/captionBlocks.ts` — legendas karaokê (mesmos blocos do .srt)
- `tools/sfx.py` — efeitos e cama sonora sintetizados; `tools/finalize.sh` — monta as entregas

## Render
```bash
npm i
npx remotion render src/index.ts Reel out/base.mp4 --props='{"captions":false,"audio":false}' --gl=swangle --crf=12
npx remotion render src/index.ts Legendas out/legendas.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png
python3 tools/sfx.py   # depois mixar (ver tools/finalize.sh)
node --experimental-strip-types tools/srt.mts
./tools/finalize.sh
```
No ambiente remoto, acrescente `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`.
