import httpx
from fastapi import Depends

from media_tracker.config.youtube import YouTubeConfig
from media_tracker.integrations.youtube.yt_api_client import YouTubeAPIClient
from media_tracker.integrations.youtube.providers.yt_api_provider import YouTubeAPIProvider
from media_tracker.integrations.youtube.providers.ytdlp_provider import YTDLPProvider
from media_tracker.integrations.youtube.ytdlp_client import YTDLPClient


# CONFIG
def get_youtube_config() -> YouTubeConfig:
    return YouTubeConfig()


# HTTP CLIENT (YouTube API)
def get_http_client() -> httpx.Client:
    return httpx.Client(timeout=10.0)


# YT-DLP CLIENT
def get_ytdlp_client() -> YTDLPClient:
    return YTDLPClient()


# YT-DLP PROVIDER
def get_ytdlp_provider(
    client: YTDLPClient = Depends(get_ytdlp_client)
) -> YTDLPProvider:
    return YTDLPProvider(client)


# YOUTUBE API CLIENT
def get_youtube_api_client(
    config: YouTubeConfig = Depends(get_youtube_config),
    http_client: httpx.Client = Depends(get_http_client)
) -> YouTubeAPIClient:
    return YouTubeAPIClient(config, http_client)


# YOUTUBE API PROVIDER
def get_youtube_api_provider(
    client: YouTubeAPIClient = Depends(get_youtube_api_client)
) -> YouTubeAPIProvider:
    return YouTubeAPIProvider(client)