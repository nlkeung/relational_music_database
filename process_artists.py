"""
This script handles all remaining artsists from artists_to_check.json. It also adds genres and the artist-genre relationship.

"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import json
import time
import os

# Initialize globals
artists_to_check = set()
artists = {}
genres = set()
artist_genre = set()

DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}", exist_ok=True)

def load_data():
    global artists_to_check, artists, genres, artist_genre

    # ----- ENTITIES -----
    # Artists To Check (list of IDs to check) - set
    try:
        with open(f"{DATA_DIR}/artists_to_check.json", "r") as f:
            artists_to_check = set(json.load(f))
    except FileNotFoundError:
        print(f"❌ No artists_to_check.json file found.")
        exit()
    
    # Artists - dict
    try:
        with open(f"{DATA_DIR}/artists.json", "r") as f:
            artists = json.load(f)
    except FileNotFoundError:
        artists = {}

    # Genres - set
    try:
        with open(f"{DATA_DIR}/genres.json", "r") as f:
            genres = set(json.load(f))
    except FileNotFoundError:
        genres = set()
    
    # ----- RELATIONSHIPS -----
    # Artist - Genre - set
    try:
        with open(f"{DATA_DIR}/artist_genre.json", "r") as f:
            raw = json.load(f)
            artist_genre = set(tuple(k.split('|')) for k in raw)
    except FileNotFoundError:
        artist_genre = set()
    

def checkpoint():
    print(f"✅ Checkpointing...")

    # Artists To Check (list of IDs to check) - set
    with open(f"{DATA_DIR}/artists_to_check.json", "w") as f:
        json.dump(list(artists_to_check), f)
    
    # Artists - dict
    with open(f"{DATA_DIR}/artists.json", "w") as f:
        json.dump(artists, f)

    # Genres - set
    with open(f"{DATA_DIR}/genres.json", "w") as f:
        json.dump(list(genres), f)
        
    # Artist - Genre
    with open(f"{DATA_DIR}/artist_genre.json", "w") as f:
        json.dump( [f"{k[0]}|{k[1]}" for k in artist_genre], f)

    print(f"💾 Checkpoint: {len(artists)} artists saved\n")
    

def main():
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    load_data()

    processed_artists = 0

    print(f"Beginning processing! {len(artists)} exist, {len(artists_to_check)} to add.")

    while artists_to_check:
        artist_id = artists_to_check.pop()
        
        while True:
            try:
                item = sp.artist(artist_id)
                break
            except spotipy.SpotifyException as e:
                if e.http_status == 429:
                    retry_after = int(e.headers.get('Retry-After', 1))
                    print(f"❌ Rate limit hit. Retrying after {retry_after} seconds.\n")
                    time.sleep(retry_after)
                    print(f"Retrying...\n")
                else:
                    raise
        
        # Attributes
        if artist_id not in artists:
            artists[artist_id] = {
                "artistName": item["name"],
                "artistPopularity": item["popularity"],
                "artistArtURL": item["images"][0]["url"] if item.get("images") else None
            }
            processed_artists += 1
        
        # Genres
        for g in item["genres"]:
            if g not in genres:
                genres.add(g)
            if (artist_id, g) not in artist_genre:
                artist_genre.add((artist_id, g))
        
        if processed_artists % 25 == 0:
            print(f"Processed {processed_artists} / {processed_artists + len(artists_to_check)} artists...")
            checkpoint()
    
    checkpoint()
    print(f"✅ Finished! Successfully saved {processed_artists} artists. Total artists: {len(artists)}\n")
    print(f"✅ Finished! Successfully saved {len(genres)} genres.")


if __name__ == "__main__":
    main()
