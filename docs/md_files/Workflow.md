<!-- markdownlint-disable MD033 -->

# Project Workflow {#project_workflow}

The whole point of this project is normalizing an audio collection.<br>
That means a workflow, using the external tools and project functions.

I use these 5 working directories for the processing workflow.

## Source

The original audio, playlist, and occasionally artwork files.<br>
These are the source of truth that start the workflow, and as such, they **DO NOT GET MODIFIED**.

The audio files are in flac, mp3, m4a, wma, and m3u formats.<br>
The audio metadata (text and art) are in APE, ASF, ID3v1, ID3v2.2, ID3v2.3, ID3v2.4, MP4, and Vorbis formats.<br>
The audio metadata is NOT guaranteed complete or accurate.

Copy the originals, directory structure intact, to `Source`.<br>
Use whatever floats your boat to move the files - but be careful to **NOT** set read-only permissions.

## Prepped

This where the real work begins.<br>
I like to work alphabetically - I start with the lowest artist, eg. 3 Doors Down, followed by Abba, BTO, etc.<br>
For each artist, copy ALL of that artist's albums & files to `Prepped`

A word about metadata:<br>
At this point, you *could* ensure all of your metadata is accurate.<br>
But bear in mind how much work that could be.<br>
For right now, I would suggest only 3 fields need to be accurate: artist, album name and song title.

### Directory Tree

Now your are looking at normalizing the artist album directory structure.<br>
Depending on the organization of your sources, you could be doing a little, or a lot.<br>
The directory tree can be a real pain, dependent on your source quality.

Presuming your sources have good artist names, then a big chunk of the work is done.<br>
Artist names need to follow the valid characters for your OS rules.<br>

Album directories are the next hurdle.
Album directories should almost always match album metadata - the exception being when the metadata has invalid for the OS characters.<br>
I use the Windows invalid character set - it's more restrictive and therefore OS agnostic; you can use them on Linux & Mac.<br>
Bottom line, your album name metadata needs to be valid. You may need a metadata editor like MP3Tag/puddleTag or MusicBrainz Picard.<br>
Nice thing about MP3tag/puddleTag is you can bulk change metadata values.

#### Manual Album creation

You can use a file explorer to manually create album directories.<br>
I *think* you can also use MP3tag/puddleTag, just haven't tried.

#### create-albums

create-albums function is for songs standing alone in a 1st level artist directory.

1. ensure that all the songs that need an album directory are sitting by themselves in the **artist 1st level directory**
2. at least one song has viable album name metadata
   1. the function will sanitize the characters `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` to `-`.
3. all songs with matching album name metadata are moved into the new album directory
4. command line: `python main.py create-albums "Drive:/path/to/tld"`

before/after execution:

```text
tld
|_ artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_song 1
|    |_song i
|    |_song n

tld
|_ artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album 2
|    |    |_song 1
|    |    |_song i
|    |    |_song n
```

**Compilation Albums**<br>
ipsum lorem

**Multi Disc Albums**<br>
ipsum lorem

#### rename_album_directories.py

album_directory_rename is for bulk renaming **EXISTING BUT INCORRECT ALBUM DIRECTORIES**.<br>
This means the audio files will not move, but the album directory name will change.

1. modify `TOP_LEVEL_DIR = "F:/path/to/tld"` appropriately
2. ensure that that at least one song has viable album name metadata **AND** the rest either have none or matching metadata
   1. the script will create an album directory based on unique viable album name metadata
   2. the script will remove the characters `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` - a subtle difference from create-albums
3. command line: `python D:\MusicProcessing\docs\scripts\google\album_directory_rename.py`

before/after execution:

```text
tld
|_ artist 1
|    |_album 1 wrong name    # where wrong name is not appropriate or equal to album name metadata
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album 2: something    # where the colon is invalid character from metadata
|    |    |_song 1
|    |    |_song i
|    |    |_song n

tld
|_ artist 1
|    |_album 1 metadata value
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album 2 sanitized metadata value
|    |    |_song 1
|    |    |_song i
|    |    |_song n
```

### Audio File Names

I prefer the `artist` - `title` or `artist`-`title` format.<br>
Why? Artists can have songs with same title.<br>
Eg: Lindsey Buckingham-Trouble vs Pink-Trouble. `artist`-`title` makes it clear.<br>
If an artist has different versions of same song, that's what album name metadata is for.

#### normalize-`type`-filename and normalize-`type`-filename-walk

Two variants; single file & directory walk.

1. `type` is one of `flac`, `mp3`, `mp4`, or `wma`
2. `filename` is for single files
3. `walk` is for a directory walk
   1. The directory can be the top level, 1st level artist, or 2nd level album directory
4. The artist and title metadata have to be accurate
   1. The artist and title metadata will be sanitized for validity
6. command line: `python main.py normalize-flac-filename "Drive:/path/to/file"`
7. command line: `python main.py normalize-flac-filename-walk "Drive:/path/to/dir"`

before/after execution:

```text
01 Buckingham Trubl.flac

Lindsey Buckinham-Trouble.flac
```

### Album Art

Audio file conversion requires an album art file named Folder.jpg co-located with the audio file.<br>
If an audio file has embedded art *and* was played by Windows Media Player at some point,
WMP will create a copy of it called Folder.jpg in the audio file directoty.<br>
So there's a good chance your source files include the external art file.

ipsum lorem functions to use

### Bulk Genre Setting

ipsum lorem

ipsum lorem functions to use

### Extraneous File Cleanup

ipsum lorem

ipsum lorem functions to use

## Converted

Congratulations! The hard work is now over. Now comes the waiting game - conversion to mp3 format.<br>
Average time to convert a song from any format is ~ 6 seconds. So the more you have, the longer it takes.<br>

ipsum lorem

ipsum lorem functions to use

## Normalized

ipsum lorem

ipsum lorem functions to use

## Finalized

Finish Line in sight!<br>
Move everything from `Normalized` to `Finalized`

Remember those m3u files mentioned way back? Here's where they get updated.<br>
A reminder about m3u playlists - they are *relative* pathed. They **must** sit in the top level directory that contains all audio files!<br>
Heres a snapshot of the guts of an m3u file:

```text
#EXTINF:0,Sawyer Fredricks - Shots Fired.mp3
Sawyer Fredericks\A Good Storm\Sawyer Fredricks - Shots Fired.mp3

#EXTINF:0,Crush-Live.mp3
Crush\Here\Crush-Live.mp3
```

The first line: `#EXTINF:0,Sawyer Fredricks - Shots Fired.mp3` is the song displayed by the playing software.<br>
The second line: `Sawyer Fredericks\A Good Storm\Sawyer Fredricks - Shots Fired.mp3` is the relative path to the audio file.<br>
The blank line is just to much the file readable. And yes, an m3u file is a text file, and editable by any text editor.

ipsum lorem functions to use

- Prepare textual metadata
  - this is where compilation albums will be handled
    - ascertain the correct artist for each song in compilation album
    - ensure song(s) are in correct `Prepped/artist/` where artist is correct artist for song
  - verify required textual metadata
  - try to verify optional textual metadata
  - Prepare each `Prepped/Artist` directory structure
    - Move each artist's album songs and artwork to appropriate `Prepped/Artists/Album` directory
    - If a an artist has songs NOT in an album directory, leave them in `Prepped/Artist`
      - run create-albums to create the album directories
  - normalize file names, run normalize-`type`->-filename or normalize-`type`-filename-walk where `type` is file ext of audio file
  - run update-genres-from-csv to bulk update an artist(s) genre; requires appropriate csv file
- Prepare art metadata
  - run extract-file or extract-walk to get embedded artwork into a usable jpg file
  - run set-album-art if needed
    - this is primarily for songs from compilation albums and looks in src/generated_files/AlbumArt for appropriate Folder.jpgs
    - but can also work for song files that are not part of compilations
- Convert music files to mp3 with embedded art
  - run convert-file or convert-walk; album art MUST be present in every album directory
- Normalize music
  - run ebu-file, single file EBU R128 standard for most files
  - run peak-file, single file Peak normalization when required
  - run rms-file, single file RMS normalization when required
  - run level-normalize-walk with normalization type to walk all files
- Finalize music with updated playlists
  - run update-paths for single playlists
  - run update-walk for all playlist in top level directory

### External Tool Processing

I will use MP3Tag/MusicBrainz Picard/puddletag to:

- verify all wma files have only WMA tags
- verify all m4a files have only MP4 tags
- verify all flac files only have Vorbis tags
- remove all APEv2 tags from mp3 files
  - remove all non ID3v2.3 tags from mp3 files
  - verify all mp3 files have only ID2v2.3 tags
- find accurate metadata for preferred tags
- find cover art for albums if necessary

python main.py --help
usage: main.py [-h]
{convert-file,convert-walk,create-albums,ebu-file,extract-file,extract-walk,get-ffprobe-media-info,get-ffprobe-media-info-walk,get-ffprobe-media-tags,get-mutagen-tags,get-tags-walk,get-unique-media,level-normalize-walk,list-audio,list-type,normalize-flac-filename,normalize-mp3-filename,normalize-mp4-filename,normalize-wma-filename,normalize-flac-filename-walk,normalize-mp3-filename-walk,normalize-mp4-filename-walk,normalize-wma-filename-walk,remove-albums,remove-pattern,remove-set-list,peak-file,rms-file,set-album-art,update-m3u,update-genres-from-csv,update-walk}

Music Processing

options:
  -h, --help                        show this help message and exit

subcommands:
    convert-file                    Converts an audio file to mp3
    convert-walk                    Converts all audio files to mp3
    create-albums                   Create album sub-directories
    ebu-file                        EBU R128 normalizes a mp3 audio file level
    extract-file                    Extracts embedded art from audio file
    extract-walk                    Extracts embedded art from all audio files
    get-ffprobe-media-info          Gets ffprobe media info for audio file
    get-ffprobe-media-info-walk     Gets ffprobe media info for audio files
    get-ffprobe-media-tags          Gets ffprobe media tags for audio file
    get-mutagen-tags                Gets metadata tags from audio file
    get-tags-walk                   Gets metadata tags from audio files
    get-unique-media                Gets set of unique ffprobe tags from collection
    level-normalize-walk            Normalizes files with specified pattern
    list-audio                      Generates a csv containing full path for all audio files
    list-type                       Generates a csv containing full file path for an audio file type
    normalize-flac-filename         Renames a FLAC from its metadata
    normalize-mp3-filename          Renames an MP3 from its metadata
    normalize-mp4-filename          Renames an M4A from its metadata
    normalize-wma-filename          Renames a WMA from its metadata
    normalize-flac-filename-walk    Renames FLAC files from metadata
    normalize-mp3-filename-walk     Renames MP3 files from metadata
    normalize-mp4-filename-walk     Renames M4A files from metadata
    normalize-wma-filename-walk     Renames WMA files from metadata
    remove-albums                   Remove empty album sub-directories
    remove-pattern                  Removes files with specified pattern
    remove-set-list                 Removes files matching a hard-coded set of patterns
    peak-file                       Peak normalizes a mp3 audio file level
    rms-file                        Rms normalizes a mp3 audio file level
    set-album-art                   Set album art file
    update-m3u                      Update playlist paths
    update-genres-from-csv          Updates genre metadata from artist genre CSV mappings
    update-walk                     Update playlist paths
