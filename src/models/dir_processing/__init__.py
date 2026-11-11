'''
@package src.models.dir_processing
@file src/models/dir_processing/__init__.py
@author Gerald Manweiler

@brief Package for directory processing.

@details Exposes directory processing functionality through a single package interface.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Classes
# exposes directory processing operations
from src.models.dir_processing.directory_processing import DirectoryProcessing

## @var __all__
# @brief Exposes class for importing by other modules.
# @details In modules needing the class, add `from src.models.dir_processing import DirectoryProcessing`.
__all__ = [
    "DirectoryProcessing",
]
