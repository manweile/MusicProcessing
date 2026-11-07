'''
@module errors
@file src/errors.py
@author Gerald Manweiler

@brief Defines the errors module shim.

@details Re-exports the custom exceptions used in the MusicProcessing module shim.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Modules
from src.core.errors import FfmpegProcessError              # Shim for old import path
from src.core.errors import JSONOutputError                 # Shim for old import path
from src.core.errors import MetadataTypeError               # Shim for old import path
from src.core.errors import MusicProcessingError            # Shim for old import path
from src.core.errors import MusicProcessingException        # Shim for old import path
from src.core.errors import PathInfoError                   # Shim for old import path
from src.core.errors import PlaylistError                   # Shim for old import path
from src.core.errors import VideoStreamError                # Shim for old import path
