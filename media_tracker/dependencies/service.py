from fastapi import Depends

from media_tracker.services.youtube.yt_resolver_service import YTResolverService
from media_tracker.dependencies.youtube import (
    get_ytdlp_provider,
    get_youtube_api_provider
)


def get_yt_resolver_service(
    provider=Depends(get_ytdlp_provider),
    youtube_api=Depends(get_youtube_api_provider)
) -> YTResolverService:
    return YTResolverService(provider, youtube_api)