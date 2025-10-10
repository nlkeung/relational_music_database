"""
This script takes in a Spotify playlist ID. It then creates and updates playlist.json. Afterwards, it searches each song in 
the playlist and adds the songs to songs.json. It also updates song-artist, song-playlist, and song-album relationships.
Finally, it creates artists_to_check.json and albums_to_check.json, containing a list of IDs that should be added to the database.
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import json
import time
import os


# Initialize globals
playlists = {}
songs = {}
artists_to_check = set()
albums_to_check = set()
song_album = {}
song_artist = set()
song_playlist = {}

DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}", exist_ok=True)


def load_data():
    global playlists, songs, artists_to_check, albums_to_check, song_album, song_artist, song_playlist
    # --------- ENTITIES ---------
    # Playlists - dict
    try:
        with open(f"{DATA_DIR}/playlists.json", "r") as f:
            playlists = json.load(f)
    except FileNotFoundError:
        playlists = {}

    # Songs - dict
    try:
        with open(f"{DATA_DIR}/songs.json", "r") as f:
            songs = json.load(f)
    except FileNotFoundError:
        songs = {}

    # Artists To Check (populate attributes later) - set
    try:
        with open(f"{DATA_DIR}/artists_to_check.json", "r") as f:
            artists_to_check = set(json.load(f))
    except FileNotFoundError:
        artists_to_check = set()

    # Albums To Check (populate attributes later) - set
    try:
        with open(f"{DATA_DIR}/albums_to_check.json", "r") as f:
            albums_to_check = set(json.load(f))
    except FileNotFoundError:
        albums_to_check = set()

    # ------- RELATIONSHIPS -------
    # Song - Album
    try:
        with open(f"{DATA_DIR}/song_album.json", "r") as f:
            raw = json.load(f)
            song_album = {tuple(k.split('|')) : v for k, v in raw.items()}
    except FileNotFoundError:
        song_album = {}

    # Song - Artist
    try:
        with open(f"{DATA_DIR}/song_artist.json", "r") as f:
            raw = json.load(f)
            song_artist = set(tuple(k.split('|')) for k in raw)
    except FileNotFoundError:
        song_artist = set()

    # Song - Playlist
    try:
        with open(f"{DATA_DIR}/song_playlist.json", "r") as f:
            raw = json.load(f)
            song_playlist = {tuple(k.split('|')) : v for k, v in raw.items()}
    except FileNotFoundError:
        song_playlist = {}


# ------- HELPER FUNCTIONS -------

"""
Grabs the item objects associated with the playlist ID. This function handles
rate limits from Spotify API and accumulates all entries across pagination
Input: playlist_id, Spotify client credentials
"""
def get_playlist_items(playlist_id, sp):
    all_items = []
    results = None
    while True:
        try:
            if results is None:
                results = sp.playlist_items(playlist_id, limit=100)
            else:
                if results.get("next"):
                    results = sp.next(results)
                else:
                    break  # no more pages

            all_items.extend(results["items"])
            print(f"🔹 Fetched {len(all_items)} items so far...\n")

        except spotipy.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get('Retry-After', 1))
                print(f"❌ Rate limit hit. Retrying after {retry_after} seconds.\n")
                time.sleep(retry_after)
                print(f"Retrying...\n")
            else:
                raise
    return all_items

"""
This function takes in track information and looks up its associated album ID.
It then makes another API call to check if the album is actually a single or a
compilation. If it is one of the two, it is not an album, and we do not add it to 
albums_to_check or song_album.
"""
def process_track_album(track, sp):
    song_id = track["id"]
    album_id = track["album"]["id"]

    # Look up if album is an "album", "single", or "compilation". If not an album, skip
    while True:
        try:
            album = sp.album(album_id)
            break
        except spotipy.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", 1))
                print(f"❌ Rate limit hit. Retrying after {retry_after} seconds.\n")
                time.sleep(retry_after)
            else:
                raise
    if album.get("album_type") in ["single", "compilation"]:
        # Album is actually a single or compilation. Do not include this in the relationship
        return
    
    else:
        if album_id not in albums_to_check:
            albums_to_check.add(album_id)
        if (song_id, album_id) not in song_album:
            song_album[(song_id, album_id)] = {
                "trackNumber": track["track_number"]
            }

"""
Saves all necessary attributes for Song entity, along with all of its relationships.
Relationships include song_artist, song_album, song_playlist
"""
def save_song(track, sp):
    song_id = track["id"]
    # Attributes
    if song_id not in songs:
        songs[song_id] = {
            "songTitle": track["name"],
            "duration": track["duration_ms"],
            "releaseDate": track["album"]["release_date"],
            "popularity": track.get("popularity", None),
            "artURL": track["album"]["images"][0]["url"] if track["album"].get("images") else None
        }
    # Relationships
    # Albums
    process_track_album(track, sp)
    # Artists
    for artist in track["artists"]:
        artist_id = artist["id"]
        if artist_id not in artists_to_check:
            artists_to_check.add(artist_id)
        if (song_id, artist_id) not in song_artist:
            song_artist.add((song_id, artist_id))
    # Playlist - handled in main loop

"""
Checkpoint data in case of rate limits or other errors
"""
def checkpoint():
    print(f"✅ Checkpointing...")

    # Playlists
    with open(f"{DATA_DIR}/playlists.json", "w") as f:
        json.dump(playlists, f)
    # Songs
    with open(f"{DATA_DIR}/songs.json", "w") as f:
        json.dump(songs, f)
    # Artists
    with open(f"{DATA_DIR}/artists_to_check.json", "w") as f:
        json.dump(list(artists_to_check), f)
    # Albums
    with open(f"{DATA_DIR}/albums_to_check.json", "w") as f:
        json.dump(list(albums_to_check), f)
    
    # Relationships
    # Require flattening tuple keys, must reshape later
    # Song-Album
    with open(f"{DATA_DIR}/song_album.json", "w") as f:
        json.dump({ f"{k[0]}|{k[1]}":v for k, v in song_album.items() }, f)
    # Song-Artist
    with open(f"{DATA_DIR}/song_artist.json", "w") as f:
        json.dump([f"{k[0]}|{k[1]}" for k in song_artist], f)
    # Song-Playlist
    with open(f"{DATA_DIR}/song_playlist.json", "w") as f:
        json.dump({ f"{k[0]}|{k[1]}":v for k, v in song_playlist.items() }, f)
    
    print(f"💾 Checkpoint: {len(songs)} songs, {len(song_artist)} song-artist relations, {len(song_playlist)} items saved\n")




# ------- MAIN -------
def main():
    # Log in to Spotify
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Load saved JSONs
    load_data()

    playlist_id = "6UeSakyzhiEt4NB3UAd6NQ"
    playlist_info = sp.playlist(playlist_id)
    playlist_name = playlist_info["name"]

    # Populate playlist basic information
    if playlist_id not in playlists:
        playlists[playlist_id] = {
            "playlist_name": playlist_name,
            "playlist_art_url": playlist_info["images"][0]["url"] if playlist_info["images"] else None
        }

    # Iterating through songs in playlist
    playlist_items = get_playlist_items(playlist_id, sp)
    try:
        for song_index, item in enumerate(playlist_items, start=1):             # item contains track, along with position info relative to playlist
            track = item["track"]               # Track info
            if not track:
                continue

            # Song-Playlist relationship
            if (track["id"], playlist_id) not in song_playlist:
                song_playlist[(track["id"], playlist_id)] = {
                    "dateAdded": item["added_at"],
                    "songOrder": song_index
                } 
            # Song Entity and Other Relationships   
            save_song(track, sp)

            # Checkpointing
            if song_index % 50 == 0:
                checkpoint()

            song_index += 1
    except Exception as e:
        print(f"⚠️ Error occurred: {e}\n")
        checkpoint()

    checkpoint()
    print(f"✅ Successfully saved all playlists from {playlist_name}. Saved {len(songs)} songs total\n")

if __name__ == "__main__":
    main()
