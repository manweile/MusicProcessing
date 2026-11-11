'''
@package src.dir_processing
@file src/dir_processing/__init__.py
@author Gerald Manweiler

@brief Provides compatibility imports for directory-processing models.

@details Re-exports the model package while legacy imports are being migrated.

@version 1.0.0
@date 2026-11-10

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import sys                                                  # for registering legacy module paths

# Local Module Classes
from src.models.dir_processing import DirectoryProcessing   # exposes directory-processing operations

from src.models.dir_processing import directory_processing  # provides legacy module access

sys.modules[f"{__name__}.directory_processing"] = directory_processing

## @var __all__
# @brief Exposes the public compatibility class.
# @details The class is implemented in src.models.dir_processing.
__all__ = [
    "DirectoryProcessing"
]
