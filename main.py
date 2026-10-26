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
import re                                                   # regular expression module
import shutil                                               # terminal size lookup module
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
from src.audio_info.audio_utilities import AudioUtilities   # audio utility functions class
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

## @var utilities
# @brief Utility functions instance.
# @details Provides various utility functions for the application.
utilities = AudioUtilities()


class CustomHelpFormatter(argparse.HelpFormatter):
    '''
    @brief Formats command-line help with space for long command names.

    @details Keeps command descriptions aligned after the longest subcommand.
    '''


    def __init__(self, prog):
        '''
        @brief Initializes the help formatter.

        @details Sets the description column far enough right for long commands.

        @param self {CustomHelpFormatter} The instance of the custom help formatter.
        @param prog {str} The program name displayed in usage.
        '''

        # Set the maximum help position for aligning command descriptions
        max_help_position = 60
        # Determine the terminal width for formatting help output
        width = max(shutil.get_terminal_size().columns - 2, 220)

        # Initialize the help formatter with a maximum help position for alignment
        super().__init__(prog, max_help_position=max_help_position, width=width)


    def _format_action(self, action):
        '''
        @brief Formats help descriptions at a fixed column.

        @details Aligns help options and subcommand descriptions.

        @param self {CustomHelpFormatter} The instance of the custom help formatter.
        @param action {argparse.Action} The action being formatted.
        @return {str} Formatted help string for the action.
        '''

        # Check if the action is the root help action (top-level help)
        root_help_action = (action.dest == "help" and action.option_strings and os.path.basename(self._prog) == os.path.basename(__file__))

        # Determine if the action is a subcommand action
        subcommand_action = isinstance(action, argparse._SubParsersAction._ChoicesPseudoAction)

        # Format the action differently if it is the root help action or a subcommand action
        if root_help_action or subcommand_action:
            # get the current action max length before modifying it
            action_max_length = self._action_max_length
            self._action_max_length = self._max_help_position - 2

            try:
                # Format the action using the parent class's method with the adjusted max length
                formatted = super()._format_action(action)
            finally:
                # Restore the original action max length after formatting
                self._action_max_length = action_max_length

            return formatted

        return super()._format_action(action)


class CustomArgumentParser(argparse.ArgumentParser):
    '''
    @brief Custom argument parser so argparse errors can be logged.

    @details Logs argparse error messages that would otherwise be written to standard error.
    '''


    def __init__(self, *args, **kwargs):
        '''
        @brief Initializes the argument parser with the custom help formatter.

        @details Applies consistent command help formatting to the parser and its subparsers.

        @param self {CustomArgumentParser} The instance of the custom argument parser.
        @param args {*args} Positional arguments for the argument parser.
        @param kwargs {**kwargs} Keyword arguments for the argument parser.
        '''

        # Set the custom help formatter as the default for this parser
        kwargs.setdefault("formatter_class", CustomHelpFormatter)
        super().__init__(*args, **kwargs)


    def _print_message(self, message, file=None):
        '''
        @brief Override argparse.ArgumentParser._print_message so stderr gets logged and output to console.

        @details Logs standard-error messages while preserving default handling for all other output.

        @param self {CustomArgumentParser} The instance of the custom argument parser.
        @param message {str} The error message to log.
        @param file {TextIOWrapper} A file-like object for stderr.
        '''

        # want to log errors if the message is intended for stderr and print to console
        if message:
            if file is sys.stderr:
                logger.error(f"Argparse Error: {message.strip()}")

            super()._print_message(message, file)


## @name Subcommand Handlers
# @{
def clip_check_file(file_path):
    '''
    @brief Checks peak, RMS, and EBU R128 leveling for a single audio file.

    @details Reports peak and RMS clipping estimates and whether EBU leveling can use linear normalization.

    @param file_path {str} The full path to the audio file.
    '''

    utilities.clip_check_file(file_path)


def clip_check_walk(tld_path):
    '''
    @brief Checks peak, RMS, and EBU R128 leveling for audio files in a directory.

    @details Reports peak and RMS clipping estimates and whether EBU leveling can use linear normalization.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    utilities.clip_check_walk(tld_path)


def convert_file(file_path, target):
    '''
    @brief Converts specified audio file to mp3 format.

    @details Converts the specified audio file to mp3 format using the metadata conversion functionality.<br>
    Can accept optional optional target directory for the exported file.

    @param file_path {str} The full path to audio file.
    @param target {str} The optional target directory for exported files.
    '''

    metadata.convert_file(file_path, target)


def convert_walk(tld_path, file_pattern, target):
    '''
    @brief Converts all audio files in specified top level directory to mp3 format.

    @details Walks through the top level directory and converts all audio files to mp3 format.<br>
    Can accept an optional file pattern to filter which files to convert.<br>
    Can accept an optional target directory for the exported files.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The optional file pattern we want to convert.
    @param target {str} The optional target directory for exported files.
    '''

    metadata.convert_walk(tld_path, file_pattern, target)


def create_albums(tld_path):
    '''
    @brief Create album 2nd level directories under artist first level directories in top level directory.

    @details Creates album directories under first-level artist directories in the specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    metadata.create_album_dirs(tld_path)


def ebu_file(file_path, target):
    '''
    @brief EBU R128 normalize the specified mp3 audio file.

    @details Normalizes the mp3 audio file to the EBU R128 loudness standard.

    @param file_path {str} The full path to audio file.
    @param target {str} The optional target directory for exported files.
    '''

    normalization.ebu_normalize_file(file_path, target)


def extract_album_art(file_path):
    '''
    @brief Extracts and saves embedded album art from specified audio file.

    @details Saves the embedded album art from the specified audio file, co-locates the art with the audio file in the same directory.

    @param file_path {str} The full path to audio file.
    '''

    art.extract_album_art(file_path)


def extract_walk(tld_path, file_pattern):
    '''
    @brief Extracts and saves embedded album art from all audio files in specified top level directory with specified pattern.

    @details Extracts & saves the embedded album art from all audio files in the specified top level directory that match the given file pattern.<br>
    The extracted album art is co-located with the corresponding audio files in the same directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to extract album art from.
    '''

    art.extract_walk(tld_path, file_pattern)


def get_audio_file_list(tld_path):
    '''
    @brief Gets lists of all audio files from specified top level directory.

    @details Retrieves a list of all audio files from the specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    directory.get_audio_file_list(tld_path)


def get_ext_file_list(tld_path, file_pattern=None):
    '''
    @brief Gets lists of all files from specified top level directory by specified extension.

    @details Retrieves a list of all files with the specified extension from the specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern of extension to get list of.
    '''

    directory.get_ext_file_list(tld_path, file_pattern)


def get_media_info_walk(start_path, file_pattern):
    '''
    @brief Gets media info.

    @details Retrieves detailed media information for all audio files in the specified top level directory that match the given file pattern.<br>
    Uses ffprobe to gather the media information.

    @param start_path {str} The full path to the top level directory containing audio files.
    @param file_pattern {str} The file pattern we want to get media info for.
    '''

    metadata.get_media_info_walk(start_path, file_pattern)


def get_tags_walk(tld_path, file_pattern, ffprobe):
    '''
    @brief Gets metadata from all audio files in specified top level directory with specified pattern.

    @details Retrieves all available metadata tags from all audio files in the specified top level directory that match the given file pattern.<br>
    Defaults to mutagen if ffprobe is not specified.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to get tags for.
    @param ffprobe {bool} Get ffprobe tags instead of mutagen specific tags.
    '''

    metadata.get_tags_walk(tld_path, file_pattern, ffprobe)


def level_normalize_walk(tld_path, norm_type, target):
    '''
    @brief Level normalizes all audio files in specified top level directory per input normalization type.

    @details Level normalizes all mp3 audio files in the specified top level directory according to the specified normalization type.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param norm_type {str} The type of normalization to perform.
    @param target {str} The optional target directory for exported files.
    '''

    normalization.level_normalize_walk(tld_path, norm_type, target)


def normalize_filename(file_path):
    '''
    @brief Renames an audio file using its album artist and title metadata.

    @details Renames any valid audio file using its album artist and title metadata.

    @param file_path {str} The full path to the audio file.
    '''

    metadata.normalize_filename(file_path)


def normalize_filename_walk(tld_path):
    '''
    @brief Wrapper function to normalize filenames of audio files in specified directory.

    @details Renames all supported audio files in the specified tld, fld, or sld, using their album artist and title metadata.

    @param tld_path {str} The top level directory (tld), artist folder (fld), or album folder (sld) path that contains all the music files.
    '''

    metadata.normalize_filename_walk(tld_path)


def peak_file(file_path, target):
    '''
    @brief Peak normalize the specified audio file.

    @details Peak normalizes the specified audio file with ffmpeg.

    @param file_path {str} The full path to audio file.
    @param target {str} The optional target directory for exported files.
    '''

    normalization.peak_normalize_file(file_path, target)


def rms_file(file_path, target):
    '''
    @brief RMS normalize the specified audio file.

    @details RMS normalizes the specified audio file with ffmpeg.

    @param file_path {str} The full path to audio file.
    @param target {str} The optional target directory for exported files.
    '''

    normalization.rms_normalize_file(file_path, target)


def remove_empty_albums(tld_path):
    '''
    @brief Remove empty album directories from specified top level directory.

    @details Recursively scans the specified top level directory and removes any empty album directories.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    directory.remove_empty_albums(tld_path)


def remove_pattern(tld_path, file_pattern):
    '''
    @brief Remove files with specified pattern from specified top level directory.

    @details Recursively scans the specified top level directory and removes any files that match the given pattern.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern we want to delete.
    '''

    directory.remove_pattern(tld_path, file_pattern)


def remove_set_list(tld_path):
    '''
    @brief Remove files matching a hard-coded set of patterns from the specified top level directory.

    @details Recursively scans the specified top level directory and removes any files that match the hard-coded set of patterns.

    @param tld_path {str} The top level directory path that contains all the music files.

    '''

    directory.remove_set_list(tld_path)


def rename_album_directories(tld_path):
    '''
    @brief Renames album directories based on metadata.

    @details Traverses the top level directory, reads album metadata, and renames album directories accordingly.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    metadata.rename_album_directories(tld_path)


def set_album_art(tld_path):
    '''
    @brief Sets album art file for an album directory.

    @details Sets the album art for all album directories matching stored art files.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    art.set_album_art(tld_path)


def update_genres(tld_path, csv_path):
    '''
    @brief Updates genre metadata using artist genre mappings from a CSV file.

    @details Updates supported descendant audio files for artist directories that exactly match CSV artist names.

    @param tld_path {str} The top level directory containing artist directories.
    @param csv_path {str} The full path to the artist genre CSV file.
    '''

    metadata.update_genres(tld_path, csv_path)


def update_playlist(tld_path, input_m3u):
    '''
    @brief Updates an old playlist relative pathing.

    @details Updates the relative paths in the specified playlist file based on the current top level directory structure.

    @param tld_path {str} The top level directory where playlist is located.
    @param input_m3u {str} The full file path to playlist needing conversion.
    '''

    playlist.update_playlist(tld_path, input_m3u)


def update_walk(tld_path):
    '''
    @brief Updates an old playlist relative pathing.

    @details Updates the relative paths in all playlist files within the specified top level directory based on the current directory structure.

    @param tld_path {str} The top level directory where playlists are located.
    '''

    playlist.update_walk(tld_path)
## @}


## @name Application Entry Point
# @{
def main(args) -> None:
    '''
    @brief Module entry point.

    @details Takes command line arguments and executes per arguments.

    @dotfile functions.dot "Application startup and task flow"

    @param args {argparse.Namespace} Arguments for execution.

    @return exit_code {int} Process exit code for the requested subcommand.

    @exception {NotImplementedError} Indicates a subcommand has not been implemented.
    @exception {Exception} Handles unforeseen errors.
    '''

    try:
        if args.subcommand == "clip-check-file":
            file_path = getattr(args, "file")
            clip_check_file(file_path)

        if args.subcommand == "clip-check-walk":
            tld_path = getattr(args, "tld")
            clip_check_walk(tld_path)

        if args.subcommand == "convert-file":
            file_path = getattr(args, "file")
            target = getattr(args, "target")
            convert_file(file_path, target)

        if args.subcommand == "convert-walk":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            target = getattr(args, "target")
            convert_walk(tld_path, file_pattern, target)

        if args.subcommand == "create-albums":
            tld_path = getattr(args, "tld")
            create_albums(tld_path)

        if args.subcommand == "ebu-file":
            file_path = getattr(args, "file")
            target = getattr(args, "target")
            ebu_file(file_path, target)

        if args.subcommand == "extract-album-art":
            file_path = getattr(args, "file")
            extract_album_art(file_path)

        if args.subcommand == "extract-walk":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            extract_walk(tld_path, file_pattern)

        if args.subcommand == "get-audio-file-list":
            tld_path = getattr(args, "tld")
            get_audio_file_list(tld_path)

        if args.subcommand == "get-ext-file-list":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            get_ext_file_list(tld_path, file_pattern)

        if args.subcommand == "get-media-info-walk":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            get_media_info_walk(tld_path, file_pattern)

        if args.subcommand == "get-tags-walk":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            ffprobe = getattr(args, "ffprobe")
            get_tags_walk(tld_path, file_pattern, ffprobe)

        if args.subcommand == "level-normalize-walk":
            tld_path = getattr(args, "tld")
            norm_type = getattr(args, "type")
            target = getattr(args, "target")
            level_normalize_walk(tld_path, norm_type, target)

        if args.subcommand == "normalize-filename":
            file_path = getattr(args, "file")
            normalize_filename(file_path)

        if args.subcommand == "normalize-filename-walk":
            tld_path = getattr(args, "tld")
            normalize_filename_walk(tld_path)

        if args.subcommand == "peak-file":
            file_path = getattr(args, "file")
            target = getattr(args, "target")
            peak_file(file_path, target)

        if args.subcommand == "rms-file":
            file_path = getattr(args, "file")
            target = getattr(args, "target")
            rms_file(file_path, target)

        if args.subcommand == "remove-empty-albums":
            tld_path = getattr(args, "tld")
            remove_empty_albums(tld_path)

        if args.subcommand == "remove-pattern":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            remove_pattern(tld_path, file_pattern)

        if args.subcommand == "remove-set-list":
            tld_path = getattr(args, "tld")
            remove_set_list(tld_path)

        if args.subcommand == "rename-album-directories":
            tld_path = getattr(args, "tld")
            rename_album_directories(tld_path)

        if args.subcommand == "set-album-art":
            tld_path = getattr(args, "tld")
            set_album_art(tld_path)

        if args.subcommand == "update-genres":
            tld_path = getattr(args, "tld")
            csv_path = getattr(args, "csv")
            update_genres(tld_path, csv_path)

        if args.subcommand == "update-playlist":
            tld_path = getattr(args, "tld")
            input_m3u = getattr(args, "m3u")
            update_playlist(tld_path, input_m3u)

        if args.subcommand == "update-walk":
            tld_path = getattr(args, "tld")
            update_walk(tld_path)

    except Exception as e:
        logger.exception(f"Exception propagated to main: {type(e).__name__}: {e}", stack_info=True)
        print(f"Error in subcommand '{args.subcommand}': {type(e).__name__}: {e}")
## @}


## @name Argument Validation Helpers
# @{
def existing_file(file):
    '''
    @brief Checks if file exists.

    @details Checks if the specified file exists and raises an ArgumentTypeError if it does not.<br>
    Helper function for ArgumentParser to validate file paths.

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

    @details Checks if the specified directory exists and raises an ArgumentTypeError if it does not.<br>
    Helper function for ArgumentParser to validate directory paths.

    @param path {str} The directory path.
    @return path {str} The directory path.

    @exception {ArgumentTypeError} Indicates the directory was not found.
    '''

    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Directory not found: {path}")

    return path
## @}


if __name__ == "__main__":
    '''
    @brief Top level script environment entry point.

    @details Sets up argument parsing and subcommand handling.

    @note Any input file paths that contain spaces must be enclosed in quotes.

    @exception {Exception} Handles unforeseen errors.
    '''

    try:
        parser = CustomArgumentParser(description='Music Processing')
        subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", metavar="command")

        # check peak, RMS, and EBU R128 leveling for a single audio file
        # 1 mandatory arg, the audio file path
        # clip-check-file "D:\MusicProcessing\tests\Music\Abba\Waterloo\Abba-Waterloo.mp3"
        clip_check_file_parser = subparsers.add_parser("clip-check-file", help="Check peak, RMS, and EBU R128 leveling for a single audio file")
        clip_check_file_parser.add_argument("file", type=existing_file, help="mandatory audio file path")
        clip_check_file_parser.set_defaults(func=clip_check_file)

        # check max volume and clip level of audio files
        # 1 mandatory arg, the start path (can be tld, fld, or sld)
        # clip-check-walk "D:\MusicProcessing\tests\Music"
        # clip-check-walk "D:\MusicProcessing\tests\Music\Abba"
        # clip-check-walk "D:\MusicProcessing\tests\Music\Abba\Waterloo"
        # clip-check-walk "D:\MusicProcessing\tests\Music\The Lord of the Rings"
        clip_check_walk_parser = subparsers.add_parser("clip-check-walk", help="Check peak, RMS, and EBU R128 leveling options for audio files")
        clip_check_walk_parser.add_argument("tld", type=existing_path, help="mandatory start path tld/fld/sld")
        clip_check_walk_parser.set_defaults(func=clip_check_walk)

        # convert audio file specified to mp3 format
        # 1 mandatory arg, the audio file path
        # 1 optional arg, the target directory for exported files
        # convert-file "C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a"
        convert_file_parser = subparsers.add_parser("convert-file", help="Convert audio file to mp3")
        convert_file_parser.add_argument("file", type=existing_file, help="mandatory audio file path")
        convert_file_parser.add_argument("--target", type=str, help="optional converted file target path")
        convert_file_parser.set_defaults(func=convert_file)

        # convert all audio files found in top level directory
        # 1 mandatory arg, the start path (can be tld, fld, or sld)
        # 1 optional arg, the file pattern to match (.flac, .mp3, .m4a .wma)
        # 1 optional arg, the target directory for exported files
        # convert-walk "C:\Music" --pattern .m4a "C:\ConvertedMusic"
        # convert-walk "C:\Music"
        # convert-walk "C:\Music\Abba"
        # convert-walk "C:\Music\Abba\Waterloo"
        convert_walk_parser = subparsers.add_parser("convert-walk", help="Convert audio files to mp3")
        convert_walk_parser.add_argument("tld", type=existing_path, help="mandatory start path tld/fld/sld")
        convert_walk_parser.add_argument("--pattern", type=str, help="optional file ext {.flac|.mp3|.m4a|.wma}")
        convert_walk_parser.add_argument("--target", type=str, help="optional converted files target path")
        convert_walk_parser.set_defaults(func=convert_walk)

        # create album directories
        # 1 mandatory arg, the tld path (must be the tld, fld and sld will not work)
        # create-albums C:\Music
        create_albums_parser = subparsers.add_parser("create-albums", help="Create album sub-directories")
        create_albums_parser.add_argument("tld", type=existing_path, help="mandatory start path tld only")
        create_albums_parser.set_defaults(func=create_albums)

        # ebu normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # 1 optional arg, the target directory for exported files
        # ebu-file "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"
        ebu_file_parser = subparsers.add_parser("ebu-file", help="EBU R128 level audio file")
        ebu_file_parser.add_argument("file", type=existing_file, help="mandatory audio file path")
        ebu_file_parser.add_argument("--target", type=str, help="optional leveled file target path")
        ebu_file_parser.set_defaults(func=ebu_file)

        # extract album art from specified audio file
        # 1 mandatory arg, the path to audio file
        # extract-file "C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"
        extract_album_art_parser = subparsers.add_parser("extract-album-art", help="Extract audio file embedded art")
        extract_album_art_parser.add_argument("file", type=existing_file, help="mandatory audio file path")
        extract_album_art_parser.set_defaults(func=extract_album_art)

        # extract album art from all audio files found in top level directory
        # 1 mandatory arg, the start path (can be tld or fld, but not sld)
        # 1 optional arg, the file pattern to match (.flac, .mp3, .m4a, .wma)
        # extract-walk C:\Music --pattern .flac
        # extract-walk C:\Music --pattern .mp3
        # extract-walk C:\Music --pattern .m4a
        # extract-walk C:\Music --pattern .wma
        # extract-walk C:\Music\Abba
        # extract-walk C:\Music
        extract_walk_parser = subparsers.add_parser("extract-walk", help="Extract audio files embedded art")
        extract_walk_parser.add_argument("tld", type=existing_path, help="mandatory start path tld/fld")
        extract_walk_parser.add_argument("--pattern", type=str, help="optional file ext {.flac|.mp3|.m4a|.wma}")
        extract_walk_parser.set_defaults(func=extract_walk)

        # list all audio files
        # 1 mandatory arg, the tld path
        # get-audio-file-list D:\MusicProcessing\tests\Music
        get_audio_file_list_audio_parser = subparsers.add_parser("get-audio-file-list", help="Get CSV list of audio file paths")
        get_audio_file_list_audio_parser.add_argument("tld", type=existing_path, help="mandatory start path tld only")
        get_audio_file_list_audio_parser.set_defaults(func=get_audio_file_list)

        # list files by extension
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file extension (.flac, .mp3, .m4a .wma)
        # get-ext-file-list C:\Music --pattern .flac
        # get-ext-file-list C:\Music --pattern .mp3
        # get-ext-file-list C:\Music --pattern .m4a
        # get-ext-file-list C:\Music --pattern .wma
        # get-ext-file-list D:\MusicProcessing\tests\Music
        get_ext_file_list_parser = subparsers.add_parser("get-ext-file-list", help="Get CSV list of audio file extensions")
        get_ext_file_list_parser.add_argument("tld", type=existing_path, help="mandatory start path tld/fld/sld")
        get_ext_file_list_parser.add_argument("--pattern", type=str, help="optional file ext {.flac|.mp3|.m4a|.wma}")
        get_ext_file_list_parser.set_defaults(func=get_ext_file_list)

        # get media information for files
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file ext to match {.flac|.mp3|.m4a|.wma}
        # get-media-info-walk C:\Music --pattern .mp3``
        # get-media-info-walk C:\Music --pattern .m4a
        # get-media-info-walk C:\Music --pattern .wma
        # get-media-info-walk C:\Music --pattern .flac
        # get-media-info-walk D:\MusicProcessing\tests\Music
        get_media_info_walk_parser = subparsers.add_parser("get-media-info-walk", help="Get text list of audio files media info")
        get_media_info_walk_parser.add_argument("tld", type=existing_path, help="mandatory start path tld/fld")
        get_media_info_walk_parser.add_argument("--pattern", type=str, help="optional file ext {.flac|.mp3|.m4a|.wma}")
        get_media_info_walk_parser.set_defaults(func=get_media_info_walk)

        # get metadata tags from all audio files found in top level directory
        # 1 mandatory arg, the tld or fld path
        # 1 optional arg, the file ext to match (.flac, .mp3, .m4a .wma)
        # 1 optional arg, use ffprobe boolean
        # get-tags-walk C:\Music
        # get-tags-walk C:\Music --pattern .mp3 --ffprobe True
        # get-tags-walk C:\Music --pattern .m4a --ffprobe True
        # get-tags-walk C:\Music --pattern .wma --ffprobe True
        # get-tags-walk C:\Music --pattern .flac --ffprobe True
        # get-tags-walk D:\MusicProcessing\tests\Music --ffprobe True
        get_tags_walk_parser = subparsers.add_parser("get-tags-walk", help="Get text list of audio files metadata tags")
        get_tags_walk_parser.add_argument("tld", type=existing_path, help="mandatory start path tld/fld")
        get_tags_walk_parser.add_argument("--pattern", type=str, help="optional file ext {.flac|.mp3|.m4a|.wma}")
        get_tags_walk_parser.add_argument("--ffprobe", type=bool, help="optional use ffprobe True")
        get_tags_walk_parser.set_defaults(func=get_tags_walk)

        # level normalize mp3 files from tld
        # 2 mandatory arg, the tld path and the normalization type (ebu, peak, rms)
        # 1 optional arg, the target directory for exported files
        # level-normalize-walk C:\Music ebu
        # level-normalize-walk C:\Music peak
        # level-normalize-walk C:\Music rms
        # level-normalize-walk "F:\Rick\RickConverted\Elton John" ebu --target "F:\Rick\RickLeveled"
        level_normalize_walk_parser = subparsers.add_parser("level-normalize-walk", help="Level normalize files per type")
        level_normalize_walk_parser.add_argument("tld", type=existing_path, help="mandatory start path tld/fld")
        level_normalize_walk_parser.add_argument("type", type=str, help="mandatory level type {ebu|peak|rms}")
        level_normalize_walk_parser.add_argument("--target", type=str, help="optional leveled files target path")
        level_normalize_walk_parser.set_defaults(func=level_normalize_walk)

        # normalize a filename from its metadata
        # 1 mandatory arg, the audio file path
        # normalize-filename "C:\Music\song.flac"
        # normalize-filename "C:\Music\song.mp3"
        # normalize-filename "C:\Music\song.m4a"
        # normalize-filename "C:\Music\song.wma"
        normalize_filename_parser = subparsers.add_parser("normalize-filename", help="Normalize audio file from its metadata")
        normalize_filename_parser.add_argument("file", type=existing_file, help="mandatory audio file path")
        normalize_filename_parser.set_defaults(func=normalize_filename)

        # normalize audio filenames from metadata for all acceptable audio file types in directory
        # 1 mandatory arg, the start path (can be tld, fld, or sld)
        # normalize-filename-walk "F:\Rick\RickPrepped"
        # normalize-filename-walk "F:\Rick\RickPrepped\Duffy"
        # normalize-filename-walk "F:\Rick\RickPrepped\Duffy\Rockferry"
        normalize_filename_walk_parser = subparsers.add_parser("normalize-filename-walk", help="Normalize audio files from their metadata")
        normalize_filename_walk_parser.add_argument("tld", type=existing_path, help="mandatory start path tld/fld/sld")
        normalize_filename_walk_parser.set_defaults(func=normalize_filename_walk)

        # remove empty album directories
        # 1 mandatory arg, the tld path
        # remove-empty-albums C:\Music
        remove_empty_albums_parser = subparsers.add_parser("remove-empty-albums", help="Remove empty album sub-directories")
        remove_empty_albums_parser.add_argument("tld", type=existing_path, help="mandatory start path tld/fld")
        remove_empty_albums_parser.set_defaults(func=remove_empty_albums)

        # remove files matching specified file pattern
        # 1st mandatory args, the start path (can be tld, fld, or sld)
        # 2nd mandatory arg, the file pattern
        # remove-pattern C:\Music *.db
        # remove-pattern C:\Music *.ini
        # remove-pattern C:\Music AlbumArtSmall.jpg
        # remove-pattern C:\Music AlbumArt*Small.jpg
        # remove-pattern C:\Music AlbumArt*Large.jpg
        remove_pattern_parser = subparsers.add_parser("remove-pattern", help="Remove files with specified pattern")
        remove_pattern_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        remove_pattern_parser.add_argument("pattern", type=str, help="mandatory file pattern")
        remove_pattern_parser.set_defaults(func=remove_pattern)

        # remove files matching a hard-coded set of patterns
        # 1 mandatory arg, the tld path
        # remove-set-list "F:\Rick\RickPrepped\Huey Lewis & The News"
        remove_set_list_parser = subparsers.add_parser("remove-set-list", help="Remove files matching hard-coded pattern set")
        remove_set_list_parser.add_argument("tld", type=existing_path, help="mandatory starting path tld/fld/sld")
        remove_set_list_parser.set_defaults(func=remove_set_list)

        # rename album directories based on metadata
        # 1 mandatory arg, the tld path
        # rename-album-directories "F:\Rick\RickPrepped"
        rename_album_directories_parser = subparsers.add_parser("rename-album-directories", help="Rename album paths from metadata")
        rename_album_directories_parser.add_argument("tld", type=existing_path, help="mandatory start path tld only")
        rename_album_directories_parser.set_defaults(func=rename_album_directories)

        # peak normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # 1 optional arg, the target directory for exported files
        # peak-file "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"
        peak_file_parser = subparsers.add_parser("peak-file", help="Peak level audio file")
        peak_file_parser.add_argument("file", type=existing_file, help="mandatory audio file path")
        peak_file_parser.add_argument("--target", type=str, help="optional leveled file target path")
        peak_file_parser.set_defaults(func=peak_file)

        # rms normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # 1 optional arg, the target directory for exported files
        # rms-file "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"
        rms_file_parser = subparsers.add_parser("rms-file", help="RMS level audio file")
        rms_file_parser.add_argument("file", type=existing_file, help="mandatory audio file path")
        rms_file_parser.add_argument("--target", type=str, help="optional leveled file target path")
        rms_file_parser.set_defaults(func=rms_file)

        # set album art file
        # 1 mandatory arg, the tld path
        # set-album-art C:\Music
        set_album_art_parser = subparsers.add_parser("set-album-art", help="Set albums art file")
        set_album_art_parser.add_argument("tld", type=existing_path, help="mandatory starting path tld/fld")
        set_album_art_parser.set_defaults(func=set_album_art)

        # update genre metadata from artist directory mappings in a CSV file
        # 2 mandatory args, the tld path and artist genre CSV path
        # update-genres-from-csv F:/Rick/RickPrepped D:/MusicProcessing/src/generated_files/csv_files/artist_genre.csv
        update_genres_parser = subparsers.add_parser("update-genres", help="Update songs genre from CSV")
        update_genres_parser.add_argument("tld", type=existing_path, help="mandatory start path tld only")
        update_genres_parser.add_argument("csv", type=existing_file, help="mandatory artist genre CSV file path")
        update_genres_parser.set_defaults(func=update_genres)

        # update m3u playlist
        # 2 mandatory args, the tld path and the m3u path
        # update-playlist D:\MusicProcessing\tests\Music D:\MusicProcessing\tests\Music\test.m3u
        # update-walk C:\Music
        update_playlist_parsers = subparsers.add_parser("update-playlist", help="Update playlist file songs path")
        update_playlist_parsers.add_argument("tld", type=existing_path, help="mandatory start path tld only")
        update_playlist_parsers.add_argument("m3u", type=existing_file, help="mandatory playlist file in tld path")
        update_playlist_parsers.set_defaults(func=update_playlist)

        # update m3u playlist walk
        # 1 mandatory arg, the tld path
        # update-walk C:\Music
        update_walk_parsers = subparsers.add_parser("update-walk", help="Update playlist files songs path")
        update_walk_parsers.add_argument("tld", type=existing_path, help="mandatory start path tld only")
        update_walk_parsers.set_defaults(func=update_walk)

        # append each argument's help text (mandatory first, then optional) to its subcommand help so the top level help displays them
        for choice_action in subparsers._choices_actions:
            sub_actions = [a for a in subparsers.choices[choice_action.dest]._actions if not isinstance(a, argparse._HelpAction)]
            sub_actions.sort(key=lambda a: bool(a.option_strings))
            arg_help = [re.sub(r"^(mandatory|optional)\s+", r"\1: ", a.help) for a in sub_actions if a.help]

            if arg_help:
                choice_action.help += "; " + "; ".join(arg_help)

            # show the command followed by its positional arguments and flags with value placeholders
            arg_usage = [
                f"{a.option_strings[0]} {a.dest}" if a.option_strings and a.nargs != 0 else (a.option_strings[0] if a.option_strings else a.dest)
                for a in sub_actions
            ]
            choice_action.metavar = " ".join([choice_action.dest] + arg_usage)

        args = parser.parse_args()
        sys.exit(main(args))

    except Exception as e:
        logger.exception(f"Exception propagated to entry point: {type(e).__name__}: {e}", stack_info=True)
        print(f"Error in entry point: {type(e).__name__}: {e}")
