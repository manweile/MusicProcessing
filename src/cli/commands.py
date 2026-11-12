'''
@module commands
@file commands.py
@author Gerald Manweiler

@brief Defines the command-line dispatch module.

@details Adapts parsed command arguments to the existing model operations.

@version 1.0.0
@date 2026-11-11

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import logging                                              # for recording command errors
from argparse import Namespace                              # for typing parsed arguments

# Local Module Methods
from src.core.logging_config import bootstrap_logging       # for configuring package logging
from src.gui.wx_app import run_gui                          # for launching the graphical interface

# MUST configure logging before importing modules that register logging handlers
# imports after executable code require noqa: E402 (module import after code) to stop error warning
bootstrap_logging()

# Local Module Classes
from src.audio_info import AudioArt                         # noqa: E402, for audio artwork operations
from src.audio_info import AudioMetadata                    # noqa: E402, for audio metadata operations
from src.audio_info import AudioPlaylist                    # noqa: E402, for playlist operations
from src.audio_info import AudioUtilities                   # noqa: E402, for audio utility operations
from src.audio_normalize import AudioNormalization          # noqa: E402, for audio normalization operations
from src.cli.progress import SpinnerProgress                # noqa: E402, for command-line spinner display
from src.cli.progress import TqdmProgress                   # noqa: E402, for command-line progress bars
from src.dir_processing import DirectoryProcessing          # noqa: E402, for directory operations

## @var logger
# @brief Module logger.
# @details Records command dispatch errors.
logger = logging.getLogger(__name__)

## @var art
# @brief Audio artwork handler.
# @details Provides audio artwork operations for CLI commands.
art = AudioArt()

## @var directory
# @brief Directory processing handler.
# @details Provides directory operations for CLI commands.
directory = DirectoryProcessing()

## @var metadata
# @brief Audio metadata handler.
# @details Provides audio metadata operations for CLI commands.
metadata = AudioMetadata()

## @var normalization
# @brief Audio normalization handler.
# @details Provides audio normalization operations for CLI commands.
normalization = AudioNormalization()

## @var playlist
# @brief Playlist handler.
# @details Provides playlist operations for CLI commands.
playlist = AudioPlaylist()

## @var utilities
# @brief Audio utilities handler.
# @details Provides audio utility operations for CLI commands.
utilities = AudioUtilities()

## @var _COMMAND_ARGUMENTS
# @brief Argument names passed to each command handler.
# @details Preserve the parser's positional argument order for command dispatch.
_COMMAND_ARGUMENTS = {
    "clip-check-file": ("file",),
    "clip-check-walk": ("tld",),
    "convert-file": ("file", "target"),
    "convert-walk": ("tld", "pattern", "target"),
    "create-albums": ("tld",),
    "ebu-file": ("file", "target"),
    "extract-album-art": ("file",),
    "extract-walk": ("tld", "pattern"),
    "get-audio-file-list": ("tld",),
    "get-ext-file-list": ("tld", "pattern"),
    "get-media-info-walk": ("tld", "pattern"),
    "get-tags-walk": ("tld", "pattern", "ffprobe"),
    "gui": (),
    "level-normalize-walk": ("tld", "type", "target"),
    "normalize-filename": ("file",),
    "normalize-filename-walk": ("tld",),
    "peak-file": ("file", "target"),
    "remove-empty-albums": ("tld",),
    "remove-pattern": ("tld", "pattern"),
    "remove-set-list": ("tld",),
    "rename-album-directories": ("tld",),
    "rms-file": ("file", "target"),
    "set-album-art": ("tld",),
    "update-genres": ("tld", "csv"),
    "update-playlist": ("tld", "m3u"),
    "update-walk": ("tld",)
}


## @name Subcommand Handlers
# @{
def gui():
    '''
    @brief Launches the graphical user interface.

    @details Imports and starts the existing GUI only when the GUI command is dispatched.
    '''

    # from src.gui.wx_app import run_gui                        # for launching the graphical interface

    run_gui()


def clip_check_file(file_path: str):
    '''
    @brief Checks leveling for a single audio file.

    @details Reports peak, RMS, and EBU R128 clipping estimates.

    @param file_path {str} The full path to the audio file.
    '''

    utilities.clip_check_file(file_path, progress=SpinnerProgress())


def clip_check_walk(tld_path: str):
    '''
    @brief Checks leveling for audio files in a directory.

    @details Reports peak, RMS, and EBU R128 clipping estimates for matching files.

    @param tld_path {str} The directory containing audio files.
    '''

    utilities.clip_check_walk(tld_path, progress=SpinnerProgress())


def convert_file(file_path: str, target: str | None):
    '''
    @brief Converts an audio file to MP3 format.

    @details Converts the specified audio file and optionally writes it to a target directory.

    @param file_path {str} The full path to the audio file.
    @param target {str | None} The optional target directory.
    '''

    metadata.convert_file(file_path, target, progress=SpinnerProgress())


def convert_walk(tld_path: str, file_pattern: str | None, target: str | None):
    '''
    @brief Converts audio files in a directory to MP3 format.

    @details Filters files by an optional pattern and optionally writes them to a target directory.

    @param tld_path {str} The directory containing audio files.
    @param file_pattern {str | None} The optional file pattern.
    @param target {str | None} The optional target directory.
    '''

    metadata.convert_walk(tld_path, file_pattern, target, progress=SpinnerProgress())


def create_albums(tld_path: str):
    '''
    @brief Creates album subdirectories.

    @details Creates album directories under first-level artist directories.

    @param tld_path {str} The top-level directory containing audio files.
    '''

    metadata.create_album_dirs(tld_path, TqdmProgress())


def ebu_file(file_path: str, target: str | None):
    '''
    @brief Normalizes an audio file to EBU R128.

    @details Applies EBU R128 normalization and optionally writes to a target directory.

    @param file_path {str} The full path to the audio file.
    @param target {str | None} The optional target directory.
    '''

    normalization.ebu_normalize_file(file_path, target, progress=SpinnerProgress())


def extract_album_art(file_path: str):
    '''
    @brief Extracts embedded album artwork from an audio file.

    @details Saves the embedded artwork alongside the audio file.

    @param file_path {str} The full path to the audio file.
    '''

    art.extract_album_art(file_path)


def extract_walk(tld_path: str, file_pattern: str | None):
    '''
    @brief Extracts embedded artwork from audio files in a directory.

    @details Extracts artwork from files matching the optional file pattern.

    @param tld_path {str} The directory containing audio files.
    @param file_pattern {str | None} The optional file pattern.
    '''

    art.extract_walk(tld_path, file_pattern)


def get_audio_file_list(tld_path: str):
    '''
    @brief Lists audio file paths.

    @details Retrieves audio file paths from the specified directory.

    @param tld_path {str} The directory containing audio files.
    '''

    directory.get_audio_file_list(tld_path)


def get_ext_file_list(tld_path: str, file_pattern: str | None = None):
    '''
    @brief Lists files by extension.

    @details Retrieves matching file paths from the specified directory.

    @param tld_path {str} The directory containing files.
    @param file_pattern {str | None} The optional file extension pattern.
    '''

    directory.get_ext_file_list(tld_path, file_pattern)


def get_media_info_walk(start_path: str, file_pattern: str | None):
    '''
    @brief Retrieves media information for audio files.

    @details Uses ffprobe to gather media information for matching files.

    @param start_path {str} The directory containing audio files.
    @param file_pattern {str | None} The optional file pattern.
    '''

    metadata.get_media_info_walk(start_path, file_pattern)


def get_tags_walk(tld_path: str, file_pattern: str | None, ffprobe: bool | None):
    '''
    @brief Retrieves metadata tags from audio files.

    @details Uses ffprobe when requested and otherwise uses Mutagen.

    @param tld_path {str} The directory containing audio files.
    @param file_pattern {str | None} The optional file pattern.
    @param ffprobe {bool | None} Whether to retrieve tags with ffprobe.
    '''

    metadata.get_tags_walk(tld_path, file_pattern, ffprobe)


def level_normalize_walk(tld_path: str, norm_type: str, target: str | None):
    '''
    @brief Normalizes audio files in a directory.

    @details Applies the requested normalization mode and optional target directory.

    @param tld_path {str} The directory containing audio files.
    @param norm_type {str} The normalization mode.
    @param target {str | None} The optional target directory.
    '''

    normalization.level_normalize_walk(tld_path, norm_type, target, progress=SpinnerProgress())


def normalize_filename(file_path: str):
    '''
    @brief Renames an audio file from its metadata.

    @details Uses album artist and title metadata to normalize the filename.

    @param file_path {str} The full path to the audio file.
    '''

    metadata.normalize_filename(file_path)


def normalize_filename_walk(tld_path: str):
    '''
    @brief Renames audio files from their metadata.

    @details Normalizes supported audio filenames under the specified directory.

    @param tld_path {str} The directory containing audio files.
    '''

    metadata.normalize_filename_walk(tld_path)


def peak_file(file_path: str, target: str | None):
    '''
    @brief Peak-normalizes an audio file.

    @details Applies peak normalization and optionally writes to a target directory.

    @param file_path {str} The full path to the audio file.
    @param target {str | None} The optional target directory.
    '''

    normalization.peak_normalize_file(file_path, target, progress=SpinnerProgress())


def remove_empty_albums(tld_path: str):
    '''
    @brief Removes empty album directories.

    @details Recursively scans the specified directory for empty album directories.

    @param tld_path {str} The directory containing audio files.
    '''

    directory.remove_empty_albums(tld_path)


def remove_pattern(tld_path: str, file_pattern: str):
    '''
    @brief Removes files matching a pattern.

    @details Recursively scans the specified directory and removes matching files.

    @param tld_path {str} The directory containing files.
    @param file_pattern {str} The file pattern to remove.
    '''

    directory.remove_pattern(tld_path, file_pattern)


def remove_set_list(tld_path: str):
    '''
    @brief Removes files matching the built-in pattern set.

    @details Recursively scans the specified directory and removes matching files.

    @param tld_path {str} The directory containing files.
    '''

    directory.remove_set_list(tld_path)


def rename_album_directories(tld_path: str):
    '''
    @brief Renames album directories from metadata.

    @details Traverses the specified directory and renames album directories.

    @param tld_path {str} The top-level directory containing audio files.
    '''

    metadata.rename_album_directories(tld_path)


def rms_file(file_path: str, target: str | None):
    '''
    @brief RMS-normalizes an audio file.

    @details Applies RMS normalization and optionally writes to a target directory.

    @param file_path {str} The full path to the audio file.
    @param target {str | None} The optional target directory.
    '''

    normalization.rms_normalize_file(file_path, target, progress=SpinnerProgress())


def set_album_art(tld_path: str):
    '''
    @brief Sets album artwork for album directories.

    @details Applies matching stored artwork to albums under the specified directory.

    @param tld_path {str} The directory containing albums.
    '''

    art.set_album_art(tld_path)


def update_genres(tld_path: str, csv_path: str):
    '''
    @brief Updates genre metadata from a CSV file.

    @details Applies artist genre mappings to supported descendant audio files.

    @param tld_path {str} The top-level directory containing audio files.
    @param csv_path {str} The path to the artist genre CSV file.
    '''

    metadata.update_genres(tld_path, csv_path)


def update_playlist(tld_path: str, input_m3u: str):
    '''
    @brief Updates playlist-relative paths.

    @details Updates paths in the specified playlist based on the directory structure.

    @param tld_path {str} The top-level directory containing audio files.
    @param input_m3u {str} The path to the playlist file.
    '''

    playlist.update_playlist(tld_path, input_m3u)


def update_walk(tld_path: str):
    '''
    @brief Updates playlist-relative paths in a directory.

    @details Updates paths in all playlist files under the specified directory.

    @param tld_path {str} The top-level directory containing playlists.
    '''

    playlist.update_walk(tld_path)
## @}


## @name CLI Command Dispatcher
## @{
def run_cli_command(args: Namespace) -> int:
    '''
    @brief Dispatches a parsed command-line request.

    @details Runs the matching command handler and returns a process exit code.

    @param args {Namespace} Parsed command-line arguments.

    @retval {int} Exit code, zero on success, or one when command execution fails.
    '''

    subcommand = getattr(args, "subcommand", None)
    if subcommand is None:
        return 0

    try:
        handler = getattr(args, "func", None)

        if handler is None or subcommand not in _COMMAND_ARGUMENTS:
            logger.exception(f"Subcommand '{subcommand}' is not implemented", exc_info=True)
            raise NotImplementedError(f"Subcommand '{subcommand}' is not implemented")

        handler(*(getattr(args, name) for name in _COMMAND_ARGUMENTS[subcommand]))
        return 0

    except NotImplementedError as ni_error:
        raise ni_error
    except Exception as e_error:
        logger.exception(f"Error executing subcommand '{subcommand}'", stack_info=True)
        raise e_error
## @}
