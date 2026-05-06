# Paso a paso Linux / WSL / Ubuntu

## 1. Requisitos

```bash
git --version
conda --version
ffmpeg -version
nvidia-smi
```

En Ubuntu:

```bash
sudo apt update
sudo apt install -y git ffmpeg
```

---

## 2. Instala

```bash
bash scripts/install_linux.sh
conda activate MuseTalk
```

Instala dependencias:

```bash
cd MuseTalk
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
pip install --no-cache-dir -U openmim
mim install "mmengine"
mim install "mmcv==2.0.1"
mim install "mmdet==3.1.0"
mim install "mmpose==1.1.0"
cd ..
pip install -r requirements-wrapper.txt
```

---

## 3. Descarga modelos

```bash
bash scripts/download_weights_linux.sh
```

---

## 4. Prepara archivos

```bash
cp /ruta/video.mp4 input/video.mp4
cp /ruta/audio.wav input/audio.wav
```

O convierte:

```bash
bash scripts/prepare_media_linux.sh /ruta/video.mp4 /ruta/audio.mp3
```

---

## 5. Ejecuta

```bash
python run_musetalk.py
```

Resultado:

```text
output/final_lipsync.mp4
```
