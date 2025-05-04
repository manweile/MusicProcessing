#!/usr/bin/env python3
'''
@file main.py
@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.
'''

from src.dir_processing.directory_processing import DirectoryProcessing
from src.audio_info.audio_metadata import AudioMetadata

def main():
    '''
    @brief Module entry point.
    @details Takes command line arguments and executes per arguments.
    '''

    # processing = DirectoryProcessing('H', 'Music')
    # processing.ext_list_files("aac")
    metadata = AudioMetadata()
    file_list = ["H:\\Music\\Kenny Rogers\\Daytime Friends - The Very Best of Kenny\\18 Lady.mp3",
                 "H:\\Music\\Albert Collins\\Albert Collins - Trash Talkin'.mp3",
                 "H:\\Music\\4 Non Blondes\\Bigger, Better, Faster, More!\\4 Non Blondes-What's Up.mp3",
                ]

    for song in file_list:
        metadata_type = metadata.get_metadata_type(song)
        print("Song: {0} has metadata type: {1}".format(song, metadata_type))

        tag = metadata.get_mp3_tag_info(song)
        print(tag)

if __name__ == "__main__":
    '''
    @brief Top level script environment entry point
    '''

    main()

