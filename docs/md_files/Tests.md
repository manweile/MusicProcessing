<!-- markdownlint-disable MD033 -->

# Unit Testing

ipsum lorem

## Music Files

Music files are audio files (flac, mp3, m4a, wma) and m3u playlist files<b>
The music files in `tests/Music` are test fixtures.<br>
Root-level fixtures in `tests/` are also listed when referenced by a test.<br>
`test_audio_utilities` and `test_directory_processing` walk the complete fixture directory.

| Artist | Album Dir | Song | Test Suite | Notes |
| --- | --- | --- | --- | --- |
| 10cc | 10cc | 04 - Donna.mp3 | test_audio_metadata | MP3 filename normalization |
| 10cc | 10cc | 04 - Donna.mp3 | test_audio_metadata | Already-normalized filename |
| 10cc | 10cc | 04 - Donna.mp3 | test_audio_metadata | Windows filename-character sanitization |
| 10cc | 10cc | 04 - Donna.mp3 | test_audio_metadata | Directory-walk filename normalization |
| 38 Special | Teachers | 38 Special-Teacher Teacher.mp3 | test_audio_utilities | Directory-walk volume analysis |
| 38 Special | Teachers | 38 Special-Teacher Teacher.mp3 | test_directory_processing | Directory-walk file listing |
| Abba | Waterloo | ABBA-Waterloo.mp3 | test_audio_art | Existing folder art |
| Abba | Waterloo | ABBA-Waterloo.mp3 | test_audio_metadata | ID3v2.3 Metadata Mapping |
| Abba | Waterloo | ABBA-Waterloo.mp3 | test_audio_metadata | ID3v2.3 Tag retrieval |
| Abba | Waterloo | ABBA-Waterloo.mp3 | test_audio_normalization | Dynamic normalization |
| Abba | Waterloo | ABBA-Waterloo.mp3 | test_audio_playlist | Fictional m4a file ext resolved to MP3 |
| Aerosmith | Devil's Got a New Disguise-The Very Best of Aerosmith | Aerosmith-Dream On.mp3 | test_audio_playlist | Playlist album-path correction |
| Alannah Myles | A-Lan-Nah | Alannah Myles-Do You Really Wanna Know Me.flac | test_audio_art | Embedded FLAC artwork extraction |
| Albert Collins | Best Of The Blues, Vol. 1 | Albert Collins - Trash Talkin'.mp3 | test_audio_art | Missing album art creation |
| Albert Collins | Best Of The Blues, Vol. 1 | Albert Collins - Trash Talkin'.mp3 | test_audio_metadata | Directory-walk metadata keys |
| Albert Collins | Best Of The Blues, Vol. 1 | Albert Collins - Trash Talkin'.mp3 | test_audio_utilities | Directory-walk volume analysis |
| Albert Collins | Best Of The Blues, Vol. 1 | Albert Collins - Trash Talkin'.mp3 | test_directory_processing | Directory-walk file listing |
| Bear McCreary | Battlestar Galactica | Bear McCreary - BSG Gayatri Mantra Theme Song.mp3 | test_audio_art | Directory-walk album-art processing |
| Bear McCreary | Battlestar Galactica | Bear McCreary - BSG Gayatri Mantra Theme Song.mp3 | test_audio_metadata | Directory-walk metadata keys |
| Bear McCreary | Battlestar Galactica | Bear McCreary - BSG Gayatri Mantra Theme Song.mp3 | test_audio_utilities | Directory-walk volume analysis |
| Bear McCreary | Battlestar Galactica | Bear McCreary - BSG Gayatri Mantra Theme Song.mp3 | test_directory_processing | Directory-walk file listing |
| Billie Holiday | Georgia On My Mind | Billie Holiday-Georgia On My Mind.wma | test_audio_art | WM/Picture artwork without a video stream |
| Cream | Goodbye | 02. Politician.flac | test_audio_metadata | FLAC filename normalization |
| Cream | Goodbye | Cream-Badge.flac | test_audio_metadata | Vorbis Metadata Mapping |
| Cream | Goodbye | Cream-Badge.flac | test_audio_metadata | Vorbis Tag retrieval |
| CCR | Chronicle, Vol. 1 | Creedence Clearwater Revival-Fortunate Son.wma | test_audio_metadata | Co-located folder art |
| CCR | Chronicle, Vol. 1 | Creedence Clearwater Revival-Fortunate Son.wma | test_audio_metadata | WMA Metadata Mapping |
| CCR | Chronicle, Vol. 1 | Creedence Clearwater Revival-Fortunate Son.wma | test_audio_metadata | WMA Tag retrieval |
| CCR | Chronicle, Vol. 1 | Creedence Clearwater Revival-Fortunate Son.wma | test_audio_playlist | Playlist WMA entry resolved to MP3 |
| Crush | Here | Crush-Live.mp3 | test_audio_art | ID3 APIC artwork fixture |
| Crush | Here | Crush-Live.mp3 | test_audio_metadata | Media-information retrieval |
| Crush | Here | Crush-Live.mp3 | test_audio_metadata | ID3v2.3 Tag retrieval |
| Crush | Here | Crush-Live.mp3 | test_audio_normalization | Linear normalization |
| Crush | Here | Crush-Live.mp3 | test_audio_normalization | Volume analysis |
| Crush | Here | Crush-Live.mp3 | test_audio_playlist | Invalid playlist input |
| Crush | Here | Crush-Live.mp3 | test_subprocess_utilities | Valid media command |
| Crush | Here | No_tag_Crush-Live.mp3 | test_audio_art | Absent artwork |
| Crush | Here | No_tag_Crush-Live.mp3 | test_audio_metadata | Mutagen tag retrieval returns None |
| Crush | Here | No_tag_Crush-Live.mp3 | test_audio_metadata | FFprobe tag retrieval returns None |
| Crush | Here | No_tag_Crush-Live.mp3 | test_audio_metadata | Absent embedded artwork tag |
| Crush | /tests | No_audio_Crush-Live.mp3 | test_subprocess_utilities | Malformed audio data |
| Daughtry | Leave This Town | Daughtry-No Surprise.mp3 | test_audio_art | Directory-walk album-art processing |
| Daughtry | Leave This Town | Daughtry-No Surprise.mp3 | test_audio_metadata | Directory-walk metadata keys |
| Daughtry | Leave This Town | Daughtry-No Surprise.mp3 | test_audio_utilities | Directory-walk volume analysis |
| Daughtry | Leave This Town | Daughtry-No Surprise.mp3 | test_directory_processing | Directory-walk file listing |
| Diamond Rio | Diamond Rio | Diamond Rio-Lyin' Eyes.mp3 | test_audio_art | Directory-walk album-art processing |
| Diamond Rio | Diamond Rio | Diamond Rio-Lyin' Eyes.mp3 | test_audio_metadata | Directory-walk metadata keys |
| Diamond Rio | Diamond Rio | Diamond Rio-Lyin' Eyes.mp3 | test_audio_utilities | Directory-walk volume analysis |
| Diamond Rio | Diamond Rio | Diamond Rio-Lyin' Eyes.mp3 | test_directory_processing | Directory-walk file listing |
| Elton John | Goodbye Yellow Brick Road | Elton John-Saturday Night's Alright for Fighting.wma | test_audio_art | WM/Picture artwork fixture |
| Elton John | Goodbye Yellow Brick Road | Elton John-Saturday Night's Alright for Fighting.wma | test_directory_processing | File path information |
| Genesis | In Too Deep-I’d Rather Be You | Genesis-In Too Deep.mp3 | test_audio_metadata | Album-directory creation |
| Joshua Davis | The Voice Peformance | Joshua Davis-The Workingman's Hymn.m4a | test_audio_art | MP4 cover-art fixture |
| Joshua Davis | The Voice Peformance | Joshua Davis-The Workingman's Hymn.m4a | test_audio_metadata | MP4 filename normalization |
| Joshua Davis | The Voice Peformance | Joshua Davis-The Workingman's Hymn.m4a | test_audio_metadata | Directory-walk MP4 filename normalization |
| Joshua Davis | The Voice Peformance | Joshua Davis-The Workingman's Hymn.m4a | test_directory_processing | File path information |
| Sawyer Fredericks | A Good Storm | Sawyer Fredricks - Shots Fired.mp3 | test_audio_playlist | Playlist path lookup |
| Sawyer Fredericks | A Good Storm | Sawyer Fredricks - Shots Fired.mp3 | test_directory_processing | File-directory lookup |
| The Eagles | Desperado | The Eagles-Desperado.m4a | test_audio_metadata | Co-located folder art |
| The Eagles | Desperado | The Eagles-Desperado.m4a | test_audio_metadata | M4A Metadata Mapping |
| The Eagles | Desperado | The Eagles-Desperado.m4a | test_audio_playlist | Playlist M4A parsing |
| The Lord of the Rings | The Return of the King | Annie Lennox - Into the West.mp3 | test_audio_playlist | Playlist artist-path correction |
| The Lord of the Rings | The Two Towers | Howard Shore-The Taming Of Smeagol.mp3 | test_audio_normalization | RMS normalization |
| X Ambassadors | VHS | X Ambassadors-Renegades.mp3 | test_audio_normalization | Max-volume check |
| N/A | /tests | expected.m3u | test_audio_playlist | Expected playlist output |
| N/A | /tests/Music | test.m3u | test_audio_art | Rejects non-audio album-art input |
| N/A | /tests/Music | test.m3u | test_audio_metadata | Mutagen metadata type returns None |
| N/A | /tests/Music | test.m3u | test_audio_metadata | Rejects invalid embedded-art extension |
| N/A | /tests/Music | test.m3u | test_audio_metadata | Rejects non-audio file loading |
| N/A | /tests/Music | test.m3u | test_audio_playlist | Playlist path updates |
| N/A | /tests/Music | test.m3u | test_directory_processing | Preserves playlist during album cleanup |
| N/A | /tests/Music | test.m3u | test_directory_processing | Removes matching playlist file |
| N/A | /tests/Music | test.m3u | test_subprocess_utilities | FFprobe rejects playlist input |
| N/A | /tests/Music | test.m3u | test_subprocess_utilities | FFmpeg rejects playlist input |
