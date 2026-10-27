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
from src.generated_files import GENERATED_PATH              # path to the directory where generated files are stored

# Local Module Errors
from src.errors import FfmpegProcessError                   # custom error for ffmpeg process failures
from src.errors import JSONOutputError                      # custom error for JSON output issues
from src.errors import MetadataTypeError                    # custom error for metadata type mismatches
from src.errors import MusicProcessingError                 # custom error for general music processing issues
from src.errors import PathInfoError                        # custom error for path information issues
from src.errors import PlaylistError                        # custom error for playlist related issues
from src.errors import VideoStreamError                     # custom error for video stream related issues

## @var APP_NAME
# @brief The app description
# @details use when needing application name/description
APP_NAME = "Music Processing"

## @var ARG_CLI_EXT
# @brief add argument cli
# @details use when needing mandatory file extension cli
ARG_CLI_EXT = "ext"

## @var ARG_CLI_FFPROBE
# @brief add argument cli
# @details use when needing optional ffprobe cli
ARG_CLI_FFPROBE = "ffprobe"

## @var ARG_CLI_FILE
# @brief add argument cli
# @details use when needing mandatory file cli
ARG_CLI_FILE = "file"

## @var ARG_CLI_PLAYLIST
# @brief add argument cli
# @details use when needing optional playlist cli
ARG_CLI_PLAYLIST = "m3u"

## @var ARG_CLI_PATTERN
# @brief add argument cli
# @details use when needing mandatory pattern cli
ARG_CLI_PATTERN = "pattern"

## @var ARG_CLI_TLD
# @brief add argument cli
# @details use when needing mandatory tld cli
ARG_CLI_TLD = "tld"

## @var ARG_CLI_TYPE
# @brief add argument cli
# @details use when needing mandatory type cli
ARG_CLI_TYPE = "type"

## @var ARG_HELP_AUDIO
# @brief add argument help
# @details use when needing mandatory file path input
ARG_HELP_AUDIO = "mandatory full path to audio file"

## @var ARG_HELP_FFPROBE
# @brief add argument help
# @details use when needing optional ffprobe input
ARG_HELP_FFPROBE = "optional ffprobe tags"

## @var ARG_HELP_FILE
# @brief add argument help
# @details use when needing optional file extension
ARG_HELP_FILE = "optional file extension"

## @var ARG_HELP_NORMAL
# @brief add argument help
# @details use when needing mandatory normalization type
ARG_HELP_NORMAL = "mandatory normalization type"

## @var ARG_HELP_PATTERN_MAN
# @brief add argument help
# @details use when needing mandatory pattern input
ARG_HELP_PATTERN_MAN = "mandatory file pattern"

## @var ARG_HELP_PATTERN_OPT
# @brief add argument help
# @details use when needing optional pattern input
ARG_HELP_PATTERN_OPT = "optional file pattern"

## @var ARG_HELP_PLAYLIST
# @brief add argument help
# @details use when needing mandatory m3u file path
ARG_HELP_PLAYLIST = "mandatory m3u file path"

## @var ARG_HELP_TLD
# @brief add argument help
# @details use when needing mandatory directory input
ARG_HELP_TLD = "mandatory top level directory"

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
# @details In modules needing the method, add: `from src import add_module_handler`.
# @details In modules needing the constant, add: `from src import ASF_TYPE`.
# @details In modules needing the constant, add: `from src import AUDIO_EXTS`.
# @details In modules needing the constant, add: `from src import AUDIO_FILES`.
# @details In modules needing the constant, add: `from src import CSV_DIR`.
# @details In modules needing the constant, add: `from src import CSV_EXT`.
# @details In modules needing the constant, add: `from src import ERROR_LOG_FORMAT`.
# @details In modules needing the constant, add: `from src import FLAC_EXT`.
# @details In modules needing the constant, add: `from src import FLAC_TYPE`.
# @details In modules needing the constant, add: `from src import FOLDER_ART`.
# @details In modules needing the class, add: `from src.errors import FfmpegProcessError`.
# @details In modules needing the constant, add: `from src import ILT`.
# @details In modules needing the class, add: `from src.errors import JSONOutputError`.
# @details In modules needing the constant, add: `from src import LOG_DIR`.
# @details In modules needing the constant, add: `from src import LOG_EXT`.
# @details In modules needing the constant, add: `from src import LRA`.
# @details In modules needing the constant, add: `from src import M3U_EXT`.
# @details In modules needing the constant, add: `from src import M4A_EXT`.
# @details In modules needing the class, add: `from src.errors import MetadataTypeError`.
# @details In modules needing the constant, add: `from src import MP3_EXT`.
# @details In modules needing the constant, add: `from src import MP3_TYPE`.
# @details In modules needing the constant, add: `from src import MP4_TYPE`.
# @details In modules needing the constant, add: `from src import MUSIC_TLD`.
# @details In modules needing the class, add: `from src.errors import MusicProcessingError`.
# @details In modules needing the class, add: `from src.errors import PathInfoError`.
# @details In modules needing the constant, add: `from src import PLAYLIST_EXTS`.
# @details In modules needing the constant, add: `from src import PLAYLIST_TYPES`.
# @details In modules needing the class, add: `from src.errors import PlaylistError`.
# @details In modules needing the constant, add: `from src import RESULT_DIR`.
# @details In modules needing the constant, add: `from src import RESULT_EXT`.
# @details In modules needing the constant, add: `from src import TP`.
# @details In modules needing the constant, add: `from src import UTF8`.
# @details In modules needing the class, add: `from src.errors import VideoStreamError`.
# @details In modules needing the constant, add: `from src import WMA_EXT`.
__all__ = [
    "add_module_handler",
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
