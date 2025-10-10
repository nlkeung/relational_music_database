# Relational Music Database
## Overview
This project builds a relational database to model songs, artists, albums, playlists, and genres from the Spotify Web API. The database also models user entities, allowing users to follow artists and like the songs or playlists in the database. 

This repository generates .tsv files for bulk importing into an SQL database.

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
7. Generate output files in `.tsv` format
