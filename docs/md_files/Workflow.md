<!-- @page project_workflow API Documentation -->
<!-- markdownlint-disable MD033 -->

# Project Workflow

The whole point of this project is normalizing an audio collection.

## Project Tools

The project has a whole raft of scripts - the tools needed for the workflow.

### Art Tools

ipsum lorem

### Metadata Tools

ipsum lorem

### Playlist Tools

ipsum lorem

### Directory Tools

ipsum lorem

## Processing Workflow

- Copy source music to `Source` directory
- Create `Prepped/Music` directory
- Copy all of an artist's files from `Source/Artist` directory to `Prepped/Artist` directory
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
