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

# Load Entity data
entities = ["albums", "artists", "genres", "songs", "users"]
entity_data = {}

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
df = pd.DataFrame({
    "genreID": range(1, len(genres)+1),
    "genreName": genres_list,
})
tsv_path = os.path.join(OUTPUT_DIR, "genres.tsv")
df.to_csv(tsv_path, sep="\t", index=False)
if os.path.exists(tsv_path):
    print(f"✅ Successfully saved {entity} in {tsv_path}")

    