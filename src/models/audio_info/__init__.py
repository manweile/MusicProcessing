'''
@package src.models.audio_info
@file src/models/audio_info/__init__.py
@author Gerald Manweiler

@brief Package for audio information processing.

@details Exposes audio-information model classes through a single package interface.

@version 1.0.0
@date 2026-09-21

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Classes
from src.models.audio_info.audio_art import AudioArt               # exposes audio artwork operations
# exposes audio metadata operations
from src.models.audio_info.audio_metadata import AudioMetadata
# exposes audio playlist operations
from src.models.audio_info.audio_playlist import AudioPlaylist
# exposes audio utility operations
from src.models.audio_info.audio_utilities import AudioUtilities

## @var __all__
# @brief Exposes class for importing by other modules.
# @details  In modules needing the class, add `from src.models.audio_info.audio_art import AudioArt`
# @details  In modules needing the class, add `from src.models.audio_info.audio_metadata import AudioMetadata`
# @details  In modules needing the class, add `from src.models.audio_info.audio_playlist import AudioPlaylist`
# @details  In modules needing the class, add `from src.models.audio_info.audio_utilities import AudioUtilities`
__all__ = [
    "AudioArt",
    "AudioMetadata",
    "AudioPlaylist",
    "AudioUtilities"
]
