"""
This script takes the outputs from songs_from_playlist.py to search for all associated albums. For every song
found from the playlists, their albums are grabbed here. This code then adds albums to the schema, finds new songs
to add, and new artists to add.
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import json
import time
import os

# Initialize globals
songs = {}
albums = {}
albums_to_check = set()
songs_to_check = set()
artists_to_check = set()
song_album = {}

DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}", exist_ok=True)


def load_data():
    global songs, albums, albums_to_check, songs_to_check, artists_to_check, song_album
    # ------- ENTITIES -------
    # Songs (only for checking if it was already found) - dict
    try:
        with open(f"{DATA_DIR}/songs.json", "r") as f:
            songs = json.load(f)
    except FileNotFoundError:
        songs = {}

    # Albums - dict
    try:
        with open(f"{DATA_DIR}/albums.json", "r") as f:
            albums = json.load(f)
    except FileNotFoundError:
        albums = {}

    # Albums To Check (our list of IDs to check) - set
    try:
        with open(f"{DATA_DIR}/albums_to_check.json", "r") as f:
            albums_to_check = set(json.load(f))
    except FileNotFoundError:
        print(f"❌ No albums_to_check.json file found.")
        exit()

    # Artists To Check (to further populate artists.json) - set
    try:
        with open(f"{DATA_DIR}/artists_to_check.json", "r") as f:
            artists_to_check = set(json.load(f))
    except FileNotFoundError:
        artists_to_check = set()

    # Songs To Check (to further populate songs.json) - set
    try:
        with open(f"{DATA_DIR}/songs_to_check.json", "r") as f:
            songs_to_check = set(json.load(f))
    except FileNotFoundError:
        songs_to_check = set()

    # ------- RELATIONSHIPS -------
    # Song - Album
    try:
        with open(f"{DATA_DIR}/song_album.json", "r") as f:
            raw = json.load(f)
            song_album = {tuple(k.split('|')) : v for k, v in raw.items()}
    except FileNotFoundError:
        song_album = {}


# ------- HELPER FUNCTIONS -------

"""
Stores album information that will be needed for the Album schema.
Also gets artist information to update artists_to_check
"""
def save_album_info(album_id, sp):
    while True:
        try:
            item = sp.album(album_id)
            break
        except spotipy.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", 1))
                print(f"❌ Rate limit hit. Retrying after {retry_after} seconds.\n")
                time.sleep(retry_after)
            else:
                raise

    if item.get("album_type") in ["single", "compilation"]:
        return

    # Attributes
    if album_id not in albums:
        albums[album_id] = {
            "albumTitle": item["name"],
            "albumReleaseDate": item["release_date"],
            "label": item["label"],
            "numberOfTracks": item["total_tracks"],
            "albumArtURL": item["images"][0]["url"] if item.get("images") else None
        }
    
    # Artists To Check
    for artist in item["artists"]:
        if artist["id"] not in artists_to_check:
            artists_to_check.add(artist["id"])

"""
Gets all tracks found on the album. Handles any rate limiting from Spotify's API
"""
def get_album_tracks(album_id, sp):
    album = sp.album(album_id)
    if album.get("album_type") in ["single", "compilation"]:
        return None     # skip

    all_tracks = []
    results = None
    while True:
        try:
            if results is None:
                results = sp.album_tracks(album_id, limit=50, offset=0)
            else:
                if results.get("next"):
                    results = sp.next(results)
                else:
                    break
            all_tracks.extend(results["items"])
            print(f"🔹 Fetched {len(all_tracks)} tracks so far...\n")

        except spotipy.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", 1))
                print(f"❌ Rate limit hit. Retrying after {retry_after} seconds.\n")
                time.sleep(retry_after)
            else:
                raise
    
    return all_tracks


"""
Save all data in JSON format.
"""
def checkpoint():
    print(f"✅ Checkpointing...")

    # Albums
    with open(f"{DATA_DIR}/albums.json", "w") as f:
        json.dump(albums, f)
    # Albums To Check
    with open(f"{DATA_DIR}/albums_to_check.json", "w") as f:
        json.dump(list(albums_to_check), f)
    # Artists To Check
    with open(f"{DATA_DIR}/artists_to_check.json", "w") as f:
        json.dump(list(artists_to_check), f)
    # Songs To Check
    with open(f"{DATA_DIR}/songs_to_check.json", "w") as f:
        json.dump(list(songs_to_check), f)
    
    # Relationships require flattening
    # Song - Album
    with open(f"{DATA_DIR}/song_album.json", "w") as f:
        json.dump({ f"{k[0]}|{k[1]}":v for k, v in song_album.items() }, f)
    
    print(f"💾 Checkpoint: {len(albums)} albums items saved\n")


def main():
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    load_data()

    processed_albums = 0

    print(f"Beginning processing! {len(albums)} exist, {len(albums_to_check)} to add.")
    while albums_to_check:
        album_id = albums_to_check.pop()     # Remove random album

        # Album entity
        save_album_info(album_id, sp)

        album_tracks = get_album_tracks(album_id, sp)
        try:
            for item in album_tracks:
                track_id = item["id"]
                # Check if song has already been found
                if track_id not in songs and track_id not in songs_to_check:
                    songs_to_check.add(track_id)

                # Add song to song - album relationship
                if (track_id, album_id) not in song_album:
                    song_album[(track_id, album_id)] = {
                        "trackNumber": item["track_number"]
                    }
        except Exception as e:
            print(f"⚠️ Error occurred: {e}\n")
            checkpoint()
            raise e
        
        processed_albums += 1
        if processed_albums % 10 == 0:
            print(f"Processed {processed_albums} albums. {len(albums_to_check)} remaining\n")
            checkpoint()
    
    checkpoint()
    print(f"✅ Saved {len(albums)} albums. {len(albums_to_check)} left to process.")


if __name__ == "__main__":
    main()
