import os

YTDLP_BINARY: str = os.getenv(
    "YTDLP_BINARY",
    "/tools/yt-dlp"  # fallback producción (Docker)
)