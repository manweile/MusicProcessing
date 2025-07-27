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

## @var HOME
# @brief linux hdd mount point
# @details use this when parsing linux hdd path
HOME = "home"

## @var MEDIA
# @brief linux usb mount point
# @details use this when parsing linux usb path
MEDIA = "media"

## @var _PLAYLIST_EXTS
# @brief playlist file extensions in my collection
# @details use this when working with os library
_PLAYLIST_EXTS = [".m3u"]

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
# @details  In modules needing the constant add 'from src.MEDIA import MEDIA`
# @details  In modules needing the constant add `from src._PLAYLIST_EXTS import _PLAYLIST_EXTS`
# @details  In modules needing the constant add `from src.PLAYLIST_TYPES import PLAYLIST_TYPES`
__all__ = ["AUDIO_EXTS", "AUDIO_TYPES", "EXPORT_TLD", "HOME", "MEDIA", "_PLAYLIST_EXTS", "PLAYLIST_TYPES"]
