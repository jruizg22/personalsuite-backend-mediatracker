import httpx
import subprocess
from pathlib import Path
import os
import stat

from media_tracker.integrations.youtube.config import YTDLP_BINARY
from media_tracker.models.ytdlp import YTDLPStatus
from media_tracker.tools.ytdlp.ytdlp_state import update_state


def get_installed_version() -> str:
    result = subprocess.run(
        [YTDLP_BINARY, "--version"],
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout.strip()

GITHUB_RELEASES = (
    "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
)


def get_latest_release() -> dict:
    response = httpx.get(GITHUB_RELEASES, timeout=10)

    response.raise_for_status()

    return response.json()

def get_status() -> YTDLPStatus:
    installed: str = get_installed_version()
    latest: str = get_latest_release()["tag_name"]

    return YTDLPStatus(
        installed=installed,
        latest=latest,
        update_available=latest > installed,
        updating=update_state.updating
    )


TOOLS_DIR = Path("/tools")

NEW_BINARY = TOOLS_DIR / "yt-dlp.new"

def download_latest_binary(download_url: str) -> None:
    with httpx.stream("GET", download_url) as response:
        response.raise_for_status()
        with open(NEW_BINARY, "wb") as file:
            for chunk in response.iter_bytes():
                file.write(chunk)


CURRENT_BINARY = TOOLS_DIR / "yt-dlp"

def replace_binary() -> None:
    os.chmod(
        NEW_BINARY,
        os.stat(NEW_BINARY).st_mode | stat.S_IEXEC
    )
    os.replace(NEW_BINARY, CURRENT_BINARY)