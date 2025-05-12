#!/usr/bin/env python3
'''
@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.
'''

# standard modules
import argparse
import csv
import logging
import os
import platform
import sys

# local modules
from src.audio_info import AudioMetadata
from src.dir_processing import DirectoryProcessing

def main():
    '''
    @brief Module entry point.
    @details Takes command line arguments and executes per arguments.
    '''

    # get the arguments


    # processing = DirectoryProcessing('H', 'Music')
    # processing.ext_list_files("aac")

    metadata = AudioMetadata()

    # # get mp3
    # mp3_file_list = ["H:\\Music\\Kenny Rogers\\Daytime Friends - The Very Best of Kenny\\18 Lady.mp3",
    #                  "H:\\Music\\Various Artists\\Best of the Blues, Volume 1\\Albert Collins-Trash Talkin'.mp3",
    #                  "H:\\Music\\4 Non Blondes\\Bigger, Better, Faster, More!\\4 Non Blondes-What's Up.mp3",
    #                  "H:\\Music\\.38 Special\\.38 Special-Teacher, Teacher.mp3",
    #                  "H:\\Music\\.38 Special\\Special Forces\\.38 Special-Caught Up in You.mp3"
    #                 ]
    # for song in mp3_file_list:
    #     metadata_type = metadata.get_any_metadata_type(song)
    #     if metadata_type == "mp3":
    #         tag = metadata.get_mp3_tag_info(song)
    #         print(tag)

    # # get any tag info
    # any_tag_info_file_list = ["H:\\Music\Dolly Parton\\Blue Smoke\\Dolly Parton-Unlikely Angel.mp3",
    #                           "H:\\Music\\The Eagles\\The Eagles-Desperado.m4a",
    #                           "H:\\Music\\Elton John\\Greatest Hits, Vol. 2\\Elton John-Island Girl.wma"
    #                          ]
    # for song in any_tag_info_file_list:
    #     metadata_type = metadata.get_any_metadata_type(song)
    #     print("Song: {0} has metadata type: {1}".format(song, metadata_type))

    # conversion testing
    # Create an os appropriate list of file paths for audio files that are intended for conversion to MP3 format.
    # The paths are specified as strings, with each string representing the file path of an audio file.
    if platform.system() == "Linux":
        conversion_file_list = [
                                r"/media/gerald/Music/Music/.38 Special/Special Forces/.38 Special-Caught Up in You.mp3",
                                r"/home/gerald/Music/Alejandro Escovedo/Alejandro Escovedo-Broken Bottle.wma",
                                r"/media/gerald/Music/Music/The Eagles/Desperado/The Eagles-Desperado.m4a",
                                r"/media/gerald/Music/Music/The Eagles/Hotel California/The Eagles-Hotel California.wma",
                                ]
    elif platform.system() == "Windows":
        conversion_file_list = [
                                r"H:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a",
                                r"H\Music\Alejandro Escovedo\Alejandro Escovedo-Broken Bottle.wma",
                                r"H:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a",
                                r"H:\Music\The Eagles\Hotel California\The Eagles-Hotel California.wma",
                                r"H:\Music\.38 Special\Special Forces\.38 Special-Caught Up in You.mp3"
                                ]


    for song in conversion_file_list:
        metadata.convert_any_to_mp3(song)

if __name__ == "__main__":
    '''
    @private
    Top level script environment entry point, parses and validates input arguments
    '''

    # parser = argparse.ArgumentParser(description='Music Processing')
    # parser.add_argument('-l', '--list', type=valid_date, help='Start date in YYYY-MM-DD', required=True)
    # parser.add_argument('-e', '--end', type=valid_date, help='End date in YYYY-MM-DD', required=True)
    # parser.add_argument('-a', '--aor', type=valid_aor, help='AOR text', required=True)
    # parser.add_argument('-d', '--dir', type=valid_dir, help='Source directory', required=True)

    # args = parser.parse_args()

    main()

