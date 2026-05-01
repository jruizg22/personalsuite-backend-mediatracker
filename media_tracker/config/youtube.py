import os


class YouTubeConfig:
    API_KEY: str = os.getenv("YT_API_KEY", "")
    BASE_URL: str = "https://www.googleapis.com/youtube/v3"