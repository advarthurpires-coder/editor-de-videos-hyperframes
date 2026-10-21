#!/usr/bin/env bash
# Leva o mix a -14 LUFS (padrão de redes) com limitador em -1,5 dBTP (duas passadas: o limitador come ~1 dB).
# Uso: bash tools/masterizar.sh   (lê assets/media/mix_pre.wav, grava assets/media/mix_master.wav)
set -euo pipefail
IN=assets/media/mix_pre.wav; OUT=assets/media/mix_master.wav
lufs() { ffmpeg -hide_banner -nostats -i "$1" -af ebur128 -f null - 2>&1 | grep -A3 Summary | grep -oE "I: +-?[0-9.]+" | grep -oE -- "-?[0-9.]+"; }
G=$(python3 -c "print(round(-14.0 - ($(lufs "$IN")), 2))")
for pass in 1 2 3; do
  ffmpeg -hide_banner -loglevel error -y -i "$IN" -af "volume=${G}dB,alimiter=limit=0.79:attack=3:release=60:level=disabled" -ar 48000 -c:a pcm_s16le "$OUT"
  O=$(lufs "$OUT"); echo "passada $pass: ganho ${G} dB -> $O LUFS"
  G=$(python3 -c "print(round($G + (-14.0 - ($O)), 2))")
done
ffmpeg -hide_banner -nostats -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -A20 Summary | grep -E "I:|Peak:"
