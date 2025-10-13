-- Entities
\copy Artist FROM 'output/artists.tsv' DELIMITER E'\t' CSV HEADER;
\copy Song FROM 'output/songs.tsv' DELIMITER E'\t' CSV HEADER;
\copy Genre FROM 'output/genres.tsv' DELIMITER E'\t' CSV HEADER;
\copy Album FROM 'output/albums.tsv' DELIMITER E'\t' CSV HEADER;
\copy "User" FROM 'output/users.tsv' DELIMITER E'\t' CSV HEADER;
\copy Playlist FROM 'output/playlists.tsv' DELIMITER E'\t' CSV HEADER;

--  Relationships
\copy Performs FROM 'output/performs.tsv' DELIMITER E'\t' CSV HEADER;
\copy IsGenre FROM 'output/isGenre.tsv' DELIMITER E'\t' CSV HEADER;
\copy InAlbum FROM 'output/inAlbum.tsv' DELIMITER E'\t' CSV HEADER;
\copy FollowsArtist FROM 'output/followsArtist.tsv' DELIMITER E'\t' CSV HEADER;
\copy CreatesPlaylist FROM 'output/createsPlaylist.tsv' DELIMITER E'\t' CSV HEADER;
\copy InPlaylist FROM 'output/inPlaylist.tsv' DELIMITER E'\t' CSV HEADER;
\copy FollowsPlaylist FROM 'output/followsPlaylist.tsv' DELIMITER E'\t' CSV HEADER;
\copy LikesSong FROM 'output/likesSong.tsv' DELIMITER E'\t' CSV HEADER;
\copy FollowsUser FROM 'output/followsUser.tsv' DELIMITER E'\t' CSV HEADER;