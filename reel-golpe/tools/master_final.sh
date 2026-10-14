#!/usr/bin/env bash
# Masterização final: leva o mix do render a −14 LUFS / TP ≤ −1,5 dBTP (loudnorm em duas passadas,
# modo linear = só ganho, sem compressão) e remonta o MP4 copiando o vídeo sem recodificar.
# Uso: tools/master_final.sh renders/reel_golpe_falso_advogado.mp4 entregas/reel_golpe_falso_advogado.mp4
set -euo pipefail
IN="$1"; OUT="$2"
J=$(ffmpeg -hide_banner -nostats -i "$IN" -map 0:a -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
v() { echo "$J" | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
ffmpeg -hide_banner -loglevel error -y -i "$IN" -map 0:v -map 0:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(v input_i):measured_TP=$(v input_tp):measured_LRA=$(v input_lra):measured_thresh=$(v input_thresh):offset=$(v target_offset):linear=true,aresample=48000" \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT"
ffmpeg -hide_banner -nostats -i "$OUT" -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|Peak:"
