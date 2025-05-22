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

def list_audio(tld_path):
    directory = DirectoryProcessing()
    directory.get_audio_file_list(tld_path)


def main(args):
    '''
    @brief Module entry point.
    @details Takes command line arguments and executes per arguments.
    '''

    # get the arguments


    # processing = DirectoryProcessing('H:\Music')
    # processing.ext_list_files("aac")

    # metadata = AudioMetadata()
    # directory = DirectoryProcessing()

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
    # if platform.system() == "Linux":
    #     conversion_file_list = [
    #                             r"/media/gerald/Music/Music/.38 Special/Special Forces/.38 Special-Caught Up in You.mp3",
    #                             r"/home/gerald/Music/Alejandro Escovedo/Alejandro Escovedo-Broken Bottle.wma",
    #                             r"/media/gerald/Music/Music/The Eagles/Desperado/The Eagles-Desperado.m4a",
    #                             r"/media/gerald/Music/Music/The Eagles/Hotel California/The Eagles-Hotel California.wma",
    #                             ]
    # elif platform.system() == "Windows":
    #     conversion_file_list = [
    #                             r"C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a",   # embedded art, datetime string
    #                             r"H:\Music\Alejandro Escovedo\Alejandro Escovedo-Broken Bottle.wma",                    # no embedded art
    #                             r"H:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a",                              # no embedded art even though file explorer shows it
    #                             r"H:\Music\The Eagles\Hotel California\The Eagles-Hotel California.wma",                # no embedded art
    #                             r"H:\Music\.38 Special\Special Forces\.38 Special-Caught Up in You.mp3"                 # no embedded art
    #                             ]

    # for song in conversion_file_list:
    #     metadata.convert_any_to_mp3(song)

    # creating album dirs
    # if platform.system() == "Linux":
    #     metadata.create_album_dir(r"/home/gerald/Music")
    # elif platform.system() == "Windows":
    #     metadata.create_album_dir(r"C:\Music")
    if getattr(args, 'list-audio'):
        tld_path = getattr(args, 'tld')
        list_audio(tld_path)

    # removing empty album dirs
    # if platform.system() == "Linux":
    #     directory.remove_album_dir(r"/home/gerald/Music")
    # elif platform.system() == "Windows":
    #     directory.remove_album_dir(r"C:\Music")

if __name__ == "__main__":
    '''
    @private
    Top level script environment entry point, parses and validates input arguments
    '''

    parser = argparse.ArgumentParser(description='Music Processing')
    # all audio files list
    # 1 mandatory arg, the tld path
    # sys.argv = ['MusicProcessing', 'list-audio' '--tld' '/home/gerald/Music']
    parser.add_argument("list-audio", type=str, help="required top level directory path")
    parser.add_argument("--tld", type=str, help="optional top level directory", required=False)
    # list files by extension
    # 1 mandatory arg, the tld path
    # 1 optional arg, the file extension
    # sys.argv = ['MusicProcessing', 'list-ext' '--tld' '/home/gerald/Music' --ext 'mp3' | 'm4a' | 'wma' | 'abc']
    # parser.add_argument('list-ext', type=str, help='required top level directory path')
    # parser.add_argument('--ext', type=str, help='optional file extension', required=False)


    args = parser.parse_args()
    main(args)

    # uncomment for testing command line arguments
    # change start and end paramters as needed, but they must match date range in query that produced data set
    # change data set dir path as needed, but WG_<data type>.txt file(s) must exist in dir path
    # sys.argv = ['process_for_ml', '-s', '2019-9-27', '-e', '2019-10-3', '-a', 'RM06A', '-d', '/home/pt/PTData/DataExtraction/RM06A/RM06A_Sep27_2019_to_Oct3_2019/']

    # parser = argparse.ArgumentParser(description='Process data for Clairvoyance')
    # parser.add_argument('-s', '--start', type=valid_date, help='Start date in YYYY-MM-DD', required=True)
    # parser.add_argument('-e', '--end', type=valid_date, help='End date in YYYY-MM-DD', required=True)
    # parser.add_argument('-a', '--aor', type=valid_aor, help='AOR text', required=True)
    # parser.add_argument('-d', '--dir', type=valid_dir, help='Source directory', required=True)

    # args = parser.parse_args()

    # verify_dates((getattr(args, 'start'), getattr(args, 'end')))

    # main(args)

# parser = argparse.ArgumentParser(description="calculate X to the power of Y")
# group = parser.add_mutually_exclusive_group()
# group.add_argument("-v", "--verbose", action="store_true")
# group.add_argument("-q", "--quiet", action="store_true")
# parser.add_argument("x", type=int, help="the base")
# parser.add_argument("y", type=int, help="the exponent")
# args = parser.parse_args()
# answer = args.x**args.y

# if args.quiet:
#     print(answer)
# elif args.verbose:
#     print(f"{args.x} to the power {args.y} equals {answer}")
# else:
#     print(f"{args.x}^{args.y} == {answer}")

    # main()

