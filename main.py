#!/usr/bin/env python3
'''
@file main.py
@author Gerald Manweiler

@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import argparse                                             # argument parsing module
import gc                                                   # garbage collection module
import logging                                              # logging module
import os                                                   # operating system module
import pprint                                               # pretty-print module
import sys                                                  # system-specific parameters and functions module

# Local Module Constants
from src import ERROR_LOG_FORMAT                            # error log format
from src import LOG_DIR                                     # log directory
from src import LOG_EXT                                     # log file extension
from src import UTF8                                        # utf encoding for file writing
from src.generated_files import GENERATED_PATH              # generated files path

# Local Module Classes
from src.audio_info import AudioArt                         # audio art handling class
from src.audio_info import AudioMetadata                    # audio metadata handling class
from src.audio_info import AudioPlaylist                    # audio playlist handling class
from src.audio_normalize import AudioNormalization          # audio normalization handling class
from src.dir_processing import DirectoryProcessing          # directory processing handling class

gc.enable()

# Configure logging
## @var basename
# @brief Module file base name.
# @details Gets the current module file name for constructing the log file name.
basename = os.path.basename(__file__)

## @var stem
# @brief Module file stem.
# @details Removes the extension from the module file base name.
stem = os.path.splitext(basename)[0]

## @var file
# @brief Module log file name.
# @details Appends the configured log extension to the module file stem.
file = stem + LOG_EXT

## @var log_filename
# @brief Module log file path.
# @details Joins the generated-files path, log directory, and module log file name.
log_filename = os.path.join(GENERATED_PATH, LOG_DIR, file)

# override the default logging level WARN to lowest level so we can log all levels
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=ERROR_LOG_FORMAT, filemode="a", encoding=UTF8)

## @var logger
# @brief Module logger.
# @details Records application events using the module name.
logger = logging.getLogger(__name__)

## @var art
# @brief AudioArt handling instance.
# @details Provides audio art handling functionality.
art = AudioArt()

## @var directory
# @brief Directory processing instance.
# @details Provides directory processing functionality.
directory = DirectoryProcessing()

## @var metadata
# @brief Audio metadata handling instance.
# @details Provides audio metadata handling functionality.
metadata = AudioMetadata()

## @var normalization
# @brief Audio normalization instance.
# @details Provides audio normalization functionality.
normalization = AudioNormalization()

## @var playlist
# @brief Audio playlist handling instance.
# @details Provides audio playlist handling functionality.
playlist = AudioPlaylist()


class CustomArgumentParser(argparse.ArgumentParser):
    '''
    @brief Custom argument parser so argparse errors can be logged.

    @details Logs argparse error messages that would otherwise be written to standard error.
    '''


    def _print_message(self, message, file=None):
        '''
        @brief Override argparse.ArgumentParser._print_message so stderr gets logged instead of output to console.

        @details Logs standard-error messages while preserving default handling for all other output.

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


def convert_file(file_path):
    '''
    @brief Converts specified audio file to mp3 format.

    @details Converts the specified audio file to mp3 format using the metadata conversion functionality.

    @param file_path {str} The full path to audio file.
    '''

    metadata.convert_file(file_path)


def convert_walk(tld_path, file_pattern):
    '''
    @brief Converts all audio files in specified top level directory to mp3 format.

    @details Converts all audio files matching the specified file pattern in the top level directory to mp3 format.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to convert.
    '''

    metadata.convert_walk(tld_path, file_pattern)


def create_albums(tld_path):
    '''
    @brief Create album 2nd level directories under artist first level directories in top level directory.

    @details Creates album directories under first-level artist directories in the specified top-level directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    metadata.create_album_dirs(tld_path)


def ebu_file(file_path):
    '''
    @brief EBU R128 normalize the specified audio file.

    @details Normalizes the audio file to the EBU R128 loudness standard.

    @param file_path {str} The full path to audio file.
    '''

    normalization.ebu_normalize_file(file_path)


def existing_file(file):
    '''
    @brief Checks if file exists.

    @details Checks if the specified file exists and raises an ArgumentTypeError if it does not.

    @param file {str} The file path.
    @return file {str} The file path.

    @exception {ArgumentTypeError} Indicates the file was not found.
    '''

    if not os.path.isfile(file):
        raise argparse.ArgumentTypeError(f"File not found: {file}")

    return file


def existing_path(path):
    '''
    @brief Checks if directory exists.

    @details Checks if the specified directory exists and raises an ArgumentTypeError if it does not.

    @param path {str} The directory path.
    @return path {str} The directory path.

    @exception {ArgumentTypeError} Indicates the directory was not found.
    '''

    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Directory not found: {path}")

    return path


def extract_file(file_path):
    '''
    @brief Extracts and saves embedded album art from specified audio file.

    @details Extracts and saves the embedded album art from the specified audio file.

    @param file_path {str} The full path to audio file.
    '''

    art.extract_album_art(file_path)


def extract_walk(tld_path, file_pattern):
    '''
    @brief Extracts and saves embedded album art from all audio files in specified top level directory with specified pattern.

    @details Extracts and saves the embedded album art from all audio files in the specified top level directory that match the given file pattern.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to extract album art from.
    '''

    art.extract_walk(tld_path, file_pattern)


def get_ffprobe_media_info(file_path):
    '''
    @brief Gets media info.

    @details Retrieves detailed media information for the specified audio file.

    @param file_path {str} The full path to audio file.
    '''

    metadata.get_ffprobe_media_info(file_path)


def get_ffprobe_media_info_walk(start_path, file_pattern):
    '''
    @brief Gets media info.

    @details Retrieves detailed media information for all audio files in the specified top level directory that match the given file pattern.

    @param start_path {str} The full path to the top level directory containing audio files.
    @param file_pattern {str} The file pattern we want to get media info for.
    '''

    metadata.get_ffprobe_media_info_walk(start_path, file_pattern)


def get_ffprobe_media_tags(file_path):
    '''
    @brief Gets media tags.

    @details Retrieves the metadata tags for the specified audio file.

    @param file_path {str} The full path to audio file.
    '''

    metadata.get_ffprobe_media_tags(file_path)


def get_mutagen_tags(file_path):
    '''
    @brief Gets metadata from specified audio file.

    @details Retrieves all available metadata tags from the specified audio file.

    @param file_path {str} The full path to audio file.
    @return tags {mutagen.FileType} The metadata tags retrieved from the audio file.
    '''

    tags = metadata.get_mutagen_tags(file_path)
    return tags


def get_tags_walk(tld_path, file_pattern, ffprobe):
    '''
    @brief Gets metadata from all audio files in specified top level directory with specified pattern.

    @details Retrieves all available metadata tags from all audio files in the specified top level directory that match the given file pattern.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to get tags for.
    @param ffprobe {bool} Get ffprobe tags instead of mutagen specific tags.
    '''

    metadata.get_tags_walk(tld_path, file_pattern, ffprobe)


def get_unique_media(tld_path):
    '''
    @brief Gets set of unique keys for entire collection found by ffprobe.

    @details Retrieves a set of unique metadata keys from all audio files in the specified top level directory using ffprobe.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    metadata.get_unique_media_keys(tld_path)


def level_normalize_walk(tld_path, norm_type):
    '''
    @brief Normalizes all audio files in specified top level directory per input normalization type.

    @details Normalizes all audio files in the specified top level directory according to the specified normalization type.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param norm_type {str} The type of normalization to perform.
    '''

    normalization.level_normalize_walk(tld_path, norm_type)


def list_audio(tld_path):
    '''
    @brief List all audio files from specified top level directory.

    @details Retrieves a list of all audio files from the specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    directory.get_audio_file_list(tld_path)


def list_type(tld_path, file_ext=None):
    '''
    @brief List files from specified top level directory by specified extension.

    @details Retrieves a list of all files with the specified extension from the specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_ext {str} The specified extension to get list of.
    '''

    directory.get_ext_file_list(tld_path, file_ext)


def normalize_flac_filename(file_path):
    '''
    @brief Renames a FLAC using its album artist and title metadata.

    @details Renames the specified FLAC file using its album artist and title metadata.

    @param file_path {str} The full path to the FLAC file.
    '''

    metadata.normalize_flac_filename(file_path)


def normalize_mp3_filename(file_path):
    '''
    @brief Renames an MP3 using its album artist and title metadata.

    @details Renames the specified MP3 file using its album artist and title metadata.

    @param file_path {str} The full path to the MP3 file.
    '''

    metadata.normalize_mp3_filename(file_path)


def normalize_mp4_filename(file_path):
    '''
    @brief Renames an M4A using its album artist and title metadata.

    @details Renames the specified M4A file using its album artist and title metadata.

    @param file_path {str} The full path to the M4A file.
    '''

    metadata.normalize_mp4_filename(file_path)


def normalize_wma_filename(file_path):
    '''
    @brief Renames a WMA using its album artist and title metadata.

    @details Renames the specified WMA file using its album artist and title metadata.

    @param file_path {str} The full path to the WMA file.
    '''

    metadata.normalize_wma_filename(file_path)


def normalize_flac_filename_walk(tld_path):
    '''
    @brief Renames FLAC files in specified top level directory using album artist and title metadata.

    @details Renames all FLAC files in the specified top level directory using their album artist and title metadata.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    metadata.normalize_flac_filename_walk(tld_path)


def normalize_mp3_filename_walk(tld_path):
    '''
    @brief Renames MP3 files in specified top level directory using album artist and title metadata.

    @details Renames all MP3 files in the specified top level directory using their album artist and title metadata.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    metadata.normalize_mp3_filename_walk(tld_path)


def normalize_mp4_filename_walk(tld_path):
    '''
    @brief Renames M4A files in specified top level directory using album artist and title metadata.

    @details Renames all M4A files in the specified top level directory using their album artist and title metadata.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    metadata.normalize_mp4_filename_walk(tld_path)


def normalize_wma_filename_walk(tld_path):
    '''
    @brief Renames WMA files in specified top level directory using album artist and title metadata.

    @details Renames all WMA files in the specified top level directory using their album artist and title metadata.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    metadata.normalize_wma_filename_walk(tld_path)


def peak_file(file_path):
    '''
    @brief Peak normalize the specified audio file.

    @details Peak normalizes the specified audio file.

    @param file_path {str} The full path to audio file.
    '''

    normalization.peak_normalize_file(file_path)


def rms_file(file_path):
    '''
    @brief RMS normalize the specified audio file.

    @details RMS normalizes the specified audio file.

    @param file_path {str} The full path to audio file.
    '''

    normalization.rms_normalize_file(file_path)


def remove_albums(tld_path):
    '''
    @brief Remove empty album directories from specified top level directory.

    @details Recursively scans the specified top level directory and removes any empty album directories.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    directory.remove_empty_album_dir(tld_path)


def remove_pattern(tld_path, file_pattern):
    '''
    @brief Remove files with specified pattern from specified top level directory.

    @details Recursively scans the specified top level directory and removes any files that match the given pattern.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to delete.
    '''

    directory.remove_pattern(tld_path, file_pattern)


def set_album_art(tld_path):
    '''
    @brief Sets album art file for an album directory.

    @details Sets the album art for all album directories within the specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    art.set_album_art(tld_path)


def update_paths(tld_path, input_m3u):
    '''
    @brief Updates an old playlist relative pathing.

    @details Updates the relative paths in the specified playlist file based on the current top level directory structure.

    @param tld_path {str} The top level directory where playlist is located.
    @param input_m3u {str} The full file path to playlist needing conversion.
    '''

    playlist.update_paths(tld_path, input_m3u)


def update_walk(tld_path):
    '''
    @brief Updates an old playlist relative pathing.

    @details Updates the relative paths in all playlist files within the specified top level directory based on the current directory structure.

    @param tld_path {str} The top level directory where playlists are located.
    '''

    playlist.update_walk(tld_path)


def main(args):
    '''
    @brief Module entry point.

    @details Takes command line arguments and executes per arguments.

    @param args {argparse.Namespace} Arguments for execution.

    @exception {NotImplementedError} Indicates a subcommand has not been implemented.
    @exception {Exception} Handles unforeseen errors.
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

        if args.subcommand == "ebu-file":
            file_path = getattr(args, "file")
            ebu_file(file_path)

        if args.subcommand == "extract-file":
            file_path = getattr(args, "file")
            extract_file(file_path)

        if args.subcommand == "extract-walk":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            extract_walk(tld_path, file_pattern)

        if args.subcommand == "get-ffprobe-media-info":
            file_path = getattr(args, "file")
            get_ffprobe_media_info(file_path)

        if args.subcommand == "get-ffprobe-media-info-walk":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            get_ffprobe_media_info_walk(tld_path, file_pattern)

        if args.subcommand == "get-ffprobe-media-tags":
            file_path = getattr(args, "file")
            get_ffprobe_media_tags(file_path)

        if args.subcommand == "get-mutagen-tags":
            file_path = getattr(args, "file")
            tags = get_mutagen_tags(file_path)
            # mutagen returns tags as ASFTags, ID3Tags, MP4Tags objects
            # not as a simple dict of string key/value
            # so need mutagen pprint and splitlines to "format" into simple dict
            pprint.pprint(tags.pprint().splitlines())

        if args.subcommand == "get-tags-walk":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            ffprobe = getattr(args, "ffprobe")
            get_tags_walk(tld_path, file_pattern, ffprobe)

        if args.subcommand == "get-unique-media":
            tld_path = getattr(args, "tld")
            get_unique_media(tld_path)

        if args.subcommand == "level-normalize-walk":
            tld_path = getattr(args, "tld")
            norm_type = getattr(args, "type")
            level_normalize_walk(tld_path, norm_type)

        if args.subcommand == "list-audio":
            tld_path = getattr(args, "tld")
            list_audio(tld_path)

        if args.subcommand == "list-type":
            tld_path = getattr(args, "tld")
            file_ext = getattr(args, "ext")
            list_type(tld_path, file_ext)

        if args.subcommand == "normalize-mp3-filename":
            file_path = getattr(args, "file")
            normalize_mp3_filename(file_path)

        if args.subcommand == "normalize-flac-filename":
            file_path = getattr(args, "file")
            normalize_flac_filename(file_path)

        if args.subcommand == "normalize-mp4-filename":
            file_path = getattr(args, "file")
            normalize_mp4_filename(file_path)

        if args.subcommand == "normalize-wma-filename":
            file_path = getattr(args, "file")
            normalize_wma_filename(file_path)

        if args.subcommand == "normalize-flac-filename-walk":
            tld_path = getattr(args, "tld")
            normalize_flac_filename_walk(tld_path)

        if args.subcommand == "normalize-mp3-filename-walk":
            tld_path = getattr(args, "tld")
            normalize_mp3_filename_walk(tld_path)

        if args.subcommand == "normalize-mp4-filename-walk":
            tld_path = getattr(args, "tld")
            normalize_mp4_filename_walk(tld_path)

        if args.subcommand == "normalize-wma-filename-walk":
            tld_path = getattr(args, "tld")
            normalize_wma_filename_walk(tld_path)

        if args.subcommand == "peak-file":
            file_path = getattr(args, "file")
            peak_file(file_path)

        if args.subcommand == "rms-file":
            file_path = getattr(args, "file")
            rms_file(file_path)

        if args.subcommand == "remove-albums":
            tld_path = getattr(args, "tld")
            remove_albums(tld_path)

        if args.subcommand == "remove-pattern":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            remove_pattern(tld_path, file_pattern)

        if args.subcommand == "set-album-art":
            tld_path = getattr(args, "tld")
            set_album_art(tld_path)

        if args.subcommand == "update-m3u":
            tld_path = getattr(args, "tld")
            input_m3u = getattr(args, "m3u")
            update_paths(tld_path, input_m3u)

        if args.subcommand == "update-walk":
            tld_path = getattr(args, "tld")
            update_walk(tld_path)

    except Exception as e:
        logger.exception(f"Exception propagated to main: {type(e).__name__}: {e}", stack_info=True)


if __name__ == "__main__":
    '''
    @brief Top level script environment entry point.

    @details Sets up argument parsing and subcommand handling.

    @note Any input file paths that contain spaces must be enclosed in quotes.

    @exception {Exception} Handles unforeseen errors.
    '''

    try:
        parser = CustomArgumentParser(description='Music Processing')
        subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

        # convert audio file specified to mp3 format
        # 1 mandatory arg, the audio file path
        # sys.argv = ['D:\MusicProcessing\main.py', 'convert-file',
        # 'C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'convert-file',
        # '/home/gerald/Music/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.m4a']
        # convert-file "C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a"
        convert_file_parser = subparsers.add_parser("convert-file", help="Converts an audio file to mp3")
        convert_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        convert_file_parser.set_defaults(func=convert_file)

        # convert all audio files found in top level directory
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file pattern to match
        # sys.argv = ['D:\MusicProcessing\main.py', 'convert-walk', 'C:\Music', '--pattern', { '.flac' | '.mp3' | '.m4a' | '.wma' } ]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'convert-walk', '/home/gerald/Music',
        # '--pattern', { '.flac' | '.mp3' | '.m4a' | '.wma' } ]
        # convert-walk C:\Music --pattern .m4a
        # convert-walk F:\RickPrepped
        convert_walk_parser = subparsers.add_parser("convert-walk", help="Converts all audio files to mp3")
        convert_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        convert_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
        convert_walk_parser.set_defaults(func=convert_walk)

        # create album directories
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'create-album', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'create-album', '/home/gerald/Music']
        # create-albums C:\Music
        create_albums_parser = subparsers.add_parser("create-albums", help="Create album sub-directories")
        create_albums_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        create_albums_parser.set_defaults(func=create_albums)

        # ebu normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'ebu-file',
        # "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'ebu-file',
        # "/home/gerald/ConvertedMusic/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.mp3"]
        # ebu-file "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"
        ebu_file_parser = subparsers.add_parser("ebu-file", help="EBU R128 normalizes a mp3 audio file level")
        ebu_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        ebu_file_parser.set_defaults(func=ebu_file)

        # extract album art from specified audio file
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'extract-art',
        # 'C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'extract-art',
        # '/home/gerald/Music/Elton John/Goodbye Yellow Brick Road/Elton John-Saturday Night's Alright for Fighting.wma']
        # extract-file "C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"
        extract_file_parser = subparsers.add_parser("extract-file", help="Extracts embedded art from audio file")
        extract_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        extract_file_parser.set_defaults(func=extract_file)

        # extract album art from all audio files found in top level directory
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file pattern to match
        # sys.argv = ['D:\MusicProcessing\main.py', 'extract-walk', 'C:\Music', '--pattern', { '.flac' | '.mp3' | '.m4a' | '.wma' } ]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'extract-walk', '/home/gerald/Music',
        # '--pattern', { '.flac' | '.mp3' | '.m4a' | '.wma' } ]
        # extract-walk C:\Music --pattern .flac
        # extract-walk C:\Music --pattern .mp3
        # extract-walk C:\Music --pattern .m4a
        # extract-walk C:\Music --pattern .wma
        # extract-walk C:\Music
        extract_walk_parser = subparsers.add_parser("extract-walk", help="Extracts embedded art from all audio files")
        extract_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        extract_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
        extract_walk_parser.set_defaults(func=extract_walk)

        # get ffprobe media information for a file
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'get-ffprobe-media-info',
        # 'C:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'get-ffprobe-media-info',
        # '/home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a']
        # get-ffprobe-media-info "C:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a"
        # get-ffprobe-media-info D:\MusicProcessing\tests\Music\Cream\Goodbye\Cream-Goodbye.flac
        get_ffprobe_media_info_parser = subparsers.add_parser(
            "get-ffprobe-media-info", help="Gets ffprobe media info for audio file"
        )
        get_ffprobe_media_info_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        get_ffprobe_media_info_parser.set_defaults(func=get_ffprobe_media_info)

        # get ffprobe media information for files
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file pattern to match
        # sys.argv = ['D:\MusicProcessing\main.py', 'get-ffprobe-media-info-walk', 'C:\Music', '--pattern', { '.flac' | `'.mp3' | '.m4a' | '.wma' } ]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'get-ffprobe-media-info-walk', '/home/gerald/Music',
        # '--pattern', {  '.flac' | '.mp3' | '.m4a' | '.wma' } ]
        # get-ffprobe-media-info-walk C:\Music --pattern .mp3
        # get-ffprobe-media-info-walk C:\Music --pattern .m4a
        # get-ffprobe-media-info-walk C:\Music --pattern .wma
        # get-ffprobe-media-info-walk C:\Music --pattern .flac
        # get-ffprobe-media-info-walk C:\Music
        get_ffprobe_media_info_walk_parser = subparsers.add_parser(
            "get-ffprobe-media-info-walk", help="Gets ffprobe media info for audio files"
        )
        get_ffprobe_media_info_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        get_ffprobe_media_info_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
        get_ffprobe_media_info_walk_parser.set_defaults(func=get_ffprobe_media_info_walk)

        # get ffprobe media tags for a file or files
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'get-ffprobe-media-tags',
        # 'C:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'get-ffprobe-media-tags',
        # '/home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a']
        # get-ffprobe-media-tags "C:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a"
        get_ffprobe_media_tags_parser = subparsers.add_parser("get-ffprobe-media-tags", help="Gets ffprobe media tags for audio file")
        get_ffprobe_media_tags_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        get_ffprobe_media_tags_parser.set_defaults(func=get_ffprobe_media_tags)

        # get mutagen metadata tags for file
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'get-mutagen-tags', 'C:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'get-mutagen-tags', '/home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a']
        # get-mutagen-tags F:\RickPrepped\Cream\Goodbye\Cream-Badge.flac
        get_mutagen_tags_parser = subparsers.add_parser("get-mutagen-tags", help="Gets metadata tags from audio file")
        get_mutagen_tags_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        get_mutagen_tags_parser.set_defaults(func=get_mutagen_tags)

        # get metadata tags from all audio files found in top level directory
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file pattern to match
        # 1 optional arg, use ffprobe boolean
        # sys.argv = ['D:\MusicProcessing\main.py', 'get-tags-walk', 'C:\Music', '--pattern',
        # { '.mp3' | '.m4a' | '.wma' | '.flac' }, '--ffprobe', 'True']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'get-tags-walk', '/home/gerald/Music',
        # '--pattern', { '.mp3' | '.m4a' | '.wma' | '.flac' }, '--ffprobe', 'True']
        # get-tags-walk C:\Music --pattern .mp3 --ffprobe True
        # get-tags-walk C:\Music --pattern .m4a --ffprobe True
        # get-tags-walk C:\Music --pattern .wma --ffprobe True
        # get-tags-walk C:\Music --pattern .flac --ffprobe True
        # @todo need to test this
        # get-tags-walk C:\Music --ffprobe True
        get_tags_walk_parser = subparsers.add_parser("get-tags-walk", help="Gets metadata tags from audio files")
        get_tags_walk_parser.add_argument("tld", type=existing_path, help="mandatory full path to audio file")
        get_tags_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
        get_tags_walk_parser.add_argument("--ffprobe", type=bool, help="optional ffprobe tags")
        get_tags_walk_parser.set_defaults(func=get_tags_walk)

        # gets set of unique ffprobe metadata tag keys for entire collection
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'get-unique-media', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'get-unique-media', '/home/gerald/Music']
        # get-unique-media C:\Music
        get_unique_media_parser = subparsers.add_parser("get-unique-media", help="Gets set of unique ffprobe tags from collection")
        get_unique_media_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        get_unique_media_parser.set_defaults(func=get_unique_media)

        # level normalize mp3 files from tld
        # 2 mandatory arg, the tld path and the normalization type (ebu or peak)
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'level-normalize-walk', '/home/gerald/ConvertedMusic', { 'ebu' | 'peak' | 'rms' } ]
        # level-normalize-walk C:\Music ebu
        # level-normalize-walk C:\Music peak
        # level-normalize-walk C:\Music rms
        level_normalize_walk_parser = subparsers.add_parser("level-normalize-walk", help="Normalizes files with specified pattern")
        level_normalize_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        level_normalize_walk_parser.add_argument("type", type=str, help="mandatory normalization type")
        level_normalize_walk_parser.set_defaults(func=level_normalize_walk)

        # list all audio files
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'list-audio', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'list-audio', '/home/gerald/Music']
        # list-audio C:\Music
        list_audio_parser = subparsers.add_parser("list-audio", help="Generates a csv containing full path for all audio files")
        list_audio_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        list_audio_parser.set_defaults(func=list_audio)

        # list files by extension
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file extension
        # sys.argv = ['D:\MusicProcessing\main.py', 'list-type', 'C:\Music', '--ext', { '.flac' | '.mp3' | '.m4a' | '.wma' } ]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'list-type', '/home/gerald/Music', '--ext', { '.flac' | '.mp3' | '.m4a' | '.wma' } ]
        # list-type C:\Music --ext .flac
        # list-type C:\Music --ext .mp3
        # list-type C:\Music --ext .m4a
        # list-type C:\Music --ext .wma
        # list-type C:\Music
        list_type_parser = subparsers.add_parser(
            "list-type", help="Generates a csv containing full file path for an audio file type"
        )
        list_type_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        list_type_parser.add_argument("--ext", type=str, help='optional file extension')
        list_type_parser.set_defaults(func=list_type)

        # normalize a FLAC filename from its metadata
        # 1 mandatory arg, the audio file path
        # sys.argv = ['D:\\MusicProcessing\\main.py', 'normalize-flac-filename', 'C:\\Music\\song.flac']
        # normalize-flac-filename C:\Music\song.flac
        normalize_flac_filename_parser = subparsers.add_parser("normalize-flac-filename", help="Renames a FLAC from its metadata")
        normalize_flac_filename_parser.add_argument("file", type=existing_file, help="mandatory full path to FLAC file")
        normalize_flac_filename_parser.set_defaults(func=normalize_flac_filename)

        # normalize an mp3 filename from its metadata
        # 1 mandatory arg, the audio file path
        # sys.argv = ['D:\\MusicProcessing\\main.py', 'normalize-mp3-filename', 'C:\\Music\\song.mp3']
        # normalize-mp3-filename "C:\Music\song.mp3"
        normalize_mp3_filename_parser = subparsers.add_parser("normalize-mp3-filename", help="Renames an MP3 from its metadata")
        normalize_mp3_filename_parser.add_argument("file", type=existing_file, help="mandatory full path to MP3 file")
        normalize_mp3_filename_parser.set_defaults(func=normalize_mp3_filename)

        # normalize an M4A filename from its metadata
        # 1 mandatory arg, the audio file path
        # sys.argv = ['D:\\MusicProcessing\\main.py', 'normalize-mp4-filename', 'C:\\Music\\song.m4a']
        # normalize-mp4-filename C:\Music\song.m4a
        normalize_mp4_filename_parser = subparsers.add_parser("normalize-mp4-filename", help="Renames an M4A from its metadata")
        normalize_mp4_filename_parser.add_argument("file", type=existing_file, help="mandatory full path to M4A file")
        normalize_mp4_filename_parser.set_defaults(func=normalize_mp4_filename)

        # normalize an WMA filename from its metadata
        # 1 mandatory arg, the audio file path
        # sys.argv = ['D:\\MusicProcessing\\main.py', 'normalize-wma-filename', 'C:\\Music\\song.wma']
        # normalize-wma-filename C:\Music\song.wma
        normalize_wma_filename_parser = subparsers.add_parser("normalize-wma-filename", help="Renames a WMA from its metadata")
        normalize_wma_filename_parser.add_argument("file", type=existing_file, help="mandatory full path to WMA file")
        normalize_wma_filename_parser.set_defaults(func=normalize_wma_filename)

        # normalize FLAC filenames from metadata for files in top level directory
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'normalize-flac-filename-walk', 'C:\Music']
        # normalize-flac-filename-walk F:\RickPrepped
        normalize_flac_filename_walk_parser = subparsers.add_parser("normalize-flac-filename-walk", help="Renames FLAC files from metadata")
        normalize_flac_filename_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        normalize_flac_filename_walk_parser.set_defaults(func=normalize_flac_filename_walk)

        # normalize mp3 filenames from metadata for files in top level directory
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'normalize-mp3-filename-walk', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'normalize-mp3-filename-walk', '/home/gerald/Music']
        # normalize-mp3-filename-walk F:\RickPrepped
        normalize_mp3_filename_walk_parser = subparsers.add_parser("normalize-mp3-filename-walk", help="Renames MP3 files from metadata")
        normalize_mp3_filename_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        normalize_mp3_filename_walk_parser.set_defaults(func=normalize_mp3_filename_walk)

        # normalize M4A filenames from metadata for files in top level directory
        # 1 mandatory arg, the tld path
        # normalize-mp4-filename-walk F:\RickPrepped
        normalize_mp4_filename_walk_parser = subparsers.add_parser("normalize-mp4-filename-walk", help="Renames M4A files from metadata")
        normalize_mp4_filename_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        normalize_mp4_filename_walk_parser.set_defaults(func=normalize_mp4_filename_walk)

        # normalize WMA filenames from metadata for files in top level directory
        # 1 mandatory arg, the tld path
        # normalize-wma-filename-walk F:\RickPrepped
        # normalize-wma-filename-walk C:\Music
        normalize_wma_filename_walk_parser = subparsers.add_parser("normalize-wma-filename-walk", help="Renames WMA files from metadata")
        normalize_wma_filename_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        normalize_wma_filename_walk_parser.set_defaults(func=normalize_wma_filename_walk)

        # remove empty album directories
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'remove-album', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'remove-album', '/home/gerald/Music']
        # remove-albums C:\Music
        remove_albums_parser = subparsers.add_parser("remove-albums", help="Remove empty album sub-directories")
        remove_albums_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        remove_albums_parser.set_defaults(func=remove_albums)

        # remove files matching specified file pattern
        # 2 mandatory args, the tld path and the file pattern
        # sys.argv = ['D:\MusicProcessing\main.py', 'remove-pattern', 'C:\Music', { 'AlbumArtSmall.jpg' | 'AlbumArt*Small.jpg' | '*.db' | '*.ini' } ]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'remove-pattern', '/home/gerald/Music',
        # { 'AlbumArtSmall.jpg' | 'AlbumArt*Small.jpg' | '*.db' | '*.ini' } ]
        # remove-pattern C:\Music *.db
        # remove-pattern C:\Music *.ini
        # remove-pattern C:\Music AlbumArtSmall.jpg
        # remove-pattern C:\Music AlbumArt*Small.jpg
        # remove-pattern C:\Music AlbumArt*Large.jpg
        remove_pattern_parser = subparsers.add_parser("remove-pattern", help="Removes files with specified pattern")
        remove_pattern_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        remove_pattern_parser.add_argument("pattern", type=str, help="mandatory file pattern")
        remove_pattern_parser.set_defaults(func=remove_pattern)

        # peak normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'peak-file',
        # "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'peak-file',
        # "/home/gerald/ConvertedMusic/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.mp3"]
        # peak-file "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"
        peak_file_parser = subparsers.add_parser("peak-file", help="Peak normalizes a mp3 audio file level")
        peak_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        peak_file_parser.set_defaults(func=peak_file)

        # rms normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # sys.argv = ['D:\MusicProcessing\main.py', 'rms-file',
        # "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"]
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'rms-file',
        # "/home/gerald/ConvertedMusic/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.mp3"]
        # rms-file "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"
        rms_file_parser = subparsers.add_parser("rms-file", help="Rms normalizes a mp3 audio file level")
        rms_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        rms_file_parser.set_defaults(func=rms_file)

        # set album art file
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py', 'set-art', 'C:\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'set-art', '/home/gerald/Music']
        # set-album-art C:\Music
        set_album_art_parser = subparsers.add_parser("set-album-art", help="Set album art file")
        set_album_art_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        set_album_art_parser.set_defaults(func=set_album_art)

        # update m3u playlist
        # 2 mandatory args, the tld path and the m3u path
        # update-m3u D:\MusicProcessing\tests\Music D:\MusicProcessing\tests\Music\test.m3u
        # sys.argv = ['D:\MusicProcessing\main.py'', 'update-m3u', 'D:\MusicProcessing\tests\Music', 'D:\MusicProcessing\tests/Music\test.m3u']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'update-m3u', '~/MusicProcessing/tests/Music', '~/MusicProcessing/tests/Music/test.m3u']
        # update-walk C:\Music
        update_m3u_parsers = subparsers.add_parser("update-m3u", help="Update playlist paths")
        update_m3u_parsers.add_argument("tld", type=existing_path, help="mandatory top level directory")
        update_m3u_parsers.add_argument("m3u", type=existing_file, help="mandatory m3u file path")
        update_m3u_parsers.set_defaults(func=update_paths)

        # update m3u playlist walk
        # 1 mandatory arg, the tld path
        # sys.argv = ['D:\MusicProcessing\main.py'', 'update-walk', 'D:\MusicProcessing\tests\Music']
        # sys.argv = ['/home/gerald/MusicProcessing/main.py', 'update-walk', '~/MusicProcessing/tests/Music']
        # update-walk C:\Music
        update_walk_parsers = subparsers.add_parser("update-walk", help="Update playlist paths")
        update_walk_parsers.add_argument("tld", type=existing_path, help="mandatory top level directory")
        update_walk_parsers.set_defaults(func=update_walk)

        args = parser.parse_args()
        main(args)

    except Exception as e:
        logger.exception(f"Exception propagated to entry point: {type(e).__name__}: {e}", stack_info=True)
