<!-- markdownlint-disable MD033 -->

# README

## Purpose

A project for audio file collection metadata.

My music collection is large and varies widely in metadata quality & accuracy.<br>
I finally got very tired of the inconsistencies and inaccuracies, so here we are:<br>
A large Python project to normalize my files the standards I want for my collection.

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
  - ensure all songs have this minimum metadata:
    - album
    - album artist
    - artist
    - date
    - genre
    - title
    - front cover album art
  - if possible, populate these "nice to have" metadata:
    - composer
    - copyright
    - disc
    - publisher
    - track
- Normalize volume levels
  - I get truly annoyed when a playlist moves to a next song and you are suddenly lowering or increasing the volume.

## Sources

I have these primary sources:

- Digital files from my HTPC (home theatre personal computer)
  - These files have all been metadata edited with Windows Media Player
  - Almost all have album art
  - Almost all song files are in my preferred filename format
  - The majority are mp3 files (my preferred format)
  - Most have my preferred directory structure
- Digital purchases from iTunes
  - they have great metadata & quality
  - just need to be converted from m4a to mp3
  - will need proper directory structure
- Digital acquisitions from friends
  - wildly varying in metadata quality
  - MusicBrainz Picard, Discogs, MP3Tag all get used as necessary to complete the metadata
  - may need conversion to mp3 format
  - will need proper directory structure
- Compact Discs I have personally ripped
  - of course the metadata is perfect ... at least for the newest CD's
  - ripping software like Exact Audio Copy uses online databases like MusicBrainzPicard et al
    - not absolutely guaranteed accurate, but I have the CD sleeve, so I can hand bomb in the metadata
  - will need proper directory structure
- Vinyl LPS I have digitized
  - they do need conversion from wav to mp3
  - metadata has to added post export
  - this means getting all the metadata from sources like MusicBrainz Picard & Discogs, and packaging it for addition to files
    - not absolutely guaranteed accurate, but I have the LP sleeve, so I can hand bomb in the metadata
  - will need proper directory structure

## Directory Structure

My preferred directory structure is: "drive":\"top level dir"\"artist name"\"album name"\, with the songs for the album.

- All the songs for that artist, irregardless of what album they are from, will be under the artist directory
  - songs from compilation albums are under the contributing artist
  - eg: "drive":\"top level dir"\"contributing artist name"\"compilation album name"\
  - songs from compilation albums will NOT have "compilation" metadata
    - Compilation metadata tags are a bit of a gong show in how various metadata formats implement them
    - I found it just wasn't worth the coding effort to deal with them
  - so there will never be a directory for compilation albums
- multi-disc albums will be consolidated under 1 album name
  - multi-disc albums are also a bit of gong show in regards to how the metadata is implemented
  - also in how audio files actually HAVE correct disc number metadata
  - songs on multi-disc albums will have a "disc number" metadata field populated with correct disc number
  - songs on single disc albums will just have "1" in "disc number" field

## Audio Filename Format & Type/Metadata

My preferred filename format is "artist name"-"song title", or "artist name" - "song title".<br>
My preferred audio file type & metadata is mp3 with ID3v2.3 tags.

## Audio File Types

There are different audio file types:

- flac
  - these are contributed by friends
- mp3
  - this is the majority file type, and my preferred final file type
- wma
  - not near as many as mp3, but 2nd most likely file type
- m4a
  - these are iTunes purchase & downloads

## Playlist File Types

- m3u
  - general playlist file

## Tools

There are several different tools I can use.

### Tag Editors & Databases

### [Mp3Tag](https://www.mp3tag.de/en/)

Mp3Tag is a multi-format (audio files & metadata schemas) tag editor.<br>
It supports uses Discogs, MusicBrainz picard and freedb for information sources.<br>
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

puddletag is essentially the Ubuntu equivalent of MP3Tag

#### puddletag Cons

- up to date code

### [MusicBrainz Picard](https://picard-docs.musicbrainz.org/v2.13/en/index.html)

MusicBrainz is both a tag editor (Picard) & database (MusicBrainz).<br>
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

### [Audacity](https://www.audacityteam.org/)

Open source, free software for recording and editing audio.

#### Audacity Pros

ipsum lorem

#### Audacity Cons

ipsum lorem

### [Exact Audio Copy](https://www.exactaudiocopy.de/)

Exact Audio Copy is a so called audio grabber for audio CDs using standard CD and DVD-ROM drives.

#### EAC Pros

Best replacement I have found for playlist generation & editing now that WMP is belly up.

#### EAC Cons

ipsum lorem

### [ffmpeg](https://www.ffmpeg.org/)

FFMPEG is a universal media converter.

#### FFMPEG Pros

- fast & versatile
- It can read a wide variety of inputs, and transcode them into a plethora of output formats
- The python sub-process module can directly run ffmpeg & ffprobe command lines scripting use.

#### FFMPEG Cons

- documentation is difficult to use
- very complex command line only interface

### [Goldwave](https://goldwave.com/)

Goldwave is a professional, full featured, digital audio editor.

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
- works quite well on my Windows 7 HTPC

#### WMP Cons

- hard coded defaults are a real PITA
  - album art displaying properly
  - playlists
    - wpl files use absolute paths, which makes them not very portable for use on other devices
    - m3u can be created, but not best ui functionality to do so
  - is useless as of Windows 10 and greater

### [VLC](https://www.videolan.org/vlc/)

VLC is a multimedia player and framework that plays most multimedia files as well as DVDs, Audio CDs, VCDs, and various streaming protocols.

#### VLS Pros

- can so some tag editing, but is really a media player at heart
- can rip mp3's from cd's, but Audacity/EAC/Goldwave are probably better

#### VLC Cons

- ui could be more intuitive

## Processing Workflow

- Copy source music.
- Prepare metadata (text and art), directory structure & file names.
- Convert music files to mp3 with embedded art.
- Normalize music to EBU R128 standard.
- Finalize music with updated playlists.

## Tag Editor Preprocessing

I will use MP3Tag/MusicBrainz Picard/puddletag to:

- verify all wma files have only WMA tags
- verify all m4a files have only MP4 tags
- verify all flac files only have Vorbis tags
- remove all APEv2 tags from mp3 files
  - remove all non ID3v2.3 tags from mp3 files
  - verify all mp3 files have only ID2v2.3 tags
- find accurate metadata for all tags
- find cover art for all albums

## Python Processing

I will use the music processing python code to:

1. Gather information
   - create csv lists
     - all audio files and their extension
     - all flac files
     - all mp3 files
     - all wma files
     - all m4a files
2. Normalize filenames and directory names
   - rename audio files that have incorrect filename format
   - verify all albums have file system acceptable names for directory creation
   - create album sub-dirs for artist directories
3. Ensure cover art exists
   - extract embedded cover art if no cover art exists for album
   - set cover art for compilation albums
4. Convert audio to mp3 file type
   - convert flac files to mp3 files with my preferred ID3v2.3 tags
   - convert wma files to mp3 files with my preferred ID3v2.3 tags
   - convert m4a files to mp3 files with my preferred ID3v2.3 tags
   - convert mp3 file to mp3 files with my preferred ID3v2.3 tags
5. Level normalize mp3 files
   - level normalize mp3 files to EBU R128 standard
6. Update playlist files
