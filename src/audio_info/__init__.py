'''
@package src.audio_info
@file src/audio_info/__init__.py
@author Gerald Manweiler

@brief Provides compatibility imports for audio information models.

@details Re-exports the model package while legacy imports are being migrated.

@version 1.0.0
@date 2026-11-10

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import sys                                                  # for registering legacy module paths

# Local Module Classes
from src.models.audio_info import AudioArt                  # exposes audio artwork operations
from src.models.audio_info import AudioMetadata             # exposes audio metadata operations
from src.models.audio_info import AudioPlaylist             # exposes audio playlist operations
from src.models.audio_info import AudioUtilities            # exposes audio utility operations

from src.models.audio_info import audio_art                 # provides legacy audio-art module access
from src.models.audio_info import audio_metadata            # provides legacy metadata module access
from src.models.audio_info import audio_playlist            # provides legacy playlist module access
from src.models.audio_info import audio_utilities           # provides legacy utility module access

sys.modules[f"{__name__}.audio_art"] = audio_art
sys.modules[f"{__name__}.audio_metadata"] = audio_metadata
sys.modules[f"{__name__}.audio_playlist"] = audio_playlist
sys.modules[f"{__name__}.audio_utilities"] = audio_utilities

## @var __all__
# @brief Exposes public compatibility classes.
# @details The classes are implemented in src.models.audio_info.
__all__ = [
    "AudioArt",
    "AudioMetadata",
    "AudioPlaylist",
    "AudioUtilities"
]
