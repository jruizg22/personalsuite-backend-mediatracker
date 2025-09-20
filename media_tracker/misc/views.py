from enum import Enum

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

class MediaTranslationView(str, Enum):
    BASIC = 'basic'
    WITH_MEDIA = 'with_media'

class MediaVisualizationView(str, Enum):
    BASIC = 'basic'
    WITH_MEDIA = 'with_media'

class TVShowEpisodeView(str, Enum):
    BASIC = 'basic'
    WITH_TV_SHOW = 'with_tv_show'
    WITH_TRANSLATIONS = 'with_translations'
    WITH_VISUALIZATIONS = 'with_visualizations'

class TVShowEpisodeTranslationView(str, Enum):
    BASIC = 'basic'
    WITH_EPISODE = 'with_episode'

class TVShowEpisodeVisualizationView(str, Enum):
    BASIC = 'basic'
    WITH_EPISODE = 'with_episode'