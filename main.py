#!/usr/bin/env python3
'''
@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.
'''

# standard modules
import argparse

from mutagen.id3 import ID3

# local modules
from src.audio_info import AudioMetadata
from src.dir_processing import DirectoryProcessing

directory = DirectoryProcessing()
metadata = AudioMetadata()


def convert_file(file_path):
    '''
    @brief Converts specified audio file to mp3 format.
    '''

    metadata.convert_file(file_path)


def convert_walk(tld_path, file_pattern):
    '''
    @brief Converts all audio files in specified top level directory to mp3 format.
    '''

    metadata.convert_walk(tld_path, file_pattern)


def create_albums(tld_path):
    '''
    @brief Create album 2nd level directories under artist first level directories in top level directory.
    '''

    metadata.create_album_dir(tld_path)


def extract_art(file_path):
    '''
    @brief Extracts and saves embedded album art from specified audio file.
    '''

    metadata.extract_album_art(file_path)


def extract_walk(tld_path, file_pattern):
    '''
    @brief Extracts and save embedded art from  all audio files in specified top level directory with specified pattern.
    '''

    metadata.extract_walk(tld_path, file_pattern)


def get_tags(file_path):
    '''
    @brief Gets metadata from specified audio file.
    '''

    tags = metadata.get_any_tags(file_path)
    return tags


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

        if args.subcommand == "extract-art":
            file_path = getattr(args, "file")
            extract_art(file_path)

        if args.subcommand == "extract-walk":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            extract_walk(tld_path, file_pattern)

        if args.subcommand == "get-tags":
            file_path = getattr(args, "file")
            tags = get_tags(file_path)
            print(tags.pprint())

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

    except NotImplementedError:
        raise NotImplementedError(f"Command {args.subcommand} does not exist")
    except Exception as e:
        raise Exception(f"Exception {e} executing subcommand {args.subcommand}")


if __name__ == "__main__":
    '''
    @brief Top level script environment entry point

    @details Parses and validates input arguments.
    '''

    parser = argparse.ArgumentParser(description='Music Processing')
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    # convert audio file specified to mp3 format
    # "/media/gerald/Music/Music/.38 Special/Special Forces/.38 Special-Caught Up in You.mp3",
    # "/home/gerald/Music/Alejandro Escovedo/More Miles Than Money- Live 1994-1996/Alejandro Escovedo-Broken Bottle.wma",
    # "/home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a",
    # "/media/gerald/Music/Music/The Eagles/Hotel California/The Eagles-Hotel California.wma"
    # "C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a",   # embedded art, datetime string
    # "H:\Music\Alejandro Escovedo\Alejandro Escovedo-Broken Bottle.wma",                    # no embedded art
    # "C:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a",                              # no embedded art even though file explorer shows it
    # "H:\Music\The Eagles\Hotel California\The Eagles-Hotel California.wma",                # no embedded art
    # "H:\Music\.38 Special\Special Forces\.38 Special-Caught Up in You.mp3"                 # no embedded art
    # 1 mandatory arg, the audio file path
    # sys.argv = ['D:\MusicProcessing\main.py', 'convert-file', 'C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a']
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'convert-file', '/home/gerald/Music/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.m4a']
    # "/home/gerald/Music/Crush/Here/Crush-Live.mp3"
    convert_file_parser = subparsers.add_parser("convert-file", help="Converts an audio file to mp3")
    convert_file_parser.add_argument("file", type=str, help="mandatory full path to audio file")
    convert_file_parser.set_defaults(func=convert_file)

    # convert all audio files found in top level directory
    # 1 mandatory arg, the tld path
    # 1 optional arg, the file pattern to match
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

    # extract album art from specified audio file
    # C:\Music\Alberta Hunter\The Blues\Alberta Hunter - Amtrak Blues.mp3                                   #no embedded, no Folder.jpg
    # C:\Music\38 Special\Special Forces\Caught Up in You.mp3                                               #no embedded, has Folder.jpg
    # C:\Music\Joshua Davis\The Voice Peformance\Joshau Davis-The Workingman's Hym.m4a                      #has embedded, no Folder.jpg
    # C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma    #has embedded, no Folder.jpg
    # C:\Music\Billie Holiday\Georgia On My Mind\Billie Holiday-Georgia On My Mind.wma                      #has embedded, but not in a video stream, so will fail with ffmpeg
    # 1 mandatory arg, the path to audio file
    # sys.argv = ['D:\MusicProcessing\main.py', 'extract-art', 'C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma',
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'extract-art', '/home/gerald/Music/Elton John/Goodbye Yellow Brick Road/Elton John-Saturday Night's Alright for Fighting.wma',
    extract_art_parser = subparsers.add_parser("extract-art", help="Extracts embedded art from audio file")
    extract_art_parser.add_argument("file", type=str, help="mandatory full path to audio file")
    extract_art_parser.set_defaults(func=extract_art)

    # extract album art from all audio files found in top level directory
    # 1 mandatory arg, the tld path
    # 1 optional arg, the file pattern to match
    # sys.argv = ['D:\MusicProcessing\main.py', 'extract-walk', 'C:\Music', '--pattern', '*.mp3' | '*.m4a' | '*.wma']
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'extract-walk', '/home/gerald/Music', '--pattern', '*.mp3' | '*.m4a' | '*.wma']
    extract_walk_parser = subparsers.add_parser("extract-walk", help="Extracts embedded art from all audio files")
    extract_walk_parser.add_argument("tld", type=str, help="mandatory top level directory")
    extract_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
    extract_walk_parser.set_defaults(func=extract_walk)

    # get metadata tags for file
    # 1 mandatory arg, the path to audio file
    # sys.argv = ['D:\MusicProcessing\main.py', 'get-tags', 'C:\Music\Buckingham McVie\Buckingham McVie\Buckingham McVie-Too Far Gone.mp3',
    # sys.argv = [D:\MusicProcessing\main.py', 'get-tags', 'C:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a']
    get_tags_parser = subparsers.add_parser("get-tags", help="Gets metadata tags from audio file")
    get_tags_parser.add_argument("file", type=str, help="mandatory full path to audio file")
    get_tags_parser.set_defaults(func=get_tags)

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
    set_album_parser = subparsers.add_parser("set-art", help="Set album art file")
    set_album_parser.add_argument("tld", type=str, help="mandatory top level directory")
    set_album_parser.set_defaults(func=set_album_art)

    args = parser.parse_args()
    main(args)
