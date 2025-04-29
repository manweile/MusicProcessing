'''
@package generated_files
@brief Gets directory name for importing by other modules
@details The generated files directory is where files are created by project.
@details Code needing to know this location will be located in other directories.
@details To modularize code, get the absolute path of this file and expose it for importing.
'''
import os

## @var generated_files
# @brief gets directory name so don't need a "magic spell" else where in codebase.
generated_files = ""
generated_files = os.path.dirname(os.path.abspath(__file__))

## @var __all__
# @brief exposes list for imports
__all__ = ['generated_files']
