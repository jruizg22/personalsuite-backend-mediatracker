from enum import Enum

class YTChannelView(str, Enum):
    BASIC = 'basic'
    WITH_VIDEOS = 'with_videos'
    WITH_PLAYLISTS = 'with_playlists'