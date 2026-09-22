'''
@package src.generated_files
@file src/generated_files/__init__.py
@author Gerald Manweiler

@brief Package for generated project files.

@details Exposes the directory path used for project-generated files.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os                                                   # for operating-system path operations

## @var GENERATED_PATH
# @brief Generated-files directory path.
# @details Provides a shared path without hard-coded directory values elsewhere in the codebase.
GENERATED_PATH = os.path.dirname(os.path.abspath(__file__))

## @var __all__
# @brief Exposes variable for importing by other modules.
# @details Import GENERATED_PATH with `from src.generated_files import GENERATED_PATH`.
__all__ = [
    "GENERATED_PATH",
]
