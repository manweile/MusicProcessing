'''
@file audio_playlist.py
@brief Defines the audio playlist class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import os
# from pathlib import Path

# third party modules

# local modules
# from src import _PLAYLIST_EXTS, _PLAYLIST_TYPES
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


    def update_paths(self, file_path):
        '''
        @brief Updates an old playlist relative pathing.

        @details Walks through a m3u playlist updating relative paths.

        @param file_path {str} The path for audio file to be converted.
        '''

        r'''
        see https://en.wikipedia.org/wiki/M3U
        My playlists are relative pathed (unlike windows pls files, which are absolute pathed).
        Because I use relative pathing, m3u files MUST live in the top level directory.

        I can ignore the header line (#EXTM3U)
        The track info (#EXTINF:0) line, after the comma, give me the filename I need to find
        The relative pathing - the line after the track info - is what I need to verify or update

        eg 1 incorrect relative path, because there is no album 2nd level directory
        #EXTINF:0,Daughtry-Home.mp3
        Daughtry\Daughtry-Home.mp3

        eg 2 correct relative path
        #EXTINF:0,Sawyer Fredricks - Shots Fired.mp3
        Sawyer Fredericks\A Good Storm\Sawyer Fredricks - Shots Fired.mp3

        eg 3 incorrect relative path because the album directory changed


        eg 4 incorrect relative path because the file name changed


        #EXTM3U
        #EXTINF:0,Daughtry-Home.mp3
        Daughtry\Daughtry-Home.mp3

        #EXTINF:0,Sawyer Fredricks - Shots Fired.mp3
        Sawyer Fredericks\A Good Storm\Sawyer Fredricks - Shots Fired.mp3
        '''
        try:
            export_path = generated_files
            export_name = os.path.basename(file_path)
            export_file = os.path.join(export_path, export_name)

        except Exception as e:
            raise Exception(f"Exception {e} updating {file_path}")
