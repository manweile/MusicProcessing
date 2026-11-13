#!/usr/bin/env python3
'''
@file main.py
@author Gerald Manweiler

@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import logging                                              # logging module
import os                                                   # operating system module
import sys                                                  # system-specific parameters and functions module

# Local Module Methods
from src.cli.commands import run_cli_command                # function to run CLI commands
from src.cli.parser import build_parser                     # function to build the CLI argument parser
from src.core.logging_config import bootstrap_logging       # for package logging startup
from src.gui.wx_app import run_gui                          # GUI application runner

# Local Module Constants
from src.core.constants import ERROR_LOG_FORMAT             # error log format
from src.core.constants import LOG_DIR                      # log directory
from src.core.constants import LOG_EXT                      # log file extension
from src.core.constants import UTF8                         # utf encoding for file writing
from src.core.paths import GENERATED_PATH                   # generated files path

# MUST configure logging before importing modules that register logging handlers
# imports after executable code require noqa: E402 (module import after code) to stop error warning
bootstrap_logging()

# Local Module Classes
from src.audio_info import AudioArt                         # noqa: E402, audio art handling class
from src.audio_info import AudioMetadata                    # noqa: E402, audio metadata handling class
from src.audio_info import AudioPlaylist                    # noqa: E402, audio playlist handling class
from src.audio_info import AudioUtilities                   # noqa: E402, audio utility functions class
from src.audio_normalize import AudioNormalization          # noqa: E402, audio normalization handling class
from src.dir_processing import DirectoryProcessing          # noqa: E402, directory processing handling class

# Configure logging
## @var basename
# @brief Module file base name.
# @details Gets the current module file name for constructing the log file name.
basename = os.path.basename(__file__)

## @var stem
# @brief Module file stem.
# @details Removes the extension from the module file base name.
stem = os.path.splitext(basename)[0]

## @var file
# @brief Module log file name.
# @details Appends the configured log extension to the module file stem.
file = stem + LOG_EXT

## @var log_filename
# @brief Module log file path.
# @details Joins the generated-files path, log directory, and module log file name.
log_filename = os.path.join(GENERATED_PATH, LOG_DIR, file)

# override the default logging level WARN to lowest level so we can log all levels
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=ERROR_LOG_FORMAT, filemode="a", encoding=UTF8)

## @var logger
# @brief Module logger.
# @details Records application events using the module name.
logger = logging.getLogger(__name__)

## @var art
# @brief AudioArt handling instance.
# @details Provides audio art handling functionality.
art = AudioArt()

## @var directory
# @brief Directory processing instance.
# @details Provides directory processing functionality.
directory = DirectoryProcessing()

## @var metadata
# @brief Audio metadata handling instance.
# @details Provides audio metadata handling functionality.
metadata = AudioMetadata()

## @var normalization
# @brief Audio normalization instance.
# @details Provides audio normalization functionality.
normalization = AudioNormalization()

## @var playlist
# @brief Audio playlist handling instance.
# @details Provides audio playlist handling functionality.
playlist = AudioPlaylist()

## @var utilities
# @brief Utility functions instance.
# @details Provides various utility functions for the application.
utilities = AudioUtilities()


## @name Application Entry Point
# @{
def main(args) -> int:
    '''
    @brief Main entry point for the application.

    @details Dispatches to the appropriate subcommand handler based on the parsed arguments.

    @param args {Namespace} The parsed command-line arguments.

    @retval {int} Exit code, zero for success, one for failure.
    '''

    result_code = 0
    subcommand = args.subcommand

    try:
        # user want GUI mode, which doesn't have an explicit result code
        if subcommand == "gui":
            run_gui()
            result_code = 0
            return result_code

        # user want CLI mode, which does have an explicit result code
        run_cli_command(args)
        result_code = 0
        return result_code

    except Exception as e_error:
        logger.exception(f"Exception propagated to main: {type(e_error).__name__}: {e_error}", stack_info=True)

        # we need a message no matter what mode was ran
        message = (f"Error in subcommand '{subcommand}': {type(e_error).__name__}: {e_error}")
        if subcommand == "gui":
            import wx
            wx.MessageBox(message, "Error", wx.OK | wx.ICON_ERROR)
        else:
            print(message)

        result_code = 1
        return result_code
## @}


if __name__ == "__main__":
    '''
    @brief Top level script environment entry point.

    @details Sets up argument parsing and subcommand handling.

    @note Any input file paths that contain spaces must be enclosed in quotes.

    @exception {Exception} Handles unforeseen errors.
    '''

    try:
        parser = build_parser()
        args = parser.parse_args()
        sys.exit(main(args))

    except Exception as e:
        logger.exception(f"Exception propagated to entry point: {type(e).__name__}: {e}", stack_info=True)
        print(f"Exception propagated to entry point: {type(e).__name__}: {e}")
        sys.exit(1)
