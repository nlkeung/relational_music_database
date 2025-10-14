# Relational Music Database
## Overview
This project builds a relational database to model songs, artists, albums, playlists, and genres from the Spotify Web API. The database also models user entities, allowing users to follow artists and like the songs or playlists in the database. 

This repository generates .tsv files for bulk importing into an SQL database.

## Requirements
* Python 3.10+
* Install dependencies:
  ```bash
  pip install spotipy pandas requests

## Setup
1. Create a Spotify developer account at https://developer.spotify.com/
2. Create an application to get your `CLIENT_ID` and `CLIENT_SECRET`
3. Set environment variables
   ```bash
   export SPOTIPY_CLIENT_ID='<your_client_id>'
   export SPOTIPY_CLIENT_SECRET='<your_client_secret>'

## Data Collection Flow

Data is collected following a structured pipeline. Each step follows from the one before it.

1. Process playlists - Grabs all songs in the playlist
   * Stores `song` attributes and their relationships with other entities
   * Populates `albums_to_check` from the songs we found
3. Process albums - Fetches all songs in the albums
   * Populates `songs_to_check` for every other song in the album that has not been already added
4. Process songs - Retrieve all remaining songs and their attributes
5. Process artists from `artists_to_check`
6. Process genre from the artists
7. Simulate artificial users profiles using randomuser.me
8. Generate output files in `.tsv` format to `output/`
9. Randomly simulate users creating playlists, following artists, etc. and create `.tsv` files

## Database Import
1. Create the database using `schema.sql`
2. Use `load_data.sql` to import `.tsv` files

Example queries are included in `queries.sql`

## Note:
* To incorporate other real playlists, see `songs_from_playlist.py`, `generate_users.py`, and `user_relationships.py` and modify accordingly
* `user_relationships.py` simulates data randomly, so intermediate files are not saved. Be careful re-running this, as it can create stale or contradictory data
