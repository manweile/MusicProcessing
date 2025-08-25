F:\NormalizedMusic directory is the result of normalization on ConvertedMusic directory.

Created Jul 12, this directory was updated on Jul 13th after debugging normalization def.
F:\ConvertedMusic is up to date as of Jul 9.

Only audio files are present.
All audio files are in mp3 format.
All audio files have minimum set of ID3v2.3 metadata:
    album
    album artist
    artist
    date
    genre
    title
Any of the nice to have metadata that was found is also mapped to ID3v2.3:
    composer
    copyright
    disc
    publisher
    track
All audio files have embedded album art (as ID3v2.3 APIC tag).
All audio files have been normalized to EBU R128 standard.
All album directories contain only mp3 files.

The playlist files can now be copied from PreppedMusic directory and then edited for filename changes.

Directory structure is:
```text
tld
|_ playlist 1
|_ playlist i
|_ playlist n
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
     |_album 1
     |    |_song 1
     |    |_song i
     |    |_song n
     |_album i
     |    |_song 1
     |    |_song i
     |    |_song n
     |_album n
          |_song 1
          |_song i
          |_song n
```