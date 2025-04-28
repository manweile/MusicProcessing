#!/usr/bin/env python3
'''!
@brief Music Processing Project
'''

##
# @mainpage Music Processing Project
#
# @section description_main Description
# A python program for manipulating & normalizing audio files.
#
# @section notes_main Notes
# Music Processing recognizes the following file types:
# - Audio file types:
#     - mp3
#     - m4a
#     - wma
# - Playlist file types:
#     - m3u
#
# @copyright GWN Software 2025. All rights reserved.


##
# @file music_processing.py
#
# @brief Music Processing program.
#
# @section description_music_processing Description
# A python program for manipulating & normalizing audio files.
#
# @section notes_music_processing Notes
# Usage:
#   python music_processing.py
#
# @copyright GWN Software 2025. All rights reserved.

from src.dir_processing.directory_processing import DirectoryProcessing

def main():
    '''!
    @public
    @brief Module entry point.
    @details Takes command line arguments and executes per arguments
    '''

    processing = DirectoryProcessing('H', 'Music')
    processing.ext_list_files("aac")

if __name__ == "__main__":
    '''!
    @private
    @brief Top level script environment entry point
    '''

    main()

