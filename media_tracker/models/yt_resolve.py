from datetime import datetime
from typing import TypedDict

from pydantic import BaseModel

from media_tracker.models.yt_api import YouTubeChannelDTO, MetadataError


class YTResolvedChannel(YouTubeChannelDTO):
    metadata_error: MetadataError | None = None

class YTResolvedVideo(BaseModel):
    id: str
    title: str
    description: str | None = None
    published_at: datetime | None = None
    url: str | None = None
    channel: YTResolvedChannel | None = None

class YouTubeVideoDTO(BaseModel):
    id: str
    title: str
    description: str | None = None
    published_at: datetime | None = None
    url: str | None = None

    channel_id: str
    channel_name: str | None = None
    channel_url: str | None = None