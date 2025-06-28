'''
@brief Package with audio_info module
'''
# using absolute import as don't expect to be re-organizing directories
from src.audio_info.audio_metadata import AudioMetadata

## @var __all__
# @brief Exposes class for importing by other modules.
# @details  In modules needing the class, add `from src.audio_info.audio_metadata import AudioMetadata`
__all__ = ['AudioMetadata']