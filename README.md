# MuseTalk Pipeline Comercial — ZIP listo para usar

Este paquete te deja una estructura limpia para usar **MuseTalk 1.5** como herramienta de lip-sync comercial en tu pipeline:

```text
video base / Wan / cámara / avatar
        +
audio en español / TTS / voz real
        ↓
MuseTalk 1.5
        ↓
video final con labios sincronizados
```

> Importante: este ZIP **no incluye los modelos de IA** porque pesan varios GB. Incluye los scripts para descargarlos desde el repositorio oficial de MuseTalk.

---

## 1. Qué trae este ZIP

```text
musetalk_pipeline_comercial/
│
├── run_musetalk.py                  # Script principal
├── config.env                       # Rutas y parámetros editables
├── requirements-wrapper.txt         # Dependencias ligeras del wrapper
│
├── input/
│   ├── video.mp4                    # Aquí pones tu video
│   └── audio.wav                    # Aquí pones tu audio
│
├── output/                          # Aquí queda el resultado final
├── logs/                            # Logs de ejecución
│
├── scripts/
│   ├── install_windows.ps1          # Instalación Windows / PowerShell
│   ├── install_linux.sh             # Instalación Linux / WSL / Ubuntu
│   ├── download_weights_windows.ps1 # Descargar modelos en Windows
│   ├── download_weights_linux.sh    # Descargar modelos en Linux
│   ├── prepare_media_windows.ps1    # Convierte video a 25fps/audio WAV
│   └── prepare_media_linux.sh       # Convierte video a 25fps/audio WAV
│
└── docs/
    ├── PASO_A_PASO_WINDOWS.md
    ├── PASO_A_PASO_LINUX_WSL.md
    ├── MODELOS_Y_RUTAS.md
    ├── PROBLEMAS_COMUNES.md
    └── USO_COMERCIAL_LICENCIA.md
```

---

## 2. Requisitos

### Recomendado

- GPU NVIDIA.
- Python 3.10.
- CUDA compatible.
- Conda o Miniconda.
- Git.
- FFmpeg.

MuseTalk recomienda Python 3.10 y CUDA 11.7/11.8. En Windows normalmente es más cómodo usar **Conda**.

---

## 3. Uso rápido

### Windows PowerShell

Abre PowerShell en esta carpeta:

```powershell
cd C:\ruta\a\musetalk_pipeline_comercial
```

Instala:

```powershell
.\scripts\install_windows.ps1
```

Descarga modelos:

```powershell
.\scripts\download_weights_windows.ps1
```

Pon tus archivos:

```text
input/video.mp4
input/audio.wav
```

Ejecuta:

```powershell
conda activate MuseTalk
python run_musetalk.py
```

---

### Linux / WSL / Ubuntu

```bash
cd /ruta/a/musetalk_pipeline_comercial
bash scripts/install_linux.sh
bash scripts/download_weights_linux.sh
conda activate MuseTalk
python run_musetalk.py
```

---

## 4. Cambiar rutas fácilmente

Edita `config.env`:

```env
VIDEO_PATH=input/video.mp4
AUDIO_PATH=input/audio.wav
OUTPUT_DIR=output
OUTPUT_NAME=final_lipsync.mp4
MUSETALK_DIR=MuseTalk
FFMPEG_PATH=ffmpeg
VERSION=v15
BBOX_SHIFT=0
USE_FLOAT16=true
```

Puedes poner rutas absolutas:

```env
VIDEO_PATH=C:\Users\vhgal\Videos\mi_video.mp4
AUDIO_PATH=C:\Users\vhgal\Videos\voz.wav
```

o en Linux:

```env
VIDEO_PATH=/mnt/c/Users/vhgal/Videos/mi_video.mp4
AUDIO_PATH=/mnt/c/Users/vhgal/Videos/voz.wav
```

---

## 5. Recomendación para tu RTX 4070 12GB

Empieza así:

```env
VERSION=v15
BBOX_SHIFT=0
USE_FLOAT16=true
```

Si la boca queda muy abierta o rara, prueba:

```env
BBOX_SHIFT=-3
```

Si la boca queda muy cerrada, prueba:

```env
BBOX_SHIFT=3
```

---

## 6. Consejo para mejor calidad

El input importa muchísimo:

- Video a **25 FPS**.
- Cara visible y estable.
- Audio limpio, sin ruido.
- Mejor WAV que MP3.
- La persona no debe hablar ya en el video base; idealmente boca cerrada o movimiento mínimo.

Para convertir tu video y audio:

### Windows

```powershell
.\scripts\prepare_media_windows.ps1 -InputVideo "mi_video.mp4" -InputAudio "mi_audio.mp3"
```

### Linux

```bash
bash scripts/prepare_media_linux.sh mi_video.mp4 mi_audio.mp3
```

---

## 7. Pipeline recomendado con Wan 2.2

```text
1. Generas video base con Wan 2.2
2. Exportas video a 25fps
3. Generas voz en español con TTS
4. Pasas video + audio por MuseTalk
5. Editas en DaVinci / FFmpeg
```

---

## 8. Nota legal

MuseTalk indica que:

- El código está bajo licencia MIT.
- Los modelos entrenados están disponibles para cualquier propósito, incluso comercial.
- Los modelos externos usados por el proyecto deben respetar sus propias licencias.

Lee `docs/USO_COMERCIAL_LICENCIA.md`.


---

## Barra de progreso añadida

`run_musetalk.py` ahora muestra en consola:

- Porcentaje de avance cuando MuseTalk imprime progreso tipo `tqdm`.
- Frames procesados cuando aparecen como `actual/total`.
- Tiempo transcurrido.
- ETA aproximado.
- Etapa estimada del proceso: carga de modelos, audio, inferencia y render final.
- Log completo en `logs/last_run.log`.

El uso no cambia:

```bash
python run_musetalk.py
```

