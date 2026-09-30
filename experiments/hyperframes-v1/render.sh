#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export HYPERFRAMES_NO_TELEMETRY=1
export DO_NOT_TRACK=1
python prepare.py
python -m manim --disable_caching --media_dir media -o nina-base base_scene.py NinaBase
ffmpeg -y -v error -i media/videos/base_scene/1280p30/nina-base.mp4 -c:v libx264 -preset fast -crf 18 -g 30 -keyint_min 30 -sc_threshold 0 -pix_fmt yuv420p -an -movflags +faststart assets/base.mp4
python sound_design.py
python build.py
npx --no-install hyperframes lint .
npx --no-install hyperframes render . --output Nina_HyperFrames_Teste_1_Minuto.mp4 --workers 2 --no-browser-gpu
