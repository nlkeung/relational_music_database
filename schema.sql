
-- ENTITY TABLES

CREATE TABLE Artist (
    ArtistID VARCHAR(50) PRIMARY KEY,
    ArtistName VARCHAR(100) NOT NULL,
    ArtistPopularity INT CHECK (ArtistPopularity BETWEEN 0 AND 100),
    ArtistArtURL VARCHAR(500)
);

CREATE TABLE Song (
    SongID VARCHAR(50) PRIMARY KEY,
    SongTitle VARCHAR(100) NOT NULL,
    Duration_ms INT CHECK (Duration_ms > 0),
    SongReleaseDate DATE CHECK (SongReleaseDate <= CURRENT_DATE),
    SongPopularity INT CHECK (SongPopularity BETWEEN 0 AND 100),
    SongArtURL VARCHAR(500)
);

CREATE TABLE Genre (
    GenreID VARCHAR(50) PRIMARY KEY,
    GenreName VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Album (
    AlbumID VARCHAR(50) PRIMARY KEY,
    AlbumTitle VARCHAR(100) NOT NULL,
    AlbumReleaseDate DATE CHECK (AlbumReleaseDate <= CURRENT_DATE),
    Label VARCHAR(100),
    NumberOfTracks INT NOT NULL CHECK (NumberOfTracks >= 1),
    AlbumArtURL VARCHAR(500)
);

-- Note: User is a reserved keyword, so we use double quotes.
CREATE TABLE "User" (
    UserID VARCHAR(50) PRIMARY KEY,
    Username VARCHAR(100) UNIQUE NOT NULL,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100),
    UserArtURL VARCHAR(500)
);

CREATE TABLE Playlist (
    PlaylistID VARCHAR(50) PRIMARY KEY,
    PlaylistName VARCHAR(100) NOT NULL,
    PlaylistArtURL VARCHAR(500)
);

-- RELATIONSHIP TABLES


-- Every song must have a performer (total participation)
CREATE TABLE Performs (
    ArtistID VARCHAR(50) REFERENCES Artist(ArtistID) ON DELETE CASCADE,
    SongID VARCHAR(50) REFERENCES Song(SongID) ON DELETE CASCADE,
    PRIMARY KEY (ArtistID, SongID)
);

-- Every artist must have a genre (total participation)
CREATE TABLE IsGenre (
    ArtistID VARCHAR(50) REFERENCES Artist(ArtistID) ON DELETE CASCADE,
    GenreID VARCHAR(50) REFERENCES Genre(GenreID) ON DELETE CASCADE,
    PRIMARY KEY (ArtistID, GenreID)
);

CREATE TABLE InAlbum (
    SongID VARCHAR(50) REFERENCES Song(SongID) ON DELETE CASCADE,
    AlbumID VARCHAR(50) REFERENCES Album(AlbumID) ON DELETE CASCADE,
    TrackNumber INT CHECK (TrackNumber >= 1),
    PRIMARY KEY (AlbumID, SongID)
);

CREATE TABLE FollowsArtist (
    UserID VARCHAR(50) REFERENCES "User"(UserID) ON DELETE CASCADE,
    ArtistID VARCHAR(50) REFERENCES Artist(ArtistID) ON DELETE CASCADE,
    PRIMARY KEY (UserID, ArtistID)
);

CREATE TABLE CreatesPlaylist (
    UserID VARCHAR(50) REFERENCES "User"(UserID) ON DELETE CASCADE,
    PlaylistID VARCHAR(50) REFERENCES Playlist(PlaylistID) ON DELETE CASCADE,
    PRIMARY KEY (UserID, PlaylistID)
    -- Every playlist must have a creator (total participation)
);

CREATE TABLE InPlaylist (
    SongID VARCHAR(50) REFERENCES Song(SongID) ON DELETE CASCADE,
    PlaylistID VARCHAR(50) REFERENCES Playlist(PlaylistID) ON DELETE CASCADE,
    DateAdded DATE DEFAULT CURRENT_DATE CHECK (DateAdded <= CURRENT_DATE),
    SongOrder INT CHECK (SongOrder >= 1),
    PRIMARY KEY (PlaylistID, SongID)
);

CREATE TABLE FollowsPlaylist (
    UserID VARCHAR(50) REFERENCES "User"(UserID) ON DELETE CASCADE,
    PlaylistID VARCHAR(50) REFERENCES Playlist(PlaylistID) ON DELETE CASCADE,
    PRIMARY KEY (UserID, PlaylistID)
);

CREATE TABLE LikesSong (
    UserID VARCHAR(50) REFERENCES "User"(UserID) ON DELETE CASCADE,
    SongID VARCHAR(50) REFERENCES Song(SongID) ON DELETE CASCADE,
    PRIMARY KEY (UserID, SongID)
);

CREATE TABLE FollowsUser (
    FollowerID VARCHAR(50) REFERENCES "User"(UserID) ON DELETE CASCADE,
    FollowedID VARCHAR(50) REFERENCES "User"(UserID) ON DELETE CASCADE,
    CHECK (FollowerID <> FollowedID),
    PRIMARY KEY (FollowerID, FollowedID)
);
