'''
@brief Gets directory name for importing by other modules.
'''
import os

## @var generated_files
# @brief Path to where files created by the project are stored.
# @details Getting the directory name for importing means will not need a hard coded "magic spell" else where in codebase.
generated_files = ""
generated_files = os.path.dirname(os.path.abspath(__file__))

## @var __all__
# @brief Exposes variable for importing by other modules.
# @details  In modules needing the directory, add `from src.generated_files import generated_files`
__all__ = ['generated_files']
