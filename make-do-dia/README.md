# Make do dia — reel de automaquiagem (9:16)

Vídeo bruto de automaquiagem (câmera fixa, sem narração) transformado em reel
"tutorial rápido de make" com jump cuts sincronizados à batida.

**Entregas:** `entregas/make_do_dia/`
- `make_do_dia_reels_1080x1920.mp4`: 48,5 s, 1080×1920, 30 fps, H.264, AAC 192 kbps, −14 LUFS
- `make_do_dia_whatsapp_leve.mp4`: 720×1280, versão leve para envio
- `folha_de_contato.png`: os 46 cortes com tempo, duração, enquadramento e etapa

## Como foi montado
- **Fontes:** gravação principal (9 min 39 s) e um segundo clipe de 39 s (gloss, fixador e revelação final), ambos verticais 464×832 a 60 fps.
- **Estrutura:** gancho (1,5 s do resultado final, depois corte seco para o rosto sem make), passo a passo
  cronológico (preparo → base → corretivo → contorno → fixador → pó → blush → iluminador →
  sobrancelha → sombra → delineado → máscara → lápis/batom/gloss) e final de 6 s com tomadas longas.
- **Ritmo:** cortes de 1,0 s (2 batidas a 120 BPM). Gancho e final com 1,5 a 2,0 s. Velocidade real, sem aceleração.
- **Enquadramento:** rosto rastreado por quadro (YuNet/OpenCV, suavizado). `w` = base do peito para cima,
  `m` = +25%, `eye`/`lip` = close de olhos ou boca, ancorados nos pontos dos olhos e da boca.
- **Cor:** gama levemente aberta, +4% de saturação, laranja da madeira neutralizado, glow suave nos realces
  e nitidez leve para compensar o upscale.
- **Áudio:** áudio original removido. Trilha original sintetizada (pop/house 120 BPM, Lá maior),
  que fecha com acorde final junto com o vídeo.
- **Título:** "Make do dia ✨💋" (Inter SemiBold, branco, centralizado no topo) de 0 a 2 s, com fade.

## Re-renderizar
Coloque os vídeos brutos em `src/A.mp4` (gravação principal) e `src/B.mp4` (clipe final) e o modelo
`face_detection_yunet_2023mar.onnx` (opencv_zoo) como `yunet.onnx` na pasta de trabalho. A estrutura de
pastas que os scripts esperam é `<trabalho>/code/*.py` e `<trabalho>/src/`. Os brutos não são versionados.
```bash
pip install opencv-python-headless pillow numpy
python3 code/track.py src/A.mp4 trackA.npy yunet.onnx
python3 code/track.py src/B.mp4 trackB.npy yunet.onnx
python3 code/music.py trilha.wav 48.5          # duração = soma das batidas da EDL × 0,5 s
python3 code/render.py video_full.mp4 1.0       # 0.5 = prévia em meia resolução
python3 code/title.py
# mux: overlay do título (0–2 s) + trilha com volume −3,6 dB e limitador (ver histórico do commit)
```
Para mudar cortes, edite `code/edl.py` (fonte, início, batidas, enquadramento, etapa).
