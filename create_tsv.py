"""
Converts .json files to .tsv ready to use with PostgreSQL. All tables are generated with the exception of 
all relationship tables with Users and Playlists. Those will be generated in user_relationships.py using these files. 
Input .json files should be in data/, and .tsv files will be saved in output/
"""

import os
import pandas as pd
import json

DATA_DIR = "data"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----- ENTITIES -----

# Load Entity data
entities = ["albums", "artists", "genres", "songs", "users"]
entity_data = {}

print(f"Loading entities...\n")
for e in entities:
    path = os.path.join(DATA_DIR, f"{e}.json")
    try:
        with open(path, "r") as f:
            entity_data[e] = json.load(f)
        print(f"✅ Successfully loaded {e}.json")
    except FileNotFoundError:
        print(f"❌ {path} not found. Initializing empty object")

albums = entity_data["albums"]
artists = entity_data["artists"]
genres = entity_data["genres"]
songs = entity_data["songs"]
users = entity_data["users"]

# Saving in TSV files
id_columns = {
    "albums": "albumID",
    "artists": "artistID",
    "genres": "genreID",
    "songs": "songID",
    "users": "userID"
}

print(f"\nSaving entities...")
for entity in entity_data.keys():
    if entity == "genres":
        # Genre is a set, cannot process like a dictionary
        continue

    df = pd.DataFrame.from_dict(entity_data[entity], orient="index")
    df.index.name = id_columns[entity]
    df.reset_index(inplace=True)

    tsv_path = os.path.join(OUTPUT_DIR, f"{entity}.tsv")
    df.to_csv(tsv_path, sep="\t", index=False)
    if os.path.exists(tsv_path):
        print(f"✅ Successfully saved {entity} in {tsv_path}")

# Save genres
genres_list = list(genres)
genres_df = pd.DataFrame({
    "genreID": range(1, len(genres)+1),
    "genreName": genres_list,
})
tsv_path = os.path.join(OUTPUT_DIR, "genres.tsv")
genres_df.to_csv(tsv_path, sep="\t", index=False)
if os.path.exists(tsv_path):
    print(f"✅ Successfully saved {entity} in {tsv_path}")


# ----- RELATIONSHIPS -----
print(f"\nLoading relationships...\n")
# Save song-artist, song-album, and artist-genre

# Song - Artist
path = os.path.join(DATA_DIR, "song_artist.json")
try:
    with open(path, "r") as f:
        raw = list(json.load(f))
        song_artist = [pair.split("|") for pair in raw]
        print(f"✅ Successfully loaded song_artist.json")
    df = pd.DataFrame(song_artist, columns=["songID", "artistID"])
    df = df.reindex(columns = ["artistID", "songID"])   # Reorder to match schema
    
    # Saving
    song_artist_path = os.path.join(OUTPUT_DIR, "performs.tsv")
    df.to_csv(song_artist_path, sep="\t", index=False)
    if os.path.exists(song_artist_path):
            print(f"✅ Successfully saved song_artist in {song_artist_path}\n")

except FileNotFoundError:
        print(f"❌ {path} not found. Skipping...")

# Song - Album
path = os.path.join(DATA_DIR, "song_album.json")
try:
    with open(path, "r") as f:
        raw = json.load(f)
        song_album = {tuple(k.split('|')): v for k, v in raw.items()}
        print(f"✅ Successfully loaded song_album.json")
    
        df = pd.DataFrame([
            {"songID": song, "albumID": album, **trackNums} for (song, album), trackNums in song_album.items()
        ])
        
        # Saving
        song_album_path = os.path.join(OUTPUT_DIR, "inAlbum.tsv")
        df.to_csv(song_album_path, sep="\t", index=False)
        if os.path.exists(song_album_path):
            print(f"✅ Successfully saved song_album in {song_album_path}\n")

except FileNotFoundError:
     print(f"❌ {path} not found. Skipping...")

# Artist - Genre
path = os.path.join(DATA_DIR, "artist_genre.json")
try:
    with open(path, "r") as f:
        raw = json.load(f)
        artist_genre = [pair.split('|') for pair in raw]
        print(f"✅ Successfully loaded artist_genre.json")
    
    artist_genre_df = pd.DataFrame(artist_genre, columns=["artistID", "genreName"])
    # Replace "genreName" with "genreID"
    # Left outer join on artist_genre and genre on genreName, then drop genreName
    merged = artist_genre_df.merge(
        genres_df[["genreID", "genreName"]],
        on="genreName",
        how="left"
    )
    merged = merged.drop(columns="genreName")
    
    # Saving
    artist_genre_path = os.path.join(OUTPUT_DIR, "isGenre.tsv")
    merged.to_csv(artist_genre_path, sep="\t", index=False)
    if os.path.exists(artist_genre_path):
        print(f"✅ Successfully saved artist_genre in {artist_genre_path}\n")

except FileNotFoundError:
    print(f"❌ {path} not found. Skipping...")
