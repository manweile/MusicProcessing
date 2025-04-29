#!/usr/bin/env python3
'''
@file main.py
@brief Music Processing Project
@mainpage Music Processing Project

@section description_main Description
A python program for manipulating & normalizing audio files.

@section notes_main Notes
Music Processing recognizes the following file types:
- Audio file types:
    - mp3
    - m4a
    - wma
- Playlist file types:
    - m3u

@section usage_main Usage
>python.exe main.py

@copyright GWN Software 2025. All rights reserved.
'''

from src.dir_processing.directory_processing import DirectoryProcessing

def main():
    '''
    @public
    @brief Module entry point.
    @details Takes command line arguments and executes per arguments
    '''

    processing = DirectoryProcessing('H', 'Music')
    processing.ext_list_files("aac")

if __name__ == "__main__":
    '''
    @private
    @brief Top level script environment entry point
    '''

    main()

