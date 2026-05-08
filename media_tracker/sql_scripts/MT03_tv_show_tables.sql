/*
This script defines the tables for the "tv_show_episodes" entities within the media tracking module.
This script is designed for PostgreSQL.
*/

BEGIN;

/*
Table to store TV show episodes.
*/
CREATE TABLE tv_show_episodes (
	id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	tv_show_id BIGINT, -- Foreign key to media table where type='tv_show'
	season_num INT, -- Season number
	episode_num INT, -- Episode number
	original_title titleLength NOT NULL, -- Original title of the episode
	FOREIGN KEY (tv_show_id) REFERENCES media(id) ON DELETE CASCADE ON UPDATE CASCADE
);

/*
Indexes to optimize queries on tv_show_episodes table.
*/
CREATE INDEX idx_tv_show_episodes_tv_show_id ON tv_show_episodes(tv_show_id);
CREATE INDEX idx_tv_show_episodes_tmdb_id ON tv_show_episodes(tmdb_id);
CREATE INDEX idx_tv_show_episodes_original_title ON tv_show_episodes(original_title);

/*
Table to store translations for TV show episode titles in different languages.
*/
CREATE TABLE tv_show_episode_translations (
    episode_id BIGINT, -- Foreign key to tv_show_episodes table
    language_code languageCode, -- Locale codes (BCP 47) (e.g., 'en-US', 'es-ES')
    title titleLength NOT NULL, -- Translated title
    PRIMARY KEY (episode_id, language_code),
    FOREIGN KEY (episode_id) REFERENCES tv_show_episodes(id) ON DELETE CASCADE ON UPDATE CASCADE
);

/*
Indexes to optimize queries on tv_show_episode_translations table.
*/
CREATE INDEX idx_tv_show_episode_translations_episode_id ON tv_show_episode_translations(episode_id);
CREATE INDEX idx_tv_show_episode_translations_title ON tv_show_episode_translations(title);

/*
Table to track visualizations of TV show episodes.
*/
CREATE TABLE tv_show_episode_visualizations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    episode_id BIGINT, -- Foreign key to tv_show_episodes table
    visualization_date DATE NOT NULL, -- Date of visualization
	resume INT DEFAULT NULL CHECK (resume >= 0), -- Resume time (in seconds) if applicable. If NULL, it means the episode was watched completely.
    FOREIGN KEY (episode_id) REFERENCES tv_show_episodes(id) ON DELETE CASCADE ON UPDATE CASCADE
);

/*
Indexes to optimize queries on tv_show_episode_visualizations table.
*/
CREATE INDEX idx_tv_show_episode_visualizations_episode_id ON tv_show_episode_visualizations(episode_id);

/*
Function that will be used in a trigger to ensure only TV shows have episodes.
*/
CREATE OR REPLACE FUNCTION check_tv_show()
RETURNS TRIGGER AS $$
DECLARE
    media_type media_type;
BEGIN
    -- Get the related media type
    SELECT type INTO media_type
    FROM media
    WHERE id = NEW.media_id;

    -- Validate that it's a 'tv_show'
    IF media_type IS NULL THEN
        RAISE EXCEPTION 'Media with id % not found', NEW.tv_show_id;
    ELSIF media_type <> 'tv_show' THEN
        RAISE EXCEPTION 'A TV episode can not be inserted into a media that is not a TV show (id: %)', NEW.media_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

/*
Trigger to validate that TV show episodes can not be inserted for a media that is not a TV show.
*/
CREATE TRIGGER tv_show_episode_insert_trigger
BEFORE INSERT OR UPDATE ON tv_show_episodes
FOR EACH ROW
EXECUTE FUNCTION check_tv_show();

COMMIT;