'''
@brief Package with directory_processing module
'''

# using absolute import as don't expect to be re-organizing directories
from src.dir_processing.directory_processing import DirectoryProcessing

## @var __all__
# @brief Exposes class for importing by other modules.
# @details  In modules needing the class, add `src.dir_processing.directory_processing import DirectoryProcessing`
__all__ = ['DirectoryProcessing']
