'''
@package src.core
@file src/core/__init__.py
@author Gerald Manweiler

@brief Package for MusicProcessing core infrastructure.

@details Contains shared infrastructure used across application layers.

@version 1.0.0
@date 2026-11-02

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Classes
from src.core.null_progress import NullProgress                  # no-op progress reporter
from src.core.progress import ProgressReporter                   # progress reporting interface

## @var __all__
# @brief Exposes class for importing by other modules.
# @details  In modules needing the class, add `from src.core import <Class>`
__all__ = [
    "NullProgress",
    "ProgressReporter"
]
