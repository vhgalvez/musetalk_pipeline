#!/usr/bin/env bash
set -e

if [ ! -d "MuseTalk" ]; then
  echo "ERROR: no existe ./MuseTalk. Ejecuta primero scripts/install_linux.sh"
  exit 1
fi

cd MuseTalk

if [ -f "./download_weights.sh" ]; then
  sh ./download_weights.sh
else
  echo "ERROR: no encuentro download_weights.sh dentro de MuseTalk."
  exit 1
fi

echo "✅ Descarga de modelos finalizada. Verifica la carpeta MuseTalk/models"
