from datetime import date
from enum import Enum
from typing import List

from sqlmodel import SQLModel, Field, Relationship

from ..constants import TITLE_MAX_LENGTH, LANGUAGE_CODE_MAX_LENGTH


class MediaType(str, Enum):
    """Enum for media types."""
    MOVIE = 'movie'
    TV_SHOW = 'tv_show'
    OTHER = 'other'

class MediaBase(SQLModel):
    tmdb_id: int | None = Field(default=None, index=True)
    type: MediaType = Field(nullable=False)
    original_title: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)
    release_date: date | None = None

class Media(MediaBase, table=True):
    __tablename__ = "media"

    id: int | None = Field(default=None, primary_key=True)
    tv_show_episodes: List["TVShowEpisode"] = Relationship(back_populates="tv_show")
    translations: list["MediaTranslation"] = Relationship(back_populates="media")
    visualizations: list["MediaVisualization"] = Relationship(back_populates="media")

class MediaCreate(MediaBase):
    pass

class MediaPublic(MediaBase):
    id: int

class MediaUpdate(SQLModel):
    tmdb_id: int | None = None
    type: MediaType | None = None
    original_title: str | None = None
    release_date: date | None = None

class MediaTranslationBase(SQLModel):
    media_id: int = Field(foreign_key="media.id", primary_key=True)
    language_code: str = Field(primary_key=True, max_length=LANGUAGE_CODE_MAX_LENGTH)
    title: str

class MediaTranslation(MediaTranslationBase, table=True):
    __tablename__ = "media_translations"

    media: Media = Relationship(back_populates="translations")

class MediaTranslationCreate(MediaTranslationBase):
    pass

class MediaTranslationPublic(MediaTranslationBase):
    pass

class MediaTranslationUpdate(SQLModel):
    media_id: int | None = None
    language_code: str | None = None
    title: str | None = None

class MediaVisualizationBase(SQLModel):
    media_id: int = Field(foreign_key="media.id", index=True)
    visualization_date: date
    resume: int | None = None

class MediaVisualization(MediaVisualizationBase, table=True):
    __tablename__ = "media_visualizations"

    id: int | None = Field(default=None, primary_key=True)
    media: Media = Relationship(back_populates="visualizations")

class MediaVisualizationCreate(MediaVisualizationBase):
    pass

class MediaVisualizationPublic(MediaVisualizationBase):
    id: int

class MediaVisualizationUpdate(SQLModel):
    media_id: int | None = None
    visualization_date: date | None = None
    resume: int | None = None

# Media model combinations

class MediaVisualizationPublicWithMedia(MediaVisualizationPublic):
    media: MediaPublic

class MediaWithVisualizations(MediaPublic):
    visualizations: list[MediaVisualizationPublic] = []

class MediaTranslationPublicWithMedia(MediaTranslationPublic):
    media: MediaPublic

class MediaPublicWithTranslations(MediaPublic):
    translations: list[MediaTranslationPublic] = []

class MediaFull(MediaPublic):
    translations: list[MediaTranslationPublic] = []
    visualizations: list[MediaVisualizationPublic] = []

# End of Media model combinations