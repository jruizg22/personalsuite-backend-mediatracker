from datetime import datetime
from pydantic import BaseModel

class YTResolvedChannel(BaseModel):
    id: str
    name: str | None = None
    created_at: datetime | None = None
    description: str | None = None
    url: str | None = None

class YTResolvedVideo(BaseModel):
    id: str
    title: str
    description: str | None = None
    published_at: datetime | None = None
    url: str
    channel_id: str | None = None