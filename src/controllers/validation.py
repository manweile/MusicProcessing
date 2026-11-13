'''
@module src.controllers.validation
@file validation.py
@author Gerald Manweiler

@brief Defines the shared path validation module.

@details Provides wxPython-independent checks for file and directory paths.

@version 1.0.0
@date 2026-11-13

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os                                                   # for checking file-system paths


def validate_dir(path: str) -> bool:
    '''
    @brief Check whether the provided path is an existing directory.

    @details Returns whether the path identifies an existing directory.

    @param path {str} The directory path to validate.

    @retval {bool} Whether the path identifies an existing directory.
    '''

    return bool(path) and os.path.isdir(path)


def validate_file(path: str) -> bool:
    '''
    @brief Check whether the provided path is an existing file.

    @details Returns whether the path identifies an existing file.

    @param path {str} The file path to validate.

    @retval {bool} Whether the path identifies an existing file.
    '''

    return bool(path) and os.path.isfile(path)
