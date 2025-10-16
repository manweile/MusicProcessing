'''
@package src
@brief Holds package level constants and imports used by other modules.
'''

# standard modules
import logging
import os
from logging import DEBUG, FileHandler, Formatter

# local module constants
from src.generated_files import GENERATED_PATH
# local module errors
from src.errors import FfmpegProcessError
from src.errors import JSONOutputError
from src.errors import MetadataTypeError
from src.errors import MusicProcessingError
from src.errors import PathInfoError
from src.errors import PlaylistError
from src.errors import VideoStreamError
# local module classes
from src.level_filter import LevelFilter

## @var ASF_TYPE
# @brief mutagen audio file type
# @details use this when working with mutagen library
ASF_TYPE = "ASF"

## @var AUDIO_EXTS
# @brief audio file extensions in my collection
# @details use this when working with os library
AUDIO_EXTS = [".mp3", ".m4a", ".wma"]

## @var AUDIO_FILES
# @brief audio file type to mutagen class mapping
# @details use this when working with mutagen library
AUDIO_FILES = ["MP3", "MP4", "ASF"]

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

## @var __all__
# @brief Exposes variables for importing by other modules.
# @details In modules needing the constant add 'from src import <constant>'
# @details In modules needing the error class, add 'from src.errors import <error>'
__all__ = [
    "ASF_TYPE",
    "AUDIO_EXTS", "AUDIO_FILES",
    "CSV_DIR", "CSV_EXT",
    "ERROR_LOG_FORMAT",
    "LOG_DIR", "LOG_EXT",
    "FOLDER_ART",
    "ILT",
    "LRA",
    "M4A_EXT", "MP3_EXT", "MP3_TYPE", "MP4_TYPE", "MUSIC_TLD",
    "PLAYLIST_EXTS", "PLAYLIST_TYPES",
    "RESULT_DIR", "RESULT_EXT",
    "TP",
    "UTF8",
    "WMA_EXT",
    "FfmpegProcessError",
    "JSONOutputError",
    "MetadataTypeError", "MusicProcessingError",
    "PathInfoError", "PlaylistError",
    "VideoStreamError"
]

r'''
MusicProcessing has multi-level logging setup.
from https://realpython.com/python-logging-source-code/#a-multi-handler-design tutorial.
All loggers wil have file handlers.
Every module will instantiate it's own logger.
This will cause all logging initiated within a module to log to that modules log.
Additionally, there will be level based loggers.
The debug logger will not have a filter, making it the master log repository.
The info through critical loggers will be filtered to only accept log records of their level.
'''
## @var handler
# @brief log file handler
# @details creates log file handler for log level
handler = FileHandler

## @var handler_formatter
# @brief logging formatter
# @details the logging format for log level
handler_formatter = Formatter

## @ var handler_level
# @brief handler log level
# @details the log level for handler
handler_level = int()

## @var levels
# @brief logging levels for project
# @details specifies what log levels will generate logs
levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

## @var level_log_file
# @brief log file name
# @details creates log file name from log level
level_log_file = str()

## @var level_log_path
# @brief log file path
# @details creates log file path for a log file
level_log_path = str()

## @var log_path
# @brief path to log files
# @details specifies fixed log path for project
log_path = os.path.join(GENERATED_PATH, LOG_DIR)

## @var src_logger
# @brief logger for package
# @details uses name of package so logger is parent to loggers in other modules in same package
src_logger = logging.getLogger(__name__)

# override the default logging level WARN to lowest level so we can log all levels
src_logger.setLevel(DEBUG)

# add a handler for each level and attach it to the single logger at top of hierarchy
for level in levels:
    level_log_file = f"{level.lower()}{LOG_EXT}"
    level_log_path = os.path.join(log_path, level_log_file)

    handler = FileHandler(level_log_path, mode="a", encoding=UTF8)

    handler_formatter = Formatter(ERROR_LOG_FORMAT)
    handler.setFormatter(handler_formatter)

    handler_level = getattr(logging, level)

    if level != "DEBUG":
        handler.addFilter(LevelFilter(handler_level, handler_level))

    src_logger.addHandler(handler)


def add_module_handler(logger, basename, level=DEBUG, format=ERROR_LOG_FORMAT, propagate=True):
    '''
    @brief Adds FileHandler to a logger.

    @details Logger is expected to be defined with __name__ dunder by calling module.
    @details basename is expected to be defined by __file__ dunder in calling module.

    @param logger (Logger) Logger instance for a module.
    @param basename {str} File handler log file name for logger.
    @param level {int} Optional, Logger & file handler logging level.
    @param format {str} Optional, File handler logging format.
    @param propagate {bool} Optional, Logger propagation to root logger.
    '''

    logger.setLevel(level)

    # log files always go to fixed location
    stem = os.path.splitext(basename)[0]
    log_file = stem + LOG_EXT
    log_path = os.path.join(GENERATED_PATH, LOG_DIR, log_file)

    formatter = Formatter(format)

    handler = FileHandler(log_path, encoding=UTF8)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    logger.addHandler(handler)
    logger.propagate = propagate
