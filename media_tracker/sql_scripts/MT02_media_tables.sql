/*
This script defines the tables for the "media" entities within the media tracking module.
This script is designed for PostgreSQL.
*/

BEGIN;

/*
Table definitions for tracking movies, TV shows, etc.
*/
CREATE TABLE media (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tmdb_id BIGINT, -- The Movie Database (TMDb) ID
    type media_type NOT NULL, -- Type of media
    original_title titleLength NOT NULL, -- Original title of the media
    release_date DATE -- Release date of the media

    /*
    According to TMDB, their ids are only unique within each namespace.
    Which means, there can not be two movies with the same id,
    but there can be a movie and a TV show with the same id.
    */
    CONSTRAINT unique_media_tmdb_type UNIQUE (tmdb_id, type)
);

/*
Indexes to optimize queries on media table.
*/
CREATE INDEX idx_media_tmdb_id ON media(tmdb_id);
CREATE INDEX idx_media_original_title ON media(original_title);

/*
Table to store translations for media titles in different languages.
*/
CREATE TABLE media_translations (
    media_id BIGINT, -- Foreign key to media table
    language_code languageCode, -- Locale codes (BCP 47) (e.g., 'en-US', 'es-ES')
    title titleLength NOT NULL, -- Translated title
    PRIMARY KEY (media_id, language_code),
    FOREIGN KEY (media_id) REFERENCES media(id)
);

/*
Indexes to optimize queries on media and media_translations tables.
*/
CREATE INDEX idx_media_translations_media_id ON media_translations(media_id);

/*
Table to track visualizations of media.
*/
CREATE TABLE media_visualizations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    media_id BIGINT, -- Foreign key to media table
    visualization_date DATE NOT NULL, -- Date of visualization
    resume INT DEFAULT NULL, -- Resume time (in seconds) if applicable. If NULL, it means the media was watched completely.
    FOREIGN KEY (media_id) REFERENCES media(id)
);

/*
Index to optimize queries on media_id in media_visualizations table.
*/
CREATE INDEX idx_media_visualizations_id ON media_visualizations(media_id);

COMMIT;