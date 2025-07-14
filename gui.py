#!/usr/bin/env python3
'''
@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.
'''

# standard modules
import argparse
import gc

# third party modules
from gooey import Gooey, GooeyParser

# local modules
from src.audio_info import AudioArt
from src.audio_info import AudioMetadata
from src.audio_normalize import AudioNormalization
from src.dir_processing import DirectoryProcessing

gc.enable()

art = AudioArt()
directory = DirectoryProcessing()
metadata = AudioMetadata()
normalization = AudioNormalization()

running = True


def convert_file(file_path):
    '''
    @brief Converts specified audio file to mp3 format.

    @param file_path {str} The full path to audio file.
    '''

    metadata.convert_file(file_path)


def extract_file(file_path):
    '''
    @brief Extracts and saves embedded album art from specified audio file.

    @param file_path {str} The full path to audio file.
    '''

    art.extract_album_art(file_path)


def extract_walk(tld_path, file_pattern):
    '''
    @brief Extracts and save embedded art from  all audio files in specified top level directory with specified pattern.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to delete.
    '''

    art.extract_walk(tld_path, file_pattern)


@Gooey(optional_cols=2, program_name="Music Processing")
def parse_args():
    '''
    @brief

    @details
    @return
    '''

    parser = GooeyParser(description='Music Processing')
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    # convert audio file specified to mp3 format
    # 1 mandatory arg, the audio file path
    # sys.argv = ['D:\MusicProcessing\main.py', 'convert-file', 'C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a']
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'convert-file', '/home/gerald/Music/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.m4a']
    convert_file_parser = subparsers.add_parser("convert-file", help="Converts an audio file to mp3")
    convert_file_parser.add_argument("file", type=str, help="mandatory full path to audio file", widget="FileChooser")
    convert_file_parser.set_defaults(func=convert_file)

    # extract album art from specified audio file
    # 1 mandatory arg, the path to audio file
    # sys.argv = ['D:\MusicProcessing\main.py', 'extract-art', 'C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma',
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'extract-art', '/home/gerald/Music/Elton John/Goodbye Yellow Brick Road/Elton John-Saturday Night's Alright for Fighting.wma',
    extract_file_parser = subparsers.add_parser("extract-file", help="Extracts embedded art from audio file")
    extract_file_parser.add_argument("file", type=str, help="mandatory full path to audio file", widget="FileChooser")
    extract_file_parser.set_defaults(func=extract_file)

    # extract album art from all audio files found in top level directory
    # 1 mandatory arg, the tld path
    # 1 optional arg, the file pattern to match
    # sys.argv = ['D:\MusicProcessing\main.py', 'extract-walk', 'C:\Music', '--pattern', { '*.mp3' | '*.m4a' | '*.wma' } ]
    # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'extract-walk', '/home/gerald/Music', '--pattern', { '*.mp3' | '*.m4a' | '*.wma' } ]
    extract_walk_parser = subparsers.add_parser("extract-walk", help="Extracts embedded art from all audio files")
    extract_walk_parser.add_argument("tld", type=str, help="mandatory top level directory", widget="DirChooser")
    extract_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
    extract_walk_parser.set_defaults(func=extract_walk)
    args = parser.parse_args()
    return args


def main(args):
    '''
    @brief Module entry point.

    @details Takes command line arguments and executes per arguments.

    @param args {Namespace} Arguments for execution.
    @exception NotImplementedError A subcommand not implemented error.
    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        if args.subcommand == "convert-file":
            file_path = getattr(args, "file")
            convert_file(file_path)

        if args.subcommand == "extract-file":
            file_path = getattr(args, "file")
            extract_file(file_path)

        if args.subcommand == "extract-walk":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            extract_walk(tld_path, file_pattern)

    except NotImplementedError:
        raise NotImplementedError(f"Command {args.subcommand} does not exist")
    except Exception as e:
        raise Exception(f"Exception {e} executing subcommand {args.subcommand}")


if __name__ == '__main__':
    '''
    @brief Code execution guard.

    @details Allows code to run only when script is executed.
    '''

    args = parse_args()
    main(args)
