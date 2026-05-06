param(
    [Parameter(Mandatory=$true)][string]$InputVideo,
    [Parameter(Mandatory=$true)][string]$InputAudio
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "ffmpeg no está en PATH."
}

New-Item -ItemType Directory -Force -Path ".\input" | Out-Null

ffmpeg -y -i "$InputVideo" -vf "fps=25,format=yuv420p" -an ".\input\video.mp4"
ffmpeg -y -i "$InputAudio" -ac 1 -ar 16000 ".\input\audio.wav"

Write-Host "✅ Preparado:"
Write-Host "input/video.mp4"
Write-Host "input/audio.wav"
