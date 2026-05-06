#!/usr/bin/env bash
set -e

if [ $# -lt 2 ]; then
  echo "Uso: bash scripts/prepare_media_linux.sh video.mp4 audio.mp3"
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg no está instalado."
  exit 1
fi

mkdir -p input

ffmpeg -y -i "$1" -vf "fps=25,format=yuv420p" -an "input/video.mp4"
ffmpeg -y -i "$2" -ac 1 -ar 16000 "input/audio.wav"

echo "✅ Preparado:"
echo "input/video.mp4"
echo "input/audio.wav"
