#!/usr/bin/env python3
'''
@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.
'''

# standard modules
import argparse

# local modules
from src.audio_info import AudioMetadata
from src.dir_processing import DirectoryProcessing


directory = DirectoryProcessing()
metadata = AudioMetadata()

def convert_file(file_path):
    '''
    @brief Convert audio file specified by extension to mp3 format.
    '''

    metadata.convert_file(file_path)


def convert_walk(tld_path, file_pattern):
    '''
    @brief Convert all audio files in specified top level directory to mp3 format.
    '''

    metadata.convert_walk(tld_path, file_pattern)


def create_albums(tld_path):
    '''
    @brief Create album 2nd level directories under artist first level directories in top level directory.
    '''

    metadata.create_album_dir(tld_path)


def list_audio(tld_path):
    '''
    @brief List all audio files from specified top level directory.
    '''

    directory.get_audio_file_list(tld_path)


def list_type(tld_path, file_ext=None):
    '''
    @brief List files from specified top level directory by specified extension.
    '''

    directory.get_ext_file_list(file_ext, tld_path)


def remove_albums(tld_path):
    '''
    @brief Remove empty album directories from specified top level directory.
    '''

    directory.remove_album_dir(tld_path)


def remove_pattern(tld_path, file_pattern):
    '''
    @brief Remove files with specified pattern from specified top level directory.
    '''

    directory.remove_pattern(tld_path, file_pattern)

def set_album_art(tld_path):
    '''
    @brief Sets album art file for an album directory.
    '''

    metadata.set_album_art(tld_path)


def main(args):
    '''
    @brief Module entry point.

    @details Takes command line arguments and executes per arguments.

    @exception NotImplementedError A subcommand not implemented error.
    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        if args.subcommand == "convert-file":
            file_path = getattr(args, "file")
            convert_file(file_path)

        if args.subcommand == "convert-walk":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            convert_walk(tld_path, file_pattern)

        if args.subcommand == "create-albums":
            tld_path = getattr(args, "tld")
            create_albums(tld_path)

        if args.subcommand == "list-audio":
            tld_path = getattr(args, "tld")
            list_audio(tld_path)

        if args.subcommand == "list-type":
            tld_path = getattr(args, "tld")
            file_ext = getattr(args, "ext")
            list_type(tld_path, file_ext)

        if args.subcommand == "remove-albums":
            tld_path = getattr(args, "tld")
            remove_albums(tld_path)

        if args.subcommand == "remove-pattern":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            remove_pattern(tld_path, file_pattern)

        if args.subcommand == "set-art":
            tld_path = getattr(args, "tld")
            set_album_art(tld_path)

    except NotImplementedError as e:
        raise NotImplementedError(f"Command {args.subcommand} does not exist")
    except Exception as e:

        raise Exception(f"Exception {e} executing subcommand {args.subcommand}")


    # # get mp3
    # mp3_file_list = ["H:\\Music\\Kenny Rogers\\Daytime Friends - The Very Best of Kenny\\18 Lady.mp3",
    #                  "H:\\Music\\Various Artists\\Best of the Blues, Volume 1\\Albert Collins-Trash Talkin'.mp3",
    #                  "H:\\Music\\4 Non Blondes\\Bigger, Better, Faster, More!\\4 Non Blondes-What's Up.mp3",
    #                  "H:\\Music\\.38 Special\\.38 Special-Teacher, Teacher.mp3",
    #                  "H:\\Music\\.38 Special\\Special Forces\\.38 Special-Caught Up in You.mp3"
    #                 ]
    # for song in mp3_file_list:
    #     metadata_type = metadata.get_metadata_type(song)
    #     if metadata_type == "mp3":
    #         tag = metadata.get_mp3_tag_info(song)
    #         print(tag)

    # # get any tag info
    # any_tag_info_file_list = ["H:\\Music\Dolly Parton\\Blue Smoke\\Dolly Parton-Unlikely Angel.mp3",
    #                           "H:\\Music\\The Eagles\\The Eagles-Desperado.m4a",
    #                           "H:\\Music\\Elton John\\Greatest Hits, Vol. 2\\Elton John-Island Girl.wma"
    #                          ]
    # for song in any_tag_info_file_list:
    #     metadata_type = metadata.get_metadata_type(song)
    #     print("Song: {0} has metadata type: {1}".format(song, metadata_type))


if __name__ == "__main__":
    '''
    @brief Top level script environment entry point

    @details Parses and validates input arguments.
    '''

    parser = argparse.ArgumentParser(description='Music Processing')
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    # "/media/gerald/Music/Music/.38 Special/Special Forces/.38 Special-Caught Up in You.mp3",
    # "/home/gerald/Music/Alejandro Escovedo/Alejandro Escovedo-Broken Bottle.wma",
    # "/media/gerald/Music/Music/The Eagles/Desperado/The Eagles-Desperado.m4a",
    # "/media/gerald/Music/Music/The Eagles/Hotel California/The Eagles-Hotel California.wma"
    # "C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a",   # embedded art, datetime string
    # "H:\Music\Alejandro Escovedo\Alejandro Escovedo-Broken Bottle.wma",                    # no embedded art
    # "H:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a",                              # no embedded art even though file explorer shows it
    # "H:\Music\The Eagles\Hotel California\The Eagles-Hotel California.wma",                # no embedded art
    # "H:\Music\.38 Special\Special Forces\.38 Special-Caught Up in You.mp3"                 # no embedded art
    # convert audio file specified to mp3 format
    # 1 mandatory arg, the audio file path
    # sys.argv = ['D:\MusicProcessing\main.py', 'convert-file', 'C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a']
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'convert-file', '/home/gerald/Music/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.m4a']
    convert_file_parser = subparsers.add_parser("convert_file", help="Converts an audio file to mp3")
    convert_file_parser.add_argument("file", type=str, help="mandatory audio file path")
    convert_file_parser.set_defaults(func=convert_file)

    # convert all audio files found in top level directory
    # 1 mandatory arg, the tld path
    # sys.argv = ['D:\MusicProcessing\main.py', 'convert-walk', 'C:\Music', '--pattern', '*.mp3' | '*.m4a' | '*.wma']
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'convert-walk', '/home/gerald/Music', '--pattern', '*.mp3' | '*.m4a' | '*.wma']
    convert_walk_parser = subparsers.add_parser("convert-walk", help="Converts all audio files to mp3")
    convert_walk_parser.add_argument("tld", type=str, help="mandatory top level directory")
    convert_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
    convert_walk_parser.set_defaults(func=convert_walk)

    # create album directories
    # 1 mandatory arg, the tld path
    # sys.argv = ['D:\MusicProcessing\main.py', 'create-album', 'C:\Music']
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'create-album', '/home/gerald/Music']
    create_album_parser = subparsers.add_parser("create-albums", help="Create album sub-directories")
    create_album_parser.add_argument("tld", type=str, help="mandatory top level directory")
    create_album_parser.set_defaults(func=create_albums)

    # list all audio files
    # 1 mandatory arg, the tld path
    # sys.argv = ['D:\MusicProcessing\main.py', 'list-audio', 'C:\Music']
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'list-audio', '/home/gerald/Music']
    list_audio_parser = subparsers.add_parser("list-audio", help="Generates a csv containing full path for all audio files")
    list_audio_parser.add_argument("tld", type=str, help="mandatory top level directory")
    list_audio_parser.set_defaults(func=list_audio)

    # list files by extension
    # 1 mandatory arg, the tld path
    # 1 optional arg, the file extension
    # sys.argv = ['D:\MusicProcessing\main.py', 'list-type', 'C:\Music', '--ext', 'mp3' | 'm4a' | 'wma' | 'abc']
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'list-type', '/home/gerald/Music', '--ext', 'mp3' | 'm4a' | 'wma' | 'abc']
    list_type_parser = subparsers.add_parser("list-type", help="Generates a csv containing full file path for an audio file type")
    list_type_parser.add_argument("tld", type=str, help="mandatory top level directory")
    list_type_parser.add_argument("--ext", type=str, help='optional file extension')
    list_type_parser.set_defaults(func=list_type)

    # remove empty album directories
    # 1 mandatory arg, the tld path
    # sys.argv = ['D:\MusicProcessing\main.py', 'remove-album', 'C:\Music']
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'remove-album', '/home/gerald/Music']
    remove_album_parser = subparsers.add_parser("remove-albums", help="Remove empty album sub-directories")
    remove_album_parser.add_argument("tld", type=str, help="mandatory top level directory")
    remove_album_parser.set_defaults(func=remove_albums)

    # remove files matching specified file pattern
    # 2 mandatory args, the tld path and the file pattern
    # sys.argv = ['D:\MusicProcessing\main.py', 'remove-pattern', 'C:\Music', 'AlbumArtSmall.jpg' | 'AlbumArt*Small.jpg' | '*.db' | '*.ini' ]
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'remove-pattern', '/home/gerald/Music', 'AlbumArtSmall.jpg' | 'AlbumArt*Small.jpg' | '*.db' | '*.ini' ]
    remove_pattern_parser = subparsers.add_parser("remove-pattern", help="Removes files with specified pattern")
    remove_pattern_parser.add_argument("tld", type=str, help="mandatory top level directory")
    remove_pattern_parser.add_argument("pattern", type=str, help="mandatory file pattern")
    remove_pattern_parser.set_defaults(func=remove_pattern)

    # set album art file
    # 1 mandatory arg, the tld path
    # sys.argv = ['D:\MusicProcessing\main.py', 'set-art', 'C:\Music']
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'set-art', '/home/gerald/Music']
    remove_album_parser = subparsers.add_parser("set-art", help="Set album art file")
    remove_album_parser.add_argument("tld", type=str, help="mandatory top level directory")
    remove_album_parser.set_defaults(func=set_album_art)

    args = parser.parse_args()
    main(args)

