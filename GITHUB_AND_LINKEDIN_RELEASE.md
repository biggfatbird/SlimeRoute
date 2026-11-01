> HISTORICAL v4.1 / earlier document. For the repaired local supplement use README.md and REPAIR_REPORT.md. Its release status and numbers have not been updated here.

# SLIMEROUTE public release — exact checklist

This repository contains the complete audited scientific-computing experiment and historical assets.
It is **not** a web-hosted interactive application; the live deliverables are this public GitHub repo and a native LinkedIn video.

## 1. Inspect before upload

- Verify you are using the latest `SLIMEROUTE_GITHUB_READY.zip` (not older v3/v4 packages).
- Current public video: `out/slime_india_v4.mp4` (30.07 seconds, 1080 × 1350, H.264, silent).
- Current railway graphic: `out/real_rail_geometry_comparison.png`.
- Archive-only: `out/slime_india.mp4`, `out/slime_india_v3.mp4`, `out/claude_original_slime_india.mp4`, `out/claude_original_comparison.png`, and `out/slime_vs_schematic.png`.
- Public caption: `LINKEDIN_POST.md` (append the actual newly created GitHub URL when posting).

## 2. On your Mac (Python 3.12 or 3.13; not your currently installed 3.15)

```bash
cd ~/Downloads
unzip -q SLIMEROUTE_GITHUB_READY.zip -d SLIMEROUTE_RELEASE
cd SLIMEROUTE_RELEASE/SLIMEROUTE
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=. python -m pytest -q tests
python scripts/prepublish_check.py
```

The supplied artifacts already passed 21 tests and the release checker in the packaging environment; rerun on your own machine when dependencies are installed. Python 3.13 can be used by replacing `python3.12` with `python3.13`.

## 3. GitHub

At https://github.com/new create a **public**, empty `slimeroute` repository in the correct account. Do not pre-create a README, gitignore, or license. From the extracted `SLIMEROUTE` directory, run:

```bash
git init
git branch -M main
git add .
git status --short
git commit -m "Release SLIMEROUTE v4.1 with audited experiments"
git remote add origin https://github.com/Biggfatbird/slimeroute.git
git push -u origin main
```

Confirm the push succeeds, README renders, Actions tests finish green for Python 3.11–3.13, and the actual repository link opens in a logged-out/incognito browser. A password prompt requires GitHub-supported authentication, not your ordinary account password.

## 4. LinkedIn

Upload `out/slime_india_v4.mp4` as a native video. Paste the caption from `LINKEDIN_POST.md`, replacing its code-link instruction with the real URL. Inspect the first frame and endcard on your phone, set audience to Anyone, and only then post.

## Supported claims / caveats

- Physarum-*inspired* numerical dynamics on a stylized grid connecting 16 cities, **not an actual organism**.
- Coarse 0.2° occupancy raster derived from third-party mapped railway LineStrings, **not a track-topology comparison**.
- 89.2% is simulated *length* near rail-cell centers at a 25 km criterion, whereas 18.4% uses *rail-cell count* in the reverse direction; they have different denominators.
- A near-length-matched graph heuristic beats the model's mean detour in seed 7, but not a universal optimization claim.
- Ten growth seeds and 250 **static** failures, not 250 independently simulated recovery runs.
- No proof of current physical track accuracy, real transit efficiency, or superiority to railway engineering.
