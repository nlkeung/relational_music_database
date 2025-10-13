-- Query 1: Multi-table JOIN
-- Find all songs by artists that a user follows
SELECT u.FirstName AS UserName, a.ArtistName, s.SongTitle
FROM FollowsArtist fa
JOIN "User" u ON fa.UserID = u.UserID
JOIN Artist a ON fa.ArtistID = a.ArtistID
JOIN Performs p ON p.ArtistID = a.ArtistID
JOIN Song s ON p.SongID = s.SongID;

-- Query 2: Aggregation
-- Find the top 5 artists by average song popularity
SELECT a.ArtistName, ROUND(AVG(s.SongPopularity), 2) AS AvgPopularity
FROM Artist a
JOIN Performs p ON a.ArtistID = p.ArtistID
JOIN Song s ON s.SongID = p.SongID
GROUP BY a.ArtistName
ORDER BY AvgPopularity DESC
LIMIT 5;

-- Query 3: Filter + Join
-- Find playlists that contain songs released after 2020
SELECT DISTINCT pl.PlaylistName
FROM Playlist pl
JOIN InPlaylist ip ON pl.PlaylistID = ip.PlaylistID
JOIN Song s ON s.SongID = ip.SongID
WHERE s.SongReleaseDate >= '2020-01-01';
