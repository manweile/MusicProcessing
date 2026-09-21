'''
@package src
@file src/__init__.py
@author Gerald Manweiler

@brief Holds package level constants and imports used by other modules.

@details Also enables logging for the package.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Functions
from src.logging_config import add_module_handler           # for adding module-specific file handlers to loggers
from src.logging_config import configure_package_logging    # for configuring package-level file logging

# Local Module Constants
from src.generated_files import GENERATED_PATH              # path to the directory where generated files are stored

# Local Module Errors
from src.errors import FfmpegProcessError                   # custom error for ffmpeg process failures
from src.errors import JSONOutputError                      # custom error for JSON output issues
from src.errors import MetadataTypeError                    # custom error for metadata type mismatches
from src.errors import MusicProcessingError                 # custom error for general music processing issues
from src.errors import PathInfoError                        # custom error for path information issues
from src.errors import PlaylistError                        # custom error for playlist related issues
from src.errors import VideoStreamError                     # custom error for video stream related issues

## @var ASF_TYPE
# @brief mutagen audio file type
# @details use this when working with mutagen library
ASF_TYPE = "ASF"

## @var AUDIO_EXTS
# @brief audio file extensions in my collection
# @details use this when working with os library
AUDIO_EXTS = [".mp3", ".m4a", ".wma", ".flac"]

## @var AUDIO_FILES
# @brief audio file type to mutagen class mapping
# @details use this when working with mutagen library
AUDIO_FILES = ["MP3", "MP4", "ASF", "FLAC"]

## @var CSV_FILES
# @brief final part of csv files directory path
# @details use this to set csv files directory path
CSV_DIR = "csv_files"

## @var CSV_EXT
# @brief csv file extension
# @details use this to set extension for csv files
CSV_EXT = ".csv"

## @var ERROR_LOG_FORMAT
# @brief error log file format
# @details use this to set error logging file format
ERROR_LOG_FORMAT = '\n%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s'

## @var FLAC_EXT
# @brief flac file type extension
# @details use this when needing just this file type extension and not file list of valid extensions
FLAC_EXT = ".flac"

## @var FLAC_TYPE
# @brief mutagen audio file type
# @details use this when working with mutagen library
FLAC_TYPE = "FLAC"

## @var FOLDER_ART
# @brief name of album art jpg
# @details use this when need to set album art file name
FOLDER_ART = "Folder.jpg"

## @var ILT
# @brief integrated loudness target
# @details use this for ebu r128 normalization AES recommended value for streaming
ILT = "-16.0"

## @var LOG_DIR
# @brief final part of log files directory path
# @details use this to set log files directory path
LOG_DIR = "log_files"

## @var LOG_EXT
# @brief log file extension
# @details use this to set extension for log files
LOG_EXT = ".log"

## @var LRA
# @brief loudness range target
# @details use this for ebu 128 normalization wider range than AES default of 7
LRA = "11.0"

## @var M4A_EXT
# @brief m4a file typer extension
# @details use this when needing just this file type extension and not file list of valid extensions
M4A_EXT = ".m4a"

## @var MP3_EXT
# @brief mp3 file typer extension
# @details use this when needing just this file type extension and not file list of valid extensions
MP3_EXT = ".mp3"

## @var MP3_TYPE
# @brief mutagen audio file type
# @details use this when working with mutagen library
MP3_TYPE = "MP3"

## @var MP4_TYPE
# @brief mutagen audio file type
# @details use this when working with mutagen library
MP4_TYPE = "MP4"

## @var MUSIC_TLD
# @brief the top level directory that holds music files
# @details use this when exporting manipulated audio files
MUSIC_TLD = "Music"

## @var PLAYLIST_EXTS
# @brief playlist file extensions in my collection
# @details use this when working with os library
PLAYLIST_EXTS = [".m3u"]

## @var PLAYLIST_TYPES
# @brief playlist file types in my collection
# @details use this when you just need the type
PLAYLIST_TYPES = ["m3u"]

## @var RESULTS_FILES
# @brief final part of results files directory path
# @details use this to set result files directory path
RESULT_DIR = "result_files"

## @var RESULT_EXT
# @brief result text file extension
# @details use this to set extension for result text files
RESULT_EXT = ".txt"

## @var TP
# @brief loudnorm maximum true peak
# @details use this for ebu 128 normalization extra headroom
TP = "-2.0"

## @var UTF8
# @brief utf encoding for file writing
# @details use this when configuring file access
UTF8 = "utf-8"

## @var WMA_EXT
# @brief wma file type extension
# @details use this when needing just this file type extension and not file list of valid extensions
WMA_EXT = ".wma"

# Configure package-level logging
src_logger = configure_package_logging(
    GENERATED_PATH,
    CSV_DIR,
    LOG_DIR,
    RESULT_DIR,
    LOG_EXT,
    UTF8,
    ERROR_LOG_FORMAT
)

## @var __all__
# @brief Exposes variables for importing by other modules.
# @details In modules needing the constant add 'from src import <constant>'
# @details In modules needing the error class, add 'from src.errors import <error>'
__all__ = [
    "ASF_TYPE",
    "AUDIO_EXTS",
    "AUDIO_FILES",
    "CSV_DIR",
    "CSV_EXT",
    "ERROR_LOG_FORMAT",
    "LOG_DIR",
    "LOG_EXT",
    "FLAC_EXT",
    "FLAC_TYPE",
    "FOLDER_ART",
    "ILT",
    "LRA",
    "M4A_EXT",
    "MP3_EXT",
    "MP3_TYPE",
    "MP4_TYPE",
    "MUSIC_TLD",
    "PLAYLIST_EXTS",
    "PLAYLIST_TYPES",
    "RESULT_DIR",
    "RESULT_EXT",
    "TP",
    "UTF8",
    "WMA_EXT",
    "FfmpegProcessError",
    "JSONOutputError",
    "MetadataTypeError",
    "MusicProcessingError",
    "PathInfoError",
    "PlaylistError",
    "VideoStreamError",
    "add_module_handler"
]
