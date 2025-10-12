"""
This script handles synthetic user data. It uses user.tsv, song.tsv and artist.tsv to create playlists,
follow playlists, like songs, follow artists, and follow other users. This will also finish creating
playlists.tsv. 

Input Files: users.tsv, song.tsv, artist.tsv, song_playlist.json
Output Files: playlist.tsv, createsPlaylist.tsv, followsPlaylist.tsv, inPlaylist.tsv, likesSong.tsv, followsArtist.tsv, and followsUser.tsv.
"""

import os
import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
import random

DATA_DIR = "output"

# Load TSV data
print(f"----- Loading data... -----")

users_df = pd.read_csv(f"{DATA_DIR}/users.tsv", sep="\t")
songs_df = pd.read_csv(f"{DATA_DIR}/songs.tsv", sep="\t")
artists_df = pd.read_csv(f"{DATA_DIR}/artists.tsv", sep="\t")

# Load JSON info
with open("data/playlists.json", "r") as f:
    playlists = json.load(f)

try:
    with open("data/user_playlist.json", "r") as f:
        raw = json.load(f)
        user_playlist = set(tuple(parts.split('|')) for parts in raw)
except FileNotFoundError:
    user_playlist = set()

# Create Playlists
print(f"----- Playlist -----")
NUM_NEW_PLAYLISTS = 16
playlist_names = [f"random_mix_{i}" for i in range(1, NUM_NEW_PLAYLISTS+1)]
excluded_user_ids = [101, 102, 103, 104]    # real users who created playlists
eligible_users = users_df[~users_df["userID"].isin(excluded_user_ids)]

print("Generating synthetic playlists...")
for i, name in enumerate(playlist_names, start=1):
    creator = eligible_users.sample(1).iloc[0]
    created_date = datetime(2022,1,1) + timedelta(days=random.randint(0, 1000))
    
    playlist_id = str(i)
    if playlist_id not in playlists:
        playlists[playlist_id] = {
            "playlist_name": name,
            "playlist_art_url": r"\N"
        }
    if (creator["userID"], playlist_id) not in user_playlist:
        user_playlist.add((creator["userID"], playlist_id))
        print(f"Added playlist {name}")

# Save Playlist as JSON and TSV
with open("data/playlists.json", "w") as f:
    json.dump(playlists, f)
    print(f"✅ Successfully saved playlists.json. Total playlists: {len(playlists)}")
playlists_df = pd.DataFrame.from_dict(playlists, orient="index")
playlists_df.index.name = "playlistID"
playlists_df.reset_index(inplace=True)

playlists_path = os.path.join(DATA_DIR, "playlists.tsv")
playlists_df.to_csv(playlists_path, sep="\t", index=False)
if os.path.exists(playlists_path):
    print(f"✅ Successfully saved playlists.tsv\n")

# Creates Playlist (User - Playlist)
print(f"----- createsPlaylist -----")
# Real playlists
real_creators = ["Billboard", "Trap Nation", "Drake", "swift_fan"]
IDs = {
    "Billboard": 101,
    "Trap Nation": 102,
    "Drake": 103,
    "swift_fan": 104
}
real_playlistIDs = {
    "Billboard": "6UeSakyzhiEt4NB3UAd6NQ",
    "Trap Nation": "0NCspsyf0OS4BsPgGhkQXM",
    "Drake": "0GsvYNj45QjR245EWqgfDs",
    "swift_fan": "6qSYIKJihVKpWr2HDeHjxS"
}
for user in real_creators:
    if (IDs[user], real_playlistIDs[user]) not in user_playlist:
        user_playlist.add((IDs[user], real_playlistIDs[user]))

with open("data/user_playlist.json", "w") as f:
    json.dump([f"{k[0]}|{k[1]}" for k in user_playlist], f)
    print(f"✅ Successfully saved user_playlist.json")

createsPlaylist = pd.DataFrame(user_playlist, columns=["userID", "playlistID"])
createsPlaylist_path = os.path.join(DATA_DIR, "createsPlaylist.tsv")
createsPlaylist.to_csv(createsPlaylist_path, sep="\t", index=False)
if os.path.exists(createsPlaylist_path):
    print(f"✅ Successfully saved createsPlaylist.tsv\n")

# Song - Playlist
print(f"----- inPlaylist -----")
# Load song_playlist.json
with open("data/song_playlist.json", "r") as f:
    raw = json.load(f)
    song_playlist = {tuple(k.split('|')) : v for k, v in raw.items()}

skip_IDs = set(real_playlistIDs.values())
for p_id in playlists_df["playlistID"]:
    if p_id in real_playlistIDs:
        continue
    # Sample random songs
    songs_to_add = songs_df.sample(random.randint(0, 100))["songID"].tolist()
    
    song_pos = 1
    # Add songs to playlist
    for s_id in songs_to_add:
        if (s_id, p_id) not in song_playlist:
            song_playlist[(s_id, p_id)] = {
                "dateAdded": (datetime(2025, 10, 11) - timedelta(days=random.randint(0, 750))).strftime("%Y-%m-%d"),
                "songOrder": song_pos
            }
            song_pos += 1

with open("data/song_playlist.json", "w") as f:
    json.dump({ f"{k[0]}|{k[1]}":v for k, v in song_playlist.items() }, f)
print(f"✅ Successfully saved song_playlist.json")

in_playlist_df = pd.DataFrame([
    {"songID": k[0], "playlistID": k[1], **v}
    for k, v in song_playlist.items()
])
in_playlist_path = os.path.join(DATA_DIR, "inPlaylist.tsv")
in_playlist_df.to_csv(in_playlist_path, sep="\t", index=False)
if os.path.exists(in_playlist_path):
    print(f"✅ Successfully saved inPlaylist.tsv\n")


# User follows playlist (followsPlaylist.tsv)
print(f"----- followsPlaylist -----")
follows_playlist = set()
for user_id in users_df["userID"]:
    # Sample random playlists
    following_playlist = playlists_df.sample(random.randint(0, 10))["playlistID"].tolist()

    for p_id in following_playlist:
        if (user_id, p_id) not in follows_playlist:
            follows_playlist.add((user_id, p_id))

followsPlaylist_df = pd.DataFrame(list(follows_playlist), columns=["userID", "playlistID"])

fol_play_path = os.path.join(DATA_DIR, "followsPlaylist.tsv")
followsPlaylist_df.to_csv(fol_play_path, sep='\t', index=False)
if os.path.exists(fol_play_path):
    print(f"✅ Successfully saved followsPlaylist.tsv\n")


# User - Song (likesSong)
print("----- likesSong -----")
likes_song_set = set()
random_users = []
for i in range(random.randint(10, 100)):            # Random number of users
    random_users.append(random.randint(1, 100))     # Random user IDs

for u_id in random_users:
    # Sample random songs
    liked_songs = songs_df.sample(random.randint(0, 25))["songID"].tolist()

    for s_id in liked_songs:
        if (u_id, s_id) not in likes_song_set:
            likes_song_set.add((u_id, s_id))

likes_song_list = list(likes_song_set)
likes_song_list.sort(key=lambda pair:pair[0])
likesSong_df = pd.DataFrame(likes_song_list, columns=["userID", "songID"])

likes_song_path = os.path.join(DATA_DIR, "likesSong.tsv")
likesSong_df.to_csv(likes_song_path, sep='\t', index=False)
if os.path.exists(likes_song_path):
    print(f"✅ Succesfully saved likesSong.tsv\n")


# User - Artist (followsArtist)
print("----- followsArtist -----")
follows_artist_set = set()
random_users = []
for i in range(random.randint(10, 100)):            # Random number of users
    random_users.append(random.randint(1, 100))     # Random user IDs

for u_id in random_users:
    # Sample random artists
    artists = artists_df.sample(random.randint(0, 25))["artistID"].tolist()

    for a_id in artists:
        if (u_id, a_id) not in follows_artist_set:
            follows_artist_set.add((u_id, a_id))

follows_artist_list = list(follows_artist_set)
follows_artist_list.sort(key=lambda pair:pair[0])
followsArtist_df = pd.DataFrame(follows_artist_list, columns=["userID", "artistID"])

follows_artist_path = os.path.join(DATA_DIR, "followsArtist.tsv")
followsArtist_df.to_csv(follows_artist_path, sep='\t', index=False)
if os.path.exists(follows_artist_path):
    print(f"✅ Succesfully saved followsArtist.tsv\n")


# User - User (followsUser)
print("----- followsUser -----")
follows_user_set = set()
random_users = []
for i in range(random.randint(10, 100)):            # Random number of users
    random_users.append(random.randint(1, 100))     # Random user IDs

for u_id in random_users:
    # Sample random users
    followees = users_df.sample(random.randint(0, 25))["userID"].tolist()

    for followee_id in followees:
        if u_id == followee_id:
            continue
        if (u_id, followee_id) not in follows_user_set:
            follows_user_set.add((u_id, followee_id))
        # Check if they mutually follow each other
        if (followee_id, u_id) not in follows_user_set and random.choices([True, False], weights=[0.7, 0.3], k=1)[0]:
            follows_user_set.add((followee_id, u_id))

follows_user_list = list(follows_user_set)
follows_user_list.sort(key=lambda pair:pair[0])
followsUser_df = pd.DataFrame(follows_user_list, columns=["followerID", "followeeID"])

follows_user_path = os.path.join(DATA_DIR, "followsUser.tsv")
followsUser_df.to_csv(follows_user_path, sep="\t", index=False)
if os.path.exists(follows_user_path):
    print("✅ Successfully saved followsUser.tsv")
    