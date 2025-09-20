# --- Rebuilding models with forward references ---
from typing import TypeAlias, Union

from media_tracker.models.media import MediaPublic, MediaPublicWithTranslations, MediaPublicWithVisualizations, \
    MediaFull, TVShowEpisodePublic, MediaFullWithTVShowEpisodes, MediaTranslationPublic, \
    MediaTranslationPublicWithMedia, MediaVisualizationPublic, MediaVisualizationPublicWithMedia

# These calls to .model_rebuild() force Pydantic/SQLModel to "resolve"
# type annotations declared as strings (forward references).
# They are necessary when we have models that reference each other
# (e.g., MediaFullWithTVShowEpisodes → TVShowEpisodePublic)
# and are defined in separate modules or have circular dependencies.

MediaPublic.model_rebuild()
MediaPublicWithTranslations.model_rebuild()
MediaPublicWithVisualizations.model_rebuild()
MediaFull.model_rebuild()
TVShowEpisodePublic.model_rebuild()
MediaFullWithTVShowEpisodes.model_rebuild()

# --- TypeAlias for endpoint responses ---

# MediaResponse is a union of several possible output models.
# It allows us to declare, in a single alias, the different "views" of a Media,
# so endpoints can use MediaResponse as response_model
# and indicate that they will return a list of any of these variants.

MediaResponse: TypeAlias = Union[
    list[MediaPublic],
    list[MediaPublicWithTranslations],
    list[MediaPublicWithVisualizations],
    list[MediaFull],
    list[MediaFullWithTVShowEpisodes]
]

# MediaResponseItem for individual objects

MediaResponseItem: TypeAlias = Union[
    MediaPublic,
    MediaPublicWithTranslations,
    MediaPublicWithVisualizations,
    MediaFull,
    MediaFullWithTVShowEpisodes
]

MediaTranslationPublic.model_rebuild()
MediaTranslationPublicWithMedia.model_rebuild()

MediaTranslationResponse: TypeAlias = Union[
    list[MediaTranslationPublic],
    list[MediaTranslationPublicWithMedia]
]

MediaTranslationResponseItem: TypeAlias = Union[
    MediaTranslationPublic,
    MediaTranslationPublicWithMedia
]

MediaVisualizationPublic.model_rebuild()
MediaVisualizationPublicWithMedia.model_rebuild()

MediaVisualizationResponse: TypeAlias = Union[
    list[MediaVisualizationPublic],
    list[MediaVisualizationPublicWithMedia]
]

MediaVisualizationResponseItem: TypeAlias = Union[
    MediaVisualizationPublic,
    MediaVisualizationPublicWithMedia
]