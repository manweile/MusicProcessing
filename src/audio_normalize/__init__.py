'''
@brief Package with audio_normalize module
'''

# using absolute import as don't expect to be re-organizing directories
from src.audio_normalize.audio_normalization import AudioNormalization

## @var __all__
# @brief Exposes class for importing by other modules.
# @details  In modules needing the class, add `from src.audio_normalize.audio_normalization import AudioNormalization`
__all__ = ['AudioNormalization']
