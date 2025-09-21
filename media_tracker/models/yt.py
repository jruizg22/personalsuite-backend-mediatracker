from datetime import date

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

from ..constants import CHANNEL_ID_MAX_LENGTH, LINK_MAX_LENGTH, TITLE_MAX_LENGTH, \
    VIDEO_ID_MAX_LENGTH, PLAYLIST_ID_MAX_LENGTH


# --- YouTube Channel models ---

class YTChannelBase(SQLModel):
    """
    Base model for a YouTube channel.

    Attributes:
        name (str): Name of the channel.
        url (str): Optional URL of the channel.
        created_at (date | None): Optional creation date of the channel.
        description (str | None): Optional description of the channel.
    """
    name: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)
    url: str = Field(max_length=LINK_MAX_LENGTH, index=True)
    created_at: date | None = None
    description: str | None = None

class YTChannel(YTChannelBase, table=True):
    """
    Database model representing a YouTube channel.

    Inherits from YTChannelBase and adds:
        id (str): Primary key, YouTube channel ID.
        videos (list["YTVideo"]): Relationship to videos in the channel.
        playlists (list["YTPlaylist"]): Relationship to playlists in the channel.
    """
    __tablename__ = "yt_channels"

    id: str = Field(max_length=CHANNEL_ID_MAX_LENGTH, primary_key=True)
    videos: list["YTVideo"] = Relationship(back_populates="channel")
    playlists: list["YTPlaylist"] = Relationship(back_populates="channel")

class YTChannelCreate(YTChannelBase):
    """
    Model for creating a new YouTube channel.

    Inherits from YTChannelBase and adds:
        id (str): YouTube channel ID.
    """
    int: str

class YTChannelPublic(YTChannelBase):
    """
    Model for exposing YouTube channel publicly.

    Inherits from YTChannelBase and adds:
        id (str): YouTube channel ID.
    """
    id: str

class YTChannelUpdate(SQLModel):
    """Model for updating a YouTube channel; all fields optional."""
    name: str | None = None
    url: str | None = None
    created_at: date | None = None
    description: str | None = None

# --- YouTube Video models ---

class YTVideoBase(SQLModel):
    """
    Base model for a YouTube video.

    Attributes:
        channel_id (str): Foreign key to YTChannel.id.
        title (str): Video title.
        published_at (date | None): Optional publication date.
        description (str | None): Optional description.
        url (str | None): Optional URL.
    """
    channel_id: str = Field(foreign_key="yt_channels.id", max_length=CHANNEL_ID_MAX_LENGTH, index=True)
    title: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)
    published_at: date | None = None
    description: str | None = None
    url: str | None = Field(max_length=LINK_MAX_LENGTH)

class YTVideo(YTVideoBase, table=True):
    """
    Database model representing a YouTube video.

    Inherits from YTVideoBase and adds:
        id (str): Primary key, YouTube video ID.
        channel (YTChannel): Relationship back to the channel.
        visualizations (list["YTVideoVisualization"]): Relationship to video visualizations.
        playlists (list["YTPlaylistVideo"]): Relationship to playlists containing the video.
    """
    __tablename__ = "yt_videos"

    id: str = Field(max_length=VIDEO_ID_MAX_LENGTH, primary_key=True)
    channel: YTChannel = Relationship(back_populates="videos")
    visualizations: list["YTVideoVisualization"] = Relationship(back_populates="video")
    playlists: list["YTPlaylistVideo"] = Relationship(back_populates="video")

class YTVideoCreate(YTVideoBase):
    """
    Model for creating a new YouTube video.

    Inherits from YTVideoBase and adds:
        id (str): YouTube video ID.
    """
    id: str

class YTVideoPublic(YTVideoBase):
    """
    Model for exposing YouTube video publicly.

    Inherits from YTVideoBase and adds:
        id (str): YouTube video ID.
    """
    id: str

class YTVideoUpdate(SQLModel):
    """Model for updating a YouTube video; all fields optional."""
    channel_id: str | None = None
    title: str | None = None
    published_at: date | None = None
    description: str | None = None
    url: str | None = None

# --- YouTube Video Visualization models ---

class YTVideoVisualizationBase(SQLModel):
    """
    Base schema for a video visualization.

    Attributes:
        video_id (str): Foreign key to YTVideo.id.
        visualization_date (date): Date when the video was viewed.
        resume (int | None): Optional resume point in seconds.
    """
    video_id: str = Field(foreign_key="yt_videos.id", max_length=VIDEO_ID_MAX_LENGTH, index=True)
    visualization_date: date
    resume: int | None = None

class YTVideoVisualization(YTVideoVisualizationBase, table=True):
    """
    Database model representing a video visualization.

    Inherits from YTVideoVisualizationBase and adds:
        id (int | None): Primary key.
        video (YTVideo): Relationship back to the video.
    """
    __tablename__ = "yt_video_visualizations"

    id: int | None = Field(default=None, primary_key=True)
    video: YTVideo = Relationship(back_populates="visualizations")

class YTVideoVisualizationCreate(YTVideoVisualizationBase):
    """Model for creating a new YTVideoVisualization entry."""
    pass

class YTVideoVisualizationPublic(YTVideoVisualizationBase):
    """
    Model for exposing YTVideoVisualization data publicly.

    Inherits from YTVideoVisualizationBase and adds:
        id (int): Primary key.
    """
    id: int

class YTVideoVisualizationUpdate(SQLModel):
    """Model for updating YTVideoVisualization entries; all fields optional."""
    video_id: str | None = None
    visualization_date: date | None = None
    resume: int | None = None

# --- YouTube Playlist models ---

class YTPlaylistBase(SQLModel):
    """
    Base schema for a YouTube playlist.

    Attributes:
        channel_id (str): Foreign key to YTChannel.id.
        title (str): Playlist title.
        url (str): Optional playlist URL.
    """
    channel_id: str = Field(foreign_key="yt_channels.id", max_length=CHANNEL_ID_MAX_LENGTH, index=True)
    title: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)
    url: str = Field(max_length=LINK_MAX_LENGTH)

class YTPlaylist(YTPlaylistBase, table=True):
    """
    Database model representing a YouTube playlist.

    Inherits from YTPlaylistBase and adds:
        id (str): Primary key, YouTube playlist ID.
        channel (YTChannel): Relationship back to the channel.
        videos (list["YTPlaylistVideo"]): Relationship to videos in the playlist.
    """
    __tablename__ = "yt_playlists"

    id: str = Field(max_length=PLAYLIST_ID_MAX_LENGTH, primary_key=True)
    channel: YTChannel = Relationship(back_populates="playlists")
    videos: list["YTPlaylistVideo"] = Relationship(back_populates="playlist")

class YTPlaylistCreate(YTPlaylistBase):
    """
    Model for creating a new YouTube playlist.

    Inherits from YTPlaylistBase and adds:
        id (str): YouTube playlist ID.
    """
    id: str

class YTPlaylistPublic(YTPlaylistBase):
    """
    Model for exposing YouTube playlist publicly.

    Inherits from YTPlaylistBase and adds:
        id (str): YouTube playlist ID.
    """
    id: str

class YTPlaylistUpdate(SQLModel):
    """Model for updating a YouTube playlist; all fields optional."""
    channel_id: str | None = None
    title: str | None = None
    url: str | None = None

# --- Playlist Video models (association table) ---

class YTPlaylistVideoBase(SQLModel):
    """
    Base schema for linking videos to playlists.

    Attributes:
        playlist_id (str): Foreign key to YTPlaylist.id.
        video_id (str): Foreign key to YTVideo.id.
        position (int | None): Optional position in the playlist.
    """
    playlist_id: str = Field(foreign_key="yt_playlists.id", max_length=PLAYLIST_ID_MAX_LENGTH, index=True)
    video_id: str = Field(foreign_key="yt_videos.id", max_length=VIDEO_ID_MAX_LENGTH, index=True)
    position: int | None = None

class YTPlaylistVideo(YTPlaylistVideoBase, table=True):
    """
    Database model linking videos to playlists.

    Unique constraint on (playlist_id, position) to ensure no duplicate positions in a playlist.

    Inherits from YTPlaylistVideoBase and adds:
        id (int | None): Primary key.
        playlist (YTPlaylist): Relationship back to the playlist.
        video (YTVideo): Relationship back to the video.
    """
    __tablename__ = "yt_playlist_videos"
    __table_args__ = (
        UniqueConstraint("playlist_id", "position", name="uq_playlist_position"),
    )

    id: int | None = Field(default=None, primary_key=True)
    playlist: YTPlaylist = Relationship(back_populates="videos")
    video: YTVideo = Relationship(back_populates="playlists")

class YTPlaylistVideoCreate(YTPlaylistVideoBase):
    """Model for creating a new YTPlaylistVideo entry."""
    pass

class YTPlaylistVideoPublic(YTPlaylistVideoBase):
    """
    Model for exposing YouTube playlist video publicly.

    Inherits from YTPlaylistVideoBase and adds:
        id (str): YouTube playlist video ID.
    """
    id: str

class YTPlaylistVideoUpdate(SQLModel):
    """Model for updating a YouTube playlist video; all fields optional."""
    playlist_id: str | None = None
    video_id: str | None = None
    position: int | None = None

# --- YouTube model combinations ---

class YTVideoPlaylistDetailed(SQLModel):
    """Model for exposing YouTube playlist with its channel publicly, with their position."""
    playlist: YTPlaylistPublic
    position: int | None = None

class YTPlaylistVideoDetailed(SQLModel):
    """Video inside a playlist, with its position."""
    video: YTVideoPublic
    position: int | None = None

class YTChannelPublicWithVideos(YTChannelPublic):
    """Model for exposing YouTube channel with its videos publicly."""
    videos: list[YTVideoPublic] = []

class YTChannelPublicWithPlaylists(YTChannelPublic):
    """Model for exposing YouTube channel with its playlists publicly."""
    playlists: list[YTPlaylistPublic] = []

class YTChannelFull(YTChannelPublic):
    """Model for exposing YouTube channel with its videos and playlists publicly."""
    videos: list[YTVideoPublic] = []
    playlists: list[YTPlaylistPublic] = []

class YTVideoPublicWithChannel(YTVideoPublic):
    """Model for exposing YouTube video with its channel publicly."""
    channel: YTChannelPublic

class YTVideoPublicWithVisualizations(YTVideoPublic):
    """Model for exposing YouTube video with its visualizations publicly."""
    visualizations: list[YTVideoVisualizationPublic] = []

class YTVideoPublicWithPlaylists(YTVideoPublic):
    """Model for exposing YouTube video with its playlists publicly."""
    playlists: list[YTVideoPlaylistDetailed] = []

class YTVideoVisualizationPublicWithVideo(YTVideoVisualizationPublic):
    """Model for exposing YouTube video visualization with its video."""
    video: YTVideoPublic

class YTVideoFull(YTVideoPublic):
    """Model for exposing YouTube video with its channel, visualizations, and playlists publicly."""
    channel: YTChannelPublic
    visualizations: list[YTVideoVisualizationPublic] = []
    playlists: list[YTVideoPlaylistDetailed] = []

class YTPlaylistPublicWithChannel(YTPlaylistPublic):
    """Model for exposing YouTube playlist with its channel publicly."""
    channel: YTChannelPublic

class YTPlaylistPublicWithVideos(YTPlaylistPublic):
    """Model for exposing YouTube playlist with its videos publicly."""
    videos: list[YTPlaylistVideoDetailed] = []

class YTPlaylistFull(YTPlaylistPublic):
    """Model for exposing YouTube playlist with its channel and videos publicly."""
    channel: YTChannelPublic
    videos: list[YTPlaylistVideoDetailed] = []