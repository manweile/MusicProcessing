F:\FinalizedMusic directory is the result of manual metadata checks and playlist updates on NormalizedMusic directory.

F:\NormalizedMusic is up to date as of Jul 11th.
Created July 11th, audio metadata in this directory was updated on July 12th.
Playlists were updated to have relative paths for this directory on July 17th.

This directory can replace \\Office1\Music, and be used on micro sd card for truck.

Only mp3 audio files and m3u playlist files are present.

All playlist files are relative pathed m3u files.

All audio files are in mp3 format.
All audio files have minimum set of ID3v2.3 metadata:
- album
- album artist
- artist
- date
- genre
- title

Any of the nice to have metadata that was found is also mapped to ID3v2.3:
- composer
- copyright
- disc
- publisher
- track

All audio files have embedded album art (as ID3v2.3 APIC tag).
All audio files have been normalized to EBU R128 standard.

Play test music.
- Make any required metadata only changes here.
- If any normalization changes are required:
  - copy the file from Converted directory to here
  - normalize
  - update metadata if required
- update \\Office1\Music, and micro sd card(s)

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
