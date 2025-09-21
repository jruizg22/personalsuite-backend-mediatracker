from enum import Enum

class YTChannelView(str, Enum):
    BASIC = 'basic'
    WITH_VIDEOS = 'with_videos'
    WITH_PLAYLISTS = 'with_playlists'
    FULL = 'full'

class YTVideoView(str, Enum):
    BASIC = 'basic'
    WITH_VISUALIZATIONS = 'with_visualizations'
    WITH_PLAYLISTS = 'with_playlists'
    WITH_CHANNEL = 'with_channel'
    FULL = 'full'