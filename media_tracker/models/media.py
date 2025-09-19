from datetime import date
from enum import Enum
from typing import List, Union, TypeAlias

from sqlmodel import SQLModel, Field, Relationship

from ..constants import TITLE_MAX_LENGTH, LANGUAGE_CODE_MAX_LENGTH

class MediaView(str, Enum):
    """
    Enum representing different views for media retrieval.

    Attributes:
        BASIC: Basic view with minimal fields.
        WITH_VISUALIZATIONS: View including associated visualizations.
        WITH_TRANSLATIONS: View including associated translations.
        FULL: Full view with all related data.
        FULL_WITH_TV_SHOW_EPISODES: Full view including TV show episodes.
    """
    BASIC = 'basic'
    WITH_VISUALIZATIONS = 'with_visualizations'
    WITH_TRANSLATIONS = 'with_translations'
    FULL = 'full'
    FULL_WITH_TV_SHOW_EPISODES = 'full_with_tv_show_episodes'

class MediaType(str, Enum):
    """
    Enum representing different types of media.

    Attributes:
        MOVIE: Represents a movie.
        TV_SHOW: Represents a TV show.
        OTHER: Represents any other type of media.
    """
    MOVIE = 'movie'
    TV_SHOW = 'tv_show'
    OTHER = 'other'

# --- Media models ---

class MediaBase(SQLModel):
    """
    Base model for Media with common fields.

    Attributes:
        tmdb_id (int | None): Optional TMDB identifier for the media.
        type (MediaType): The type of media (movie, TV show, etc.).
        original_title (str): The original title of the media.
        release_date (date | None): Optional release date of the media.
    """
    tmdb_id: int | None = Field(default=None, index=True)
    type: MediaType = Field(nullable=False)
    original_title: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)
    release_date: date | None = None

class Media(MediaBase, table=True):
    """
    Database model representing media entries.

    Inherits from MediaBase and adds:
        id (int | None): Primary key.
        tv_show_episodes (List["TVShowEpisode"]): Relationship to episodes if TV show.
        translations (list["MediaTranslation"]): Related translations for the media.
        visualizations (list["MediaVisualization"]): Related visualization records.
    """
    __tablename__ = "media"

    id: int | None = Field(default=None, primary_key=True)
    tv_show_episodes: List["TVShowEpisode"] = Relationship(back_populates="tv_show")
    translations: list["MediaTranslation"] = Relationship(back_populates="media")
    visualizations: list["MediaVisualization"] = Relationship(back_populates="media")

class MediaCreate(MediaBase):
    """Model for creating a new Media entry."""
    pass

class MediaPublic(MediaBase):
    """
    Model for exposing Media data publicly.

    Inherits from MediaBase and adds:
        id (int): The unique identifier of the media.
    """
    id: int

class MediaUpdate(SQLModel):
    """Model for updating Media entries; all fields optional."""
    tmdb_id: int | None = None
    type: MediaType | None = None
    original_title: str | None = None
    release_date: date | None = None

# --- MediaTranslation models ---

class MediaTranslationBase(SQLModel):
    """
    Base model for Media translations.

    Attributes:
        media_id (int): Foreign key to Media.id.
        language_code (str): Language code of the translation.
        title (str): Translated title of the media.
    """
    media_id: int = Field(foreign_key="media.id", primary_key=True)
    language_code: str = Field(primary_key=True, max_length=LANGUAGE_CODE_MAX_LENGTH)
    title: str

class MediaTranslation(MediaTranslationBase, table=True):
    """
    Database model representing media translations.

    Inherits from MediaTranslationBase and adds:
        media (Media): Relationship back to the Media entry.
    """
    __tablename__ = "media_translations"

    media: Media = Relationship(back_populates="translations")

class MediaTranslationCreate(MediaTranslationBase):
    """Model for creating a new MediaTranslation entry."""
    pass

class MediaTranslationPublic(MediaTranslationBase):
    """Model for exposing MediaTranslation data publicly."""
    pass

class MediaTranslationUpdate(SQLModel):
    """Model for updating MediaTranslation entries; all fields optional."""
    media_id: int | None = None
    language_code: str | None = None
    title: str | None = None

# --- MediaVisualization models ---

class MediaVisualizationBase(SQLModel):
    """
    Base model for Media visualizations.

    Attributes:
        media_id (int): Foreign key to Media.id.
        visualization_date (date): Date when media was visualized.
        resume (int | None): Optional resume point in seconds, None indicates full visualization.
    """
    media_id: int = Field(foreign_key="media.id", index=True)
    visualization_date: date
    resume: int | None = None

class MediaVisualization(MediaVisualizationBase, table=True):
    """
    Database model representing media visualizations.

    Inherits from MediaVisualizationBase and adds:
        id (int | None): Primary key.
        media (Media): Relationship back to the Media entry.
    """
    __tablename__ = "media_visualizations"

    id: int | None = Field(default=None, primary_key=True)
    media: Media = Relationship(back_populates="visualizations")

class MediaVisualizationCreate(MediaVisualizationBase):
    """Model for creating a new MediaVisualization entry."""
    pass

class MediaVisualizationPublic(MediaVisualizationBase):
    """
    Model for exposing MediaVisualization data publicly.

    Inherits from MediaVisualizationBase and adds:
        id (int): The unique identifier of the visualization record.
    """
    id: int

class MediaVisualizationUpdate(SQLModel):
    """Model for updating MediaVisualization entries; all fields optional."""
    media_id: int | None = None
    visualization_date: date | None = None
    resume: int | None = None

# --- Combined Media models for nested relationships ---

class MediaPublicWithVisualizations(MediaPublic):
    """Model combining MediaPublic with its associated visualizations."""
    visualizations: list[MediaVisualizationPublic] = []

class MediaPublicWithTranslations(MediaPublic):
    """Model combining MediaPublic with its associated translations."""
    translations: list[MediaTranslationPublic] = []

class MediaVisualizationPublicWithMedia(MediaVisualizationPublic):
    """Model combining MediaVisualizationPublic with its associated Media."""
    media: MediaPublic

class MediaTranslationPublicWithMedia(MediaTranslationPublic):
    """Model combining MediaTranslationPublic with its associated Media."""
    media: MediaPublic

class MediaFull(MediaPublic):
    """Comprehensive model combining MediaPublic with translations and visualizations."""
    translations: list[MediaTranslationPublic] = []
    visualizations: list[MediaVisualizationPublic] = []

class MediaFullWithTVShowEpisodes(MediaFull):
    """Comprehensive model combining MediaFull with related TV show episodes."""
    tv_show_episodes: list["TVShowEpisodePublic"] = []

# --- TV Show Episode models ---

class TVShowEpisodeBase(SQLModel):
    """
    Base model for a TV show episode.

    Attributes:
        tv_show_id (int): Foreign key to the parent TV show (Media.id).
        tmdb_id (int | None): Optional TMDB identifier for the episode.
        season_num (int | None): Season number of the episode.
        episode_num (int | None): Episode number within the season.
        original_title (str): Original title of the episode.
    """
    tv_show_id: int = Field(foreign_key="media.id", index=True)
    tmdb_id: int | None = Field(default=None, index=True)
    season_num: int | None = None
    episode_num: int | None = None
    original_title: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)

class TVShowEpisode(TVShowEpisodeBase, table=True):
    """
    Database model representing a TV show episode.

    Inherits from TVShowEpisodeBase and adds:
        id (int | None): Primary key.
        tv_show (Media): Relationship to the parent TV show (Media).
        translations (list["TVShowEpisodeTranslation"]): Related translations for the episode.
        visualizations (list["TVShowEpisodeVisualization"]): Related visualization records.
    """
    __tablename__ = "tv_show_episodes"

    id: int | None = Field(default=None, primary_key=True)
    tv_show: Media = Relationship(back_populates="tv_show_episodes")
    translations: list["TVShowEpisodeTranslation"] = Relationship(back_populates="episode")
    visualizations: list["TVShowEpisodeVisualization"] = Relationship(back_populates="episode")

class TVShowEpisodeCreate(TVShowEpisodeBase):
    """Model for creating a new TV show episode."""
    pass

class TVShowEpisodePublic(TVShowEpisodeBase):
    """
    Public model for a TV show episode.

    Inherits from TVShowEpisodeBase and adds:
        id (int): Primary key.
    """
    id: int

class TVShowEpisodeUpdate(SQLModel):
    """Model for updating a TV show episode; all fields are optional."""
    tv_show_id: int | None = None
    tmdb_id: int | None = None
    season_num: int | None = None
    episode_num: int | None = None
    original_title: str | None = None

# --- TV Show Episode Translation models ---

class TVShowEpisodeTranslationBase(SQLModel):
    """
    Base schema for a TV show episode translation.

    Attributes:
        episode_id (int): Foreign key to TVShowEpisode.id.
        language_code (str): Language code of the translation.
        title (str): Translated title of the episode.
    """
    episode_id: int = Field(foreign_key="tv_show_episodes.id", primary_key=True, index=True)
    language_code: str = Field(primary_key=True, max_length=LANGUAGE_CODE_MAX_LENGTH)
    title: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)

class TVShowEpisodeTranslation(TVShowEpisodeTranslationBase, table=True):
    """
    Database model representing a TV show episode translation.

    Inherits from TVShowEpisodeTranslationBase and adds:
        episode (TVShowEpisode): Relationship to the associated TV show episode.
    """
    __tablename__ = "tv_show_episode_translations"

    episode: TVShowEpisode = Relationship(back_populates="translations")

class TVShowEpisodeTranslationCreate(TVShowEpisodeTranslationBase):
    """Model for creating a new TV show episode translation."""
    pass

class TVShowEpisodeTranslationPublic(TVShowEpisodeTranslationBase):
    """Model for exposing TV show episode translation data publicly."""
    pass

class TVShowEpisodeTranslationUpdate(SQLModel):
    """Model for updating TV show episode translations; all fields optional."""
    episode_id: int | None = None
    language_code: str | None = None
    title: str | None = None

# --- TV Show Episode Visualization models ---

class TVShowEpisodeVisualizationBase(SQLModel):
    """
    Base model for a TV show episode visualization.

    Attributes:
        episode_id (int): Foreign key to TVShowEpisode.id.
        visualization_date (date): Date when the episode was visualized.
        resume (int | None): Optional resume point in seconds, None indicates full visualization.
    """
    episode_id: int = Field(foreign_key="tv_show_episodes.id", index=True)
    visualization_date: date
    resume: int | None = None

class TVShowEpisodeVisualization(TVShowEpisodeVisualizationBase, table=True):
    """
    Database model representing a TV show episode visualization.

    Inherits from TVShowEpisodeVisualizationBase and adds:
        id (int | None): Primary key.
        episode (TVShowEpisode): Relationship to the associated TV show episode.
    """
    __tablename__ = "tv_show_episode_visualizations"

    id: int | None = Field(default=None, primary_key=True)
    episode: TVShowEpisode = Relationship(back_populates="visualizations")

class TVShowEpisodeVisualizationCreate(TVShowEpisodeVisualizationBase):
    """Model for creating a new TV show episode visualization."""
    pass

class TVShowEpisodeVisualizationPublic(TVShowEpisodeVisualizationBase):
    """
    Model for exposing TV show episode visualization data publicly.

    Inherits from TVShowEpisodeVisualizationBase and adds:
        id (int): Primary key.
    """
    id: int

class TVShowEpisodeVisualizationUpdate(SQLModel):
    """Model for updating TV show episode visualizations; all fields optional."""
    episode_id: int | None = None
    visualization_date: date | None = None
    resume: int | None = None

# --- Combined models for TV Show Episodes ---

class MediaPublicWithTVShowEpisodes(MediaPublic):
    """MediaPublic model including related TV show episodes."""
    tv_show_episodes: list[TVShowEpisodePublic] = []

class TVShowEpisodeVisualizationPublicWithTVShow(MediaPublic):
    """Combines TVShowEpisodeVisualizationPublic with its associated TV show (Media)."""
    tv_show: MediaPublic

class TVShowEpisodeVisualizationPublicWithEpisode(TVShowEpisodeVisualizationPublic):
    """Combines TVShowEpisodeVisualizationPublic with its associated episode."""
    episode: TVShowEpisodePublic

class TVShowEpisodeWithVisualizations(TVShowEpisodePublic):
    """Combines TVShowEpisodePublic with its associated visualizations."""
    visualizations: list[TVShowEpisodeVisualizationPublic] = []

class TVShowEpisodeTranslationPublicWithEpisode(TVShowEpisodeTranslationPublic):
    """Combines TVShowEpisodeTranslationPublic with its associated episode."""
    episode: TVShowEpisodePublic

class TVShowEpisodePublicWithTranslations(TVShowEpisodePublic):
    """Combines TVShowEpisodePublic with its associated translations."""
    translations: list[TVShowEpisodeTranslationPublic] = []

class TVShowEpisodeFull(TVShowEpisodePublic):
    """Comprehensive model combining TVShowEpisodePublic with translations and visualizations."""
    translations: list[TVShowEpisodeTranslationPublic] = []
    visualizations: list[TVShowEpisodeVisualizationPublic] = []

class TVShowEpisodeFullWithTVShow(TVShowEpisodeFull):
    """Comprehensive model combining TVShowEpisodeFull with its parent TV show (Media)."""
    tv_show: MediaPublic


# --- Rebuilding models with forward references ---

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