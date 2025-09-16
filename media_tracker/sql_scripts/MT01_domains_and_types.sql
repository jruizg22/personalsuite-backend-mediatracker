/*
This script contains the SQL statements to create custom domains and types
for the media tracking tables.
This script is designed for PostgreSQL.
*/

BEGIN;

/*
Drop domains if they already exist (with CASCADE to remove dependencies).
*/
DROP DOMAIN IF EXISTS titleLength CASCADE;
DROP DOMAIN IF EXISTS languageCode CASCADE;
DROP DOMAIN IF EXISTS channelId CASCADE;
DROP DOMAIN IF EXISTS videoId CASCADE;
DROP DOMAIN IF EXISTS playlistId CASCADE;
DROP DOMAIN IF EXISTS link CASCADE;

/*
Drop type if it already exists.
*/
DROP TYPE IF EXISTS media_type CASCADE;

/*
Domain definitions for consistent ID and url/title formats.
*/
CREATE DOMAIN titleLength AS VARCHAR(255); -- Titles up to 255 characters
CREATE DOMAIN languageCode AS VARCHAR(5); -- Locale codes (BCP 47) (e.g., 'en-US', 'es-ES')
CREATE DOMAIN channelId AS VARCHAR(32);
CREATE DOMAIN videoId AS VARCHAR(16);
CREATE DOMAIN playlistId AS VARCHAR(40);
CREATE DOMAIN link AS VARCHAR(2048);

/*
Enum type for media types.
*/
CREATE TYPE media_type AS ENUM ('movie', 'tv_show', 'other');

COMMIT;