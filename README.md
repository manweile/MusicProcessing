# Music Processing
These scripts process my audio files to the standards I want for my collection.

## Purpose
There are many things I need to do:
- Organize folders per my standard
  - top level dir
    - artist sub dir
      - album sub dirs
- Rename files per my format
  - artist-title
- Convert all non-mp3 audio files to mp3
- Update metadata tags
  - ensure all tags are ID3v2.3
    - up convert any ID3 < v2.3 to 2.3
    - down convert any ID3v2.4 to 2.3
    - convert APEv2 to ID3v2.3
  - ensure all songs have correct:
    - title
    - artist
    - album
    - genre
    - year
    - bit rate (>=128 kbps)
    - front cover album art
    - media source
      - vinyl
        - recorded from vinyl lp
      - cd
        - ripped from cd
      - digital
        - downloaded

## Source Files

### Location
The source location is on my HTPC (home theatre personal computer).
These files have all been metadata edited with Windows Media Player.
- Almost all have album art
- Almost all song files are in my preferred filename format
- The majority are mp3 files (my preferred format)
- Most have my preferred directory structure

### Working Copy
The files on the HTPC will be copied as is to a micro-sd card.
The project will read files from the micro-sd card.

### Directory Structure
My preferred directory structure is: "drive":\"top level dir"\"artist name"\"album name"\, with the songs for the album.
- Some artists will not have album sub-directories
- All the songs for that artist, irregardless of what album they are from will be under the artist directory
- There is not a directory for compilation albums
  - songs from compilation albums are under the contributing artist

### Audio Filename Format & Type/Metadata
My preferred filename format is "artist name"-"song title", or "artist name" - "song title".
My preferred audio file type & metadata is mp3 with ID3v2.3 tags.

## Audio File Types
There are different audio file types
- mp3
  - this is the majority file type, and my preferred final file type
- wma
  - not near as many as mp3, but 2nd most likely file type
- m4a
  - these are iTunes purchase & downloads

## Playlist File Types
- m3u
  - general playlist file

# Tools
There are several different tools I can use.

## Tag Editors & Databases

### [Mp3Tag](https://www.mp3tag.de/en/)
Mp3Tag is a multi-format (audio files & metadata schemas) tag editor.
It supports uses Discogs, MusicBrainz picard and freedb for information sources.
Basic paradigm is batch editing of single audio files.
#### MP3Tag Pros
- doesn't add a lot of extraneous metadata
- batch editing of tags & files
- reasonably intuitive UI
#### MP3Tag Cons
- will prefer APE tags or ID3, which can be confusing and cause saving failures
- metadata browser search & retrieval can fail on same song that MusicBrainz succeeds with

### [MusicBrainz Picard](https://picard-docs.musicbrainz.org/v2.13/en/index.html):
MusicBrainz is both a tag editor (Picard) & database (MusicBrainz).
Basic paradigm is processing one album at a time.
#### MusicBrainz Picard Pros
- can add a significant amount of metadata (more than  I really need)
- better metadata browser search and retrieval
- good metadata accuracy
#### MusicBrainz Picard Cons
- not as intuitive UI
- does not have full support for .wav files
- not a great batch editor

### [Discogs](https://www.discogs.com/)
Discogs is a music info database.
#### Discogs Pros
- tends to have more metadata available
#### Discogs Cons
- metadata is mostly user uploaded and not as accurate as official release images

## Audio File Processing

### [ffmpeg](https://www.ffmpeg.org/)
FFMPEG is ipsum lorem
#### FFMPEG Pros
- ipsum lorem
#### FFMPEG Cons
- ipsum lorem

### [Goldwave](https://goldwave.com/)
Goldwave is ipsum lorem
#### Goldwave Pros
- very good for vinyl LP recording
- can convert file formats (m4a, wav, wma) to mp3
- can rip mp3's from cd's
- can play all of my audio file formats
#### Goldwave Cons
- ipsum lorem

## Audio File Players

### [Windows Media Player](https://support.microsoft.com/en-us/windows/windows-media-player-12-e8f84f54-cd64-865c-2e83-1d8ec121b5b8)
WMP is a ipsum lorem
#### WMP Pros
- can do some tag editing
- adequate for ripping mp3's from cd's
- can create m3u playlists
#### WMP Cons
- hard coded defaults are a real PITA
  - album art displaying properly
  - playlists
    - wpl files use absolute paths, which makes them not very portable for use on other devices
    - m3u can be created, but not best ui functionality to do so

### [VLC](https://www.videolan.org/vlc/):
VLC is a ipsum lorem
#### VLS Pros
- can so some tag editing, but is really a media player at heart
- can rip mp3's from cd's, but goldwave is probably better
#### VLC Cons
- ui could be more intuitive

# Processing Steps

## Tag Editor Preprocessing
I will use MP3Tag to:
- verify all wma files have only WMA tags
- verify all m4a files have only MP4 tags
- remove all APEv2 tags from mp3 files
  - remove all non ID3v2.3 tags from mp3 files
  - verify all mp3 files have only ID2v2.3 tags
- rename the few audio files that have incorrect filename format

## Python Music Processing
I will use the music processing  python code to:
- create csv lists
  - all audio files and their extension
  - all mp3 files
  - all wma files
  - all m4a files
- convert wma files to mp3 files
- convert m4a files to mp3 files
- create album sub-dirs for artist directories