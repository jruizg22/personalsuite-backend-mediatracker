import httpx

from media_tracker.integrations.youtube.utils.dates import parse_datetime
from media_tracker.models.yt_api import YouTubeChannelMetadataResult, YouTubeChannelDTO


class YouTubeAPIProvider:

    def __init__(self, client):
        self.client = client

    def get_channel(
        self,
        channel_id: str
    ) -> YouTubeChannelMetadataResult:

        try:

            data = self.client.get_channel(channel_id)

            if not data:
                return YouTubeChannelMetadataResult(
                    data=None,
                    error="Channel not found",
                    error_type="not_found"
                )

            snippet = data.get("snippet", {})

            dto = YouTubeChannelDTO(
                id=data["id"],
                name=snippet.get("title"),
                description=snippet.get("description"),
                created_at=parse_datetime(
                    snippet.get("publishedAt")
                ),
                url=f"https://www.youtube.com/channel/{data['id']}"
            )

            return YouTubeChannelMetadataResult(
                data=dto
            )

        except httpx.HTTPStatusError as e:

            status = e.response.status_code

            if status == 403:
                return YouTubeChannelMetadataResult(
                    data=None,
                    error="Quota exceeded or access forbidden",
                    error_type="quota_or_forbidden"
                )

            if status == 404:
                return YouTubeChannelMetadataResult(
                    data=None,
                    error="Channel not found",
                    error_type="not_found"
                )

            return YouTubeChannelMetadataResult(
                data=None,
                error=str(e),
                error_type="http_error"
            )

        except httpx.TimeoutException:
            return YouTubeChannelMetadataResult(
                data=None,
                error="Timeout contacting YouTube API",
                error_type="timeout"
            )

        except Exception as e:
            return YouTubeChannelMetadataResult(
                data=None,
                error=str(e),
                error_type="unknown"
            )