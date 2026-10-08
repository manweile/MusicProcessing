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

**A word about metadata:**<br>
Ensuring all of your metadata is accurate is entirely dependent on your source's quality.
There is good argument for doing it in the `Prepped` stage; but bear in mind how much work that could be.<br>
For right now, directory structure only needs 3 fields to be accurate: artist, album name and song title.

### Directory Structure

Now your are looking at organizing the collections directory structure.<br>
Depending on the existing directory organization & metadata accuracy of your sources, you could be doing a little, or a lot.<br>
I am using file explorer/file manager for the transfers - don't have a function or script, and not sure if I will write one.

*Naming* I use the Windows invalid character set ( `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`).<br>
It's more restrictive and therefore OS agnostic; you can use it on Linux & Mac.

The directory structure is important; the project function logic **requires** this set structure.<br>
There are three directory levels:

#### Top Level Directory

The music top level directory (*tld*) is where all music related files live.<br>
The tld can be nested as deep as you want (with respect to your OS depth rules); it could as short as drive:\tld.<br>
You can name the tld whatever you want. I personally prefer to call it "Music", which follows Windows OS practice.

Playlist files (m3u) **must** exist here; they use *relative pathing* to the artists/albums/songs they play, and playlist functions reflect that.

#### Artist Level Directories

The artist level directories are the first level directories (*fld*) under the tld.<br>
Artist directories **must** be unique; OS'es don't allow duplicate sibling directories.<br>
Of course, the artist directory must also comply with allowable OS character set.

Therefore, at least one song has to have what you want for that artist; the rest can be blank.<br>
Preferably all songs have the artist name you want for the artist directory.<br>

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
It's a top level directory walking function, so you **must** supply the tld, and **only** the tld. Does not work with fld & sld.

1. ensure that all the songs that need an album directory are sitting by themselves in the **artist 1st level directory**
2. at least one song has viable album name metadata
   1. the function will sanitize the characters `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` to `-`.
   2. the function does **not** handle attempted creation of duplicate directories
      1. ensure album metadata for songs from *different albums* will not clash
3. all songs with matching album metadata are moved into the new album directory
4. command line: `python main.py create-albums "Drive:/path/to/tld"`

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
Compilation metadata tags are a gong show with respect to how various metadata formats implement them, it wasn't worth the effort to map them.<br>
Most compilation albums use a variant of "various artists" for artist/album artist metadata, this invariably conflicts with "contributing artist".<br>
This is antithetical to the concept of unique 1st level artist directories, and OS'es don't allow sibling duplicate directories in any case.

Instead, all songs from an artist who contributed to a compilation album will be **solely under the artist's name**.<br>
Eg: The "Back to the Future" soundtrack has "Johnny B. Goode" by Huey Lewis & The News.<br>

Best Practice: copy the song(s) from the compilation to an *artist's 1st level directory* (create if needed),<br>
then run create-albums, and cleanup empty compilation album manually or with remove-empty-albums.<br>
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
It's a top level directory only walking function, so you **must** supply the tld, and **only** the tld. Does not work with fld & sld.

1. ensure that at least one song in an album has accurate & viable album name metadata **AND** the rest either have none or matching metadata
   1. the function will create an album directory based on unique viable album name metadata
   2. the function will sanitize the characters `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` to `-`.
   3. unlike create-albums, attempted duplicate directory creation **is handled**
      1. duplicates will be appended with an ordinal number
2. command line: `python main.py rename-album-directories "Drive:/path/to/tld"`

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

I prefer the `artist` - `title` or `artist`-`title` format.<br>
Why? Different artists can have songs with same title.<br>
Eg: Lindsey Buckingham-Trouble vs Pink-Trouble. `artist`-`title` makes it clear.<br>
If an artist has different versions of the same song, that's what the second level album directories & album name metadata are for.<br>
Quite often the other versions will have a slightly different title, in which case, no worries.

Best Practice: ensure the artist/title metadata for each song is accurate, then run a filename changing function.<br>
For the directory walk versions, directory input can be the tld, fld artist, or sld album directory.

### normalize-`type`-filename and normalize-`type`-filename-walk

Two variants: single file & directory walk.

1. `type` is one of `flac`, `mp3`, `mp4`, or `wma`
2. `filename` is for single files
3. `walk` is for a directory walk
4. The artist and title metadata have to be accurate
   1. The artist and title metadata will be sanitized for validity
5. command line: `python main.py normalize-flac-filename "Drive:/path/to/file"`
6. command line: `python main.py normalize-flac-filename-walk "Drive:/path/to/tld/or fld/or sld"`

before/after execution:

```text
01 Buckingham Trubl.flac

Lindsey Buckingham-Trouble.flac
```

## Album Art

Audio file conversion **requires** an album art file named Folder.jpg co-located with the audio file.

If an audio file has embedded art *and* was played by Windows Media Player, WMP will create a copy of it called Folder.jpg in that directory.<br>
So there's a good chance your source files include the external art Folder.jpg file, which you can just copy over.<br>
Use MP3tag/puddleTag/Discogs/MusicBrainz Picard to find acceptable art if there is no art at all.

The extract function extracts embedded art from the first audio file it finds with embedded art.<br>
The extracted art is saved as Folder.jpg in the same directory as the audio source file.<br>
The embedded art is NOT removed from the audio source file.<br>
Directories with a Folder.jpg will be skipped.

Best Practice: ensure the lowest alphabetically named song in an album has the correct embedded art.<br>
Run one of the extract functions.

### extract-file

Extracts embedded art from a single audio file.<br>
command line: `python main.py extract-file "Drive:/path/to/file"`

### extract-walk

Extracts embedded art from all audio files supplied path.<br>
Works with tld (top) & fld (artist) input, but *not* sld (album) input.<br>
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
Rename to `compilation album name`.jpg file.<br>
Eg. for the album `Best Of The Blues, Vol. 1`: `Best Of The Blues, Vol. 1.jpg`.<br>
Copy it to to the special `/MusicProcessing/src/generated_files/AlbumArt` folder.

### set-album-art

Sets album art file for an compilation album folder. Looks for `compilation album name`.jpg file in special `AlbumArt` folder.<br>
Found matches get copied & renamed to `compilation album name/Folder.jpg`.<br>
It won't overwrite an existing Folder.jpg in fld or sld directories.<br>
The match does not get consumed, it stays in `AlbumArt` folder.

Works with tld (top) & fld (artist) input, but *not* sld (album) input.<br>
command line: `python main.py set-album-art "Drive:/path/to/tld/or fld"`<br>
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

MP3Tag really shines here. From File Explorer, or MP3Tag, highlight the directory(s) with the songs you want to update.<br>
Can be tld, fld, or sld; what level you use determines how many songs you want to deal with.<br>
Select the songs you want to set genre for, open the the tag view side bar, put the genre in the input field, click save icon.<br>

### update-genres-from-csv

Updates genre metadata from artist genre CSV mappings<br>
Best Practice: This function *requires a sorted* csv file in the tld; the function uses relative pathing.

CSV File Example:<br>
artist name,artist genre
Bachman-Turner Overdrive,Classic Rock
Bad Company,Classic Rock
Barenaked Ladies,Alternative Rock
Beach Boys,Pop Rock
Bee Gees, Pop Rock
Beth Hart and Joe Bonamassa,Blues
Blondie,New Wave
Blu Cantrell,Pop
Blue Rodeo,Folk Rock
Bonnie Raitt,Blues Rock
Bonnie Tyler,Pop Rock
Boston,Rock
Brad Paisley,Country
Brandi Carlile,Indie
Bruce Springsteen,Rock
Huey Lewis & The News,Movie Soundtrack
Stephen Page,Alternative Rock

command line: `python main.py update-genres-from csv "Drive:/path/to/tld/"`

## Extraneous File & Directory Cleanup

Windows File Explorer and Windows Media Player are sloppy actors.<br>
They both can add extraneous files like Thumbs.db, ini files, Art*.jpg, etc.

### remove-pattern

Removes files with specified pattern.<br>
Works for tld, fld, and sld as path input.<br>
Will throw an error if start path is a file system root or mount point, or if file pattern is full wildcard.

ipsum lorem

### remove-set-list

Removes files matching a hard-coded set of patterns. Works for tld, fld, and sld as path input.<br>
***MODIFY THE HARD CODED LIST AT YOUR OWN RISK, THE FUNCTION DOES NOT GUARD AGAINST YOUR OWN STUPIDITY***<br>
Current hard coded list is `["AlbumArt_*_*.jpg", "AlbumArt*.jpg", "Thumbs.db", "desktop.ini"]`

ipsum lorem

### remove-empty-albums

Removes empty album sub-directories. The start path can be tld or fld, but not sld.

ipsum lorem

## Converted

Congratulations! The hard work is now over. Now comes the waiting game - conversion to mp3 format.<br>
Average time to convert a song from any format is ~ 6 seconds. So the more you have, the longer it takes.<br>

Conversion logic is essentially a destructive three stage process.<br>
First, map the existing metadata from original audio file to ID3v2.3 encoding.<br>
Second, convert the original audio file with ffmpeg to mp3 format with the mapped to ID3v2.3 metadata in a different save location.<br>
Third, embed the co-located album art in the newly converted mp3 file.

Therefore, you **must** have co-located album art; you did run extract-file/extract-walk/set-album-art right?<br>
This is also a good place to have all of your song metadata up to snuff.

### convert-file

Converts an audio file to mp3

**NOTE**<br>
The mapping functions called by convert file function do NOT deal with audio files only containing APEv2 metadata encoding.<br>
That is a whole other kettle of fish. I currently do not have any files like that, and unsure if I even going to code for it. Lot of work.<br>
I do have many mp3 files with APEv2 and one ore more ID3 versions - those aren't a problem, Mutagen default with mp3 files is the ID3 versions.

Bonus functionality: since the logic maps any existing metadata before wiping it out, you can use it delete extra metadata encoding formats!<br>
Mp3 files are the usual culprit. So if you ensure your metadata is accurate (one of the ID3 versions), no worries.

ipsum lorem command line with target

ipsum lorem command line without target

### convert-walk

Converts all acceptable audio files (flac, mp3, m4a, wma) in path to mp3. Works with tld (top), fld (artist) and sld (album) path input.<br>

ipsum lorem command line with target

ipsum lorem command line without target

## Normalized

I get truly annoyed when a playlist moves to a next song and you are suddenly lowering or increasing the volume.<br>
ipsum lorem about leveling with EBU R128<br>

ipsum lorem when to use peak leveling<br>

ipsum lorem when to use rms leveling.<br>

ipsum lorem functions to use
ebu-file                        EBU R128 normalizes a single mp3 audio file level
peak-file                       Peak normalizes a single mp3 audio file level
rms-file                        Rms normalizes a single  mp3 audio file level
level-normalize-walk            Normalizes files with specified pattern. works with tld and fld input.

## Finalized

Finish Line in sight!<br>
Move everything from `Normalized` to `Finalized`

Remember those m3u files mentioned way back? Here's where they get updated.<br>
A reminder about m3u playlists - they are *relative* pathed. They **must** sit in the top level directory that contains all audio files!<br>

ipsum lorem functions to use
update-m3u                      Update playlist paths
update-walk                     Update playlist paths

## External Tool Processing

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
subcommands:
    get-ffprobe-media-info          Gets ffprobe media info for an audio file
    get-ffprobe-media-info-walk     Gets ffprobe media info for audio files
    get-ffprobe-tags                Gets ffprobe metadata tags for audio file
    get-mutagen-tags                Gets Mutagen metadata tags from audio file
    get-tags-walk                   Gets Mutagen metadata tags from audio files
    get-unique-media                Gets set of unique ffprobe tags from collection
    list-audio                      Generates a csv containing full path for all audio files
    list-type                       Generates a csv containing full file path for an audio file type
