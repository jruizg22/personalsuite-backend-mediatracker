from datetime import datetime


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    # yt-dlp format
    if len(value) == 8 and value.isdigit():
        try:
            return datetime.strptime(value, "%Y%m%d")
        except ValueError:
            return None

    # ISO format (YouTube API)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None