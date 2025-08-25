F:\PreppedMusic directory is the original audio & playlist files from the HTPC (\\Office1\Music\).
Ubuntu dev: /home/gerald/Music
Windows dev: C:\Music
None of these locations need updating.

The audio files are in mp3, m4a, and wma formats.
The playlist (m3u) files have been copied as is from source music directory.
The sundry files (csv and txt) files have not been copied from source music directory.
The audio metadata (text and art) are in ASF, ID3v2.3, and MP4 formats.
APE, ID3v1, ID3v2.2, and ID3v2.4 format metadata has been removed.

The audio metadata has been manually reviewed for:
    reasonably high accuracy
    acceptable artist name for directory name creation
    acceptable album name for directory name creation
    acceptable song title (artist-tile or artist - title) format
    minimum metadata set (for Windows display values):
        album
        album artist
        artist
        date
        genre
        title
        front cover album art

The top level directory (PreppedMusic) has been organized into:
    artist sub-directories have been created or edited as necessary:
        where artist names are drawn from metadata
    album sub-directories have been created or edited as necessary:
        where album names are drawn from metadata

Audio file names have been edited as needed into artist-title (or artist - title) format.

Album art metadata has been manually reviewed to ensure reasonably accuracy.
Album art metadata has been processed to ensure one of:
        already embedded in audio file
        present as <album directory>.jpg in AlbumArt special directory

Album art has been "extracted" to ensure a Folder.jpg album art file exists in each album sub-directory.

These audio files are now ready for conversion:
    original metadata format to ID3v2.3 metadata format mapping
    conversion to mp3 audio format
    album art embedding as ID3v2.3 art tag

Directory structure is:
```text
tld
|_ playlist 1
|_ playlist i
|_ playlist n
|_ artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album i
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album n
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|_ artist i
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album i
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album n
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|_ artist n
     |_album 1
     |    |_song 1
     |    |_song i
     |    |_song n
     |_album i
     |    |_song 1
     |    |_song i
     |    |_song n
     |_album n
          |_song 1
          |_song i
          |_song n
```