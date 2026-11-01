#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v ffmpeg >/dev/null || { echo "FFmpeg required" >&2; exit 1; }
# Rebuild seeded simulator and outputs (this also regenerates the 21-second visual).
python physarum_india.py --out out
# Graph metrics and masks are recalculated from the same seed and candidate graph.
python research/benchmark.py --out out --seed 7 --damage-sites 25
python research/equal_budget.py --out out
python research/plot_fourway.py
python research/compare_rail_raster.py
python research/make_endcard.py
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i out/endcard.png -t 4 -vf 'scale=1080:1350:flags=lanczos,format=yuv420p' -c:v libx264 -crf 19 -preset veryfast out/endcard.mp4
printf "file 'slime_india.mp4'\nfile 'endcard.mp4'\n" > out/video_parts.txt
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i out/video_parts.txt -c:v libx264 -crf 19 -preset veryfast -pix_fmt yuv420p -movflags +faststart out/slime_india_v3.mp4
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i out/real_rail_geometry_comparison.png -t 5 -vf 'scale=1080:1350:flags=lanczos,format=yuv420p' -c:v libx264 -crf 19 -preset veryfast out/rail_endcard_5s.mp4
printf "file 'slime_india_v3.mp4'\nfile 'rail_endcard_5s.mp4'\n" > out/video_parts_v4.txt
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i out/video_parts_v4.txt -c:v libx264 -crf 19 -preset veryfast -pix_fmt yuv420p -movflags +faststart out/slime_india_v4.mp4
# Other outputs (10-seed study and raster position sensitivity) are separate experiments.
PYTHONPATH=. python -m pytest -q tests
python scripts/prepublish_check.py
