'''
@module constants
@file constants.py
@author Gerald Manweiler

@brief Defines the command-line constants module.

@details Defines constants used by the command-line interface.

@version 1.0.0
@date 2026-11-02

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

## @var ARG_CLI_CSV
# @brief add argument cli
# @details use when needing mandatory CSV file
ARG_CLI_CSV = "csv"

## @var ARG_CLI_FFPROBE
# @brief add argument cli
# @details use when needing optional ffprobe cli
ARG_CLI_FFPROBE = "ffprobe"

## @var ARG_CLI_FILE
# @brief add argument cli
# @details use when needing mandatory file cli
ARG_CLI_FILE = "file"

## @var ARG_CLI_PATTERN
# @brief add argument cli
# @details use when needing mandatory pattern cli
ARG_CLI_PATTERN = "pattern"

## @var ARG_CLI_PLAYLIST
# @brief add argument cli
# @details use when needing optional playlist cli
ARG_CLI_PLAYLIST = "m3u"

## @var ARG_CLI_TARGET
# @brief add argument cli
# @details use when needing optional target path cli
ARG_CLI_TARGET = "target"

## @var ARG_CLI_TLD
# @brief add argument cli
# @details use when needing mandatory tld cli
ARG_CLI_TLD = "tld"

## @var ARG_CLI_TYPE
# @brief add argument cli
# @details use when needing mandatory type cli
ARG_CLI_TYPE = "type"

## @var ARG_HELP_OPT_FFPROBE
# @brief add argument help
# @details use when needing optional ffprobe input
ARG_HELP_OPT_FFPROBE = "optional use ffprobe True"

## @var ARG_HELP_OPT_PATTERN
# @brief add argument help
# @details use when needing optional pattern input
ARG_HELP_OPT_PATTERN = "optional file ext {.flac|.mp3|.m4a|.wma}"

## @var ARG_HELP_OPT_TARGET
# @brief add argument help
# @details use when needing optional target path input
ARG_HELP_OPT_TARGET = "optional target path"

## @var ARG_HELP_AUDIO
# @brief add argument help
# @details use when needing mandatory file path input
ARG_HELP_AUDIO = "mandatory audio file path"

## @var ARG_HELP_GENRE
# @brief add argument help
# @details use when needing mandatory genre input
ARG_HELP_GENRE = "mandatory genre csv file path"

## @var ARG_HELP_LEVEL
# @brief add argument help
# @details use when needing mandatory normalization type
ARG_HELP_LEVEL = "mandatory level type {ebu|peak|rms}"

## @var ARG_HELP_PATTERN
# @brief add argument help
# @details use when needing mandatory pattern input
ARG_HELP_PATTERN = "mandatory file pattern"

## @var ARG_HELP_PLAYLIST
# @brief add argument help
# @details use when needing mandatory m3u file path
ARG_HELP_PLAYLIST = "mandatory m3u file path"

## @var ARG_HELP_TLD
# @brief add argument help
# @details use when needing mandatory directory input
ARG_HELP_TLD = "mandatory start path tld only"

## @var ARG_HELP_TLD_FLD
# @brief add argument help
# @details use when needing mandatory mandatory tld or fld start path
ARG_HELP_TLD_FLD = "mandatory start path tld/fld"

## @var ARG_HELP_TLD_FLD_SLD
# @brief add argument help
# @details use when needing mandatory tld, fld, or sld start path
ARG_HELP_TLD_FLD_SLD = "mandatory start path tld/fld/sld"

## @var __all__
# @brief Exposes package members for importing by other modules.
# @details Include all CLI argument and help constants.
# @details In modules needing the constant, add `from src.cli.constants import <CONSTANT_NAME>`.
__all__ = [
    "ARG_CLI_CSV",
    "ARG_CLI_FFPROBE",
    "ARG_CLI_FILE",
    "ARG_CLI_PATTERN",
    "ARG_CLI_PLAYLIST",
    "ARG_CLI_TARGET",
    "ARG_CLI_TLD",
    "ARG_CLI_TYPE",
    "ARG_HELP_OPT_FFPROBE",
    "ARG_HELP_OPT_PATTERN",
    "ARG_HELP_OPT_TARGET",
    "ARG_HELP_AUDIO",
    "ARG_HELP_GENRE",
    "ARG_HELP_LEVEL",
    "ARG_HELP_PATTERN",
    "ARG_HELP_PLAYLIST",
    "ARG_HELP_TLD",
    "ARG_HELP_TLD_FLD",
    "ARG_HELP_TLD_FLD_SLD"
]
