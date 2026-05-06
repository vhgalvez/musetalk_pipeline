param(
    [string]$EnvName = "MuseTalk"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Instalador MuseTalk Windows ==="

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git no está instalado o no está en PATH. Instala Git for Windows."
}

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Error "Conda no está en PATH. Instala Miniconda o Anaconda y abre Anaconda PowerShell Prompt."
}

if (-not (Test-Path ".\MuseTalk")) {
    git clone https://github.com/TMElyralab/MuseTalk.git
} else {
    Write-Host "MuseTalk ya existe. Saltando clone."
}

conda create -n $EnvName python=3.10 -y

Write-Host ""
Write-Host "Activa el entorno:"
Write-Host "conda activate $EnvName"
Write-Host ""
Write-Host "Luego ejecuta estos comandos:"
Write-Host "cd MuseTalk"
Write-Host "pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118"
Write-Host "pip install -r requirements.txt"
Write-Host "pip install --no-cache-dir -U openmim"
Write-Host 'mim install "mmengine"'
Write-Host 'mim install "mmcv==2.0.1"'
Write-Host 'mim install "mmdet==3.1.0"'
Write-Host 'mim install "mmpose==1.1.0"'
Write-Host "cd .."
Write-Host "pip install -r requirements-wrapper.txt"
Write-Host ""
Write-Host "Después descarga modelos:"
Write-Host ".\scripts\download_weights_windows.ps1"
