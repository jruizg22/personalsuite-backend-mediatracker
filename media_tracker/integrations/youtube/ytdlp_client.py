import json
import subprocess
from media_tracker.integrations.youtube.config import YTDLP_BINARY


class YTDLPClient:

    def __init__(self, binary_path: str = YTDLP_BINARY):
        self.binary_path = binary_path

    def run_video(self, url: str) -> dict:
        return self._run([
            "--dump-single-json",
            "--skip-download",
            "--no-playlist",
            url
        ])

    def run_channel(self, url: str) -> dict:
        return self._run([
            "--dump-single-json",
            "--flat-playlist",
            "--playlist-items", "0",
            "--skip-download",
            url
        ])

    def _run(self, args: list[str]) -> dict:
        try:
            result = subprocess.run(
                [self.binary_path, *args],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "yt-dlp timed out while resolving URL"
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"yt-dlp failed: {e.stderr}"
            )
        except json.JSONDecodeError:
            raise RuntimeError(
                "Invalid JSON returned by yt-dlp"
            )