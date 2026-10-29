<!-- markdownlint-disable MD033 -->

# Music Processing Project

## Documentation Index

1. [Project Environment](docs/md_files/Environment.md) <!-- @subpage project_environment -->
2. [Example Scripts](docs/md_files/Examples.md) <!-- @subpage example_scripts -->
3. [Command Lines](docs/md_files/Commands.md) <!-- @subpage command_lines -->
4. [API Documentation](docs/md_files/Documentation.md) <!-- @subpage api_documentation -->
5. [Unit Testing](docs/md_files/Testing.md) <!-- @subpage unit_testing -->
6. [Project Workflow](docs/md_files/Workflow.md) <!-- @subpage project_workflow -->

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

## Usage

### GUI mode

GUI mode exists for accessibility and discoverability, visual feedback, and a lower barrier to entry.

- Accessibility and Discoverability: Non-technical users can see available options without memorizing text commands.
- Visual Feedback: Complex data, live previews, progress bars, and error highlights are much easier to inspect in a visual layout.
- Lower Barrier to Entry: Casual or occasional users can learn and operate the software quickly with minimal training or documentation.

### CLI Mode

CLI mode exists for automation and scripting, batch processing, remote and headless environments, and speed for power users.

- Automation and Scripting: A CLI lets users plug the app into shell scripts, cron jobs, or CI/CD pipelines to run tasks without human supervision.
- Batch Processing: Users can process dozens or hundreds of files at once using loops or wildcards instead of clicking through windows manually.
- Remote and Headless Environments: CLI runs easily on servers, Docker containers, via SSH where display monitors and window managers do not exist.
- Power Users: Experienced users can execute complex configurations with a few keystrokes faster than navigating multi-tab menus.

**Note**<br>
Any file paths with spaces must be be encapsulated in quotation marks; it's really best practice to do it all the time.

```text
PS D:\MusicProcessing> python main.py --help
usage: main.py [-h] command ...

Music Processing

options:
  -h, --help                                                show this help message and exit

subcommands:
  command
    gui                                                     Run in GUI mode

    clip-check-file                                         Check peak, RMS, and EBU R128 leveling for a single audio file;
                                                            mandatory: audio file path;

    clip-check-walk                                         Check peak, RMS, and EBU R128 leveling options for audio files;
                                                            mandatory: start path tld/fld;

    convert-file file --target target                       Convert audio file to mp3;
                                                            mandatory: audio file path;
                                                            optional: converted file target path

    convert-walk tld --pattern pattern --target target      Convert audio files to mp3;
                                                            mandatory: start path tld/fld/sld;
                                                            optional: file ext {.flac|.mp3|.m4a|.wma}; optional: converted files target path

    create-albums tld                                       Create album sub-directories;
                                                            mandatory: start path tld only

    ebu-file file --target target                           EBU R128 level audio file;
                                                            mandatory: audio file path;
                                                            optional: leveled file target path

    extract-album-art file                                  Extract audio file embedded art;
                                                            mandatory: audio file path

    extract-walk tld --pattern pattern                      Extract audio files embedded art;
                                                            mandatory: start path tld/fld;
                                                            optional: file ext {.flac|.mp3|.m4a|.wma}

    get-audio-file-list tld                                 Get CSV list of audio file paths;
                                                            mandatory: start path tld only

    get-ext-file-list tld --pattern pattern                 Get CSV list of audio file extensions;
                                                            mandatory: start path tld/fld/sld;
                                                            optional: file ext {.flac|.mp3|.m4a|.wma}

    get-media-info-walk tld --pattern pattern               Get text list of audio files media info;
                                                            mandatory: start path tld/fld;
                                                            optional: file ext {.flac|.mp3|.m4a|.wma}

    get-tags-walk tld --pattern pattern --ffprobe ffprobe   Get text list of audio files metadata tags;
                                                            mandatory: start path tld/fld;
                                                            optional: file ext {.flac|.mp3|.m4a|.wma}; optional: use ffprobe True

    level-normalize-walk tld type --target target           Level normalize files per type;
                                                            mandatory: start path tld/fld; mandatory: level type {ebu|peak|rms};
                                                            optional: leveled files target path

    normalize-filename file                                 Normalize audio file from its metadata;
                                                            mandatory: audio file path

    normalize-filename-walk tld                             Normalize audio files from their metadata;
                                                            mandatory: start path tld/fld/sld

    remove-empty-albums tld                                 Remove empty album sub-directories;
                                                            mandatory: start path tld/fld

    remove-pattern tld pattern                              Remove files with specified pattern;
                                                            mandatory: top level directory; mandatory: file pattern

    remove-set-list tld                                     Remove files matching hard-coded pattern set;
                                                            mandatory: starting path tld/fld/sld

    rename-album-directories tld                            Rename album paths from metadata;
                                                            mandatory: start path tld only

    peak-file file --target target                          Peak level audio file;
                                                            mandatory: audio file path;
                                                            optional: leveled file target path

    rms-file file --target target                           RMS level audio file;
                                                            mandatory: audio file path;
                                                            optional: leveled file target path

    set-album-art tld                                       Set albums art file;
                                                            mandatory: starting path tld/fld

    update-genres tld csv                                   Update songs genre from CSV;
                                                            mandatory: start path tld only; mandatory: artist genre CSV file path

    update-playlist tld m3u                                 Update playlist file songs path;
                                                            mandatory: start path tld only; mandatory: playlist file in tld path

    update-walk tld                                         Update playlist files songs path;
                                                            mandatory: start path tld only
```

## Project Structure

```text
MusicProcessing
|_.github
| |_ copilot-instructions.md
| |
| |_instructions
| | |_ *.instructions.md
| |
| |_workflows
|   |_ *.yml
|
|_.vscode
| |_ launch.json
| |_ settings.json
| |_ tasks.json
|
|_docs
| |_command_lines
| | |_ *.txt
| |
| |_dot_files
| | |_ *.dot
| | |_ *.png
| | |_ *.svg
| |
| |_excel_files
| | |_ *.xlsx
| |
| |_extensions
| | |_ extensions.txt
| |
| |_ffmpeg_info
| | |_ *.pdf
| |
| |_md_files
| | |_ *.md
| |
| |_planning
| | |_ *.md
| | |_ todo.txt
| |
| |_scripts
|   |_google
|   | |_purpose 1
|   | | |_ *.py
|   | |_purpose i
|   | | |_ *.py
|   | |_purpose n
|   |   |_ *.py
|   |
|   |_mine
|     |_purpose 1
|     | |_ *.py
|     |_purpose i
|     | |_ *.py
|     |_purpose n
|       |_ *.py
|
|_html
| |_ *.html
| |_ *js
| |
| |_search
| | |_ *.js
|
|_src
| |_ __init__.py
| |_ errors.py
| |_ level_filter.py
| |_ logging_config.py
| |_ subprocess_utils.py
| |
| |_audio_info
| | |_ __init__.py
| | |_ audio_art.py
| | |_ audio_metadata.py
| | |_ audio_playlist.py
| | |_ audio_utilities.py
| |
| |_audio_normalize
| | |_ __init__.py
| | |_ audio_normalization.py
| |
| |_dir_processing
| | |_ __init__.py
| | |_ directory_processing.py
| |
| |_generated_files
| | |_ .gitignore
| | |_ __init__.py
| | |_ test.m3u
| | |
| | |_AlbumArt
| | | |_*.jpg
| | |
| | |_csv_files
| | | | *.csv
| | |
| | |_icon_files
| | | |_attributions.txt
| | | |_*.png
| | |
| | |_licenses
| | | | *.pdf
| | |
| | |_log_files
| | | |_ *.log
| | |
| | |_result_files
| |   |_ *.txt
| |
| |_gui
|   |_ __init__.py
|   |_ handlers.py
|   |_ wx_app.py
|
|_tests
| |_ __init__.py
| |_ *<fixture>.csv
| |_ <fixture>.m3u
| |_ <fixture>.txt
| |_ <fixture>.mp3
| |_ support.py
| |_ test_audio_art.py
| |_ test_audio_metadata.py
| |_ test_audio_normalization.py
| |_ test_audio_playlist.py
| |_ test_audio_utilities.py
| |_ test_directory_processing.py
| |_ test_gui.py
| |_ test_subprocess_utilities.py
| |
| |_Music
|   |_ test.csv
|   |_ test.m3u
|   |_ test.sh
|   |
|   |_artists with 0 album, containing 1 song, 0 art
|   | |_ song
|   |
|   |_artists with 1 album, containing 1 song, 0 art
|   | |_album
|   |   |_ song
|   |
|   |_artists with 1 album, containing 1 song, 1 art
|   | |_album
|   |   |_ song
|   |   |_ Folder.jpg
|   |
|   |_artists with 1 album, containing 2 songs, 0 art
|   | |_album
|   |   |_ song 1
|   |   |_ song 2
|   |
|   |_artists with 1 album, containing 2 songs, 1 art
|   | |_album
|   |   |_ song 1
|   |   |_ song 2
|   |   |_ Folder.jpg
|   |
|   |_artists with 2 albums, each containing 1 song, 0 art
|     |_album 1
|     | |_ song
|     |_album 2
|       |_ song
|
|_ .gitignore
|_ Doxyfile
|_ doxygen-custom.css
|_ doxygen.log
|_ main.py
|_ MusicProcessing.code-workspace
|_ README.md
|_ requirements.txt
```

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
  - come with MP4 metadata encoding
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
They are relative pathed to the songs they list (which means the playlist *must* reside in the top level directory).<br>
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
