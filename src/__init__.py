'''
@package src
@brief Holds package level constants used by other modules.
'''

# from Mp3Tag program, I know I have these audio/playlist file extensions and types

## @var AUDIO_EXTS
# @brief audio file extensions in my collection
# @details use this when working with os library
AUDIO_EXTS = [".mp3", ".m4a", ".wma"]

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

## @var __all__
# @brief Exposes variables for importing by other modules.
# @details  In modules needing the constant add `from src.AUDIO_EXTS import AUDIO_EXTS`
# @details  In modules needing the constant add `from src.AUDIO_TYPES import AUDIO_TYPES`
# @details  In modules needing the constant add 'from src.EXPORT_TLD import EXPORT_TLD`
# @details  In modules needing the constant add 'from src.HOME import HOME`
# @details  In modules needing the constant add 'from src.FILE_LOG_FORMAT import FILE_LOG_FORMAT
# @details  In modules needing the constant add 'from src.LOG_DIR import LOG_DIR
# @details  In modules needing the constant add 'from src.LOG_EXT import LOG_EXT
# @details  In modules needing the constant add 'from src.MEDIA import MEDIA`
# @details  In modules needing the constant add `from src.PLAYLIST_EXTS import PLAYLIST_EXTS`
# @details  In modules needing the constant add `from src.PLAYLIST_TYPES import PLAYLIST_TYPES`
__all__ = ["AUDIO_EXTS", "AUDIO_TYPES", "EXPORT_TLD", "FILE_LOG_FORMAT", "HOME", "LOG_DIR", "LOG_EXT", "MEDIA", "PLAYLIST_EXTS", "PLAYLIST_TYPES"]
