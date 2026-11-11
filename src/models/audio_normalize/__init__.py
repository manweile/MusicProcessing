'''
@package src.models.audio_normalize
@file src/models/audio_normalize/__init__.py
@author Gerald Manweiler

@brief Package for audio normalization processing.

@details Exposes audio normalization functionality through a single package interface.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Classes
# exposes audio normalization operations
from src.models.audio_normalize.audio_normalization import AudioNormalization

## @var __all__
# @brief Exposes class for importing by other modules.
# @details In modules needing the class, add `from src.models.audio_normalize import AudioNormalization`.
__all__ = [
    "AudioNormalization"
]
