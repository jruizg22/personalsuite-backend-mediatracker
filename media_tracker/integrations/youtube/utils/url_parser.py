from urllib.parse import urlparse, parse_qs


def extract_youtube_video_id(url: str) -> str | None:
    parsed = urlparse(url)

    host = parsed.hostname or ""

    # youtu.be/VIDEO_ID
    if host in ("youtu.be",):
        return parsed.path.lstrip("/")

    # youtube.com/watch?v=VIDEO_ID
    if host in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        return parse_qs(parsed.query).get("v", [None])[0]

    # youtube.com/shorts/VIDEO_ID
    if host in ("www.youtube.com", "youtube.com") and "/shorts/" in parsed.path:
        return parsed.path.split("/shorts/")[1].split("/")[0]

    return None

def validate_youtube_url(url: str) -> str:
    video_id = extract_youtube_video_id(url)

    if not video_id:
        raise ValueError("Invalid YouTube URL")

    return video_id