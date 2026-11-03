'''
@module constants
@file constants.py
@author Gerald Manweiler

@brief Defines the core constants module.

@details Defines constants used by the core of the application.

@todo This module contains constants for the core of the application.<br>
They are not yet in use, just defined here.<br>
Currently, src/__init__.py contains the in-use definitions.<br>
Refer to docs/planning/mvc.plan.prompt.md for when they will be used.

@version 1.0.0
@date 2026-11-02

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

## @var APP_NAME
# @brief The app description
# @details use when needing application name/description
APP_NAME = "Music Processing"

## @var ASF_TYPE
# @brief ASF Mutagen audio file type.
# @details Identifies the Mutagen class name for ASF files.
ASF_TYPE = "ASF"

## @var AUDIO_EXTS
# @brief Supported audio file extensions.
# @details Identifies audio files during filesystem processing.
AUDIO_EXTS = [".mp3", ".m4a", ".wma", ".flac"]

## @var AUDIO_FILES
# @brief Supported Mutagen audio file types.
# @details Identifies the Mutagen class names handled by the project.
AUDIO_FILES = ["MP3", "MP4", "ASF", "FLAC"]

## @var CSV_DIR
# @brief CSV output directory name.
# @details Identifies the directory used for generated CSV files.
CSV_DIR = "csv_files"

## @var CSV_EXT
# @brief CSV file extension.
# @details Identifies generated comma-separated value files.
CSV_EXT = ".csv"

## @var ERROR_LOG_FORMAT
# @brief Error log record format.
# @details Defines the format used for logged error records.
ERROR_LOG_FORMAT = '\n%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s'

## @var FLAC_EXT
# @brief FLAC file extension.
# @details Identifies FLAC files independently of the supported-extension list.
FLAC_EXT = ".flac"

## @var FLAC_TYPE
# @brief FLAC Mutagen audio file type.
# @details Identifies the Mutagen class name for FLAC files.
FLAC_TYPE = "FLAC"

## @var FOLDER_ART
# @brief Album-art file name.
# @details Identifies the JPEG file used for album artwork.
FOLDER_ART = "Folder.jpg"

## @var ILT
# @brief Integrated loudness target.
# @details Defines the EBU R128 normalization target recommended for streaming.
ILT = "-16.0"

## @var LOG_DIR
# @brief Log output directory name.
# @details Identifies the directory used for generated log files.
LOG_DIR = "log_files"

## @var LOG_EXT
# @brief Log file extension.
# @details Identifies generated log files.
LOG_EXT = ".log"

## @var LRA
# @brief Loudness range target.
# @details Defines an EBU R128 range wider than the AES default of seven.
LRA = "11.0"

## @var M3U_EXT
# @brief M3U file extension.
# @details Identifies M3U playlist files independently of the supported-extension list.
M3U_EXT = ".m3u"

## @var M4A_EXT
# @brief M4A file extension.
# @details Identifies M4A files independently of the supported-extension list.
M4A_EXT = ".m4a"

## @var MP3_EXT
# @brief MP3 file extension.
# @details Identifies MP3 files independently of the supported-extension list.
MP3_EXT = ".mp3"

# @todo single use in audio_metadata.py
## @var MP3_TYPE
# @brief MP3 Mutagen audio file type.
# @details Identifies the Mutagen class name for MP3 files.
MP3_TYPE = "MP3"

# @todo single use in audio_metadata.py
## @var MP4_TYPE
# @brief MP4 Mutagen audio file type.
# @details Identifies the Mutagen class name for MP4 files.
MP4_TYPE = "MP4"

## @var MUSIC_TLD
# @brief Music top level directory name.
# @details Identifies the directory containing the source music collection.
MUSIC_TLD = "Music"

## @var PLAYLIST_EXTS
# @brief Supported playlist file extensions.
# @details Identifies playlist files during filesystem processing.
PLAYLIST_EXTS = [".m3u"]

## @var PLAYLIST_TYPES
# @brief Supported playlist file types.
# @details Identifies the supported playlist formats.
PLAYLIST_TYPES = ["m3u"]

## @var RESULT_DIR
# @brief Result output directory name.
# @details Identifies the directory used for generated result files.
RESULT_DIR = "result_files"

## @var RESULT_EXT
# @brief Result text-file extension.
# @details Identifies generated result text files.
RESULT_EXT = ".txt"

## @var TP
# @brief Loudnorm maximum true peak.
# @details Defines extra headroom for EBU R128 normalization.
TP = "-2.0"

## @var UTF8
# @brief UTF-8 text encoding.
# @details Configures text-file access with UTF-8 encoding.
UTF8 = "utf-8"

## @var WMA_EXT
# @brief WMA file extension.
# @details Identifies WMA files independently of the supported-extension list.
WMA_EXT = ".wma"

## @var __all__
# @brief Exposes package members for importing by other modules.
# @details In modules needing the constant, add `from src.core.constants import <CONSTANT_NAME>`.
__all__ = [
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
    "ILT",
    "LOG_DIR",
    "LOG_EXT",
    "LRA",
    "M3U_EXT",
    "M4A_EXT",
    "MP3_EXT",
    "MP3_TYPE",
    "MP4_TYPE",
    "MUSIC_TLD",
    "PLAYLIST_EXTS",
    "PLAYLIST_TYPES",
    "RESULT_DIR",
    "RESULT_EXT",
    "TP",
    "UTF8",
    "WMA_EXT"
]
