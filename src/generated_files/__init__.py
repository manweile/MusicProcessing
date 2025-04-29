'''
@package generated_files
@brief gets directory name for importing by other modules
'''
import os

## @var generated_files
# @brief gets directory name so don't need a "magic spell" else where in codebase.
generated_files = ""
generated_files = os.path.dirname(os.path.abspath(__file__))

## @var __all__
# @brief exposes list for imports
__all__ = ['generated_files']
