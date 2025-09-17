from datetime import date
from enum import Enum
from typing import List

from sqlmodel import SQLModel, Field, Relationship

from ..constants import TITLE_MAX_LENGTH, LANGUAGE_CODE_MAX_LENGTH


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

class MediaVisualizationPublicWithMedia(MediaVisualizationPublic):
    """Model combining MediaVisualizationPublic with its associated Media."""
    media: MediaPublic

class MediaWithVisualizations(MediaPublic):
    """Model combining MediaPublic with its associated visualizations."""
    visualizations: list[MediaVisualizationPublic] = []

class MediaTranslationPublicWithMedia(MediaTranslationPublic):
    """Model combining MediaTranslationPublic with its associated Media."""
    media: MediaPublic

class MediaPublicWithTranslations(MediaPublic):
    """Model combining MediaPublic with its associated translations."""
    translations: list[MediaTranslationPublic] = []

class MediaFull(MediaPublic):
    """Comprehensive model combining MediaPublic with translations and visualizations."""
    translations: list[MediaTranslationPublic] = []
    visualizations: list[MediaVisualizationPublic] = []

class MediaFullWithTVShowEpisodes(MediaFull):
    """Comprehensive model combining MediaFull with related TV show episodes."""
    tv_show_episodes: list["TVShowEpisodePublic"] = []
