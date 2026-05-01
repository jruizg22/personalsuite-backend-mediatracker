from datetime import datetime

from pydantic import BaseModel


class YouTubeChannelDTO(BaseModel):
    id: str
    name: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    url: str | None = None

class YouTubeChannelMetadata(BaseModel):
    id: str
    title: str
    description: str | None = None
    published_at: datetime | None = None
    thumbnail_url: str | None = None

class YouTubeChannelMetadataResult(BaseModel):
    data: YouTubeChannelDTO | None = None
    error: str | None = None
    error_type: str | None = None

class MetadataError(BaseModel):
    type: str | None
    message: str | None