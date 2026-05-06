# Paso a paso Windows

## 1. Instala requisitos

Necesitas:

- Git for Windows.
- Miniconda o Anaconda.
- Driver NVIDIA actualizado.
- FFmpeg en PATH.

Comprueba:

```powershell
git --version
conda --version
ffmpeg -version
nvidia-smi
```

---

## 2. Descomprime este ZIP

Ejemplo:

```text
C:\Users\vhgal\Documents\musetalk_pipeline_comercial
```

Abre **Anaconda PowerShell Prompt** en esa carpeta.

---

## 3. Clona MuseTalk y crea entorno

```powershell
.\scripts\install_windows.ps1
```

Activa entorno:

```powershell
conda activate MuseTalk
```

Instala dependencias de MuseTalk:

```powershell
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

## 4. Descarga modelos

```powershell
.\scripts\download_weights_windows.ps1
```

Debe quedar algo parecido a:

```text
MuseTalk\models\
├── musetalk\
├── musetalkV15\
├── syncnet\
├── dwpose\
├── face-parse-bisent\
├── sd-vae\
└── whisper\
```

---

## 5. Prepara video y audio

Opción manual:

```text
input/video.mp4
input/audio.wav
```

O convierte con FFmpeg:

```powershell
.\scripts\prepare_media_windows.ps1 -InputVideo "C:\ruta\video_original.mp4" -InputAudio "C:\ruta\voz.mp3"
```

---

## 6. Ejecuta

```powershell
python run_musetalk.py
```

Resultado:

```text
output/final_lipsync.mp4
```

---

## 7. Cambiar parámetros

Edita:

```text
config.env
```

Ejemplo:

```env
BBOX_SHIFT=3
USE_FLOAT16=true
```

Vuelve a ejecutar:

```powershell
python run_musetalk.py
```
