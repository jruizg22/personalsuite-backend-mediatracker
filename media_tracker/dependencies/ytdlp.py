from media_tracker.integrations.youtube.ytdlp_client import YTDLPClient


def get_ytdlp_client() -> YTDLPClient:
    return YTDLPClient()