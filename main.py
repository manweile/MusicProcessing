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


def get_ffprobe_media_info(file_path):
    '''
    @brief Gets media info.

    @details Retrieves detailed media information for the specified audio file with ffprobe.

    @param file_path {str} The full path to audio file.
    '''

    metadata.get_ffprobe_media_info(file_path)


def get_ffprobe_media_info_walk(start_path, file_pattern):
    '''
    @brief Gets media info.

    @details Retrieves detailed media information for all audio files in the specified top level directory that match the given file pattern.<br>
    Uses ffprobe to gather the media information.

    @param start_path {str} The full path to the top level directory containing audio files.
    @param file_pattern {str} The file pattern we want to get media info for.
    '''

    metadata.get_ffprobe_media_info_walk(start_path, file_pattern)


def get_ffprobe_tags(file_path):
    '''
    @brief Gets media tags.

    @details Uses ffprobe to retrieve the metadata tags for the specified audio file.

    @param file_path {str} The full path to audio file.
    '''

    metadata.get_ffprobe_tags(file_path)


def get_mutagen_tags(file_path):
    '''
    @brief Gets metadata from specified audio file.

    @details Retrieves all available metadata tags from the specified audio file using mutagen.

    @param file_path {str} The full path to audio file.
    @return tags {mutagen.FileType} The metadata tags retrieved from the audio file.
    '''

    tags = metadata.get_mutagen_tags(file_path)
    return tags


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


def get_unique_media(tld_path):
    '''
    @brief Gets set of unique keys for entire collection found by ffprobe.

    @details Retrieves a set of unique metadata keys from all audio files in the specified top level directory using ffprobe.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    metadata.get_unique_media_keys(tld_path)


def level_normalize_walk(tld_path, norm_type, target):
    '''
    @brief Level normalizes all audio files in specified top level directory per input normalization type.

    @details Level normalizes all mp3 audio files in the specified top level directory according to the specified normalization type.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param norm_type {str} The type of normalization to perform.
    @param target {str} The optional target directory for exported files.
    '''

    normalization.level_normalize_walk(tld_path, norm_type, target)


def list_audio(tld_path):
    '''
    @brief List all audio files from specified top level directory.

    @details Retrieves a list of all audio files from the specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    '''

    directory.get_audio_file_list(tld_path)


def list_type(tld_path, file_pattern=None):
    '''
    @brief List files from specified top level directory by specified extension.

    @details Retrieves a list of all files with the specified extension from the specified top level directory.

    @param tld_path {str} The top level directory path that contains all the music files.
    @param file_pattern {str} The file pattern of extension to get list of.
    '''

    directory.get_ext_file_list(tld_path, file_pattern)


def normalize_flac_filename(file_path):
    '''
    @brief Renames a FLAC using its album artist and title metadata.

    @details Renames the specified FLAC file using its VORBIS album artist and title metadata.

    @param file_path {str} The full path to the FLAC file.
    '''

    metadata.normalize_flac_filename(file_path)


def normalize_mp3_filename(file_path):
    '''
    @brief Renames an MP3 using its album artist and title metadata.

    @details Renames the specified MP3 file using its ID3 album artist and title metadata.

    @param file_path {str} The full path to the MP3 file.
    '''

    metadata.normalize_mp3_filename(file_path)


def normalize_mp4_filename(file_path):
    '''
    @brief Renames an M4A using its album artist and title metadata.

    @details Renames the specified M4A file using its MP4 album artist and title metadata.

    @param file_path {str} The full path to the M4A file.
    '''

    metadata.normalize_mp4_filename(file_path)


def normalize_wma_filename(file_path):
    '''
    @brief Renames a WMA using its album artist and title metadata.

    @details Renames the specified WMA file using its ASF album artist and title metadata.

    @param file_path {str} The full path to the WMA file.
    '''

    metadata.normalize_wma_filename(file_path)


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


def update_genres_from_csv(tld_path, csv_path):
    '''
    @brief Updates genre metadata using artist genre mappings from a CSV file.

    @details Updates supported descendant audio files for artist directories that exactly match CSV artist names.

    @param tld_path {str} The top level directory containing artist directories.
    @param csv_path {str} The full path to the artist genre CSV file.
    @return summary {dict[str, list[str]]} Updated files, skipped artists, unsupported files, and failures.
    '''

    summary = metadata.update_genres_from_csv(tld_path, csv_path)
    print(f"Updated files: {len(summary['updated_files'])}")
    print(f"Skipped artists: {len(summary['skipped_artists'])}")
    print(f"Unsupported files: {len(summary['unsupported_files'])}")
    print(f"Failures: {len(summary['failures'])}")

    for artist_name in summary["skipped_artists"]:
        print(f"Skipped artist: {artist_name}")

    for failure in summary["failures"]:
        print(f"Failure: {failure}")

    return summary


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


## @name Application Entry Point
# @{
def main(args) -> int:
    '''
    @brief Module entry point.

    @details Takes command line arguments and executes per arguments.

    @dotfile flow.dot "Application startup and task flow"

    @param args {argparse.Namespace} Arguments for execution.

    @return exit_code {int} Process exit code for the requested subcommand.

    @exception {NotImplementedError} Indicates a subcommand has not been implemented.
    @exception {Exception} Handles unforeseen errors.
    '''

    try:
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
            get_ffprobe_tags(file_path)

        if args.subcommand == "get-mutagen-tags":
            file_path = getattr(args, "file")
            tags = get_mutagen_tags(file_path)
            # mutagen returns tags as ASFTags, ID3Tags, MP4Tags objects, Vorbis objects
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
            target = getattr(args, "target")
            level_normalize_walk(tld_path, norm_type, target)

        if args.subcommand == "list-audio":
            tld_path = getattr(args, "tld")
            list_audio(tld_path)

        if args.subcommand == "list-type":
            tld_path = getattr(args, "tld")
            file_pattern = getattr(args, "pattern")
            list_type(tld_path, file_pattern)

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

        if args.subcommand == "update-genres-from-csv":
            tld_path = getattr(args, "tld")
            csv_path = getattr(args, "csv")
            summary = update_genres_from_csv(tld_path, csv_path)
            if summary["failures"]:
                return 1

        if args.subcommand == "update-m3u":
            tld_path = getattr(args, "tld")
            input_m3u = getattr(args, "m3u")
            update_paths(tld_path, input_m3u)

        if args.subcommand == "update-walk":
            tld_path = getattr(args, "tld")
            update_walk(tld_path)

    except Exception as e:
        logger.exception(f"Exception propagated to main: {type(e).__name__}: {e}", stack_info=True)
        return 1
    else:
        return 0
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
        subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

        # convert audio file specified to mp3 format
        # 1 mandatory arg, the audio file path
        # 1 optional arg, the target directory for exported files
        # convert-file "C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a"
        # convert-file "F:\Rick\RickPrepped\Bee Gees\Tales from the Brothers Gibb A History in Song 1967-1990\Bee Gees-Sir Geoffrey Saved The World.mp3"
        convert_file_parser = subparsers.add_parser("convert-file", help="Converts an audio file to mp3")
        convert_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        convert_file_parser.add_argument("--target", type=str, help="optional target directory for exported files")
        convert_file_parser.set_defaults(func=convert_file)

        # convert all audio files found in top level directory
        # 1 mandatory arg, the start path (can be tld, fld, or sld)
        # 1 optional arg, the file pattern to match (.flac, .mp3, .m4a .wma)
        # 1 optional arg, the target directory for exported files
        # convert-walk C:\Music --pattern .m4a
        # convert-walk C:\Music
        # convert-walk C:\Music\Abba
        # convert-walk C:\Music\Abba\Waterloo
        convert_walk_parser = subparsers.add_parser("convert-walk", help="Converts all audio files to mp3")
        convert_walk_parser.add_argument("tld", type=existing_path, help="mandatory starting directory")
        convert_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
        convert_walk_parser.add_argument("--target", type=str, help="optional target directory for exported files")
        convert_walk_parser.set_defaults(func=convert_walk)

        # create album directories
        # 1 mandatory arg, the tld path (must be the tld, fld and sld will not work)
        # create-albums C:\Music
        create_albums_parser = subparsers.add_parser("create-albums", help="Create album sub-directories")
        create_albums_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        create_albums_parser.set_defaults(func=create_albums)

        # ebu normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # 1 optional arg, the target directory for exported files
        # ebu-file "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"
        ebu_file_parser = subparsers.add_parser("ebu-file", help="EBU R128 normalizes a mp3 audio file level")
        ebu_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        ebu_file_parser.add_argument("--target", type=str, help="optional target directory for exported files")
        ebu_file_parser.set_defaults(func=ebu_file)

        # extract album art from specified audio file
        # 1 mandatory arg, the path to audio file
        # extract-file "C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"
        extract_file_parser = subparsers.add_parser("extract-file", help="Extracts embedded art from audio file")
        extract_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        extract_file_parser.set_defaults(func=extract_file)

        # extract album art from all audio files found in top level directory
        # 1 mandatory arg, the start path (can be tld or fld, but not sld)
        # 1 optional arg, the file pattern to match (.flac, .mp3, .m4a, .wma)
        # extract-walk C:\Music --pattern .flac
        # extract-walk C:\Music --pattern .mp3
        # extract-walk C:\Music --pattern .m4a
        # extract-walk C:\Music --pattern .wma
        # extract-walk C:\Music\Abba
        # extract-walk C:\Music
        extract_walk_parser = subparsers.add_parser("extract-walk", help="Extracts embedded art from all audio files")
        extract_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        extract_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
        extract_walk_parser.set_defaults(func=extract_walk)

        # get ffprobe media information for a file
        # 1 mandatory arg, the path to audio file
        # get-ffprobe-media-info "C:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a"
        # get-ffprobe-media-info D:\MusicProcessing\tests\Music\Cream\Goodbye\Cream-Goodbye.flac
        get_ffprobe_media_info_parser = subparsers.add_parser(
            "get-ffprobe-media-info", help="Gets ffprobe media info for audio file"
        )
        get_ffprobe_media_info_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        get_ffprobe_media_info_parser.set_defaults(func=get_ffprobe_media_info)

        # get ffprobe media information for files
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file pattern to match (.flac, .mp3, .m4a, .wma)
        # get-ffprobe-media-info-walk C:\Music --pattern .mp3``
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
        # get-ffprobe-tags "C:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a"
        get_ffprobe_tags_parser = subparsers.add_parser("get-ffprobe-tags", help="Gets ffprobe metadata tags for audio file")
        get_ffprobe_tags_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        get_ffprobe_tags_parser.set_defaults(func=get_ffprobe_tags)

        # get mutagen metadata tags for file
        # 1 mandatory arg, the path to audio file
        # get-mutagen-tags F:\RickPrepped\Cream\Goodbye\Cream-Badge.flac
        get_mutagen_tags_parser = subparsers.add_parser("get-mutagen-tags", help="Gets metadata tags from audio file")
        get_mutagen_tags_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        get_mutagen_tags_parser.set_defaults(func=get_mutagen_tags)

        # get metadata tags from all audio files found in top level directory
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file pattern to match (.flac, .mp3, .m4a .wma)
        # 1 optional arg, use ffprobe boolean
        # get-tags-walk C:\Music --pattern .mp3 --ffprobe True
        # get-tags-walk C:\Music --pattern .m4a --ffprobe True
        # get-tags-walk C:\Music --pattern .wma --ffprobe True
        # get-tags-walk C:\Music --pattern .flac --ffprobe True
        # @todo need to test this
        # get-tags-walk D:\MusicProcessing\tests\Music --ffprobe True
        get_tags_walk_parser = subparsers.add_parser("get-tags-walk", help="Gets metadata tags from audio files")
        get_tags_walk_parser.add_argument("tld", type=existing_path, help="mandatory full path to audio file")
        get_tags_walk_parser.add_argument("--pattern", type=str, help="optional file pattern")
        get_tags_walk_parser.add_argument("--ffprobe", type=bool, help="optional ffprobe tags")
        get_tags_walk_parser.set_defaults(func=get_tags_walk)

        # gets set of unique ffprobe metadata tag keys for entire collection
        # 1 mandatory arg, the tld path
        # get-unique-media C:\Music
        get_unique_media_parser = subparsers.add_parser("get-unique-media", help="Gets set of unique ffprobe tags from collection")
        get_unique_media_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        get_unique_media_parser.set_defaults(func=get_unique_media)

        # level normalize mp3 files from tld
        # 2 mandatory arg, the tld path and the normalization type (ebu, peak, rms)
        # 1 optional arg, the target directory for exported files
        # level-normalize-walk C:\Music ebu
        # level-normalize-walk C:\Music peak
        # level-normalize-walk C:\Music rms
        level_normalize_walk_parser = subparsers.add_parser("level-normalize-walk", help="Normalizes files with specified pattern")
        level_normalize_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        level_normalize_walk_parser.add_argument("type", type=str, help="mandatory normalization type")
        level_normalize_walk_parser.add_argument("--target", type=str, help="optional target directory for exported files")
        level_normalize_walk_parser.set_defaults(func=level_normalize_walk)

        # list all audio files
        # 1 mandatory arg, the tld path
        # list-audio C:\Music
        list_audio_parser = subparsers.add_parser("list-audio", help="Generates a csv containing full path for all audio files")
        list_audio_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        list_audio_parser.set_defaults(func=list_audio)

        # list files by extension
        # 1 mandatory arg, the tld path
        # 1 optional arg, the file extension (.flac, .mp3, .m4a .wma)
        # list-type C:\Music --pattern .flac
        # list-type C:\Music --pattern .mp3
        # list-type C:\Music --pattern .m4a
        # list-type C:\Music --pattern .wma
        # list-type C:\Music
        list_type_parser = subparsers.add_parser(
            "list-type", help="Generates a csv containing full file path for an audio file type"
        )
        list_type_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        list_type_parser.add_argument("--pattern", type=str, help="optional file pattern")
        list_type_parser.set_defaults(func=list_type)

        # normalize a FLAC filename from its metadata
        # 1 mandatory arg, the audio file path
        # normalize-flac-filename C:\Music\song.flac
        normalize_flac_filename_parser = subparsers.add_parser("normalize-flac-filename", help="Renames a FLAC from its metadata")
        normalize_flac_filename_parser.add_argument("file", type=existing_file, help="mandatory full path to FLAC file")
        normalize_flac_filename_parser.set_defaults(func=normalize_flac_filename)

        # normalize an mp3 filename from its metadata
        # 1 mandatory arg, the audio file path
        # normalize-mp3-filename "C:\Music\song.mp3"
        normalize_mp3_filename_parser = subparsers.add_parser("normalize-mp3-filename", help="Renames an MP3 from its metadata")
        normalize_mp3_filename_parser.add_argument("file", type=existing_file, help="mandatory full path to MP3 file")
        normalize_mp3_filename_parser.set_defaults(func=normalize_mp3_filename)

        # normalize an M4A filename from its metadata
        # 1 mandatory arg, the audio file path
        # normalize-mp4-filename C:\Music\song.m4a
        normalize_mp4_filename_parser = subparsers.add_parser("normalize-mp4-filename", help="Renames an M4A from its metadata")
        normalize_mp4_filename_parser.add_argument("file", type=existing_file, help="mandatory full path to M4A file")
        normalize_mp4_filename_parser.set_defaults(func=normalize_mp4_filename)

        # normalize an WMA filename from its metadata
        # 1 mandatory arg, the audio file path
        # normalize-wma-filename C:\Music\song.wma
        normalize_wma_filename_parser = subparsers.add_parser("normalize-wma-filename", help="Renames a WMA from its metadata")
        normalize_wma_filename_parser.add_argument("file", type=existing_file, help="mandatory full path to WMA file")
        normalize_wma_filename_parser.set_defaults(func=normalize_wma_filename)

        # normalize audio filenames from metadata for all acceptable audio file types in directory
        # 1 mandatory arg, the start path (can be tld, fld, or sld)
        # normalize-filename-walk "F:\Rick\RickPrepped"
        # normalize-filename-walk "F:\Rick\RickPrepped\Duffy"
        # normalize-filename-walk "F:\Rick\RickPrepped\Duffy\Rockferry"
        normalize_filename_walk_parser = subparsers.add_parser("normalize-filename-walk", help="Renames audio files from metadata")
        normalize_filename_walk_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        normalize_filename_walk_parser.set_defaults(func=normalize_filename_walk)

        # remove empty album directories
        # 1 mandatory arg, the tld path
        # remove-empty-albums C:\Music
        remove_empty_albums_parser = subparsers.add_parser("remove-empty-albums", help="Remove empty album sub-directories")
        remove_empty_albums_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        remove_empty_albums_parser.set_defaults(func=remove_empty_albums)

        # remove files matching specified file pattern
        # 1st mandatory args, the start path (can be tld, fld, or sld)
        # 2nd mandatory arg, the file pattern
        # remove-pattern C:\Music *.db
        # remove-pattern C:\Music *.ini
        # remove-pattern C:\Music AlbumArtSmall.jpg
        # remove-pattern C:\Music AlbumArt*Small.jpg
        # remove-pattern C:\Music AlbumArt*Large.jpg
        remove_pattern_parser = subparsers.add_parser("remove-pattern", help="Removes files with specified pattern")
        remove_pattern_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        remove_pattern_parser.add_argument("pattern", type=str, help="mandatory file pattern")
        remove_pattern_parser.set_defaults(func=remove_pattern)

        # remove files matching a hard-coded set of patterns
        # 1 mandatory arg, the tld path
        # remove-set-list "F:\Rick\RickPrepped\Huey Lewis & The News"
        remove_set_list_parser = subparsers.add_parser("remove-set-list", help="Removes files matching a hard-coded set of patterns")
        remove_set_list_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        remove_set_list_parser.set_defaults(func=remove_set_list)

        # rename album directories based on metadata
        # 1 mandatory arg, the tld path
        # rename-album-directories "F:\Rick\RickPrepped"
        rename_album_directories_parser = subparsers.add_parser("rename-album-directories", help="Renames album directories based on metadata")
        rename_album_directories_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        rename_album_directories_parser.set_defaults(func=rename_album_directories)

        # peak normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # 1 optional arg, the target directory for exported files
        # peak-file "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"
        peak_file_parser = subparsers.add_parser("peak-file", help="Peak normalizes a mp3 audio file level")
        peak_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        peak_file_parser.add_argument("--target", type=str, help="optional target directory for exported files")
        peak_file_parser.set_defaults(func=peak_file)

        # rms normalize an audio file (destructive)
        # 1 mandatory arg, the path to audio file
        # 1 optional arg, the target directory for exported files
        # rms-file "C:\ConvertedMusic\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.mp3"
        rms_file_parser = subparsers.add_parser("rms-file", help="Rms normalizes a mp3 audio file level")
        rms_file_parser.add_argument("file", type=existing_file, help="mandatory full path to audio file")
        rms_file_parser.add_argument("--target", type=str, help="optional target directory for exported files")
        rms_file_parser.set_defaults(func=rms_file)

        # set album art file
        # 1 mandatory arg, the tld path
        # set-album-art C:\Music
        set_album_art_parser = subparsers.add_parser("set-album-art", help="Set album art file")
        set_album_art_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        set_album_art_parser.set_defaults(func=set_album_art)

        # update m3u playlist
        # 2 mandatory args, the tld path and the m3u path
        # update-m3u D:\MusicProcessing\tests\Music D:\MusicProcessing\tests\Music\test.m3u
        # update-walk C:\Music
        update_m3u_parsers = subparsers.add_parser("update-m3u", help="Update playlist paths")
        update_m3u_parsers.add_argument("tld", type=existing_path, help="mandatory top level directory")
        update_m3u_parsers.add_argument("m3u", type=existing_file, help="mandatory m3u file path")
        update_m3u_parsers.set_defaults(func=update_paths)

        # update genre metadata from artist directory mappings in a CSV file
        # 2 mandatory args, the tld path and artist genre CSV path
        # update-genres-from-csv F:/Rick/RickPrepped D:/MusicProcessing/src/generated_files/csv_files/artist_genre.csv
        update_genres_parser = subparsers.add_parser(
            "update-genres-from-csv", help="Updates genre metadata from artist genre CSV mappings"
        )
        update_genres_parser.add_argument("tld", type=existing_path, help="mandatory top level directory")
        update_genres_parser.add_argument("csv", type=existing_file, help="mandatory artist genre CSV file")
        update_genres_parser.set_defaults(func=update_genres_from_csv)

        # update m3u playlist walk
        # 1 mandatory arg, the tld path
        # update-walk C:\Music
        update_walk_parsers = subparsers.add_parser("update-walk", help="Update playlist paths")
        update_walk_parsers.add_argument("tld", type=existing_path, help="mandatory top level directory")
        update_walk_parsers.set_defaults(func=update_walk)

        args = parser.parse_args()
        sys.exit(main(args))

    except Exception as e:
        logger.exception(f"Exception propagated to entry point: {type(e).__name__}: {e}", stack_info=True)
