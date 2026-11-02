'''
@module constants
@file constants.py
@author Gerald Manweiler

@brief Defines the command-line constants module.

@details Defines constants used by the command-line interface.

@todo This module contains constants for the command-line interface.<br>
They are not yet in use, just defined here.<br>
Refer to docs/planning/mvc.plan.prompt.md for when they will be used.

@version 1.0.0
@date 2026-11-02

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

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
