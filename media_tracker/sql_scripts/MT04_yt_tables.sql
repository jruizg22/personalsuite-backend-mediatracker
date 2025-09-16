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
    description TEXT -- Channel description
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
	channel_id channelId, -- Foreign key to yt_channels table
	title VARCHAR(255) NOT NULL, -- Video title
	published_at DATE, -- Video release date
	description TEXT, -- Video description
    url link, -- Video URL
	FOREIGN KEY (channel_id) REFERENCES yt_channels(id)
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
	resume INT DEFAULT NULL, -- Resume time (in seconds) if applicable. If NULL, it means the video was watched completely.
	FOREIGN KEY (video_id) REFERENCES yt_videos(id)
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
	channel_id channelId, -- Foreign key to yt_channels table
	title VARCHAR(255) NOT NULL, -- Playlist title
	description TEXT, -- Playlist description
    url link, -- Playlist URL
	FOREIGN KEY (channel_id) REFERENCES yt_channels(id)
);

/*
Indexes on channel_id and title for faster searches.
*/
CREATE INDEX idx_yt_playlists_channel_id ON yt_playlists(channel_id);
CREATE INDEX idx_yt_playlists_title ON yt_playlists(title);

/*
Table to link videos to playlists.
*/
CREATE TABLE yt_playlist_videos (
	id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	playlist_id playlistId, -- Foreign key to yt_playlists table
	video_id videoId, -- Foreign key to yt_videos table
	position INT, -- Position of the video in the playlist
	FOREIGN KEY (video_id) REFERENCES yt_videos(id),
	FOREIGN KEY (playlist_id) REFERENCES yt_playlists(id),
	CONSTRAINT uq_playlist_position UNIQUE (playlist_id, position) -- Ensure unique position per playlist, although optional with NULLs
);

/*
Indexes on playlist_id and video_id for faster searches.
*/
CREATE INDEX idx_yt_playlist_videos_playlist_id ON yt_playlist_videos(playlist_id);
CREATE INDEX idx_yt_playlist_videos_video_id ON yt_playlist_videos(video_id);

COMMIT;