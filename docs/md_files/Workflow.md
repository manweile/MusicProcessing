<!-- markdownlint-disable MD033 -->

# Project Workflow {#project_workflow}

The whole point of this project is normalizing an audio collection.<br>
That means a workflow, using the external tools and project functions.

I use these 5 working directories for the processing workflow:

- source
- prepped
- converted
- leveled
- finalized

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

### Metadata

This the required metadata:

- album
- album artist
- artist
- date
- disc number
- genre
- title
- track number
- front cover album art

this is the optional metadata:

- composer
- copyright
- publisher

I will use MP3Tag/MusicBrainz Picard/puddletag to:

- verify all wma files have WMA tags
- verify all m4a files have MP4 tags
- verify all flac files have Vorbis tags
- verify all mp3 files have at least one ID3 version tags
- find accurate metadata for preferred tags
- find cover art for albums if necessary

**A word about metadata:**<br>
Ensuring all of your metadata is accurate is entirely dependent on your source's quality.<br>
There is good argument for doing it in the `Prepped` stage; but bear in mind how much work that could be.<br>
For right now, directory structure only needs 3 fields to be accurate: artist, album name and song title.

**A note about APEv2 metadata**<br>
The mapping functions called by the convert file function do NOT deal with audio files containing *only* APEv2 metadata encoding.<br>
That is a whole other kettle of fish. I currently do not have any files like that, and unsure if I am even going to code for it. Lot of work.<br>
I do have many mp3 files with APEv2 and one or more ID3 versions; not a problem, the Mutagen default with mp3 files is use the newest ID3 version.

### Directory Structure

Now your are looking at organizing the collections directory structure.<br>
Workload depends on the existing directory organization & metadata accuracy of your sources.<br>
I am using file explorer/file manager for the transfers - don't have a function or script, and not sure if I will write one.

#### Naming

I use the Windows invalid character set, it's more restrictive and therefore OS agnostic; you can use it on Linux & Mac.<br>

1. less than
2. greater than
3. colon
4. double quote
5. forward slash
6. backslash
7. pipe
8. question mark
9. asterisk

#### Directory Levels

The directory structure is important; the project function logic **requires** this set structure.<br>
There are three directory levels:

#### Top Level Directory

The music top level directory (*tld*) is where all music related files live.<br>
The tld can be nested as deep as you want (with respect to OS depth rules); it could as short as `Drive:/tld`.<br>
You can name the tld whatever you want. I personally prefer to call it "Music", which follows Windows OS practice.

Playlist files (m3u) **must** exist here; they use *relative pathing* to the artists/albums/songs they play, and playlist functions reflect that.

#### Artist Level Directories

The artist level directories are the first level directories (*fld*) under the tld.<br>
Artist directories **must** be unique; OS'es don't allow duplicate sibling directories, and must comply with allowable OS character set.

At least one song needs your preferred artist name; the rest can be blank. Preferably all songs have the same artist name.

#### Album Level Directories

The album level directories are the second level directories (*sld*) under the fld's.<br>
Album directories **must be unique for that artist directory**; OS'es don't allow duplicate sibling directories.

Album directories should almost always match album metadata.<br>
The exception being when the metadata has invalid for the OS characters.<br>
Bottom line, your album name metadata needs to be valid. You may need a metadata editor like MP3Tag/puddleTag or MusicBrainz Picard.<br>

```text
tld
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
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album i
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album n
|         |_song 1
|         |_song i
|         |_song n
|_ playlist 1
|_ playlist i
|_ playlist n
```

### manual album directory creation

You can use a file explorer/file manager to manually create album directories.<br>
I *think* you can also use MP3tag/puddleTag, just haven't tried.

### create-albums

create-albums function is used to create the album for *songs* standing alone in a first level artist directory.<br>
It's a top level directory walking function, so you **must** supply the tld, and **only** the tld.<br>
Does not work with fld & sld.

1. ensure that all the songs that need an album directory are sitting by themselves in the **artist 1st level directory**
2. at least one song has viable album name metadata
   1. the function will sanitize the invalid Windows characters to a dash.
3. the function does **not** handle attempted creation of duplicate directories
   1. ensure album metadata for songs from *different albums* will not clash
4. all songs with matching album metadata are moved into the new album directory

command line: `python main.py create-albums "Drive:/path/to/tld"`

before/after execution:

```text
tld
|_artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album 2 song 1
|    |_album 2 song i
|    |_album 2 song n

tld
|_artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album 2
|    |    |_song 1
|    |    |_song i
|    |    |_song n
```

**Handling Compilation Album Directories**<br>
Compilation metadata tags are a gong show with respect to how various metadata formats implement them, not worth the effort to map them.<br>
Most compilation albums use a variant of "various artists" for artist/album artist metadata, this invariably conflicts with "contributing artist".<br>
This is antithetical to the concept of unique 1st level artist directories, and OS'es don't allow sibling duplicate directories in any case.

Instead, all songs from an artist who contributed to a compilation album will be **solely under the artist's name**.<br>
Eg: The "Back to the Future" soundtrack has "Johnny B. Goode" by Huey Lewis & The News.<br>

Best Practice: copy the song(s) from the compilation to an *artist's 1st level directory* (create if needed),<br>
then run create-albums, and cleanup empty compilation album manually or with remove-empty-albums.

before/after:

```text
tld
|_artist 1
|    |_album 1
|         |_song 1
|         |_song i
|         |_song n
|_compilation album
|         |_song 1 by artist 1
|         |_song i by artist 1
|         |_song n by artist 1
|         |_song 1 by artist 2

tld
|_artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_song 1 by artist 1 from compilation album
|    |_song i by artist 1 from compilation album
|    |_song n by artist 1 from compilation album
|_artist 2
|    |_song 1 by artist 2 from compilation album

tld
|_artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_compilation album
|    |    |_song 1 by artist 1
|    |    |_song i by artist 1
|    |    |_song n by artist 1
|_artist 2
|    |_compilation album
|    |    |_song 1 by artist 2
```

**Handling Multi Disc Albums**<br>
Multi-disc albums directory structure introduces a 3rd level `disc number` directory. Not necessary, that's what track & disc metadata are for.

Best Practice: ensure the track/disc metadata is accurate, and album metadata does *NOT* include something like "CD N".<br>
Move all the songs from each "disc" directory to the *artist's 1st level directory* and run create-albums.<br>
Delete the multi-disc album directories manually, or *ensure* they are empty and run remove-empty-albums.<br>
BTW, "disc" really mean "lp", or "cd", or even "cassette".

before/after:

```text
tld
|_artist 1
|    |_source multi disc album
|    |    |_CD 1
|    |    |   |_song 1/disc 1
|    |    |   |_song i/disc 1
|    |    |   |_song n/disc 1
|    |    |_CD i
|    |    |   |_song 1/disc i
|    |    |   |_song i/disc i
|    |    |   |_song n/disc i

tld
|_artist 1
|    |_song 1/disc 1
|    |_song i/disc 1
|    |_song n/disc 1
|    |_song 1/disc i
|    |_song i/disc i
|    |_song n/disc i
|    |_source multi disc album
|    |    |_CD 1
|    |    |_CD i

tld
|_artist 1
|    |_multi disc album
|    |    |_song 1/disc 1
|    |    |_song i/disc 1
|    |    |_song n/disc 1
|    |    |_song 1/disc i
|    |    |_song i/disc i
|    |    |_song n/disc i
```

### rename-album-directories

rename-album-directories is for bulk renaming *EXISTING BUT INCORRECTLY NAMED ALBUM DIRECTORIES*.<br>
This means the album directory name will change, and the audio files will stay put.<br>
It's a top level directory only walking function, so you **must** supply the tld, and **only** the tld.<br>
Does not work with fld & sld.

1. ensure that at least one song in an album has accurate & viable album name metadata **AND** the rest either have none or matching metadata
   1. the function will create an album directory based on unique viable album name metadata
   2. the function will sanitize the invalid Windows characters to a dash.
   3. unlike create-albums, attempted duplicate directory creation **is handled**
      1. duplicates will be appended with an ordinal number

command line: `python main.py rename-album-directories "Drive:/path/to/tld"`

before/after execution:

```text
tld
|_ artist 1
|    |_album 1 wrong name    # wrong name is not appropriate or equal to album name metadata
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album 2: something    # the colon is invalid character, might be in metadata too
|    |    |_song 1
|    |    |_song i
|    |    |_song n

tld
|_ artist 1
|    |_album 1 metadata value
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |_album 2 sanitized value
|    |    |_song 1
|    |    |_song i
|    |    |_song n
```

## Audio File Names

I prefer the `artist`-`title` format, and can live with `artist` - `title`.

Why? Different artists can have songs with same title.<br>
Eg: Lindsey Buckingham-Trouble vs Pink-Trouble. `artist`-`title` makes it clear.

If an artist has different versions of the same song, that's what the second level album directories & album name metadata are for.<br>
Quite often the other versions will have a slightly different title, in which case, no worries. Or just change the title yourself.

Best Practice: ensure the artist/title metadata for each song is accurate & unique, then run a filename changing function.<br>
For the directory walk versions, directory input can be the tld, fld artist, or sld album directory.

### normalize-filename and normalize-filename-walk

Two variants: single file & directory walk.

1. `normalize-filename` is for single files
2. `normalize-filename-walk` is for a directory walk
3. The artist and title metadata will be sanitized for validity

single file:<br>
command line: `python main.py normalize-filename "Drive:/path/to/flac file"`<br>
command line: `python main.py normalize-mp3-filename "Drive:/path/to/mp3 file"`<br>
command line: `python main.py normalize-mp4-filename "Drive:/path/to/m4a file"`<br>
command line: `python main.py normalize-wma-filename "Drive:/path/to/wma file"`

multi-file:<br>
command line: `python main.py normalize-filename-walk "Drive:/path/to/tld/or fld/or sld"`

before/after execution:

```text
01 Buckingham Trubl.flac

Lindsey Buckingham-Trouble.flac
```

## Album Art

Audio file conversion **requires** an album art file named Folder.jpg co-located with the audio file.

If an audio file has embedded art *and* was played by Windows Media Player, WMP will create a copy called Folder.jpg, in that directory.<br>
So there's a good chance your source files include the external art Folder.jpg file, which you can just copy over.<br>
Note that WMP also creates several "junk" art files; that's why remove-pattern & remove-set-list functions exist.

The extract function extracts the first embedded art from the first audio file it finds with embedded art.<br>
The extracted art is saved as Folder.jpg in the same directory as the audio source file.<br>
The embedded art is NOT removed from the audio source file.<br>
Directories with a existing Folder.jpg will be skipped.

Best Practice: ensure at least one song in an album has the correct embedded art as the first embedded art file.<br>
Use MP3tag/puddleTag/Discogs/MusicBrainz Picard to find acceptable art if there is no art at all.<br>
Where multiple files have embedded art, the lowest alphabetically named file should be your source.

### extract-album-art

Extracts embedded art from a single audio file.

command line: `python main.py extract-album-art "Drive:/path/to/file"`

### extract-walk

Extracts embedded art from all audio files supplied path.<br>
Works with tld (top) & fld (artist) input, but not sld (album) input.

command line: `python main.py extract-walk "Drive:/path/to/tld/or fld"`

before/after execution:

```text
tld
|_artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i with embedded art
|    |    |_song n
|_artist 2
|    |_song 1
|    |_song i with embedded art
|    |_song n

tld
|_artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i with embedded art
|    |    |_song n
|    |    |_Folder.jpg
|_artist 2
|    |_song 1
|    |_song i with embedded art
|    |_song n
|    |_Folder.jpg

```

**Handling Compilation Album Art**<br>
Compilation album art can be re-used!<br>

Best Practice: extract album art from a compilation album if there is any, or find accurate art.<br>
Rename it to `compilation album name`.jpg file.<br>
Eg. for the album `Best Of The Blues, Vol. 1`: `Best Of The Blues, Vol. 1.jpg`.<br>
Copy it to the special `/MusicProcessing/src/generated_files/AlbumArt` folder, or a folder of your choice.

### set-album-art

Sets album art file for an compilation album folder.<br>
By default, looks for `compilation album name`.jpg file in special `AlbumArt` folder.<br>
You can optionally supply the folder of your choice.

Found matches get copied & renamed to `compilation album name/Folder.jpg`.<br>
It won't overwrite an existing Folder.jpg in fld or sld directories.<br>
The match does not get consumed, it stays in `AlbumArt` folder.

Works with tld (top) & fld (artist) input, but not sld (album) input.

command line: `python main.py set-album-art "Drive:/path/to/tld/or fld"`

before/after execution:

```text
tld
|_artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n

AlbumArt
|_album 1.jpg

tld
|_artist 1
|    |_album 1
|    |    |_song 1
|    |    |_song i
|    |    |_song n
|    |    |_Folder.jpg
```

## Bulk Genre Setting

Many songs are going to have multiple genres, or incorrect genres.<br>
You could leave them be and/or you could manually edit them. Your preference.<br>
My preference is to do quick search for the single genre most commonly associated with the artist, and set all of their songs to that genre.

### manual genre setting

MP3Tag really shines here.<br>
From File Explorer, or MP3Tag, highlight the directory(s) with the songs you want to update.<br>
Can be tld, fld, or sld; what level you use determines how many songs you want to deal with.<br>
Select the songs you want to set genre for, open the the tag view side bar, put the genre in the input field, click save icon.<br>

### update-genres-from-csv

Updates genre metadata from artist & genre CSV mappings, one artist to one genre mapping.<br>
The artist name and genre datums can be a compound term where the constituent values are space separated.<br>
This function *requires an ascending sorted by artist name csv file in the tld*; the function uses relative pathing.

Example artist_genre.csv:

artist name,artist genre<br>
Bachman-Turner Overdrive,Classic Rock<br>
Bad Company,Classic Rock<br>
Barenaked Ladies,Alternative Rock<br>
Beach Boys,Pop Rock<br>
Bee Gees, Pop Rock<br>
Beth Hart and Joe Bonamassa,Blues<br>
Blondie,New Wave<br>
Blu Cantrell,Pop<br>
Blue Rodeo,Folk Rock<br>
Bonnie Raitt,Blues Rock<br>
Bonnie Tyler,Pop Rock<br>
Boston,Rock<br>
Brad Paisley,Country<br>
Brandi Carlile,Indie<br>
Bruce Springsteen,Rock<br>
Huey Lewis & The News,Movie Soundtrack<br>
Stephen Page,Alternative Rock

command line: `python main.py update-genres "Drive:/path/to/tld" "Drive:/path/to/artist_genre.csv"`

## Extraneous File & Directory Cleanup

Windows File Explorer and Windows Media Player are sloppy actors.<br>
They both can add extraneous files like Thumbs.db, ini files, Art*.jpg, etc.

### remove-pattern

Removes files with specified pattern.<br>
Works for tld, fld, and sld as path input.<br>
Will throw an error if start path is a file system root or mount point, or if file pattern is full wildcard.

command line: `python main.py remove-pattern "Drive:/path/to/tld/or fld/or sld" AlbumArtSmall.jpg`

### remove-set-list

Removes files matching a hard-coded set of patterns.<br>
Works for tld, fld, and sld as path input.

***MODIFY THE HARD CODED LIST AT YOUR OWN RISK, THE FUNCTION DOES NOT GUARD AGAINST YOUR OWN STUPIDITY***<br>
Current hard coded list is `["AlbumArt_*_*.jpg", "AlbumArt*.jpg", "Thumbs.db", "desktop.ini"]`

command line: `python main.py remove-set-list "Drive:/path/to/tld/or fld/or sld"`

### remove-empty-albums

Removes empty album sub-directories.<br>
Works for tld, fld, but not sld as path input.

command line: `python main.py remove-empty-albums "Drive:/path/to/tld/or fld"`

### Metadata redux

If you don't have all of your metadata (textual & visual) up to snuff, now is the time.

## Converted

Congratulations! The hard work is now over.<br>
Now comes the first waiting game - conversion to mp3 format, from flac, mp3, m4a, and wma audio files.<br>
Average time to convert a song from any format is ~ 6 seconds. So the more you have, the longer it takes.<br>

Bonus functionality: since the logic maps any existing metadata before wiping it out, you can use it delete extra metadata encoding formats!<br>
So if you ensure your metadata is accurate (one of the ID3 versions), no worries, go ahead and convert.<br>
Mp3 files are the usual multiple encoding culprit.

Ffmpeg is the conversion engine behind the scenes.<br>
It has one hard requirement: *the output filepath cannot be exactly the same as the input filepath.*

FFmpeg is a streaming data pipeline. It opens an input file to read a few frames, processes them, and then writes them to the output file.<br>
If the input and output are the same file, the writer will wipe out or overwrite the data blocks that the reader hasn't even reached yet.

Conversion logic is essentially a three stage process.<br>
First, map the existing metadata from original audio file to ID3v2.3 encoding.<br>
Second, convert the original audio file to mp3 format with the ID3v2.3 metadata & in a different save location.<br>
Third, embed the co-located album art in the mp3 file.

Both convert file and convert walk have optional/default target invocations.<br>
Whichever you use, it's up to you to move the converted files if you are processing them any further with level normalization.

The default save location is `/MusicProcessing/src/generated_files/Music`.

### convert-file

Converts an acceptable audio file (flac, mp3, m4a, wma) to mp3.

command line with target:  `python main.py convert-file "Drive:/path/to/audio file" --target "Drive:/path/to/target"`<br>
command line without target:  `python main.py convert-file "Drive:/path/to/audio file"`

### convert-walk

Converts all acceptable audio files (flac, mp3, m4a, wma) in path to mp3.<br>
Works with tld (top), fld (artist) and sld (album) path input.

command line with target:  `python main.py convert-walk "Drive:/path/to/tld/or fld/or sld" --target "Drive:/path/to/target"`<br>
command line without target:  `python main.py convert-walk "Drive:/path/to/tld/or fld/or sld"`

## Leveled

I get truly annoyed when a playlist moves to a next song and you are suddenly lowering or increasing the volume.<br>
Leveling normalization decreases that perceived volume change. The caveat: **you must apply leveling to all of your collection**.

All of the distinct single file level normalization functions and the leveling walk function have optional/default target invocations.<br>
Whichever you use, it's up to you to move the leveled files if you are processing them any further.

There are 3 level normalization types:

### EBU R128

I am using the the ffmpeg loudnorm filter, which is the EBU R128 international broadcast audio standard.<br>
It replaces traditional peak normalization with perceived loudness normalization to create a consistent listening experience.

The loudnorm algorithm goes like this:<br>
Measure the integrated loudness of the source file, calculate an appropriate offset gain, and then apply makeup gain.<br>
I settled on:

- integrated loudness target (ILT): -16.0, to avoid excessive peak limiting, and allow a higher dynamic range in a program stream
- loudness range target (LRA): 11.0, preserves micro-dynamics, performance nuances, and natural instrumentation
- true peak (TP): -2.0, to prevent clipping when using lossy encoders

Refer to:<br>
[Loudness Normalization](https://k.ylo.ph/2016/04/04/loudnorm.html),<br>
[FFMPEG Loudnorm Filter](https://ffmpeg.org/ffmpeg-filters.html#loudnorm), and<br>
AESTD1004_1_15_10.pdf, official document from [Audio Engineering Society]( https://aes.org/community/technical-council/)

command line with target:  `python main.py ebu-file "Drive:/path/to/audio file" --target "Drive:/path/to/target"`<br>
command line without target:  `python main.py ebu-file "Drive:/path/to/audio file"`

### Peak

Peak volume normalization is accomplished by using the ffmpeg volumedetect filter.<br>
The adjustment value is computed from true peak constant and the *maximum* volume of a song.

Use peak leveling when you want to *preserve the original dynamic range of a song.*

command line with target:  `python main.py peak-file "Drive:/path/to/audio file" --target "Drive:/path/to/target"`<br>
command line without target:  `python main.py peak-file "Drive:/path/to/audio file"`

### RMS

RMS (root mean square) normalization is accomplished by using the ffmpeg volumedetect filter.<br>
The adjustment value is computed from the true peak constant value and *mean* volume of a song.

Use RMS leveling when you want to *preserve the original artist-intended relative differences between songs.*

command line with target:  `python main.py rms-file "Drive:/path/to/audio file" --target "Drive:/path/to/target"`<br>
command line without target:  `python main.py rms-file "Drive:/path/to/audio file"`

### level-normalize-walk

Normalizes files with specified normalization type (ebu, peak, or rms).<br>
Works with tld (top) and fld (artist), but not sld (album) path input.<br>

command line with target:  `python main.py level-normalize-walk "norm type" "Drive:/path/to/tld/or fld" --target "Drive:/path/to/target"`<br>
command line without target:  `python main.py level-normalize-walk  "norm type" "Drive:/path/to/tld/or fld"`

## Finalized

Finish Line in sight!<br>
Move everything from `Leveled` to `Finalized`

Remember those m3u files mentioned way back? Here's where they get updated.<br>
A reminder about m3u playlists - they are *relative* pathed. They **must** sit in the top level directory that contains all audio files!<br>

Best practice: wait to run the playlist updating until you have everything converted & leveled - why run multiple times?

ipsum lorem functions to use
update-m3u                      Update playlist paths in a single playlist file
update-walk                     Update playlist paths for all playlist files in directory

### Information functions

These information functions generate a file (csv and/or txt).<br>
The files are in the special `/MusicProcessing/src/generated_files/` directory, under `csv_file/`s and/or `result_files/`.<br>
Any previous output files are overwritten, so save previous versions if you want to preserve history *before* running an information function.

#### get-ffprobe-media-info-walk

Generates get-ffprobe-media-info-walk.txt containing ffprobe media info for audio files.<br>
Media info is codec, duration, size, bitrate, ..., etc, *not* album, artist, album_artist, ..., etc.<br>
Has optional flag `--pattern {.flac|.mp3|.m4a|.wma}` to specify file type. No pattern retrieves from all file types.

Works with tld (top) and fld (artist), but not sld (album) path input.

command lines:<br>
`python main.py get-ffprobe-media-info-walk "Drive:/path/to/tld/or fld"`<br>
`python main.py get-ffprobe-media-info-walk "Drive:/path/to/tld/or fld" --pattern .flac`<br>

#### get-tags-walk

Generates get-tags-walk.txt containing all metadata tags from audio files.<br>
Has optional flag `--pattern {.flac|.mp3|.m4a|.wma}` to specify file type. No pattern retrieves from all file types.<br>
Has optional flag `--ffprobe True` to get ffprobe metadata instead of Mutagen.<br>
Defaults to getting Mutagen metadata tags.

Works with tld (top) and fld (artist), but not sld (album) path input.

command lines:<br>
`python main.py get-tags-walk "Drive:/path/to/tld/or fld"`<br>
`python main.py get-tags-walk "Drive:/path/to/tld/or fld" --pattern .flac`<br>
`python main.py get-tags-walk "Drive:/path/to/tld/or fld" --pattern .flac --ffprobe True`<br>
`python main.py get-tags-walk "Drive:/path/to/tld/or fld" --ffprobe True`

#### get-unique-media-keys

Generates get-unique-media-keys.txt containing all unique ffprobe metadata tags from audio files.

Works with tld (top) and fld (artist), but not sld (album) path input.<br>

command line: `python main.py get-unique-media-keys "Drive:/path/to/tld/or fld"`

#### get-audio-file-list

Generates get-audio-file-list.csv containing full path for all audio files, and get-audio-file-list.txt listing the types of files found.<br>

Works with tld (top) but not fld (artist) or sld (album) path input.

command line: `python main.py get-audio-file-list "Drive:/path/to/tld"`

#### get-ext-file-list

Generates get-ext-file-list.csv containing full file path for audio files by type.<br>
Has optional flag `--pattern {.flac|.mp3|.m4a|.wma}` to specify file type. <br>
No pattern retrieves from all file types.

Works with tld (top) and fld (artist), and sld (album) path input.

command line: command line: `python main.py get-ext-file-list "Drive:/path/to/tld/or fld/or sld"`
