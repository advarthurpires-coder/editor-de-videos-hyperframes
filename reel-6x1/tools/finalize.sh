#!/bin/bash
# Monta as entregas a partir de out/base.mp4 (render 3D sem legenda), out/legendas.mov e das mixagens.
set -e
cd "$(dirname "$0")/.."
V="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -r 30"
A="-c:a aac -b:a 192k -ar 48000"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/base.mp4)
ffmpeg -v error -y -i out/base.mp4 -i out/mix_main_lim.wav -map 0:v -map 1:a $V $A -t "$DUR" -movflags +faststart saida/reel_6x1_sem_legenda.mp4
ffmpeg -v error -y -i out/base.mp4 -i out/legendas.mov -i out/mix_main_lim.wav -filter_complex "[0:v][1:v]overlay=0:0:format=auto[v]" -map "[v]" -map 2:a $V $A -t "$DUR" -movflags +faststart saida/reel_6x1_final.mp4
ffmpeg -v error -y -i saida/reel_6x1_final.mp4 -i out/mix_trilha_lim.wav -map 0:v -map 1:a -c:v copy $A -t "$DUR" -movflags +faststart saida/reel_6x1_com_trilha_ambiente.mp4
mkdir -p saida/previews
i=1
for t in 0.2 2.6 5.1 13.9 17.25 21.4 27.5 53.9 73.9 88.6; do
  ffmpeg -v error -y -ss $t -i saida/reel_6x1_final.mp4 -frames:v 1 "saida/previews/$(printf %02d $i)_${t}s.png"; i=$((i+1))
done
ls -la saida saida/previews
