#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export MPLCONFIGDIR="${MPLCONFIGDIR:-$PWD/.matplotlib-cache}"
command -v ffmpeg >/dev/null || { echo "FFmpeg is required" >&2; exit 1; }
python research/benchmark.py --out out --seed 7 --damage-sites 25
python research/equal_budget.py --out out
python research/resilience_study.py
python research/multi_seed.py
python research/fullres_rail_analysis.py
python research/compare_rail_raster.py
python research/plot_fourway.py
python research/render_final_video.py
python research/make_carousel.py
python scripts/prepare_publication.py
PYTHONPATH=. python -m pytest -q tests
python scripts/prepublish_check.py
python scripts/prepublish_check_v42.py
python scripts/write_integrity.py
