-- Query 1: Multi-table JOIN
-- Find all songs by artists that a user follows
SELECT u.FirstName, u.LastName, u.Username, a.ArtistName, s.SongTitle
FROM FollowsArtist fa
JOIN "Users" u ON fa.UserID = u.UserID
JOIN Artists a ON fa.ArtistID = a.ArtistID
JOIN Performs p ON p.ArtistID = a.ArtistID
JOIN Songs s ON p.SongID = s.SongID
WHERE 
    u.FirstName = 'Lukas'
    AND u.LastName = 'Robert'
    AND s.SongPopularity >= 90;

-- Query 2: Aggregation
-- Find the top 5 artists by average song popularity
SELECT a.ArtistName, ROUND(AVG(s.SongPopularity), 2) AS AvgPopularity
FROM Artists a
JOIN Performs p ON a.ArtistID = p.ArtistID
JOIN Songs s ON s.SongID = p.SongID
GROUP BY a.ArtistName
ORDER BY AvgPopularity DESC
LIMIT 5;

-- Query 3: Filter + Join
-- Find playlists that contain songs released before 2020
SELECT DISTINCT pl.PlaylistName
FROM Playlists pl
JOIN InPlaylist ip ON pl.PlaylistID = ip.PlaylistID
JOIN Songs s ON s.SongID = ip.SongID
WHERE s.SongReleaseDate > '2020-01-01';
