
-- ENTITY TABLES

CREATE TABLE Artist (
    ArtistID SERIAL PRIMARY KEY,
    ArtistName VARCHAR(100) NOT NULL,
    ArtistPopularity INT CHECK (ArtistPopularity BETWEEN 0 AND 100),
    ArtistArtURL VARCHAR(500)
);

CREATE TABLE Song (
    SongID SERIAL PRIMARY KEY,
    SongTitle VARCHAR(100) NOT NULL,
    Duration_ms INT CHECK (Duration_ms > 0),
    SongReleaseDate DATE CHECK (SongReleaseDate <= CURRENT_DATE),
    SongPopularity INT CHECK (SongPopularity BETWEEN 0 AND 100),
    SongArtURL VARCHAR(500)
);

CREATE TABLE Genre (
    GenreID SERIAL PRIMARY KEY,
    GenreName VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Album (
    AlbumID SERIAL PRIMARY KEY,
    AlbumTitle VARCHAR(100) NOT NULL,
    AlbumReleaseDate DATE CHECK (AlbumReleaseDate <= CURRENT_DATE),
    Label VARCHAR(100),
    NumberOfTracks INT NOT NULL CHECK (NumberOfTracks >= 1),
    AlbumArtURL VARCHAR(500)
);

-- Note: User is a reserved keyword, so we use double quotes.
CREATE TABLE "User" (
    UserID SERIAL PRIMARY KEY,
    Username VARCHAR(100) UNIQUE NOT NULL,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100),
    UserArtURL VARCHAR(500)
);

CREATE TABLE Playlist (
    PlaylistID SERIAL PRIMARY KEY,
    PlaylistName VARCHAR(100) NOT NULL,
    PlaylistArtURL VARCHAR(500)
);

-- RELATIONSHIP TABLES


-- Every song must have a performer (total participation)
CREATE TABLE Performs (
    ArtistID INT REFERENCES Artist(ArtistID) ON DELETE CASCADE,
    SongID INT REFERENCES Song(SongID) ON DELETE CASCADE,
    PRIMARY KEY (ArtistID, SongID)
);

-- Every artist must have a genre (total participation)
CREATE TABLE IsGenre (
    ArtistID INT REFERENCES Artist(ArtistID) ON DELETE CASCADE,
    GenreID INT REFERENCES Genre(GenreID) ON DELETE CASCADE,
    PRIMARY KEY (ArtistID, GenreID)
);

CREATE TABLE InAlbum (
    SongID INT REFERENCES Song(SongID) ON DELETE CASCADE,
    AlbumID INT REFERENCES Album(AlbumID) ON DELETE CASCADE,
    TrackNumber INT CHECK (TrackNumber >= 1),
    PRIMARY KEY (AlbumID, SongID)
);

CREATE TABLE FollowsArtist (
    UserID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
    ArtistID INT REFERENCES Artist(ArtistID) ON DELETE CASCADE,
    PRIMARY KEY (UserID, ArtistID)
);

CREATE TABLE CreatesPlaylist (
    UserID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
    PlaylistID INT REFERENCES Playlist(PlaylistID) ON DELETE CASCADE,
    PRIMARY KEY (UserID, PlaylistID)
    -- Every playlist must have a creator (total participation)
);

CREATE TABLE InPlaylist (
    PlaylistID INT REFERENCES Playlist(PlaylistID) ON DELETE CASCADE,
    SongID INT REFERENCES Song(SongID) ON DELETE CASCADE,
    DateAdded DATE DEFAULT CURRENT_DATE CHECK (DateAdded <= CURRENT_DATE),
    SongOrder INT CHECK (SongOrder >= 1),
    PRIMARY KEY (PlaylistID, SongID)
);

CREATE TABLE FollowsPlaylist (
    UserID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
    PlaylistID INT REFERENCES Playlist(PlaylistID) ON DELETE CASCADE,
    PRIMARY KEY (UserID, PlaylistID)
);

CREATE TABLE Likes (
    UserID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
    SongID INT REFERENCES Song(SongID) ON DELETE CASCADE,
    PRIMARY KEY (UserID, SongID)
);

CREATE TABLE FollowsUser (
    FollowerID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
    FollowedID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
    CHECK (FollowerID <> FollowedID),
    PRIMARY KEY (FollowerID, FollowedID)
);
