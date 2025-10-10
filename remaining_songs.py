"""
This script handles all remaining songs from songs_to_check.json, including all attributes and relationships with

"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import json
import time
import os

from songs_from_playlist import save_song

# Initialize globals
songs = {}
songs_to_check = set()
artists_to_check = set()
song_artist = {}

DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}", exist_ok=True)

def load_data():
    global songs, songs_to_check, artists_to_check, song_artist
    # --------- ENTITIES ---------
    # Songs - dict
    try:
        with open(f"{DATA_DIR}/songs.json", "r") as f:
            songs = json.load(f)
    except FileNotFoundError:
        songs = {}

    # Songs To Check (list of IDs to check) - set
    try:
        with open(f"{DATA_DIR}/songs_to_check.json", "r") as f:
            songs_to_check = set(json.load(f))
    except FileNotFoundError:
        songs_to_check = set()

    # Artists To Check (to further populate artists.json) - set
    try:
        with open(f"{DATA_DIR}/artists_to_check.json", "r") as f:
            artists_to_check = set(json.load(f))
    except FileNotFoundError:
        artists_to_check = set()

    # Song - Artist
    try:
        with open(f"{DATA_DIR}/song_artist.json", "r") as f:
            raw = json.load(f)
            song_artist = set(tuple(k.split('|')) for k in raw)
    except FileNotFoundError:
        song_artist = set()


def checkpoint():
    print(f"✅ Checkpointing...")

    # Songs
    with open(f"{DATA_DIR}/songs.json", "w") as f:
        json.dump(songs, f)
    # Songs To Check
    with open(f"{DATA_DIR}/songs_to_check.json", "w") as f:
        json.dump(list(songs_to_check), f)
    # Artists To Check
    with open(f"{DATA_DIR}/artists_to_check.json", "w") as f:
        json.dump(list(artists_to_check), f)
    # Song-Artist
    with open(f"{DATA_DIR}/song_artist.json", "w") as f:
        json.dump([f"{k[0]}|{k[1]}" for k in song_artist], f)
    print(f"💾 Checkpoint: {len(songs)} songs saved\n")


def main():
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    load_data()

    processed_songs = 0

    print(f"Beginning processing! {len(songs)} exist, {len(songs_to_check)} to add.")

    while songs_to_check:
        track_id = songs_to_check.pop()
        
        while True:
            try:
                track = sp.track(track_id)
                break
            except spotipy.SpotifyException as e:
                if e.http_status == 429:
                    retry_after = int(e.headers.get('Retry-After', 1))
                    print(f"❌ Rate limit hit. Retrying after {retry_after} seconds.\n")
                    time.sleep(retry_after)
                    print(f"Retrying...\n")
                else:
                    raise
        
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
            processed_songs += 1

        for artist in track["artists"]:
            artist_id = artist["id"]
            if artist_id not in artists_to_check:
                artists_to_check.add(artist_id)
            if (song_id, artist_id) not in song_artist:
                song_artist.add((song_id, artist_id))
        
        if processed_songs % 25 == 0:
            print(f"Processed {processed_songs} / {processed_songs + len(songs_to_check)} songs...")
            checkpoint()
    
    checkpoint()
    print(f"✅ Finished! Successfully saved {processed_songs} songs. Total songs: {len(songs)}\n")

if __name__ == "__main__":
    main()
