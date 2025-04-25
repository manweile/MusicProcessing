# Music Processing
These scripts process my audio files to the standards I want for my collection

## Purpose
There are many things I need to do:
- Organize folders per my standard
  - top level dir
    - artist sub dir
      - album sub dirs
- Rename files per my format
  - artist-title
- Convert all non-mp3 audio files to mp3
- Update information tags
  - ensure all tags are ID3v2.3
    - convert ID3v2.4 to 2.3
    - convert APE to ID3v2
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
- wpl
  - windows media player playlist file

## Tools
There are several different tools I can use

### Tag Editors & Databases
Mp3Tag
- a tag editor
- uses Discogs, MusicBrainz picard and freedb for information sources
- not very intuitive UI
- so-so better help documentation
- doesn't add a lot of extraneous metadata
- will prefer APE tags or ID3, which can be confusing and cause saving failures
[MusicBrainz Picard](https://picard-docs.musicbrainz.org/v2.13/en/index.html)
- uses mutagen under the hood
- both tag editor & database
- more intuitive UI
- far more configurable
- much better help documentation
- can add a significant amount of metadata (more than  I really need)
- can do playlists
Discogs
- is a music info database

### Audio File Processing
Goldwave
- very good for vinyl LP recording
- can convert file formats (m4a, wav, wma) to mp3
- can rip mp3's from cd's
- can play all of my audio file formats

### Audio File Players
Windows Media Player
- can do some tag editing, but is really limited and flaky in re album art displaying properly
- adequate for ripping mp3's from cd's, but goldwave is probably better
- is adequate for playlists - with caveats in re playlist file types and save locations
VLC
- can so some tag editing, but is really a media player at heart
- can rip mp3's from cd's, but goldwave is probably better

### Python Modules
[eyeD3](https://eyed3.readthedocs.io/en/latest/index.html):
- eyeD3 is a Python tool for working with audio files, specifically MP3 files containing ID3 metadata (i.e. song info)
- It provides a command-line tool (eyeD3) and a Python library (import eyed3) that can be used to write your own applications or plugins that are callable from the command-line tool
- only supports mp3 file format
- not the best documentation & examples
- probably better for command line tool than mutagen

[mutagen](https://mutagen.readthedocs.io/en/latest/):
- Mutagen is a Python module to handle audio metadata
- provides a command line tool
- It supports ASF, FLAC, MP4, Monkey’s Audio, MP3, Musepack, Ogg Opus, Ogg FLAC, Ogg Speex, Ogg Theora, Ogg Vorbis, True Audio, WavPack, OptimFROG, and AIFF audio files
- much better documentation & examples
- probably better python module than eyeD3

# Python Organization
I will have a main entry point that parses input arguments

## Packages
May have 2 packages
- music processing
- directory processing

### Classes
MusicProcessing:
- class for all tag processing
  - get artist name for album sub-directory creation & existence checking
  - get artist & title for file checking file name for correct format & renaming
  - output list of audio files without metadata
    - artist
    - title
    - album
    - track number
    - genre
    - release date
    - album art
  - output list of artist directories without album sub directories
  - output list of non-mp3 files
  - output list of audio files with non-ID3v2.3 tags
    - found tag type
    - full file path
  - convert non-mp3 files to mp3 format
  - convert non ID3v2.3 tags to 2.3
  - create album sub-directories for all artist directories
  - rename all files to artist name-title format

DirProcessing
- class for OS related file handling
  - directory walking
  - file open, close, writing, renaming
  - directory creation

#### Functions
