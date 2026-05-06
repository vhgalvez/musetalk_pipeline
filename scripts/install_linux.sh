#!/usr/bin/env bash
set -e

ENV_NAME="${1:-MuseTalk}"

echo "=== Instalador MuseTalk Linux / WSL ==="

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git no está instalado."
  exit 1
fi

if ! command -v conda >/dev/null 2>&1; then
  echo "ERROR: conda no está en PATH. Instala Miniconda/Anaconda."
  exit 1
fi

if [ ! -d "MuseTalk" ]; then
  git clone https://github.com/TMElyralab/MuseTalk.git
else
  echo "MuseTalk ya existe. Saltando clone."
fi

conda create -n "$ENV_NAME" python=3.10 -y

echo ""
echo "Ahora ejecuta:"
echo "conda activate $ENV_NAME"
echo "cd MuseTalk"
echo "pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118"
echo "pip install -r requirements.txt"
echo "pip install --no-cache-dir -U openmim"
echo 'mim install "mmengine"'
echo 'mim install "mmcv==2.0.1"'
echo 'mim install "mmdet==3.1.0"'
echo 'mim install "mmpose==1.1.0"'
echo "cd .."
echo "pip install -r requirements-wrapper.txt"
echo ""
echo "Después descarga modelos:"
echo "bash scripts/download_weights_linux.sh"
