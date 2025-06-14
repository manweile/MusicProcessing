'''
@package src
@brief Holds package level constants used by other modules.
'''

# from Mp3Tag program, I know I have these audio/playlist file extensions and types

## @var _AUDIO_EXTS
# @brief audio file extensions in my collection
# @details use this when working with os library
_AUDIO_EXTS = [".mp3", ".m4a", ".wma", ".wav"]

## @var _AUDIO_TYPES
# @brief audio file types in my collection
# @details use this when you just need the type
_AUDIO_TYPES = ["mp3", "m4a", "wma", "wav"]

## @var _PLAYLIST_EXTS
# @brief playlist file extensions in my collection
# @details use this when working with os library
_PLAYLIST_EXTS = [".m3u"]

## @var _PLAYLIST_TYPES
# @brief playlist file types in my collection
# @details use this when you just need the type
_PLAYLIST_TYPES = ["m3u"]

## @var __all__
# @brief Exposes variables for importing by other modules.
# @details  In modules needing the constant add `from src._AUDIO_EXTS import _AUDIO_EXTS`
# @details  In modules needing the constant add `from src._AUDIO_TYPES import _AUDIO_TYPES`
# @details  In modules needing the constant add `from src._PLAYLIST_EXTS import _PLAYLIST_EXTS`
# @details  In modules needing the constant add `from src._PLAYLIST_TYPES import _PLAYLIST_TYPES`
__all__ = ['_AUDIO_EXTS','_AUDIO_TYPES', '_PLAYLIST_EXTS', '_PLAYLIST_TYPES']