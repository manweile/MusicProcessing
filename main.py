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
    directory = DirectoryProcessing(tld_path)
    directory.get_audio_file_list()

def list_type(tld_path, file_ext=None):
    directory = DirectoryProcessing(tld_path)
    directory.get_ext_file_list(file_ext)

def main(args):
    '''
    @brief Module entry point.
    @details Takes command line arguments and executes per arguments.
    '''

    if args.subcommand == 'list-audio':
        tld_path = getattr(args, 'tld')
        list_audio(tld_path)

    if args.subcommand == 'list-type':
        tld_path = getattr(args, 'tld')
        file_ext = getattr(args, 'ext')
        list_type(tld_path, file_ext)

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

    # removing empty album dirs
    # if platform.system() == "Linux":
    #     directory.remove_album_dir(r"/home/gerald/Music")
    # elif platform.system() == "Windows":
    #     directory.remove_album_dir(r"C:\Music")


if __name__ == "__main__":
    '''
    @brief Top level script environment entry point

    @details Parses and validates input arguments.
    '''

    parser = argparse.ArgumentParser(description='Music Processing')
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    # list all audio files
    # 1 mandatory arg, the tld path
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'list-audio', '/home/gerald/Music']
    list_audio_parser = subparsers.add_parser("list-audio", help="Generates a csv containing full path for all audio files")
    list_audio_parser.add_argument("tld", type=str, help="mandatory top level directory")
    list_audio_parser.set_defaults(func=list_audio)

    # list files by extension
    # 1 mandatory arg, the tld path
    # 1 optional arg, the file extension
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'list-type' '/home/gerald/Music' '--ext' 'mp3' | 'm4a' | 'wma' | 'abc']
    list_type_parser = subparsers.add_parser("list-type", help="Generates a csv containing full file path for an audio file type")
    list_type_parser.add_argument("tld", type=str, help="mandatory top level directory")
    list_type_parser.add_argument('--ext', type=str, help='optional file extension')
    list_type_parser.set_defaults(func=list_type)

    args = parser.parse_args()
    main(args)

