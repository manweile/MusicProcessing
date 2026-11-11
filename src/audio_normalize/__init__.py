'''
@package src.audio_normalize
@file src/audio_normalize/__init__.py
@author Gerald Manweiler

@brief Provides compatibility imports for audio normalization models.

@details Re-exports the model package while legacy imports are being migrated.

@version 1.0.0
@date 2026-11-10

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import sys                                                  # for registering legacy module paths

# Local Module Classes
from src.models.audio_normalize import AudioNormalization   # exposes audio normalization operations

from src.models.audio_normalize import audio_normalization  # provides legacy module access

sys.modules[f"{__name__}.audio_normalization"] = audio_normalization

## @var __all__
# @brief Exposes the public compatibility class.
# @details The class is implemented in src.models.audio_normalize.
__all__ = [
    "AudioNormalization"
]
