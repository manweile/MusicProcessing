#!/usr/bin/env python3
'''
@file main.py
@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import argparse
import gc
import logging
import os
import sys

# third party modules
from gooey import Gooey, GooeyParser

# local modules
# from src import APP_NAME, APP_PATH
# from src import ARG_CLI_FILE, ARG_CLI_PATTERN, ARG_CLI_TLD
# from src import ARG_HELP_AUDIO, ARG_HELP_TLD, ARG_HELP_PATTERN
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging constants
from src import M4A_EXT, MP3_EXT, WMA_EXT
from src.generated_files import GENERATED_PATH
from src.audio_info import AudioArt
from src.audio_info import AudioMetadata
from src.audio_info import AudioPlaylist
from src.audio_normalize import AudioNormalization
from src.dir_processing import DirectoryProcessing

gc.enable()

# Configure logging
basename = os.path.basename(__file__)
stem = os.path.splitext(basename)[0]
file = stem + LOG_EXT
log_filename = os.path.join(GENERATED_PATH, LOG_DIR, file)
# override the default logging level WARN to lowest level so we can log all levels
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=ERROR_LOG_FORMAT, filemode="a", encoding=UTF8)
logger = logging.getLogger(__name__)

art = AudioArt()
directory = DirectoryProcessing()
metadata = AudioMetadata()
normalization = AudioNormalization()
playlist = AudioPlaylist()

# @todo single use in main.py
## @var APP_NAME
# @brief The app description
# @details use when needing application name/description
APP_NAME = "Music Processing"

# @todo multiple use in main.py
## @var APP_PATH
# @brief The main script path
# @details Getting the directory name for importing means will not need a hard coded "magic spell" else where in codebase
APP_PATH = os.path.dirname(os.path.abspath(__file__))

# @todo multiple use in main.py
## @var ARG_CLI_FILE
# @brief add argument cli
# @details use when needing file cli
ARG_CLI_FILE = "file"

# @todo multiple use in main.py
## @var ARG_CLI_PATTERN
# @brief add argument cli
# @details use when needing pattern cli
ARG_CLI_PATTERN = "--pattern"

# @todo multiple use in main.py
## @var ARG_CLI_TLD
# @brief add argument cli
# @details use when needing tld cli
ARG_CLI_TLD = "tld"

# @todo multiple use in main.py
## @var ARG_HELP_PATH
# @brief add argument help
# @details use when needing mandatory file path input
ARG_HELP_AUDIO = "mandatory full path to audio file"

# @todo multiple use in main.py
## @var ARG_HELP_TLD
# @brief add argument help
# @details use when needing mandatory directory input
ARG_HELP_TLD = "mandatory top level directory"

# @todo multiple use in main.py
## @var ARG_HELP_PATTERN
# @brief add argument help
# @details use when needing optional pattern input
ARG_HELP_PATTERN = "optional file pattern"


class CustomArgumentParser(argparse.ArgumentParser):
    '''
    @brief Custom argument parser so argparse errors can be logged.

    @details https://stackoverflow.com/questions/48633847/python-argparse-errors-to-file
    '''

    def _print_message(self, message, file=None):
        '''
        @brief Override argparse.ArgumentParser._print_message so stderr gets logged instead of output to console.

        @param message {str} The error message to log.
        @param file {TextIOWrapper} A file-like object for stderr.
        '''

        # want to log errors if the message is intended for stderr,
        # unlike the super method which writes to console
        if message:
            if file is sys.stderr:
                logger.error(f"Argparse Error: {message.strip()}")
            else:
                super()._print_message(message, file)


'''
AudioMetadata functions
'''


def convert_file(file_path):
    '''
    @brief Converts specified audio file to mp3 format.

    @param file_path {str} The full path to audio file.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        metadata.convert_file(file_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def convert_walk(tld_path, file_pattern):
    '''
    @brief Converts all audio files in specified top level directory to mp3 format.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to convert.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        metadata.convert_walk(tld_path, file_pattern)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def create_albums(tld_path):
    '''
    @brief Create album 2nd level directories under artist first level directories in top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        metadata.create_album_dirs(tld_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def get_media_info_walk(start_path, file_pattern):
    '''
    @brief Gets media info.

    @param file_path {str} The full path to audio file.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        metadata.get_media_info_walk(start_path, file_pattern)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def get_tags_walk(tld_path, file_pattern, ffprobe):
    '''
    @brief Gets metadata from  all audio files in specified top level directory with specified pattern.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to get tags for.
    @param ffprobe {bool} Get ffprobe tags instead of mutagen specific tags.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        metadata.get_tags_walk(tld_path, file_pattern, ffprobe)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def get_unique_media(tld_path):
    '''
    @brief Gets set of unique keys for entire collection found by ffprobe.

    @param tld_path {str} The top level directory path that contains all the music files.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        metadata.get_unique_media_keys(tld_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


'''
AudioNormalization functions
'''


def ebu_file(file_path):
    '''
    @brief EBU R128 normalize the specified audio file.

    @param file_path {str} The full path to audio file.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        normalization.ebu_normalize_file(file_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def normalize_walk(tld_path, norm_type):
    '''
    @brief Normalizes all audio files in specified top level directory per input normalization type.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param norm_type {str} The type of normalization to perform.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        normalization.normalize_walk(tld_path, norm_type)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def peak_file(file_path):
    '''
    @brief Peak normalize the specified audio file.

    @param file_path {str} The full path to audio file.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        normalization.peak_normalize_file(file_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def rms_file(file_path):
    '''
    @brief Peak normalize the specified audio file.

    @param file_path {str} The full path to audio file.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        normalization.rms_normalize_file(file_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


'''
AudioArt functions
'''


def extract_file(file_path):
    '''
    @brief Extracts and saves embedded album art from specified audio file.

    @param file_path {str} The full path to audio file.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        art.extract_album_art(file_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def extract_walk(tld_path, file_pattern):
    '''
    @brief Extracts and save embedded art from  all audio files in specified top level directory with specified pattern.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to delete.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        art.extract_walk(tld_path, file_pattern)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def set_album_art(tld_path):
    '''
    @brief Sets album art file for an album directory.

    @param tld_path {str} The top level directory path that contains all the music files.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        art.set_album_art(tld_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


'''
DirectoryProcessing functions
'''


def list_audio(tld_path):
    '''
    @brief List all audio files from specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        directory.get_audio_file_list(tld_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def list_type(tld_path, file_ext=None):
    '''
    @brief List files from specified top level directory by specified extension.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_ext {str} The specified extension to get list of.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        directory.get_ext_file_list(file_ext, tld_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def remove_albums(tld_path):
    '''
    @brief Remove empty album directories from specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        directory.remove_empty_album_dir(tld_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def remove_pattern(tld_path, file_pattern):
    '''
    @brief Remove files with specified pattern from specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to delete.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        directory.remove_pattern(tld_path, file_pattern)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


'''
AudioPlaylist functions
'''


def update_paths(tld_path, input_m3u):
    '''
    @brief Updates an old playlist relative pathing.

    @param start_path {str} The top level directory where playlist is located.
    @param input_m3u {str} The full file path to playlist needing conversion.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        playlist.update_paths(tld_path, input_m3u)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


def update_walk(tld_path):
    '''
    @brief Updates an old playlist relative pathing.

    @param start_path {str} The top level directory where playlists are located.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        playlist.update_walk(tld_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


'''
Main application functions
'''


@Gooey(program_name="Music Processing")
def arg_parser():
    '''
    @brief Parses and validates input arguments.

    @return args {argparse.Namespace} The parsed input arguments.

    @exception NotImplementedError A subcommand not implemented error.
    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        # parser = CustomArgumentParser(description='Music Processing')
        parser = GooeyParser(description=APP_NAME)
        subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

        # convert audio file specified to mp3 format
        # 1 mandatory arg, the audio file path
        # sys.argv = ['D:\MusicProcessing\main.py', 'convert-file', 'C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'convert-file', '/home/gerald/Music/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.m4a']
        convert_file_parser = subparsers.add_parser("convert-file", help="Converts an audio file to mp3")

        # convert_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        convert_file_parser.add_argument(
            ARG_CLI_FILE, type=existing_file, help=ARG_HELP_AUDIO, widget="FileChooser",
            gooey_options={
                "wildcard":
                    f"Audio files (*{M4A_EXT};*{MP3_EXT};*{WMA_EXT})|*{M4A_EXT};*{MP3_EXT};*{WMA_EXT}|"
                    f"M4A files (*{M4A_EXT})|*{M4A_EXT}|"
                    f"MP3 files (*{MP3_EXT})|*{MP3_EXT}|"
                    f"WMA files (*{WMA_EXT})|*{WMA_EXT}",
                    "default_dir": APP_PATH
            }
        )
        convert_file_parser.set_defaults(func=convert_file)

        # convert all audio files found in top level directory
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file pattern to match
        # sys.argv = ['D:\MusicProcessing\main.py', 'convert-walk', 'C:\Music', '--pattern', { '*.mp3' | '*.m4a' | '*.wma' } ]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'convert-walk', '/home/gerald/Music', '--pattern', { '*.mp3' | '*.m4a' | '*.wma' } ]
        convert_walk_parser = subparsers.add_parser("convert-walk", help="Converts all audio files to mp3")

        # convert_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        convert_walk_parser.add_argument(
            ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD, widget="DirChooser",
            gooey_options={
                "default_dir": APP_PATH
            }
        )

        # convert_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
        # not working!! see https://pakstech.com/blog/python-gooey/
        pattern_choices = ["*.m4a", "*.mp3", "*.wma"]
        convert_walk_parser.add_argument(
            ARG_CLI_PATTERN, type=str, help=ARG_HELP_PATTERN, widget="Dropdown", choices=pattern_choices
        )
        convert_walk_parser.set_defaults(func=convert_walk)

        # create album directories
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'create-album', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'create-album', '/home/gerald/Music']
        create_albums_parser = subparsers.add_parser("create-albums", help="Create album sub-directories")

        # create_albums_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        create_albums_parser.add_argument(
            ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD, widget="DirChooser",
            gooey_options={
                "default_dir": APP_PATH
            }
        )
        create_albums_parser.set_defaults(func=create_albums)

        # ebu normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'ebu-file', "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'ebu-file', "/home/gerald/ConvertedMusic/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.mp3"]
        ebu_file_parser = subparsers.add_parser("ebu-file", help="EBU R128 normalizes a mp3 audio file level")

        # ebu_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        ebu_file_parser.add_argument(
            ARG_CLI_FILE, type=existing_file, help=ARG_HELP_AUDIO, widget="FileChooser",
            gooey_options={
                "wildcard":
                    f"MP3 files (*{MP3_EXT})|*{MP3_EXT}",
                    "default_dir": APP_PATH
            }
        )
        ebu_file_parser.set_defaults(func=ebu_file)

        # extract album art from specified audio file
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'extract-art', 'C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma',
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'extract-art', '/home/gerald/Music/Elton John/Goodbye Yellow Brick Road/Elton John-Saturday Night's Alright for Fighting.wma',
        extract_file_parser = subparsers.add_parser("extract-file", help="Extracts embedded art from audio file")

        # extract_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        extract_file_parser.add_argument(
            ARG_CLI_FILE, type=existing_file, help=ARG_HELP_AUDIO, widget="FileChooser",
            gooey_options={
                "wildcard":
                    f"Audio files (*{M4A_EXT};*{MP3_EXT};*{WMA_EXT})|*{M4A_EXT};*{MP3_EXT};*{WMA_EXT}|"
                    f"M4A files (*{M4A_EXT})|*{M4A_EXT}|"
                    f"MP3 files (*{MP3_EXT})|*{MP3_EXT}|"
                    f"WMA files (*{WMA_EXT})|*{WMA_EXT}",
                    "default_dir": APP_PATH
            }
        )
        extract_file_parser.set_defaults(func=extract_file)

        # extract album art from all audio files found in top level directory
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file pattern to match
        # sys.argv = ['D:\MusicProcessing\main.py', 'extract-walk', 'C:\Music', '--pattern', { '*.mp3' | '*.m4a' | '*.wma' } ]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'extract-walk', '/home/gerald/Music', '--pattern', { '*.mp3' | '*.m4a' | '*.wma' } ]
        extract_walk_parser = subparsers.add_parser("extract-walk", help="Extracts embedded art from all audio files")

        # extract_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        extract_walk_parser.add_argument(
            ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD, widget="DirChooser",
            gooey_options={
                "default_dir": APP_PATH
            }
        )

        # extract_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
        extract_walk_parser.add_argument(ARG_CLI_PATTERN, type=str, help=ARG_HELP_PATTERN)
        # @todo needs to be a select 1 from list input restricted to { '*.mp3' | '*.m4a' | '*.wma' }
        # extract_walk_parser.add_argument(
        #     "--pattern", type=str, help="optional file pattern"

        # )
        extract_walk_parser.set_defaults(func=extract_walk)

        # get ffprobe media information for files
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file pattern to match
        # sys.argv = ['D:\MusicProcessing\main.py', 'get-media-info-walk', 'C:\Music', '--pattern', { '*.mp3' | '*.m4a' | '*.wma' | '*.*' } ]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'get-tags-walk', '/home/gerald/Music', '--pattern', { '*.mp3' | '*.m4a' | '*.wma' | *.* } ]
        get_media_info_walk_parser = subparsers.add_parser("get-media-info-walk", help="Gets ffprobe media info for audio files")
        # get_media_info_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        get_media_info_walk_parser.add_argument(
            ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD,

        )
        # get_media_info_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
        get_media_info_walk_parser.add_argument(
            ARG_CLI_PATTERN, type=str, help=ARG_HELP_PATTERN,

        )
        # @todo needs to be a select 1 from list input restricted to { '*.mp3' | '*.m4a' | '*.wma' }
        # extract_walk_parser.add_argument(
        #     "--pattern",
        #     type=str,
        #     help="optional file pattern"

        # )
        get_media_info_walk_parser.set_defaults(func=get_media_info_walk)

        # get metadata tags from all audio files found in top level directory
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file pattern to match
        # 1 optional arg, use ffprobe boolean
        # sys.argv = ['D:\MusicProcessing\main.py', 'get-tags-walk', 'C:\Music', '--pattern', { '*.mp3' | '*.m4a' | '*.wma' | '*.*' } , '--ffprobe' 'True']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'get-tags-walk', '/home/gerald/Music', '--pattern', { '*.mp3' | '*.m4a' | '*.wma' | *.* }, '--ffprobe', 'True']
        get_tags_walk_parser = subparsers.add_parser("get-tags-walk", help="Gets metadata tags from audio files")
        get_tags_walk_parser.add_argument(
            ARG_CLI_TLD, type=existing_path, help=ARG_HELP_AUDIO, widget="DirChooser",
            gooey_options={
                "default_dir": APP_PATH
            }
        )
        get_tags_walk_parser.add_argument(
            ARG_CLI_PATTERN, type=str, help=ARG_HELP_PATTERN,

        )
        get_tags_walk_parser.add_argument("--ffprobe", type=bool, help="optional ffprobe tags")
        get_tags_walk_parser.set_defaults(func=get_tags_walk)

        # gets set of unique ffprobe metadata tag keys for entire collection
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'get-unique-media', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'get-unique-media', '/home/gerald/Music']
        get_unique_media_parser = subparsers.add_parser("get-unique-media", help="Gets set of unique ffprobe tags from collection")
        get_unique_media_parser.add_argument(
            ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD,

        )
        get_unique_media_parser.set_defaults(func=get_unique_media)

        # list all audio files
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'list-audio', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'list-audio', '/home/gerald/Music']
        list_audio_parser = subparsers.add_parser("list-audio", help="Generates a csv containing full path for all audio files")
        list_audio_parser.add_argument(
            ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD,

        )
        list_audio_parser.set_defaults(func=list_audio)

        # list files by extension
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file extension
        # sys.argv = ['D:\MusicProcessing\main.py', 'list-type', 'C:\Music', '--ext', { 'mp3' | 'm4a' | 'wma' | 'abc' } ]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'list-type', '/home/gerald/Music', '--ext', { 'mp3' | 'm4a' | 'wma' | 'abc' } ]
        list_type_parser = subparsers.add_parser("list-type", help="Generates a csv containing full file path for an audio file type")
        list_type_parser.add_argument(
            ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD,

        )
        list_type_parser.add_argument("--ext", type=str, help='optional file extension')
        list_type_parser.set_defaults(func=list_type)

        # normalize mp3 files from tld
        # 2 mandatory arg, the tld path and the normalization type (ebu or peak)
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'normalize-walk', '/home/gerald/ConvertedMusic', { 'ebu' | 'peak' | 'rms' } ]
        normalize_walk_parser = subparsers.add_parser("normalize-walk", help="Normalizes files with specified pattern")
        normalize_walk_parser.add_argument(ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD)
        normalize_walk_parser.add_argument("type", type=str, help="mandatory normalization type")
        normalize_walk_parser.set_defaults(func=normalize_walk)

        # remove empty album directories
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'remove-album', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'remove-album', '/home/gerald/Music']
        remove_albums_parser = subparsers.add_parser("remove-albums", help="Remove empty album sub-directories")
        remove_albums_parser.add_argument(ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD)
        remove_albums_parser.set_defaults(func=remove_albums)

        # remove files matching specified file pattern
        # 2 mandatory args, the tld path and the file pattern
        # sys.argv = ['D:\MusicProcessing\main.py', 'remove-pattern', 'C:\Music', { 'AlbumArtSmall.jpg' | 'AlbumArt*Small.jpg' | '*.db' | '*.ini' } ]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'remove-pattern', '/home/gerald/Music', { 'AlbumArtSmall.jpg' | 'AlbumArt*Small.jpg' | '*.db' | '*.ini' } ]
        remove_pattern_parser = subparsers.add_parser("remove-pattern", help="Removes files with specified pattern")
        remove_pattern_parser.add_argument(ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD)
        remove_pattern_parser.add_argument("pattern", type=str, help="mandatory file pattern")
        remove_pattern_parser.set_defaults(func=remove_pattern)

        # peak normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'peak-file', "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'peak-file', "/home/gerald/ConvertedMusic/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.mp3"]
        peak_file_parser = subparsers.add_parser("peak-file", help="Peak normalizes a mp3 audio file level")
        peak_file_parser.add_argument("file", type=existing_file, help=ARG_HELP_AUDIO)
        peak_file_parser.set_defaults(func=peak_file)

        # rms normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'rms-file', "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'rms-file', "/home/gerald/ConvertedMusic/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.mp3"]
        rms_file_parser = subparsers.add_parser("rms-file", help="Rms normalizes a mp3 audio file level")
        rms_file_parser.add_argument("file", type=existing_file, help=ARG_HELP_AUDIO)
        rms_file_parser.set_defaults(func=rms_file)

        # set album art file
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'set-art', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'set-art', '/home/gerald/Music']
        set_album_art_parser = subparsers.add_parser("set-album-art", help="Set album art file")
        set_album_art_parser.add_argument(ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD)
        set_album_art_parser.set_defaults(func=set_album_art)

        # update m3u playlist
        # 2 mandatory args, the tld path and the m3u path
        # update-m3u D:\MusicProcessing\tests\Music D:\MusicProcessing\tests\Music\test.m3u
        # sys.argv = ['D:\MusicProcessing\main.py'', 'update-m3u', 'D:\MusicProcessing\tests\Music', 'D:\MusicProcessing\tests/Music\test.m3u']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'update-m3u', '~/MusicProcessing/tests/Music', '~/MusicProcessing/tests/Music/test.m3u']
        update_m3u_parsers = subparsers.add_parser("update-m3u", help="Update playlist paths")
        update_m3u_parsers.add_argument(ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD)
        update_m3u_parsers.add_argument("m3u", type=existing_file, help="mandatory m3u file path")
        update_m3u_parsers.set_defaults(func=update_paths)

        # update m3u playlist walk
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py'', 'update-walk', 'D:\MusicProcessing\tests\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'update-walk', '~/MusicProcessing/tests/Music']
        update_walk_parsers = subparsers.add_parser("update-walk", help="Update playlist paths")
        update_walk_parsers.add_argument(ARG_CLI_TLD, type=existing_path, help=ARG_HELP_TLD)
        update_walk_parsers.set_defaults(func=update_walk)

        args = parser.parse_args()

    except NotImplementedError as ni_e:
        logger.exception(f"NotImplementedError: {type(ni_e).__name__}: {ni_e}", stack_info=True)
        raise ni_e
    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e
    else:
        return args


def existing_file(file):
    '''
    @brief Checks if file exists.

    @param file {str} The file path.
    @return file {str} The file path.

    @exception ArgumentTypeError indicating the file was not found.
    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        if not os.path.isfile(file):
            raise argparse.ArgumentTypeError(f"File not found: {file}")

    except argparse.ArgumentTypeError as at_e:
        raise at_e
    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e
    else:
        return file


def existing_path(path):
    '''
    @brief Checks if directory exists.

    @param file {str} The directory path.
    @return file {str} The directory path.

    @exception ArgumentTypeError indicating the directory was not found.
    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        if not os.path.isdir(path):
            raise argparse.ArgumentTypeError(f"Directory not found: {path}")

    except argparse.ArgumentTypeError as at_e:
        raise at_e
    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e
    else:
        return path


def main(args):
    '''
    @brief Module entry point.

    @details Takes command line arguments and executes per arguments.

    @param args {argparse.Namespace} Arguments for execution.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        if args.subcommand == "convert-file":
            file_path = getattr(args, "file")
            convert_file(file_path)

        if args.subcommand == "convert-walk":
            tld_path = getattr(args, ARG_CLI_TLD)
            file_pattern = getattr(args, "pattern")
            convert_walk(tld_path, file_pattern)

        if args.subcommand == "create-albums":
            tld_path = getattr(args, ARG_CLI_TLD)
            create_albums(tld_path)

        if args.subcommand == "ebu-file":
            file_path = getattr(args, "file")
            ebu_file(file_path)

        if args.subcommand == "extract-file":
            file_path = getattr(args, "file")
            extract_file(file_path)

        if args.subcommand == "extract-walk":
            tld_path = getattr(args, ARG_CLI_TLD)
            file_pattern = getattr(args, "pattern")
            extract_walk(tld_path, file_pattern)

        if args.subcommand == "get-media-info-walk":
            tld_path = getattr(args, ARG_CLI_TLD)
            file_pattern = getattr(args, "pattern")
            get_media_info_walk(tld_path, file_pattern)

        if args.subcommand == "get-tags-walk":
            tld_path = getattr(args, ARG_CLI_TLD)
            file_pattern = getattr(args, "pattern")
            ffprobe = getattr(args, "ffprobe")
            get_tags_walk(tld_path, file_pattern, ffprobe)

        if args.subcommand == "get-unique-media":
            tld_path = getattr(args, ARG_CLI_TLD)
            get_unique_media(tld_path)

        if args.subcommand == "list-audio":
            tld_path = getattr(args, ARG_CLI_TLD)
            list_audio(tld_path)

        if args.subcommand == "list-type":
            tld_path = getattr(args, ARG_CLI_TLD)
            file_ext = getattr(args, "ext")
            list_type(tld_path, file_ext)

        if args.subcommand == "normalize-walk":
            tld_path = getattr(args, ARG_CLI_TLD)
            norm_type = getattr(args, "type")
            normalize_walk(tld_path, norm_type)

        if args.subcommand == "peak-file":
            file_path = getattr(args, "file")
            peak_file(file_path)

        if args.subcommand == "rms-file":
            file_path = getattr(args, "file")
            rms_file(file_path)

        if args.subcommand == "remove-albums":
            tld_path = getattr(args, ARG_CLI_TLD)
            remove_albums(tld_path)

        if args.subcommand == "remove-pattern":
            tld_path = getattr(args, ARG_CLI_TLD)
            file_pattern = getattr(args, "pattern")
            remove_pattern(tld_path, file_pattern)

        if args.subcommand == "set-album-art":
            tld_path = getattr(args, ARG_CLI_TLD)
            set_album_art(tld_path)

        if args.subcommand == "update-m3u":
            tld_path = getattr(args, ARG_CLI_TLD)
            input_m3u = getattr(args, "m3u")
            update_paths(tld_path, input_m3u)

        if args.subcommand == "update-walk":
            tld_path = getattr(args, ARG_CLI_TLD)
            update_walk(tld_path)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
        raise e


if __name__ == "__main__":
    '''
    @brief Top level script environment entry point.

    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        args = arg_parser()
        main(args)

    except Exception as e:
        logger.exception(f"Exception: {type(e).__name__}: {e}", stack_info=True)
