from typing import Protocol

from media_tracker.models.yt_resolve import YTResolvedVideo


class YTMetadataProvider(Protocol):

    def resolve_video(
        self,
        url: str
    ) -> YTResolvedVideo:
        ...