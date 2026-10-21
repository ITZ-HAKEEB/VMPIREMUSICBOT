# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import shutil
from pathlib import Path

from anony import logger


def ensure_dirs():
    """
    Ensure that the necessary directories exist.
    """
    import os
    deno_home = Path.home() / ".deno" / "bin"
    if deno_home.exists() and str(deno_home) not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{deno_home}:{os.environ.get('PATH', '')}"

    if not shutil.which("deno") or not shutil.which("ffmpeg"):
        raise RuntimeError("Deno and FFmpeg must be installed and accessible in the system PATH.")

    for dir in ["cache", "downloads"]:
        Path(dir).mkdir(parents=True, exist_ok=True)
    logger.info("Cache directories updated.")
