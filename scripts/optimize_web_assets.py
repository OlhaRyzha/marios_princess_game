import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
MINIMUM_SIZE = 32 * 1024


def optimize_png(path: Path) -> int:
    """Quantize one PNG and replace it only when the result is smaller."""
    original_size = path.stat().st_size
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / path.name
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(path),
                "-vf",
                (
                    "split[source][copy];"
                    "[source]palettegen=max_colors=256:reserve_transparent=1[palette];"
                    "[copy][palette]paletteuse=dither=sierra2_4a:alpha_threshold=1"
                ),
                str(output),
            ],
            check=True,
        )
        optimized_size = output.stat().st_size
        if optimized_size < original_size:
            shutil.copyfile(output, path)
            return original_size - optimized_size
    return 0


def optimize_assets() -> tuple[int, int]:
    """Optimize large PNG assets and return file and byte savings."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to optimize assets")
    optimized_files = 0
    saved_bytes = 0
    for path in sorted(ASSETS_DIR.rglob("*.png")):
        if path.stat().st_size < MINIMUM_SIZE:
            continue
        saved = optimize_png(path)
        if saved:
            optimized_files += 1
            saved_bytes += saved
    return optimized_files, saved_bytes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize PNG assets for web delivery")
    parser.parse_args()
    count, savings = optimize_assets()
    print(f"Optimized {count} PNG files; saved {savings / 1024 / 1024:.1f} MiB")
