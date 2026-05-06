$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\MuseTalk")) {
    Write-Error "No existe .\MuseTalk. Ejecuta primero .\scripts\install_windows.ps1"
}

Push-Location ".\MuseTalk"

if (Test-Path ".\download_weights.bat") {
    .\download_weights.bat
} else {
    Write-Error "No encuentro download_weights.bat dentro de MuseTalk."
}

Pop-Location

Write-Host "✅ Descarga de modelos finalizada. Verifica la carpeta MuseTalk\models"
