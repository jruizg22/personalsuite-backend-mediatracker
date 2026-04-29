from media_tracker.integrations.youtube.providers.ytdlp_provider import YTDLPProvider
from media_tracker.models.yt_resolve import YTResolvedVideo


class YTResolverService:

    def __init__(self, provider: YTDLPProvider):
        self.provider = provider

    def resolve_video(self, url: str) -> YTResolvedVideo:
        """
        Application-level logic:
        - validate input
        - delegate to provider
        - future: caching, dedup, enrichment, etc.
        """

        if not url:
            raise ValueError("URL cannot be empty")

        return self.provider.resolve_video(url)