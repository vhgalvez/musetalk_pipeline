# Problemas comunes

## 1. `ffmpeg` no encontrado

### Solución Windows

Instala FFmpeg y añade la carpeta `bin` al PATH.

Comprueba:

```powershell
ffmpeg -version
```

También puedes poner en `config.env`:

```env
FFMPEG_PATH=C:\ffmpeg\bin
```

---

## 2. CUDA / PyTorch no detecta GPU

Comprueba:

```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```

Debe salir:

```text
True
```

---

## 3. Error con `mmcv`, `mmdet`, `mmpose`

MuseTalk depende del ecosistema MMLab. Usa las versiones recomendadas:

```bash
pip install --no-cache-dir -U openmim
mim install "mmengine"
mim install "mmcv==2.0.1"
mim install "mmdet==3.1.0"
mim install "mmpose==1.1.0"
```

---

## 4. La boca se ve rara

Edita `config.env`:

```env
BBOX_SHIFT=-3
```

o:

```env
BBOX_SHIFT=3
```

Regla práctica:

- Positivo: abre más la boca.
- Negativo: cierra más la boca.

---

## 5. El video se ve con parpadeos / jitter

MuseTalk puede tener algo de jitter porque trabaja frame a frame. Mejora con:

- Video base estable.
- Rostro frontal.
- 25 FPS.
- Cara bien iluminada.
- Evitar movimiento brusco de cabeza.

---

## 6. OOM / falta de VRAM

Activa fp16:

```env
USE_FLOAT16=true
```

Reduce duración del clip de prueba a 5–8 segundos.

---

## 7. No encuentra modelos

Comprueba:

```text
MuseTalk/models/musetalkV15/unet.pth
MuseTalk/models/musetalkV15/musetalk.json
```

Si no existen, ejecuta otra vez:

```bash
bash scripts/download_weights_linux.sh
```

o en Windows:

```powershell
.\scripts\download_weights_windows.ps1
```
