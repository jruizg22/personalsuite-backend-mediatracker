from media_tracker.integrations.youtube.utils.dates import parse_datetime
from media_tracker.models.yt_api import YouTubeChannelDTO
from media_tracker.models.yt_resolve import YouTubeVideoDTO


class YTDLPProvider:

    def __init__(self, client):
        self.client = client

    def resolve_channel(self, url: str) -> YouTubeChannelDTO:
        data = self.client.run_channel(url)

        return YouTubeChannelDTO(
            id=data["channel_id"],
            name=data.get("channel"),
            url=data.get("channel_url")
        )

    def resolve_video(self, url: str) -> YouTubeVideoDTO:
        data = self.client.run_video(url)

        return YouTubeVideoDTO(
            id=data["id"],
            title=data["title"],
            description=data.get("description"),
            published_at=parse_datetime(data.get("upload_date")),
            url=data.get("webpage_url"),
            channel_id=data["channel_id"],
            channel_name=data.get("channel"),
            channel_url=data.get("channel_url")
        )