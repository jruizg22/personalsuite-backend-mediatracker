/*
This script defines the SQL tables for tracking YouTube channels, videos, visualizations, and playlists.
This script is designed for PostgreSQL.
*/

BEGIN;

/*
Table definitions for tracking YouTube channels.
*/
CREATE TABLE yt_channels (
	id channelId PRIMARY KEY,
	name VARCHAR(255) NOT NULL, -- Channel name
    url link, -- Channel URL
    creation_date DATE, -- Channel creation date
    description TEXT, -- Channel description
    thumbnail_url TEXT -- Url to channel thumbnail
);

/*
Index on channel name for faster searches.
*/
CREATE INDEX idx_yt_channels_name ON yt_channels(name);

/*
Table definitions for tracking YouTube videos.
*/
CREATE TABLE yt_videos (
	id videoId PRIMARY KEY,
	channel_id channelId NULL, -- Foreign key to yt_channels table
	title VARCHAR(255) NOT NULL, -- Video title
	published_at DATE, -- Video release date
	description TEXT, -- Video description
    url link, -- Video URL
	FOREIGN KEY (channel_id) REFERENCES yt_channels(id) ON DELETE SET NULL ON UPDATE CASCADE
);

/*
Indexes on channel_id and title for faster searches.
*/
CREATE INDEX idx_yt_videos_channel_id ON yt_videos(channel_id);
CREATE INDEX idx_yt_videos_title ON yt_videos(title);

/*
Table to track visualizations of YouTube videos.
*/
CREATE TABLE yt_video_visualizations (
	id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	video_id videoId, -- Foreign key to yt_videos table
	visualization_date DATE NOT NULL, -- Date of visualization
	resume INT DEFAULT NULL CHECK (resume >= 0), -- Resume time (in seconds) if applicable. If NULL, it means the video was watched completely.
	FOREIGN KEY (video_id) REFERENCES yt_videos(id) ON DELETE CASCADE ON UPDATE CASCADE
);

/*
Index on video_id for faster searches.
*/
CREATE INDEX idx_yt_video_visualizations_video_id ON yt_video_visualizations(video_id);

/*
Table to track playlists made by YouTube channels.
*/
CREATE TABLE yt_playlists (
	id playlistId PRIMARY KEY,
	channel_id channelId NULL, -- Foreign key to yt_channels table
	title VARCHAR(255) NOT NULL, -- Playlist title
	description TEXT, -- Playlist description
    url link, -- Playlist URL
    thumbnail_url TEXT, -- Playlist thumbnail URL
    playlist_type yt_playlist_type NOT NULL, -- Type of playlist
	FOREIGN KEY (channel_id) REFERENCES yt_channels(id) ON DELETE SET NULL ON UPDATE CASCADE
);

/*
Indexes on channel_id and title for faster searches.
*/
CREATE INDEX idx_yt_playlists_channel_id ON yt_playlists(channel_id);
CREATE INDEX idx_yt_playlists_title ON yt_playlists(title);

/*
Table to link videos to playlists.
*/
CREATE TABLE yt_playlist_items (
	id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	playlist_id playlistId, -- Foreign key to yt_playlists table
	video_id videoId, -- Foreign key to yt_videos table
	position INT CHECK (position > 0), -- Position of the video in the playlist
	FOREIGN KEY (video_id) REFERENCES yt_videos(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (playlist_id) REFERENCES yt_playlists(id) ON DELETE CASCADE ON UPDATE CASCADE
);

/*
Indexes on playlist_id and video_id for faster searches.
*/
CREATE INDEX idx_yt_playlist_items_playlist_id ON yt_playlist_items(playlist_id);
CREATE INDEX idx_yt_playlist_items_video_id ON yt_playlist_items(video_id);

/*
Function that will be used in a trigger to enforce playlist item rules.
*/
CREATE OR REPLACE FUNCTION check_playlist_item_rules()
RETURNS TRIGGER AS $$
DECLARE
    playlist_type yt_playlist_type;
BEGIN

    SELECT type INTO playlist_type
    FROM yt_playlists
    WHERE id = NEW.playlist_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Playlist with id % not found',
            NEW.playlist_id;
    END IF;

    -- ORDERED playlists
    IF playlist_type = 'ordered' THEN

        IF NEW.position IS NULL THEN
            RAISE EXCEPTION
                'Ordered playlists require a position';
        END IF;

        -- prevent duplicate positions
        IF EXISTS (
            SELECT 1
            FROM yt_playlist_items
            WHERE playlist_id = NEW.playlist_id
              AND position = NEW.position
              AND id <> NEW.id
        ) THEN
            RAISE EXCEPTION
                'Position % already exists in playlist %',
                NEW.position,
                NEW.playlist_id;
        END IF;

        -- prevent duplicate videos
        IF EXISTS (
            SELECT 1
            FROM yt_playlist_items
            WHERE playlist_id = NEW.playlist_id
              AND video_id = NEW.video_id
              AND id <> NEW.id
        ) THEN
            RAISE EXCEPTION
                'Video % already exists in ordered playlist %',
                NEW.video_id,
                NEW.playlist_id;
        END IF;

    END IF;

    -- FREE playlists
    IF playlist_type = 'free' THEN

        -- normalize position
        NEW.position := NULL;

    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

/*
Trigger to validate that playlist items are normalized.
*/
CREATE TRIGGER yt_playlist_item_rules_trigger
BEFORE INSERT OR UPDATE ON yt_playlist_items
FOR EACH ROW
EXECUTE FUNCTION check_playlist_item_rules();

COMMIT;