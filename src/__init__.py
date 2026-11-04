'''
@package src
@file src/__init__.py
@author Gerald Manweiler

@brief Package for shared MusicProcessing constants and imports.

@details Exposes shared constants, errors, and logging helpers for MusicProcessing modules.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Methods
from src.logging_config import add_module_handler           # for adding module-specific file handlers to loggers
from src.logging_config import configure_package_logging    # for configuring package-level file logging

# Local Module Constants
from src.core.constants import APP_NAME                     # application name/description
from src.core.constants import ASF_TYPE                     # ASF Mutagen audio file type
from src.core.constants import AUDIO_EXTS                   # Supported audio file extensions
from src.core.constants import AUDIO_FILES                  # Supported Mutagen audio file types
from src.core.constants import CSV_DIR                      # CSV output directory name
from src.core.constants import CSV_EXT                      # CSV file extension
from src.core.constants import ERROR_LOG_FORMAT             # Error log record format
from src.core.constants import FLAC_EXT                     # FLAC file extension
from src.core.constants import FLAC_TYPE                    # FLAC Mutagen audio file type
from src.core.constants import FOLDER_ART                   # Album-art file name
from src.core.constants import ILT                          # Integrated loudness target
from src.core.constants import LOG_DIR                      # Log output directory name
from src.core.constants import LOG_EXT                      # Log file extension
from src.core.constants import LRA                          # Loudness range target
from src.core.constants import M3U_EXT                      # M3U file extension
from src.core.constants import M4A_EXT                      # M4A file extension
from src.core.constants import MP3_EXT                      # MP3 file extension
from src.core.constants import MP3_TYPE                     # MP3 Mutagen audio file type
from src.core.constants import MP4_TYPE                     # MP4 Mutagen audio file type
from src.core.constants import MUSIC_TLD                    # Music top-level domain
from src.core.constants import PLAYLIST_EXTS                # Supported playlist file extensions
from src.core.constants import PLAYLIST_TYPES               # Supported playlist file types
from src.core.constants import RESULT_DIR                   # Result output directory name
from src.core.constants import RESULT_EXT                   # Result file extension
from src.core.constants import TP                           # Temporary path
from src.core.constants import UTF8                         # UTF-8 encoding
from src.core.constants import WMA_EXT                      # WMA file extension
from src.core.paths import GENERATED_PATH                   # path to the directory where generated files are stored

# Local Module Errors
from src.errors import FfmpegProcessError                   # custom error for ffmpeg process failures
from src.errors import JSONOutputError                      # custom error for JSON output issues
from src.errors import MetadataTypeError                    # custom error for metadata type mismatches
from src.errors import MusicProcessingError                 # custom error for general music processing issues
from src.errors import PathInfoError                        # custom error for path information issues
from src.errors import PlaylistError                        # custom error for playlist related issues
from src.errors import VideoStreamError                     # custom error for video stream related issues

## @var src_logger
# @brief Configured package logger.
# @details Configures package-level logging for generated project files.
src_logger = configure_package_logging(
    GENERATED_PATH,
    CSV_DIR,
    LOG_DIR,
    RESULT_DIR,
    LOG_EXT,
    UTF8,
    ERROR_LOG_FORMAT
)

## @var __all__
# @brief Exposes package members for importing by other modules.
# @details In modules needing the constant, add `from src.core.constants import <CONSTANT_NAME>`.
# @details In modules needing the method, add: `from src import add_module_handler`.
# @details In modules needing the class, add: `from src.errors import <ErrorClass>`.
__all__ = [
    "add_module_handler",
    "APP_NAME",
    "ASF_TYPE",
    "AUDIO_EXTS",
    "AUDIO_FILES",
    "CSV_DIR",
    "CSV_EXT",
    "ERROR_LOG_FORMAT",
    "FLAC_EXT",
    "FLAC_TYPE",
    "FOLDER_ART",
    "FfmpegProcessError",
    "GENERATED_PATH",
    "ILT",
    "JSONOutputError",
    "LOG_DIR",
    "LOG_EXT",
    "LRA",
    "M3U_EXT",
    "M4A_EXT",
    "MetadataTypeError",
    "MP3_EXT",
    "MP3_TYPE",
    "MP4_TYPE",
    "MUSIC_TLD",
    "MusicProcessingError",
    "PathInfoError",
    "PLAYLIST_EXTS",
    "PLAYLIST_TYPES",
    "PlaylistError",
    "RESULT_DIR",
    "RESULT_EXT",
    "TP",
    "UTF8",
    "VideoStreamError",
    "WMA_EXT"
]
