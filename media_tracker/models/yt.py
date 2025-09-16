from datetime import date

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

from modules.media_tracker.constants import CHANNEL_ID_MAX_LENGTH, LINK_MAX_LENGTH, TITLE_MAX_LENGTH, \
    VIDEO_ID_MAX_LENGTH, PLAYLIST_ID_MAX_LENGTH


class YTChannelBase(SQLModel):
    name: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)
    url: str = Field(max_length=LINK_MAX_LENGTH, index=True)
    created_at: date | None = None
    description: str | None = None

class YTChannel(YTChannelBase, table=True):
    __tablename__ = "yt_channels"

    id: str = Field(max_length=CHANNEL_ID_MAX_LENGTH, primary_key=True)
    videos: list["YTVideo"] = Relationship(back_populates="channel")
    playlists: list["YTPlaylist"] = Relationship(back_populates="channel")

class YTChannelCreate(YTChannelBase):
    int: str

class YTChannelPublic(YTChannelBase):
    id: str

class YTChannelUpdate(SQLModel):
    name: str | None = None
    url: str | None = None
    created_at: date | None = None
    description: str | None = None

class YTVideoBase(SQLModel):
    channel_id: str = Field(foreign_key="yt_channels.id", max_length=CHANNEL_ID_MAX_LENGTH, index=True)
    title: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)
    published_at: date | None = None
    description: str | None = None
    url: str | None = Field(max_length=LINK_MAX_LENGTH)

class YTVideo(YTVideoBase, table=True):
    __tablename__ = "yt_videos"

    id: str = Field(max_length=VIDEO_ID_MAX_LENGTH, primary_key=True)
    channel: YTChannel = Relationship(back_populates="videos")
    visualizations: list["YTVideoVisualization"] = Relationship(back_populates="video")
    playlists: list["YTPlaylistVideo"] = Relationship(back_populates="video")

class YTVideoCreate(YTVideoBase):
    id: str

class YTVideoPublic(YTVideoBase):
    id: str

class YTVideoUpdate(SQLModel):
    title: str | None = None
    published_at: date | None = None
    description: str | None = None
    url: str | None = None

class YTVideoVisualizationBase(SQLModel):
    video_id: str = Field(foreign_key="yt_videos.id", max_length=VIDEO_ID_MAX_LENGTH, index=True)
    visualization_date: date
    resume: int | None = None

class YTVideoVisualization(YTVideoVisualizationBase, table=True):
    __tablename__ = "yt_video_visualizations"

    id: int | None = Field(default=None, primary_key=True)
    video: YTVideo = Relationship(back_populates="visualizations")

class YTVideoVisualizationCreate(YTVideoVisualizationBase):
    pass

class YTVideoVisualizationPublic(YTVideoVisualizationBase):
    id: int

class YTVideoVisualizationUpdate(SQLModel):
    video_id: str | None = None
    visualization_date: date | None = None
    resume: int | None = None

class YTPlaylistBase(SQLModel):
    channel_id: str = Field(foreign_key="yt_channels.id", max_length=CHANNEL_ID_MAX_LENGTH, index=True)
    title: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)
    url: str = Field(max_length=LINK_MAX_LENGTH)

class YTPlaylist(YTPlaylistBase, table=True):
    __tablename__ = "yt_playlists"

    id: str = Field(max_length=PLAYLIST_ID_MAX_LENGTH, primary_key=True)
    channel: YTChannel = Relationship(back_populates="playlists")

class YTPlaylistCreate(YTPlaylistBase):
    id: str

class YTPlaylistPublic(YTPlaylistBase):
    id: str

class YTPlaylistUpdate(SQLModel):
    channel_id: str | None = None
    title: str | None = None
    url: str | None = None

class YTPlaylistVideoBase(SQLModel):
    playlist_id: str = Field(foreign_key="yt_playlists.id", max_length=PLAYLIST_ID_MAX_LENGTH, index=True)
    video_id: str = Field(foreign_key="yt_videos.id", max_length=VIDEO_ID_MAX_LENGTH, index=True)
    position: int | None = None

class YTPlaylistVideo(YTPlaylistVideoBase, table=True):
    __tablename__ = "yt_playlist_videos"
    __table_args__ = (
        UniqueConstraint("playlist_id", "position", name="uq_playlist_position"),
    )

    id: int | None = Field(default=None, primary_key=True)
    playlist: YTPlaylist = Relationship(back_populates="videos")
    video: YTVideo = Relationship(back_populates="playlists")

# YouTube model combinations

class YTChannelPublicWithVideos(YTChannelPublic):
    videos: list[YTVideoPublic] = []

class YTChannelPublicWithPlaylists(YTChannelPublic):
    playlists: list[YTPlaylistPublic] = []

class YTChannelFull(YTChannelPublic):
    videos: list[YTVideoPublic] = []
    playlists: list[YTPlaylistPublic] = []

class YTVideoPublicWithChannel(YTVideoPublic):
    channel: YTChannelPublic

class YTVideoPublicWithVisualizations(YTVideoPublic):
    visualizations: list[YTVideoVisualizationPublic] = []

class YTVideoPublicWithPlaylists(YTVideoPublic):
    playlists: list[YTPlaylistPublic] = []

class YTVideoFull(YTVideoPublic):
    channel: YTChannelPublic
    visualizations: list[YTVideoVisualizationPublic] = []
    playlists: list[YTPlaylistPublic] = []

class YTPlaylistPublicWithChannel(YTPlaylistPublic):
    channel: YTChannelPublic

class YTPlaylistPublicWithVideos(YTPlaylistPublic):
    videos: list[YTVideoPublic] = []

class YTPlaylistFull(YTPlaylistPublic):
    channel: YTChannelPublic
    videos: list[YTVideoPublic] = []

# End of model combinations