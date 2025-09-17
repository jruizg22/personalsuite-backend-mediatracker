from datetime import date

from sqlmodel import SQLModel, Field, Relationship

from ..constants import TITLE_MAX_LENGTH, LANGUAGE_CODE_MAX_LENGTH
from .media import Media, MediaPublic


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