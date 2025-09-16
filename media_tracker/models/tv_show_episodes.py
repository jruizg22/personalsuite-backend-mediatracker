from datetime import date

from sqlmodel import SQLModel, Field, Relationship

from modules.media_tracker.constants import TITLE_MAX_LENGTH, LANGUAGE_CODE_MAX_LENGTH
from modules.media_tracker.models.media import Media, MediaPublic


class TVShowEpisodeBase(SQLModel):
    tv_show_id: int = Field(foreign_key="media.id", index=True)
    tmdb_id: int | None = Field(default=None, index=True)
    season_num: int | None = None
    episode_num: int | None = None
    original_title: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)

class TVShowEpisode(TVShowEpisodeBase, table=True):
    __tablename__ = "tv_show_episodes"

    id: int | None = Field(default=None, primary_key=True)
    tv_show: Media = Relationship(back_populates="tv_show_episodes")
    translations: list["TVShowEpisodeTranslation"] = Relationship(back_populates="episode")
    visualizations: list["TVShowEpisodeVisualization"] = Relationship(back_populates="episode")

class TVShowEpisodeCreate(TVShowEpisodeBase):
    pass

class TVShowEpisodePublic(TVShowEpisodeBase):
    id: int

class TVShowEpisodeUpdate(SQLModel):
    tv_show_id: int | None = None
    tmdb_id: int | None = None
    season_num: int | None = None
    episode_num: int | None = None
    original_title: str | None = None

class TVShowEpisodeTranslationBase(SQLModel):
    episode_id: int = Field(foreign_key="tv_show_episodes.id", primary_key=True, index=True)
    language_code: str = Field(primary_key=True, max_length=LANGUAGE_CODE_MAX_LENGTH)
    title: str = Field(nullable=False, max_length=TITLE_MAX_LENGTH, index=True)

class TVShowEpisodeTranslation(TVShowEpisodeTranslationBase, table=True):
    __tablename__ = "tv_show_episode_translations"

    episode: TVShowEpisode = Relationship(back_populates="translations")

class TVShowEpisodeTranslationCreate(TVShowEpisodeTranslationBase):
    pass

class TVShowEpisodeTranslationPublic(TVShowEpisodeTranslationBase):
    pass

class TVShowEpisodeTranslationUpdate(SQLModel):
    episode_id: int | None = None
    language_code: str | None = None
    title: str | None = None

class TVShowEpisodeVisualizationBase(SQLModel):
    episode_id: int = Field(foreign_key="tv_show_episodes.id", index=True)
    visualization_date: date
    resume: int | None = None

class TVShowEpisodeVisualization(TVShowEpisodeVisualizationBase, table=True):
    __tablename__ = "tv_show_episode_visualizations"

    id: int | None = Field(default=None, primary_key=True)
    episode: TVShowEpisode = Relationship(back_populates="visualizations")

class TVShowEpisodeVisualizationCreate(TVShowEpisodeVisualizationBase):
    pass

class TVShowEpisodeVisualizationPublic(TVShowEpisodeVisualizationBase):
    id: int

class TVShowEpisodeVisualizationUpdate(SQLModel):
    episode_id: int | None = None
    visualization_date: date | None = None
    resume: int | None = None

# TV Show Episode model combinations

class MediaPublicWithTVShowEpisodes(MediaPublic):
    tv_show_episodes: list[TVShowEpisodePublic] = []

class TVShowEpisodeVisualizationPublicWithTVShow(MediaPublic):
    tv_show: MediaPublic

class TVShowEpisodeVisualizationPublicWithEpisode(TVShowEpisodeVisualizationPublic):
    episode: TVShowEpisodePublic

class TVShowEpisodeWithVisualizations(TVShowEpisodePublic):
    visualizations: list[TVShowEpisodeVisualizationPublic] = []

class TVShowEpisodeTranslationPublicWithEpisode(TVShowEpisodeTranslationPublic):
    episode: TVShowEpisodePublic

class TVShowEpisodePublicWithTranslations(TVShowEpisodePublic):
    translations: list[TVShowEpisodeTranslationPublic] = []

class TVShowEpisodeFull(TVShowEpisodePublic):
    translations: list[TVShowEpisodeTranslationPublic] = []
    visualizations: list[TVShowEpisodeVisualizationPublic] = []

# End of TV Show Episode model combinations