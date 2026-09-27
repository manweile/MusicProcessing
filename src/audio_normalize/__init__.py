'''
@package src.audio_normalize
@file src/audio_normalize/__init__.py
@author Gerald Manweiler

@brief Package for audio normalization processing.

@details Exposes audio normalization functionality through a single package interface.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Classes
# for audio normalization functionality
from src.audio_normalize.audio_normalization import AudioNormalization

## @var __all__
# @brief Exposes class for importing by other modules.
# @details In modules needing the class, add `from src.audio_normalize import AudioNormalization`.
__all__ = [
    "AudioNormalization"
]
