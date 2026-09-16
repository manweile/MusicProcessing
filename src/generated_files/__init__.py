'''
@package src.generated_files
@file src/generated_files/__init__.py
@author Gerald Manweiler

@brief Gets directory name for importing by other modules.

@details Gets the directory name for importing by other modules.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import os                                                   # Standard module for interacting with the operating system

## @var GENERATED_PATH
# @brief Path to where files created by the project are stored.
# @details Getting the directory name for importing means will not need a hard coded "magic spell" else where in codebase.
GENERATED_PATH = os.path.dirname(os.path.abspath(__file__))

## @var __all__
# @brief Exposes variable for importing by other modules.
# @details  In modules needing the directory, add `from src.GENERATED_PATH`
__all__ = ["GENERATED_PATH"]
