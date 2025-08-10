'''
@package src
@brief Holds package level constants and imports used by other modules.
'''

# using absolute import as don't expect to be re-organizing directories
from src.errors import JSONOutputError
from src.errors import PathInfoError
from src.errors import PlaylistError
from src.errors import MusicProcessingError

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
LOG_DIR = "logs"

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

## @var UTF8
# @brief utf encoding for file writing
# @details use this when configuring file access
UTF8 = "utf-8"

## @var __all__
# @brief Exposes variables for importing by other modules.
# @details In modules needing the constant add `from src import AUDIO_EXTS`
# @details In modules needing the constant add `from src import AUDIO_FILES`
# @details In modules needing the constant add `from src import AUDIO_TYPES`
# @details In modules needing the constant add 'from src import EXPORT_TLD`
# @details In modules needing the constant add 'from src import ERROR_LOG_FORMAT
# @details In modules needing the constant add 'from src import FOLDER_ART'
# @details In modules needing the constant add 'from src import LOG_DIR
# @details In modules needing the constant add 'from src import LOG_EXT
# @details In modules needing the constant add `from src import PLAYLIST_EXTS`
# @details In modules needing the constant add `from src import PLAYLIST_TYPES`
# @details In modules needing the constant add `from src import UTF8'
# @details In modules needing the error class, add `from src.errors import JSONOutputError'
# @details In modules needing the error class, add `from src.errors import PathInfoError'
# @details In modules needing the error class, add `from src.errors import PlaylistError'
# @details In modules needing the error class, add `from src.errors import MusicProcessingError'
__all__ = [
    "AUDIO_EXTS", "AUDIO_FILES", "AUDIO_TYPES",
    "EXPORT_TLD",
    "ERROR_LOG_FORMAT", "LOG_DIR", "LOG_EXT",  "UTF8",
    "FOLDER_ART",
    "PLAYLIST_EXTS", "PLAYLIST_TYPES",
    "JSONOutputError", "PathInfoError", "PlaylistError", "MusicProcessingError"
]
