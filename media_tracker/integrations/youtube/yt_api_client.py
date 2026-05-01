import httpx

from media_tracker.config.youtube import YouTubeConfig


class YouTubeAPIClient:

    def __init__(self, config: YouTubeConfig, http_client: httpx.Client):
        self.config = config
        self.http_client = http_client

    def get_channel(self, channel_id: str):

        response = self.http_client.get(
            f"{self.config.BASE_URL}/channels",
            params={
                "part": "snippet",
                "id": channel_id,
                "key": self.config.API_KEY
            }
        )

        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        return items[0] if items else None