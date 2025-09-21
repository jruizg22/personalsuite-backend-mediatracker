from typing import TypeAlias, Union

from media_tracker.models.yt import *

YTChannelPublic.model_rebuild()
YTChannelPublicWithVideos.model_rebuild()
YTChannelPublicWithPlaylists.model_rebuild()
YTChannelFull.model_rebuild()

YTChannelResponse: TypeAlias = Union[
    list[YTChannelPublic],
    list[YTChannelPublicWithVideos],
    list[YTChannelPublicWithPlaylists],
    list[YTChannelFull]
]

YTChannelResponseItem: TypeAlias = Union[
    YTChannelPublic,
    YTChannelPublicWithVideos,
    YTChannelPublicWithPlaylists,
    YTChannelFull
]

YTVideoPublic.model_rebuild()
YTVideoPublicWithVisualizations.model_rebuild()
YTVideoPublicWithPlaylists.model_rebuild()
YTVideoPublicWithChannel.model_rebuild()
YTVideoFull.model_rebuild()

YTVideoResponse: TypeAlias = Union[
    list[YTVideoPublic],
    list[YTVideoPublicWithVisualizations],
    list[YTVideoPublicWithPlaylists],
    list[YTVideoPublicWithChannel],
    list[YTVideoFull]
]

YTVideoResponseItem: TypeAlias = Union[
    YTVideoPublic,
    YTVideoPublicWithVisualizations,
    YTVideoPublicWithPlaylists,
    YTVideoFull
]

YTVideoVisualizationPublic.model_rebuild()
YTVideoVisualizationPublicWithVideo.model_rebuild()

YTVideoVisualizationResponse: TypeAlias = Union[
    list[YTVideoVisualizationPublic],
    list[YTVideoVisualizationPublicWithVideo]
]

YTVideoVisualizationResponseItem: TypeAlias = Union[
    YTVideoVisualizationPublic,
    YTVideoVisualizationPublicWithVideo
]

YTPlaylistPublic.model_rebuild()
YTPlaylistPublicWithVideos.model_rebuild()
YTPlaylistPublicWithChannel.model_rebuild()
YTPlaylistFull.model_rebuild()

YTPlaylistResponse: TypeAlias = Union[
    list[YTPlaylistPublic],
    list[YTPlaylistPublicWithVideos],
    list[YTPlaylistPublicWithChannel],
    list[YTPlaylistFull]
]

YTPlaylistResponseItem: TypeAlias = Union[
    YTPlaylistPublic,
    YTPlaylistPublicWithVideos,
    YTPlaylistPublicWithChannel,
    YTPlaylistFull
]