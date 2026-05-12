"""
MuseTalk Pipeline Wrapper con barra de progreso.

Uso:
    python run_musetalk.py

Opcional:
    python run_musetalk.py --video input/video.mp4 --audio input/audio.wav --bbox-shift 2

Este script:
1. Lee config.env.
2. Crea un YAML temporal para MuseTalk.
3. Ejecuta python -m scripts.inference.
4. Muestra progreso en vivo:
   - porcentaje cuando MuseTalk/tqdm lo imprime
   - frames procesados si aparecen en stdout
   - tiempo transcurrido
   - ETA aproximado
   - etapa del proceso
5. Busca el último .mp4 generado.
6. Si no hay .mp4, busca frames PNG y los convierte a MP4 con FFmpeg.
7. Deja el resultado final en output/final_lipsync.mp4.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Falta PyYAML. Instala con: pip install -r requirements-wrapper.txt")
    raise


ROOT = Path(__file__).resolve().parent


def load_env(path: Path) -> dict:
    data = {}

    if not path.exists():
        return data

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")

    return data


def as_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    return value.strip().lower() in {"1", "true", "yes", "y", "si", "sí"}


def resolve_path(value: str, base: Path = ROOT) -> Path:
    p = Path(value)

    if p.is_absolute():
        return p

    return (base / p).resolve()


def ensure_exists(path: Path, label: str):
    if not path.exists():
        raise FileNotFoundError(f"No existe {label}: {path}")


def format_seconds(seconds: float | int | None) -> str:
    if seconds is None or seconds < 0:
        return "--:--"

    return str(timedelta(seconds=int(seconds)))


def find_latest_mp4(folder: Path, after_ts: float) -> Path | None:
    if not folder.exists():
        return None

    candidates = [
        p
        for p in folder.rglob("*.mp4")
        if p.is_file() and p.stat().st_mtime >= after_ts - 2
    ]

    if not candidates:
        candidates = [p for p in folder.rglob("*.mp4") if p.is_file()]

    if not candidates:
        return None

    return max(candidates, key=lambda p: p.stat().st_mtime)


def find_latest_png_folder(folder: Path, after_ts: float) -> Path | None:
    """
    Busca la carpeta más reciente que tenga frames PNG.

    Ejemplo esperado:
        output/_musetalk_raw/v15/MATEO_01_lipsync_bancarrota/*.png
    """
    if not folder.exists():
        return None

    pngs = [
        p
        for p in folder.rglob("*.png")
        if p.is_file() and p.stat().st_mtime >= after_ts - 2
    ]

    if not pngs:
        pngs = [p for p in folder.rglob("*.png") if p.is_file()]

    if not pngs:
        return None

    latest_png = max(pngs, key=lambda p: p.stat().st_mtime)
    return latest_png.parent


def get_ffprobe_path(ffmpeg_path: str) -> str:
    """
    Si FFMPEG_PATH es:
      - ffmpeg -> usa ffprobe
      - C:\\ffmpeg\\bin\\ffmpeg.exe -> usa C:\\ffmpeg\\bin\\ffprobe.exe
      - C:\\ffmpeg\\bin -> usa C:\\ffmpeg\\bin\\ffprobe.exe
    """
    p = Path(ffmpeg_path)

    if ffmpeg_path.lower() == "ffmpeg":
        return "ffprobe"

    if p.is_dir():
        return str(p / "ffprobe.exe")

    if p.name.lower() in {"ffmpeg.exe", "ffmpeg"}:
        return str(p.with_name("ffprobe.exe"))

    return "ffprobe"


def get_ffmpeg_executable(ffmpeg_path: str) -> str:
    """
    Si FFMPEG_PATH es:
      - ffmpeg -> usa ffmpeg
      - C:\\ffmpeg\\bin -> usa C:\\ffmpeg\\bin\\ffmpeg.exe
      - C:\\ffmpeg\\bin\\ffmpeg.exe -> usa ese ejecutable
    """
    p = Path(ffmpeg_path)

    if ffmpeg_path.lower() == "ffmpeg":
        return "ffmpeg"

    if p.is_dir():
        return str(p / "ffmpeg.exe")

    return ffmpeg_path


def get_video_fps(video_path: Path, ffmpeg_path: str = "ffmpeg") -> float:
    """
    Intenta detectar FPS con ffprobe.
    Si falla, usa 25 fps.
    """
    ffprobe = get_ffprobe_path(ffmpeg_path)

    try:
        cmd = [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=r_frame_rate",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        raw = result.stdout.strip()

        if "/" in raw:
            num, den = raw.split("/", 1)
            num_f = float(num)
            den_f = float(den)

            if den_f != 0:
                return round(num_f / den_f, 3)

        return float(raw)

    except Exception:
        return 25.0


def build_video_from_png_frames(
    frames_dir: Path,
    audio_path: Path,
    final_path: Path,
    fps: float,
    ffmpeg_path: str = "ffmpeg",
) -> None:
    """
    Ensambla frames PNG + audio WAV en un MP4 final compatible con DaVinci Resolve.
    """
    ffmpeg_exec = get_ffmpeg_executable(ffmpeg_path)
    png_pattern = frames_dir / "%08d.png"

    cmd = [
        ffmpeg_exec,
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(png_pattern),
        "-i",
        str(audio_path),
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(final_path),
    ]

    print("\n🎬 MuseTalk no generó MP4. Ensamblando frames PNG con FFmpeg...")
    print(f"Frames: {frames_dir}")
    print(f"Audio:  {audio_path}")
    print(f"FPS:    {fps}")
    print(f"Salida: {final_path}")

    subprocess.run(cmd, check=True)


class ProgressMonitor:
    """
    Barra de progreso sin dependencias externas.

    Lee la salida de MuseTalk/tqdm.
    Detecta patrones como:
        45%|████      | 45/100 [...]
        123/250
    """

    def __init__(self):
        self.start_time = time.time()
        self.percent: float = 0.0
        self.current: int | None = None
        self.total: int | None = None
        self.stage = "Inicializando"
        self.last_line = ""
        self.last_render_len = 0

    def update_from_line(self, line: str):
        clean = self._clean_line(line)

        if clean:
            self.last_line = clean[-180:]

        lower = clean.lower()

        if "extract" in lower or "video2imgs" in lower or "reading" in lower:
            self.stage = "Extrayendo frames / leyendo video"

        elif "audio" in lower or "whisper" in lower:
            self.stage = "Procesando audio"

        elif "vae" in lower or "unet" in lower or "musetalk" in lower:
            self.stage = "Cargando modelos IA"

        elif "inference" in lower or "infer" in lower or "denois" in lower:
            self.stage = "Generando labios"

        elif "ffmpeg" in lower or "saving" in lower or "write" in lower or "mux" in lower:
            self.stage = "Renderizando video final"

        m_percent = re.search(r"(\d{1,3})%\|", clean)

        if m_percent:
            value = int(m_percent.group(1))

            if 0 <= value <= 100:
                self.percent = max(self.percent, float(value))

        matches = re.findall(r"(?<!\d)(\d{1,7})/(\d{1,7})(?!\d)", clean)

        if matches:
            cur, total = matches[-1]
            cur_i, total_i = int(cur), int(total)

            if total_i > 0 and cur_i <= total_i:
                self.current = cur_i
                self.total = total_i
                frame_percent = (cur_i / total_i) * 100
                self.percent = max(self.percent, min(frame_percent, 100.0))

    def render(self):
        elapsed = time.time() - self.start_time

        eta = None

        if self.percent > 1:
            total_estimated = elapsed / (self.percent / 100.0)
            eta = max(0, total_estimated - elapsed)

        bar_width = 28
        filled = int(bar_width * min(self.percent, 100) / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        frames = ""

        if self.current is not None and self.total is not None:
            frames = f" | frames: {self.current}/{self.total}"

        msg = (
            f"\r[{bar}] "
            f"{self.percent:6.2f}% "
            f"| {self.stage}"
            f"{frames}"
            f" | elapsed: {format_seconds(elapsed)}"
            f" | ETA: {format_seconds(eta)}"
        )

        padding = " " * max(0, self.last_render_len - len(msg))
        print(msg + padding, end="", flush=True)
        self.last_render_len = len(msg)

    def done(self):
        self.percent = 100.0
        self.stage = "Completado"
        self.render()
        print()

    @staticmethod
    def _clean_line(line: str) -> str:
        line = line.replace("\r", "").replace("\n", "")
        line = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", line)
        return line.strip()


def run_process_with_progress(cmd: list[str], cwd: str, log_file: Path) -> int:
    monitor = ProgressMonitor()

    with log_file.open("w", encoding="utf-8", errors="replace") as log:
        log.write("COMMAND:\n")
        log.write(" ".join(cmd) + "\n\n")
        log.flush()

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env,
        )

        last_ui_update = 0.0

        try:
            assert process.stdout is not None

            for line in process.stdout:
                log.write(line)
                log.flush()

                monitor.update_from_line(line)

                now = time.time()

                if now - last_ui_update >= 0.2:
                    monitor.render()
                    last_ui_update = now

            return_code = process.wait()

        except KeyboardInterrupt:
            print("\n\n⚠️ Cancelado por el usuario. Terminando MuseTalk...")
            process.terminate()

            try:
                process.wait(timeout=10)

            except subprocess.TimeoutExpired:
                process.kill()

            return 130

    if return_code == 0:
        monitor.done()

    else:
        print()
        print("❌ El proceso terminó con error.")

        if monitor.last_line:
            print(f"Última línea detectada: {monitor.last_line}")

    return return_code


def main():
    parser = argparse.ArgumentParser(
        description="Wrapper simple para MuseTalk 1.5 con barra de progreso"
    )

    parser.add_argument("--video", help="Ruta del video de entrada")
    parser.add_argument("--audio", help="Ruta del audio de entrada")
    parser.add_argument("--output-dir", help="Carpeta de salida")
    parser.add_argument("--output-name", help="Nombre final del video")
    parser.add_argument("--musetalk-dir", help="Carpeta del repo MuseTalk")
    parser.add_argument("--ffmpeg-path", help="Ruta a ffmpeg o carpeta bin")
    parser.add_argument("--version", choices=["v1", "v15"], help="Versión de MuseTalk")
    parser.add_argument("--bbox-shift", type=int, help="Ajuste de boca")
    parser.add_argument("--no-float16", action="store_true", help="No usar fp16")

    args = parser.parse_args()

    cfg = load_env(ROOT / "config.env")

    video_path = resolve_path(args.video or cfg.get("VIDEO_PATH", "input/video.mp4"))
    audio_path = resolve_path(args.audio or cfg.get("AUDIO_PATH", "input/audio.wav"))
    output_dir = resolve_path(args.output_dir or cfg.get("OUTPUT_DIR", "output"))
    output_name = args.output_name or cfg.get("OUTPUT_NAME", "final_lipsync.mp4")
    musetalk_dir = resolve_path(args.musetalk_dir or cfg.get("MUSETALK_DIR", "MuseTalk"))
    ffmpeg_path = args.ffmpeg_path or cfg.get("FFMPEG_PATH", "ffmpeg")
    version = args.version or cfg.get("VERSION", "v15")

    bbox_shift = (
        args.bbox_shift
        if args.bbox_shift is not None
        else int(cfg.get("BBOX_SHIFT", "0"))
    )

    use_float16 = (not args.no_float16) and as_bool(
        cfg.get("USE_FLOAT16", "true"),
        True,
    )

    ensure_exists(video_path, "VIDEO_PATH")
    ensure_exists(audio_path, "AUDIO_PATH")
    ensure_exists(musetalk_dir, "MUSETALK_DIR / carpeta MuseTalk")

    output_dir.mkdir(parents=True, exist_ok=True)

    log_dir = ROOT / cfg.get("LOG_DIR", "logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    temp_config_dir = musetalk_dir / "configs" / "inference"
    temp_config_dir.mkdir(parents=True, exist_ok=True)

    temp_config = temp_config_dir / "wrapper_single_task.yaml"

    yaml_data = {
        "task_0": {
            "video_path": str(video_path),
            "audio_path": str(audio_path),
            "bbox_shift": int(bbox_shift),
        }
    }

    temp_config.write_text(
        yaml.safe_dump(yaml_data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    result_dir = output_dir / "_musetalk_raw"
    result_dir.mkdir(parents=True, exist_ok=True)

    if version == "v15":
        unet_model_path = "models/musetalkV15/unet.pth"
        unet_config = "models/musetalkV15/musetalk.json"

    else:
        unet_model_path = "models/musetalk/pytorch_model.bin"
        unet_config = "models/musetalk/musetalk.json"

    cmd = [
        sys.executable,
        "-u",
        "-m",
        "scripts.inference",
        "--inference_config",
        str(temp_config),
        "--result_dir",
        str(result_dir),
        "--unet_model_path",
        unet_model_path,
        "--unet_config",
        unet_config,
        "--version",
        version,
        "--ffmpeg_path",
        ffmpeg_path,
    ]

    if use_float16:
        cmd.append("--use_float16")

    print("\n================ MuseTalk Pipeline ================")
    print(f"Video:       {video_path}")
    print(f"Audio:       {audio_path}")
    print(f"MuseTalk:    {musetalk_dir}")
    print(f"Version:     {version}")
    print(f"BBox shift:  {bbox_shift}")
    print(f"Float16:     {use_float16}")
    print(f"Result dir:  {result_dir}")
    print("===================================================\n")

    start_ts = time.time()
    log_file = log_dir / "last_run.log"

    print("🚀 Ejecutando MuseTalk con monitor de progreso...\n")

    return_code = run_process_with_progress(
        cmd=cmd,
        cwd=str(musetalk_dir),
        log_file=log_file,
    )

    if return_code != 0:
        print(f"\n❌ MuseTalk falló. Revisa el log: {log_file}")
        sys.exit(return_code)

    print("\n🔎 Buscando video generado...")

    final_path = output_dir / output_name

    latest = find_latest_mp4(result_dir, after_ts=start_ts)

    if latest is not None:
        shutil.copy2(latest, final_path)

        print("\n✅ Video final generado:")
        print(final_path)
        print(f"\n📄 Log: {log_file}")
        return

    frames_dir = find_latest_png_folder(result_dir, after_ts=start_ts)

    if frames_dir is None:
        print("⚠️ MuseTalk terminó, pero no encontré ningún .mp4 ni frames .png en la carpeta de salida.")
        print(f"Revisa manualmente: {result_dir}")
        return

    fps = get_video_fps(video_path, ffmpeg_path=ffmpeg_path)

    try:
        build_video_from_png_frames(
            frames_dir=frames_dir,
            audio_path=audio_path,
            final_path=final_path,
            fps=fps,
            ffmpeg_path=ffmpeg_path,
        )

    except subprocess.CalledProcessError as e:
        print("\n❌ MuseTalk generó frames PNG, pero FFmpeg falló al crear el MP4.")
        print(e)
        return

    print("\n✅ Video final generado desde frames PNG:")
    print(final_path)
    print(f"\n📄 Log: {log_file}")


if __name__ == "__main__":
    main()

