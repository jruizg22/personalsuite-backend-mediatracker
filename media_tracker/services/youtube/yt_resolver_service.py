from media_tracker.integrations.youtube.providers.yt_api_provider import YouTubeAPIProvider
from media_tracker.integrations.youtube.providers.ytdlp_provider import YTDLPProvider
from media_tracker.models.yt_api import MetadataError, YouTubeChannelDTO, YouTubeChannelMetadataResult
from media_tracker.models.yt_resolve import YTResolvedVideo, YTResolvedChannel, YouTubeVideoDTO


class YTResolverService:

    def __init__(
        self,
        provider: YTDLPProvider,
        youtube_api: YouTubeAPIProvider
    ):
        self.provider = provider
        self.youtube_api = youtube_api

    def resolve_channel(
            self,
            url: str | None,
            channel_id: str | None
    ) -> YTResolvedChannel:
        if channel_id:
            return self._resolve_channel_by_id(channel_id)

        if url:
            channel_data: YouTubeChannelDTO = self.provider.resolve_channel(url)
            return self._resolve_channel_by_id(
                channel_data.id,
                fallback_name=channel_data.name,
                fallback_url=channel_data.url
            )

        raise ValueError("Either url or channel_id must be provided")

    def resolve_video(
            self,
            url: str,
            rich_channel: bool = False
    ) -> YTResolvedVideo:

        if not url:
            raise ValueError("URL cannot be empty")

        video_data: YouTubeVideoDTO = (
            self.provider.resolve_video(url)
        )

        channel: YTResolvedChannel = YTResolvedChannel(
            id=video_data.channel_id,
            name=video_data.channel_name,
            url=video_data.channel_url,
            metadata_error=None
        )

        if rich_channel:
            channel = self._resolve_channel_by_id(
                channel_id=video_data.channel_id,
                fallback_name=video_data.channel_name,
                fallback_url=video_data.channel_url
            )

        return YTResolvedVideo(
            id=video_data.id,
            title=video_data.title,
            description=video_data.description,
            url=video_data.url,
            published_at=video_data.published_at,
            channel=channel
        )

    def _resolve_channel_by_id(
            self,
            channel_id: str,
            fallback_name: str | None = None,
            fallback_url: str | None = None
    ) -> YTResolvedChannel:

        result: YouTubeChannelMetadataResult = self.youtube_api.get_channel(
            channel_id
        )

        if not result.data:
            return YTResolvedChannel(
                id=channel_id,
                name=fallback_name,
                url=fallback_url,
                metadata_error=MetadataError(
                    type=result.error_type,
                    message=result.error
                )
            )

        return YTResolvedChannel(
            **result.data.model_dump(),
            metadata_error=None
        )