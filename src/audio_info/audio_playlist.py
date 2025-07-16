'''
@file audio_playlist.py
@brief Defines the audio playlist class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import os
# import platform
from pathlib import Path

# third party modules

# local modules
from src import _AUDIO_EXTS
from src.dir_processing import DirectoryProcessing
from src.generated_files import generated_files

gc.enable()

directory = DirectoryProcessing()


class AudioPlaylist():
    '''
    @brief Defines the base playlist processing used by project.
    '''

    def __init__(self):
        '''
        @brief Initialize the AudioPlaylist class.

        @details A basic class implementation with no instantiation parameters.

        @return AudioPlaylist {instance} An instance of the class.
        '''

        pass


    def get_audio_name(self, line):
        '''
        @brief Gets audio file name from a #EXTINF line

        @details The audio file extension may have changed from wma or m4a to mp3
        @details A  extinf tag containing line is in format: #EXTINF:N,<name>.<ext>,
        where N is length of song in seconds, or -1 or 0, and
        @details <ext> is one of mp3, m4a, or wma.
        @param line (str) Line of text read from m3u file containing a #EXTINF tag
        @return audio_file {str} Audio file name with extension, otherwise None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        audio = None
        delimiter = ","

        try:
            index = line.find(delimiter)
            if index != -1:
                input_audio = line[index + len(delimiter):]
                # get the audio file name ext, may have to change it
                input_ext = os.path.splitext(os.path.basename(input_audio))[1]
                # wma and m4a files need mp3 extension
                if input_ext != _AUDIO_EXTS[0]:
                    input_stem = os.path.splitext(os.path.basename(input_audio))[0]
                    audio = input_stem + _AUDIO_EXTS[0]
                else:
                    audio = input_audio
            else:
                raise Exception(f"No file delimiter in {line}")

            return audio

        except Exception as e:
            raise Exception(f"Exception {e} getting file name from {line}")


    def update_paths(self, start_path, input_m3u):
        '''
        @brief Updates an old playlist relative pathing.

        @details Walks through a m3u playlist updating relative paths.
        @details The updated playlist is created in generated files directory.
        @details The new file is expected to be moved to the correct top level directory  for the relative paths.

        @param start_path {str} The top level directory where playlist is located.
        @param input_m3u {str} The full file path to playlist needing conversion.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        r'''
        see https://en.wikipedia.org/wiki/M3U
        My playlists are relative pathed (unlike windows pls files, which are absolute pathed).
        Because I use relative pathing, m3u files MUST live in the top level directory ie in \Music
        Also, my m3u's are played on Windows OS,not ubuntu, so \, not / path separator.
        So a proper relative path will be <artist>\<album>\<title>.mp3

        I can ignore the header line (#EXTM3U), just need to copy it to new file.
        The track info (#EXTINF:0) tag, up to the comma, is also copied as is.
        The file name is after the comma, which will usually give the file name, but necessarily the correct file extension.
        If the file ext is NOT mp3, it needs to change to mp3 (from m4a or wma), and then search for the mp3 filename.
        If the file name & mp3 ext is not found, need to print error and return.
        If the filename & mp3 ext is found, I need the artist\album path
        Now I can update the #EXTINF:0 tag by adding the correct file name & mp3 ext after the comma.
        After that, verify or update the relative path.

        eg 1 incorrect relative path, because there is no album 2nd level directory
        #EXTINF:0,Daughtry-Home.mp3
        Daughtry\Daughtry-Home.mp3

        eg 2 correct relative path
        #EXTINF:0,Sawyer Fredricks - Shots Fired.mp3
        Sawyer Fredericks\A Good Storm\Sawyer Fredricks - Shots Fired.mp3

        eg 3 incorrect relative path because the artist and album directory changed
        #EXTINF:0,Annie Lennox - Into the West.mp3
        Annie Lennox\Annie Lennox - Into the West.mp3
        /home/gerald/Music/The Lord of the Rings/The Return of the King/Annie Lennox - Into the West.mp3

        eg 4 incorrect relative path because the no album dir and file name changed - .38 Special-Teacher, Teacher.mp3 to 38 Special-Teacher,Teacher.mp3
        #EXTINF:0,.38 Special-Teacher, Teacher.mp3
        38 Special\.38 Special-Teacher, Teacher.mp3

        eg 5 incorrect relative path because file extension changed wma to mp3
        #EXTINF:0,Creedence Clearwater Revival-Fortunate Son.wma
        Creedence Clearwater Revival\Chronicle, Vol. 1\Creedence Clearwater Revival-Fortunate Son.wma

        #EXTM3U
        #EXTINF:0,Daughtry-Home.mp3
        Daughtry\Daughtry-Home.mp3

        #EXTINF:0,Sawyer Fredricks - Shots Fired.mp3
        Sawyer Fredericks\A Good Storm\Sawyer Fredricks - Shots Fired.mp3

        #EXTINF:0,Annie Lennox - Into the West.mp3
        Annie Lennox\Annie Lennox - Into the West.mp3

        #EXTINF:0,.38 Special-Teacher, Teacher.mp3
        38 Special\.38 Special-Teacher, Teacher.mp3

        #EXTINF:0,Creedence Clearwater Revival-Fortunate Son.wma
        Creedence Clearwater Revival\Chronicle, Vol. 1\Creedence Clearwater Revival-Fortunate Son.wma
        '''

        extheader = "#EXTM3U"
        extinf = "#EXTINF:"
        extinf_delimiter = ","

        try:
            # new m3u file gets created in generated files directory so can later be move to correct tld
            export_path = generated_files
            input_basename = os.path.basename(input_m3u)
            export_m3u = os.path.join(export_path, input_basename)

            # open input m3u for reading and export m3u for writing
            with open(input_m3u, 'r') as infile, open(export_m3u, 'w') as outfile:
                for line in infile:
                    # if we dont have text, blank line is not copied to output
                    if line.strip():
                        if extheader in line:
                            # the ext header is simply copied over
                            outfile.write(line)
                        elif extinf in line:
                            # get the audio file name, change ext to mp3 if needed
                            audio_file = self.get_audio_name(line)
                            if audio_file:
                                audio_file_path = directory.get_file_directory(start_path, audio_file)

                            # comma_index = line.find(extinf_delimiter)
                            # if comma_index != -1:
                            #     input_audio_file = line[comma_index + len(extinf_delimiter):]
                            #     # get the audio file name ext, may have to change it
                            #     input_audio_ext = os.path.splitext(os.path.basename(input_audio_file))[1]
                            #     # wma and m4a files need mp3 extstention
                            #     if input_audio_ext != _AUDIO_EXTS[0]:
                            #         input_audio_stem = os.path.splitext(os.path.basename(input_audio_file))[0]
                            #         audio_file = input_audio_stem + _AUDIO_EXTS[0]
                            #     else:
                            #         audio_file = input_audio_file

                            #     # search for the audio file, need the artist & album dirs
                            #     audio_file_path = directory.get_file_directory(start_path, audio_file)
                            #     if audio_file_path:
                            #         found_file = Path(audio_file_path)
                            #         found_parts = found_file.parts()
                            #         file = found_parts[-1:]
                            #         album = found_parts[-2:-1]
                            #         artist = found_parts[-3:-2]
                            #         relative_path = os.path.join(artist, album, file)
                            #         new_extinf = extinf + "0" + extinf_delimiter + audio_file
                            #         outfile.write(new_extinf)
                            #         outfile.write(relative_path)
                            #     else:
                            #         print(f"{audio_file} not found in {start_path}")
                            #         continue

        except Exception as e:
            raise Exception(f"Exception {e} updating {input_m3u}")
