#!/usr/bin/env bash
# QA do render: folha de contato (1 quadro a cada 3 s), tiras de sincronia de legenda,
# loudness/true peak e duração.
# Uso: tools/qa_render.sh renders/reel_golpe_falso_advogado.mp4 <pasta_saida>
set -euo pipefail
IN="$1"; OUT="$2"; mkdir -p "$OUT"

echo "== streams"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels:format=duration -of compact "$IN"

echo "== loudness (mix final)"
ffmpeg -hide_banner -nostats -i "$IN" -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -A20 "Summary" | grep -E "I:|Peak:|LRA:"

echo "== folha de contato (1 quadro a cada 3 s, com tempo)"
ffmpeg -hide_banner -loglevel error -y -i "$IN" \
  -vf "select='not(mod(n\,90))',setpts=N/TB,scale=270:480,drawtext=text='%{eif\:n*3\:d}s':x=8:y=8:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=6,tile=8x5:padding=6:color=0x0E1A2E" \
  -fps_mode passthrough -frames:v 1 "$OUT/folha_de_contato.png"

echo "== tiras de sincronia (antes/depois do início de cada frase testada)"
i=0
for t in 10.68 19.65 32.385 42.095 52.54 63.425 84.535 94.875 104.7; do
  for d in -0.10 0.05 0.20; do
    ts=$(python3 -c "print(round($t+$d,3))")
    ffmpeg -hide_banner -loglevel error -y -ss "$ts" -i "$IN" -frames:v 1 \
      -vf "crop=1080:200:0:1245,scale=540:100,drawtext=text='t=$ts':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6" \
      "$OUT/sync_$(printf %02d $i).png"
    i=$((i+1))
  done
done
ffmpeg -hide_banner -loglevel error -y -pattern_type glob -i "$OUT/sync_*.png" -vf "tile=3x9:padding=4" -frames:v 1 "$OUT/tira_sincronia.png"
rm -f "$OUT"/sync_*.png
echo "ok -> $OUT"
