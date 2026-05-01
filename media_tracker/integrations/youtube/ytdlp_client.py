import json
import subprocess
from media_tracker.integrations.youtube.config import YTDLP_BINARY


class YTDLPClient:

    def run(self, url: str) -> dict:
        result = subprocess.run(
            [
                YTDLP_BINARY,
                "--dump-single-json",
                "--skip-download",
                url
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

        return json.loads(result.stdout)