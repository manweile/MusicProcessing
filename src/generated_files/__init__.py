'''
@brief Gets directory name for importing by other modules.
'''

# standard modules
import os

## @var GENERATED_FILES
# @brief Path to where files created by the project are stored.
# @details Getting the directory name for importing means will not need a hard coded "magic spell" else where in codebase.
GENERATED_FILES = os.path.dirname(os.path.abspath(__file__))

## @var __all__
# @brief Exposes variable for importing by other modules.
# @details  In modules needing the directory, add `from src.GENERATED_FILES`
__all__ = ["GENERATED_FILES"]
