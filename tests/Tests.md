# Music Files
The audio files in tests\Music are input files for the test suites.<br>

| Artist                | Album                         | Song                                   | Test Suite                  | Comment                            |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| 38 Special            | Teachers                      | 38 Special-Teach Teacher.mp3           | test_audio_playlist         | fail path, renamed file not found  |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| Abba                  | Waterloo                      | ABBA-Waterloo.mp3                      | test_audio_art              | happy path, co-located Folder.jpg  |
| ""                    | ""                            | ""                                     | test_audio_metadata         | ""                                 |
| ""                    | ""                            | ""                                     | test_audio_normalization    | happy paths                        |
| ""                    | ""                            | ABBA-Waterloo.m4a                      | test_audio_playlist         | happy path returns mp3 extension   |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| Aerosmith             | Devils Got a New Disguise ... | Aerosmith-Dream On.mp3                 | test_audio_playlist         | happy path returns updated album   |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| Albert Collins        | Best of The Blues, Vol. 1     | Albert Collins - Trash Talkin'.mp3     | test_audio_art              | happy path, AlbumArt\<album>.jpg   |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| Bear McCreary         | Battlestar Galactica          | Bear McCreary - BSG Gayatri...mp3      | unassigned                  | possible fail path                 |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| Billie Holiday        | Georgia On My Mind            | Billie Holiday-Georgia On My Mind.wma  | test_audio_art              | fail paths, no stream              |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| C.C.R.                | Chronicle, Vol. 1             | C.C.R.-Fortunate Son.wma               | test_audio_metadata         | happy path, co-located Folder.jpg  |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| Crush                 | Here                          | Crush-Live.mp3                         | test_audio_art              | happy paths                        |
| ""                    | ""                            | ""                                     | test_audio_normalization    | ""                                 |
| ""                    | ""                            | No_tag_Crush-Live.mp3                  | ""                          | fail path, no art                  |
| ""                    | ""                            | Crush-Live.wma                         | test_audio_playlist         | happy path returns mp3 extension   |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| Daughtry              | Leave This Town               | Daughtry-No Surprise.mp3               | test_audio_playlist         | fail path, file not found in tld   |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| Elton John            | Goodby Yellow Brick Road      | Elton John-Saturday Night's...wma      | test_audio_art              | happy paths                        |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| Joshua Davis          | The Voice Peformance          | Joshua Davis-The Workingman's Hymn.m4a | test_audio_art              | happy paths                        |
| ""                    | ""                            | ""                                     | test_directory_processing   | ""                                 |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| Sawyer Fredricks      | A Good Storm                  | Sawyer Fredricks - Shots Fired.mp3     | test_audio_playlist         | ""                                 |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| The Eagles            | Desperado                     | The Eagles-Desperado.m4a               | test_audio_metadata         | happy path, co-located Folder.jpg  |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| The Lord of the Rings | The Return of the King        | Annie Lennox-Into the West.mp3         | test_audio_playlist         | happy path returns updated artist  |
| --------------------- | ----------------------------- | -------------------------------------- | --------------------------- | ---------------------------------- |
| X Ambassadors         | VHS                           | X Ambassadors-Renegades.mp3            | test_audio_normalization    | fail path                          |