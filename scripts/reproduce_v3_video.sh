#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python research/make_endcard.py
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i out/endcard.png -t 4 \
  -vf 'scale=1080:1350:flags=lanczos,format=yuv420p' -c:v libx264 -crf 18 -preset veryfast out/endcard.mp4
printf "file 'slime_india.mp4'\nfile 'endcard.mp4'\n" > out/video_parts.txt
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i out/video_parts.txt \
  -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -movflags +faststart out/slime_india_v3.mp4
printf 'Created out/slime_india_v3.mp4\n'
