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
    - convert APE to ID3v2.3
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
The source location is on my HTPC.
The files on the HTPC will be copied as is to a micro-sd card.
The project will read files from the micro-sd card.

## Audio File Types
There are different audio file types
- mp3
  - this is the majority file type, and my preferred final file type
- wma
  - not near as many as mp3, but 2nd most likely file type
- m4a
  - these are iTunes purchase & downloads
- wav
  - Goldwave recordings

## Playlist File Types
- m3u
  - general playlist file

## Tools
There are several different tools I can use

### Tag Editors & Databases
Mp3Tag:
- a tag editor
- uses Discogs, MusicBrainz picard and freedb for information sources
pros:
- doesn't add a lot of extraneous metadata
- reasonably intuitive UI
cons:
- will prefer APE tags or ID3, which can be confusing and cause saving failures
- metadata browser search & retrieval can fail on same song that MusicBrainz succeeds with

[MusicBrainz Picard](https://picard-docs.musicbrainz.org/v2.13/en/index.html):
- uses mutagen under the hood
- both tag editor & database
pros:
- can add a significant amount of metadata (more than  I really need)
- better metadata browser search and retrieval
cons:
- not as intuitive UI

Discogs:
- is a music info database

### Audio File Processing
[ffmpeg](https://www.ffmpeg.org/):

Goldwave:
- very good for vinyl LP recording
- can convert file formats (m4a, wav, wma) to mp3
- can rip mp3's from cd's
- can play all of my audio file formats

### Audio File Players
Windows Media Player:
- can do some tag editing, but is really limited and flaky in re album art displaying properly
- adequate for ripping mp3's from cd's, but goldwave is probably better
- is adequate for playlists - with caveats in re playlist file types and save locations

VLC:
- can so some tag editing, but is really a media player at heart
- can rip mp3's from cd's, but goldwave is probably better

## Processing Steps
### Tag Editor Preprocessing
I will use MP3Tag to:
- verify all wma files have only WMA tags
- verify all m4a files have only MP4 tags
- remove all APEv2 tags from mp3 files
  - remove all non ID3v2.3 tags from mp3 files
  - verify all mp3 files have only ID2v2.3 tags
- rename a few audio files that have NN title.ext to artist name-song title.ext

### Python Music Processing
I will use the music processing  python code to:
- convert wma files to mp3 files
- convert m4a files to mp3 files
-