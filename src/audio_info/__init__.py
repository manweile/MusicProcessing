'''
@package audio_info
@file src/audio_info/__init__.py
@author Gerald Manweiler

@brief Package for audio information processing.

@details Exposes audio-information classes through a single package interface.

@version 1.0.0
@date 2026-09-21

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Classes
from src.audio_info.audio_art import AudioArt               # Exposes audio artwork operations.
from src.audio_info.audio_metadata import AudioMetadata     # Exposes audio metadata operations.
from src.audio_info.audio_playlist import AudioPlaylist     # Exposes audio playlist operations.
from src.audio_info.audio_utilities import AudioUtilities   # Exposes audio utility operations.

## @var __all__
# @brief Exposes class for importing by other modules.
# @details  In modules needing the class, add `from src.audio_info.audio_art import AudioArt`
# @details  In modules needing the class, add `from src.audio_info.audio_metadata import AudioMetadata`
# @details  In modules needing the class, add `from src.audio_info.audio_playlist import AudioPlaylist`
# @details  In modules needing the class, add `from src.audio_info.audio_utilities import AudioUtilities`
__all__ = [
    "AudioArt",
    "AudioMetadata",
    "AudioPlaylist",
    "AudioUtilities"
]
