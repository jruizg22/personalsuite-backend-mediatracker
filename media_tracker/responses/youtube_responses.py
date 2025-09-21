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