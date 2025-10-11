# Music Processing
These scripts process my audio files to the standards I want for my collection.

## Purpose
There are many things I need to do:
- Organize folders per my standard
  - top level dir
    - artist sub dir
      - album sub dirs
        - find cover art for album dirs
- Rename files per my format
  - artist-title
- Convert all non-mp3 audio files to mp3
- Update metadata tags
  - ensure all tags are ID3v2.3
    - up convert any ID3 < v2.3 to 2.3
    - down convert any ID3v2.4 to 2.3
    - convert APEv2 to ID3v2.3
  - ensure all songs have these tags:
    - album
    - album artist
    - artist
    - date
    - genre
    - title
    - front cover album art
  - if possible, populate these "nice to have" tags:
    - composer
    - copyright
    - disc
    - publisher
    - track
- Normalize volume levels

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
The files will be copied to respective hdd (ubuntu laptop and win 10 desktop).
The project will read files from the respective hdd.

### Directory Structure
My preferred directory structure is: "drive":\"top level dir"\"artist name"\"album name"\, with the songs for the album.
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
- spreadsheet style display
#### MP3Tag Cons
- will prefer APE tags or ID3, which can be confusing and cause saving failures
- metadata browser search & retrieval can fail on same song that MusicBrainz succeeds with

### [puddletag](https://docs.puddletag.net/)
puddletag is essentially the Ubuntu equivalent of MP3tag

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
- not a batch editor

### [Discogs](https://www.discogs.com/)
Discogs is a music info database.
#### Discogs Pros
- tends to have more metadata available
#### Discogs Cons
- metadata is mostly user uploaded and not as accurate as official release images

## Audio File Processing

### [ffmpeg](https://www.ffmpeg.org/)
FFMPEG is a universal media converter.
It can read a wide variety of inputs - including live grabbing/recording devices - filter, and transcode them into a plethora of output formats.
The python module pydub wraps ffmpeg for scripting use.
#### FFMPEG Pros
- fast & versatile
#### FFMPEG Cons
- documentation is difficult to use
- very complex command line only interface

### [Goldwave](https://goldwave.com/)
Goldwave is a professional, full featured, digital audio editor. Use it to play, record, import, edit, restore, process, analyze, and convert audio.
#### Goldwave Pros
- very good for vinyl LP recording
- can convert file formats (m4a, wav, wma) to mp3
- can rip mp3's from cd's
- can play all of my audio file formats
#### Goldwave Cons
- paid version required for full functionality

## Audio File Players

### [Windows Media Player](https://support.microsoft.com/en-us/windows/windows-media-player-12-e8f84f54-cd64-865c-2e83-1d8ec121b5b8)
WMP is a full-featured music library that allows you to quickly browse and play your music, as well as create and manage playlists.
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
VLC is a multimedia player and framework that plays most multimedia files as well as DVDs, Audio CDs, VCDs, and various streaming protocols.
#### VLS Pros
- can so some tag editing, but is really a media player at heart
- can rip mp3's from cd's, but goldwave is probably better
#### VLC Cons
- ui could be more intuitive

# Processing Steps

## Tag Editor Preprocessing
### Normalization
I will use MP3Tag/puddletag to:
- verify all wma files have only WMA tags
- verify all m4a files have only MP4 tags
- remove all APEv2 tags from mp3 files
  - remove all non ID3v2.3 tags from mp3 files
  - verify all mp3 files have only ID2v2.3 tags
- rename the few audio files that have incorrect filename format
- verify all albums have file system acceptable names for directory creation
- find all metadata with missing tags
- find cover art for all albums
### Acquisition & Accuracy
I will use Musicbrainz Picard and Mp3Tag/puddletag to:
- acquire missing metadata
- update missing or inaccurate metadata

## Python Music Processing
I will use the music processing  python code to:
- create csv lists
  - all audio files and their extension
  - all mp3 files
  - all wma files
  - all m4a files
- convert wma files to mp3 files with my preferred ID3v2.3 tags
- convert m4a files to mp3 files with my preferred ID3v2.3 tags
- normalize mp3 file to mp3 files with my preferred ID3v2.3 tags
- create album sub-dirs for artist directories
- set cover art for compilation albums
- extract embedded cover art if no cover art exists for album

# Processing Flow
- Copy source music from HTPC (\\Office1\Music\).
- Prepare metadata (text and art), directory structure & file names.
- Convert music files to mp3 with embedded art.
- Normalize music to EBU R128 standard.
- Finalize music with updated playlists.