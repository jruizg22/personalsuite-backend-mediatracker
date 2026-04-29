from media_tracker.integrations.youtube.utils.dates import parse_ytdlp_datetime
from media_tracker.integrations.youtube.utils.url_parser import validate_youtube_url
from media_tracker.models.yt_resolve import (
    YTResolvedVideo
)


class YTDLPProvider:

    def __init__(self, client):
        self.client = client

    def resolve_video(self, url: str) -> YTResolvedVideo:
        video_id = validate_youtube_url(url)

        data = self.client.run(url)

        return YTResolvedVideo(
            id=video_id,
            title=data["title"],
            description=data.get("description"),
            url=data.get("webpage_url", url),
            published_at=parse_ytdlp_datetime(data.get("upload_date")),
            channel_id=data.get("channel_id")
        )