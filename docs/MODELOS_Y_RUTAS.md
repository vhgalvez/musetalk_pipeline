# Modelos y rutas necesarias

MuseTalk usa varios pesos/modelos. No vienen en este ZIP porque pesan varios GB.

La descarga oficial se hace con:

## Windows

```powershell
.\scripts\download_weights_windows.ps1
```

## Linux

```bash
bash scripts/download_weights_linux.sh
```

---

## Estructura esperada

Dentro de `MuseTalk/models/` debe existir:

```text
MuseTalk/models/
├── musetalk
│   ├── musetalk.json
│   └── pytorch_model.bin
├── musetalkV15
│   ├── musetalk.json
│   └── unet.pth
├── syncnet
│   └── latentsync_syncnet.pt
├── dwpose
│   └── dw-ll_ucoco_384.pth
├── face-parse-bisent
│   ├── 79999_iter.pth
│   └── resnet18-5c106cde.pth
├── sd-vae
│   ├── config.json
│   └── diffusion_pytorch_model.bin
└── whisper
    ├── config.json
    ├── pytorch_model.bin
    └── preprocessor_config.json
```

---

## Qué modelo usar

Usa por defecto:

```env
VERSION=v15
```

Esto usa:

```text
MuseTalk/models/musetalkV15/unet.pth
MuseTalk/models/musetalkV15/musetalk.json
```

---

## Si algo falla

Ejecuta:

```bash
python run_musetalk.py
```

y revisa:

```text
logs/last_run.log
```
