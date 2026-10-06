<!-- markdownlint-disable MD033 -->

# Music Processing Project

## Documentation Index

1. [Project Environment](docs/md_files/Environment.md) <!-- @subpage project_environment -->
2. [Example Scripts](docs/md_files/Examples.md) <!-- @subpage example_scripts -->
3. [API Documentation](docs/md_files/Documentation.md) <!-- @subpage api_documentation -->
4. [Unit Testing](docs/md_files/Testing.md) <!-- @subpage unit_testing -->
5. [Project Workflow](docs/md_files/Workflow.md) <!-- @subpage project_workflow -->

## Purpose

A project for audio file collection metadata.

My music collection is large and varies widely in metadata quality & accuracy.<br>
I finally got very tired of the inconsistencies and inaccuracies, so here we are:<br>
A large Python project to normalize my files the standards I want for my collection.

There are many things I need to do:

- Organize folders per my standard
- Rename songs files per my format
- Convert all non-mp3 audio files to mp3
- Map all metadata to ID3v2.3
  - Remove any other metadata encoding
- Ensure all songs have required metadata
- If possible, populate optional metadata
- Normalize volume levels

## Sources

I have these primary sources:

- Digital files from my HTPC (home theatre personal computer)
  - These files have all been metadata edited with Windows Media Player
  - Almost all have album art
  - Almost all song files are in my preferred filename format (mp3)
  - Most have my preferred directory structure
- Digital purchases from iTunes
  - they have great metadata & quality
  - just need to be converted from m4a to mp3
  - will need proper directory structure
- Digital acquisitions from friends
  - wildly varying in metadata quality
  - MusicBrainz Picard, Discogs, MP3Tag all get used as necessary to complete the metadata (textual and art)
  - may need conversion to mp3 format
  - will need proper directory structure
- Compact Discs I have personally ripped
  - of course the metadata is perfect ... at least for the newest CD's
  - ripping software like Exact Audio Copy uses online databases like MusicBrainzPicard et al
    - not absolutely guaranteed accurate, but I have the CD sleeve, so I can hand bomb in the metadata
  - will need proper directory structure
- Vinyl LPS I have digitized
  - they do need conversion from wav to mp3
  - metadata has to be added post export
  - this means getting all the metadata from sources like MusicBrainz Picard & Discogs, and packaging it for addition to files
    - not absolutely guaranteed accurate, but I have the LP sleeve, so I can hand bomb in the metadata
  - will need proper directory structure

## Audio Files

There are different audio file types, and they come with different metadata encoding formats.<br>
And of course, some audio files may have no embedded metadata (text or image).

- flac (Free Lossless Audio Codec)
  - these are contributed by friends
  - great audio quality, but larger file size
  - come with Vorbis metadata encoding
  - not 100% supported by playback software, especially on older hardware
- mp3 (MPEG-1 Audio Layer III)
  - this is the majority of my own files
  - my preferred final file type - decent compromise between file size and quality
  - can have APEv2, ID3v1, ID3v1.1, ID3v2.3, ID3v2.4 metadata encoding
    - ID3v2.3 is my preferred metadata encoding
  - almost universally supported by playback software (both the mp3 audio format and ID3v2.3 metadata encoding)
- m4a (MPEG-4 Audio)
  - these are iTunes purchase & downloads
  - come with MP4 metadata encoding (which applies to both .m4a and .mp4 extensions)
  - not 100% supported by playback software, especially on older hardware
- wma (Windows Media Audio)
  - designed to store compressed digital audio music files, similar to an MP3
    - often played back through Windows Media Player, which is no longer reliable/available Windows 10 & up
  - come with ASF metadata encoding (Microsoft - just gotta make things *confusing* and not keeping similar naming)
  - not 100% supported by playback software, especially on older hardware
- wav (Waveform Audio File Format)
  - don't have any yet, but I do anticipate needing them - best format for digitizing vinyl LPS
  - very large size but high quality
  - can come with APEv2/ID3v1/ID3v1.1/ID3v2.3/ID3v2.4 metadata encoding, also BWF/iXML/RIFF INFO chunks
  - not 100% supported by playback software, especially on older hardware

## Playlist Files

I prefer m3u playlist format. Originally designed for mp3 files, they are the de facto standard playlist format.<br>
They are relative pathed to the songs they list (they *must* reside in the top level directory).<br>
They are text editor editable, and almost universally supported by player software.<br>

I prefer to name playlist files descriptively - "Favourites", "Symphonic Rock", "Romantic", etc.

## Metadata Tag Editors & Databases

### [Mp3Tag](https://www.mp3tag.de/en/)

Mp3Tag is a multi-format (audio files & metadata encoding schemas) tag editor.<br>
It supports uses Discogs, MusicBrainz picard and freedb for information sources.<br>
Basic paradigm is batch editing of single audio files.<br>
It's my go to.

#### MP3Tag Pros

- doesn't add a lot of extraneous metadata
- batch editing of tags & files
- reasonably intuitive UI
- spreadsheet style display

#### MP3Tag Cons

- will prefer APE tags or ID3, which can be confusing and cause saving failures
- metadata browser search & retrieval can fail on same song that MusicBrainz succeeds with

### [puddletag](https://docs.puddletag.net/)

puddletag is essentially the Ubuntu equivalent of MP3Tag. My go to on Ubuntu.

#### puddletag Cons

- up to date code

### [MusicBrainz Picard](https://picard-docs.musicbrainz.org/v2.13/en/index.html)

MusicBrainz is both a multiple metadata encoding schema tag editor (Picard) & database (MusicBrainz).<br>
Basic paradigm is processing one album at a time.<br>
It's the pro from Dover when MP3tag/puddleTag don't cut the mustard.

#### MusicBrainz Picard Pros

- can add a significant amount of metadata (more than  I really need)
- better metadata browser search and retrieval
- more likely to have officially released metadata

#### MusicBrainz Picard Cons

- not as intuitive UI
- does not have full support for .wav files
- not a batch editor

### [Discogs](https://www.discogs.com/)

Discogs is a music info database. MP3tag/puddleTag use it under the hood, but you can use it directly.<br>
It's really good for album art, often succeeding when MusicBrainz Picard fails.

#### Discogs Pros

- tends to have more metadata available

#### Discogs Cons

- metadata is mostly user uploaded and not as accurate as official released

## Audio & Playlist File Processing

### [Audacious](https://audacious-media-player.org/)

Open source audio player. Alternative playlist editor and WMP alternative.

#### Audacious Pros

- Free, open source
- Runs on Windows and Linux
- Native support for flac, mp3, m4a, wav, m3u
- can use FFMPEG for more file type support

#### Audacious Cons

- No integral help
- No online help

### [Audacity](https://www.audacityteam.org/)

Open source, free software for recording and editing audio.

#### Audacity Pros

- Free, open source
- low resource usage
- plugin support

#### Audacity Cons

- Destructive editing
- limited mixing capabilities
- plugin stability issues
- requires ffmpeg install for some transcoding
- Audacity configuration to use ffmpeg is challenging
- no official direct support

### [Exact Audio Copy](https://www.exactaudiocopy.de/)

Exact Audio Copy is a so called audio grabber for audio CDs using standard CD and DVD-ROM drives.<br>
Best replacement I have found for playlist generation & editing now that WMP is belly up.

#### EAC Pros

- Freeware (on Windows)
- bit perfect accuracy
- error correction
- comprehensive format support
- detailed logging

#### EAC Cons

- Steep learning curve and setup
- slower ripping speeds
- outdated GUI
- Windows only

### [ffmpeg](https://www.ffmpeg.org/)

FFMPEG is a universal media converter. Comes with ffprobe, which is information tool.

#### FFMPEG Pros

- fast & versatile
- It can read a wide variety of inputs, and transcode them into a plethora of output formats
- The python sub-process module can directly run ffmpeg & ffprobe command lines scripting use

#### FFMPEG Cons

- documentation is difficult to use
- very complex command line only interface
- Not for metadata

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

Technically, Audacity/EAC/FFmpeg/Goldwave are also media file players, but that's not their primary function.

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

#### VLC Pros

- can so some tag editing, but is really a media player at heart
- can rip mp3's from cd's, but Audacity/EAC/Goldwave are probably better

#### VLC Cons

- GUI could be more intuitive
