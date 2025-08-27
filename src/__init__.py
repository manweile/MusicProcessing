'''
@package src
@brief Holds package level constants and imports used by other modules.
'''

# standard modules
import logging
import os

# local modules
from src.generated_files import GENERATED_FILES
from src.errors import JSONOutputError
from src.errors import MetadataTypeError
from src.errors import MusicProcessingError
from src.errors import PathInfoError
from src.errors import PlaylistError
from src.errors import VideoStreamError

## @var AUDIO_EXTS
# @brief audio file extensions in my collection
# @details use this when working with os library
AUDIO_EXTS = [".mp3", ".m4a", ".wma"]

## @var AUDIO_FILES
# @brief audio file type to mutagen class mapping
# @details use this when working with mutagen library
AUDIO_FILES = ["MP3", "MP4", "ASF"]

## @var AUDIO_TYPES
# @brief audio file types in my collection
# @details use this when you just need the type
AUDIO_TYPES = ["mp3", "m4a", "wma"]

## @var CSV_FILES
# @brief final part of csv files directory path
# @details use this to set csv files directory path
CSV_DIR = "csv_files"

## @var CSV_EXT
# @brief csv file extension
# @details use this to set extension for csv files
CSV_EXT = ".csv"

## @var EXPORT_TLD
# @brief the top level directory that holds music files
# @details use this when exporting manipulated audio files
EXPORT_TLD = "Music"

## @var ERROR_LOG_FORMAT
# @brief error log file format
# @details use this to set error logging file format
ERROR_LOG_FORMAT = '\n%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s'

## @var FOLDER_ART
# @brief name of album art jpg
# @details use this when need to set album art file name
FOLDER_ART = "Folder.jpg"

## @var LOG_DIR
# @brief final part of log files directory path
# @details use this to set log files directory path
LOG_DIR = "log_files"

## @var LOG_EXT
# @brief log file extension
# @details use this to set extension for log files
LOG_EXT = ".log"

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

## @var UTF8
# @brief utf encoding for file writing
# @details use this when configuring file access
UTF8 = "utf-8"

## @var __all__
# @brief Exposes variables for importing by other modules.
# @details In modules needing the constant add `from src import AUDIO_EXTS`
# @details In modules needing the constant add `from src import AUDIO_FILES`
# @details In modules needing the constant add `from src import AUDIO_TYPES`
# @details In modules needing the constant add 'from src import CSV_DIR
# @details In modules needing the constant add 'from src import CSV_EXT
# @details In modules needing the constant add 'from src import EXPORT_TLD`
# @details In modules needing the constant add 'from src import ERROR_LOG_FORMAT
# @details In modules needing the constant add 'from src import FOLDER_ART'
# @details In modules needing the constant add 'from src import LOG_DIR
# @details In modules needing the constant add 'from src import LOG_EXT
# @details In modules needing the constant add `from src import PLAYLIST_EXTS`
# @details In modules needing the constant add `from src import PLAYLIST_TYPES`
# @details In modules needing the constant add 'from src import RESULT_DIR
# @details In modules needing the constant add 'from src import RESULT_EXT
# @details In modules needing the constant add `from src import UTF8'
# @details In modules needing the error class, add `from src.errors import JSONOutputError'
# @details In modules needing the error class, add `from src.errors import MetadataTypeError'
# @details In modules needing the error class, add `from src.errors import MusicProcessingError'
# @details In modules needing the error class, add `from src.errors import PathInfoError'
# @details In modules needing the error class, add `from src.errors import PlaylistError'
# @details In modules needing the error class, add `from src.errors import VideoStreamError'
__all__ = [
    "AUDIO_EXTS", "AUDIO_FILES", "AUDIO_TYPES",
    "CSV_DIR", "CSV_EXT",
    "EXPORT_TLD",
    "ERROR_LOG_FORMAT",
    "LOG_DIR", "LOG_EXT",
    "FOLDER_ART",
    "PLAYLIST_EXTS", "PLAYLIST_TYPES",
    "RESULT_DIR", "RESULT_EXT",
    "UTF8",
    "JSONOutputError",
    "MetadataTypeError", "MusicProcessingError",
    "PathInfoError", "PlaylistError",
    "VideoStreamError"
]

levels = ("DEBUG", "INFO", "WARNING")
log_path = os.path.join(GENERATED_FILES, LOG_DIR)

# use name of package so logger is parent to loggers in other modules in same package
logger = logging.getLogger(__name__)

# override the default logging level WARN to lowest level so we can log all levels
logger.setLevel(logging.DEBUG)

# add a handler for each level and attach it to the single logger at top of hierarchy
for level in levels:
    level_log_file = f"{level.lower()}{LOG_EXT}"
    level_log_path = os.path.join(log_path, level_log_file)

    handler = logging.FileHandler(level_log_path, mode="a", encoding=UTF8)
    formatter = logging.Formatter(ERROR_LOG_FORMAT)

    handler.setFormatter(formatter)
    handler.setLevel(getattr(logging, level))

    logger.addHandler(handler)

logger.propagate = True


def add_module_handler(logger, basename, level=logging.DEBUG, format=ERROR_LOG_FORMAT, propagate=False):
    '''
    @brief Adds FileHandler to logger.

    @details Logger is expected to be defined with __name__ dunder by calling function.
    @details basename is expected to be defined by __file__ dunder in calling function.
    '''

    stem = os.path.splitext(basename)[0]
    log_file = stem + LOG_EXT
    log_path = os.path.join(GENERATED_FILES, LOG_DIR, log_file)

    formatter = logging.Formatter(format)

    handler = logging.FileHandler(log_path, encoding=UTF8)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    logger.addHandler(handler)
    logger.propagate = propagate
