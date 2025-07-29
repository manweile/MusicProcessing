'''
@package src
@brief Holds package level constants used by other modules.
'''

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

## @var FILE_LOG_FORMAT
# @brief log file format
# @details use this to set log file format
FILE_LOG_FORMAT = '\n%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s'

## @var FOLDER_ART
# @brief name of album art jpg
# @details use this when need to set album art file name
FOLDER_ART = "Folder.jpg"

## @var HOME
# @brief linux hdd mount point
# @details use this when parsing linux hdd path
HOME = "home"

## @var LOG_DIR
# @brief final part of log files directory path
# @details use this to set log files directory path
LOG_DIR = "logs"

## @var LOG_EXT
# @brief log file extension
# @details use this to set extension for log files
LOG_EXT = ".log"

## @var MEDIA
# @brief linux usb mount point
# @details use this when parsing linux usb path
MEDIA = "media"

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
# @details In modules needing the constant add 'from src import FILE_LOG_FORMAT
# @details In modules needing the constant add 'from src import FOLDER_ART'
# @details In modules needing the constant add 'from src import HOME`
# @details In modules needing the constant add 'from src import LOG_DIR
# @details In modules needing the constant add 'from src import LOG_EXT
# @details In modules needing the constant add 'from src import MEDIA`
# @details In modules needing the constant add `from src import PLAYLIST_EXTS`
# @details In modules needing the constant add `from src import PLAYLIST_TYPES`
# @details In modules needing the constant add `from src import UTF8'
__all__ = [
    "AUDIO_EXTS",
    "AUDIO_FILES",
    "AUDIO_TYPES",
    "EXPORT_TLD",
    "FILE_LOG_FORMAT",
    "FOLDER_ART",
    "HOME",
    "LOG_DIR",
    "LOG_EXT",
    "MEDIA",
    "PLAYLIST_EXTS",
    "PLAYLIST_TYPES",
    "UTF8"
    ]
