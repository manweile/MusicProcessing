
'''
@file audio_utilities.py
@brief Defines the audio utilities class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import logging
import math
import os
from pathlib import Path

# local module methods
from src import add_module_handler
# local module constants
from src import MP3_EXT, TP
# local module errors
# local module classes
from src.dir_processing import DirectoryProcessing
from src.audio_normalize import AudioNormalization
from src.subprocess_utils import SubprocessUtilities

gc.enable()

# Configure logging
logger = logging.getLogger(__name__)
basename = os.path.basename(__file__)
add_module_handler(logger, basename)

directory = DirectoryProcessing()
normalization = AudioNormalization()
subprocess_utils = SubprocessUtilities()


class AudioUtilities():
    '''
    @brief Defines the base audio utilities processing used by project.
    '''

    def __init__(self):
        '''
        @brief Initialize the AudioUtilities class.

        @details A basic class implementation with no instantiation parameters.

        @return AudioUtilities {instance} An instance of the class.
        '''

        pass


    '''
    Normalization utilities
    '''
    def clip_vol_check_walk(self, tld_path):
        '''
        @brief walk tld and gets max vol & clip check amount for audio files.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        true_peak = float(TP)
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            input_file_ext = None
            input_path = Path(tld_path)

            for root, dirs, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    if input_file_ext.lower() != MP3_EXT:
                        continue
                    else:
                        file_path = os.path.join(root, file)

                    data.append(f"\n{file_path}")

                    volume_info = normalization.get_volume_info(file_path)
                    # want the floor so don't inadvertently cause clipping (more negative dbs are quieter)
                    mean_volume = float(math.floor(volume_info['mean_volume']))
                    max_volume = float(math.floor(volume_info['max_volume']))

                    vol_text = ""

                    if max_volume >= 0.0:
                        vol_text = f"normalizing impossible, max volume: {max_volume:.2f} db"
                    else:
                        vol_text = f"normalizing possible, max volume: {max_volume:.2f} dB"

                    data.append(vol_text)

                    peak_adjustment = true_peak - max_volume
                    peak_clip_amount = max_volume + peak_adjustment
                    peak_clip_text = ""

                    if peak_clip_amount > 0:
                        peak_clip_text = (
                            f"peak clipping amount: {peak_clip_amount:.2f} dB "
                            f"with max volume: {max_volume:.2f} db "
                            f"and peak adjustment: {peak_adjustment:.2f} db"
                        )
                    else:
                        peak_clip_text = f"peak normalizing adjustment: {peak_adjustment:.2f} dB"

                    data.append(peak_clip_text)

                    rms_adjustment = true_peak - mean_volume
                    rms_clip_amount = max_volume + rms_adjustment
                    rms_clip_text = ""

                    if rms_clip_amount > 0:
                        rms_clip_text = (
                            f"rms clipping amount: {rms_clip_amount:.2f} dB "
                            f"with mean volume: {mean_volume:.2f} db, max volume: {max_volume:.2f} db "
                            f"and rms adjustment: {rms_adjustment:.2f} db"
                        )
                    else:
                        rms_clip_text = f"rms normalizing adjustment: {rms_adjustment:.2f} dB"

                    data.append(rms_clip_text)

            directory.create_txt(txt_filename, data)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} while clip and max volume checking audio file: {file}", stack_info=True)
            raise e_error


    def normalize_walk(self, tld_path, norm_type, show_spinner=True):
        '''
        @brief Normalizes all audio files in specified top level directory per input normalization type.

        @details Will only normalize mp3 files.

        @param tld_path {str} The top level directory path that contains all the music files.
        @param norm_type {str} The type of normalization to perform.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\audio_normalize\audio_normalization.py
        pass


    '''
    Art Utilities
    '''
    def extract_walk(self, start_path, file_pattern):
        '''
        @brief Extracts all embedded album art from audio files.

        @details Extracts embedded art from m4a, mp3, and wma files.

        @param start_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to transform.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\audio_info\audio_art.py
        pass


    def set_album_art(self, input_path):
        '''
        @brief Sets album art file for an album directory.

        @details First check to see a folder art file is present in album directory.
        @details Second checks if there is a /AlbumArt/<album>.jpg cover art file,
        renames it to album art folder constant and moves it to album directory.

        @param input_path {str} The full path to album directory.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\audio_info\audio_art.py
        pass


    '''
    Metadata utilities
    '''
    def convert_walk(self, start_path: str, file_pattern: str, show_spinner=True) -> None:
        '''
        @brief Converts all audio files found in specified path to mp3 format.

        @details Calling functions MUST verify valid start path.

        @param start_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to transform.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\audio_info\audio_metadata.py
        pass


    def create_album_dir(self, start_path: str) -> None:
        '''
        @brief Creates an album sub-directory in an artist directory.

        @details Calling functions MUST verify valid start path.
        @details Creates the album sub directory for the artist if needed.
        @details The album name for the directory is drawn from the album metadata field.
        @details Also creates csv of all audio file paths, album metadata values and sanitized album directory names.

        @param start_path {str} The tld holding music files.

        @exception ValidationError A pathlib module validation error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\audio_info\audio_metadata.py
        pass


    def get_media_info_walk(self, start_path: str, file_pattern: str) -> None:
        '''
        @brief Gets media info (codec, duration, size, bitrate...) for audio files and saves to file.

        @param file_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to get tags from.

        @exception ValueError A function or operation received an argument of correct type but inappropriate value.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\audio_info\audio_metadata.py
        pass


    def get_tags_walk(self, file_path: str, file_pattern: str, ffprobe=False) -> None:
        '''
        @brief Gets tags for audio files and saves to file.

        @details File walk will skip any non-audio files like playlists, jpgs, etc.
        @details Therefore a non-audio ext input will never have a pattern match.

        @param file_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to get tags from.
        @param ffprobe {bool} Optional, return ffprobe tags instead of mutagen tags.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\audio_info\audio_metadata.py
        pass


    def get_unique_media_keys(self, file_path: str) -> None:
        '''
        @brief Gets set of ffprobe keys and saves to file.

        @details Walks from starting path and saves set of unique metadata keys found by ffprobe.

        @param file_path {str} The starting point of the directory walk.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\audio_info\audio_metadata.py
        pass


    '''
    Playlist utilities
    '''
    def update_walk(self, tld_path):
        '''
        @brief Updates playlists relative pathing.

        @param tld_path {str} The top level directory where playlist and music files are located.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\audio_info\audio_playlist.py
        pass


    '''
    Directory Utilities
    '''
    def get_audio_file_list(self, start_path):
        '''
        @brief Generates a csv containing full path for all audio files.

        @details Without a start path input, the top level directory MUST have been set.
        @details The csv file is created in the designated generated files directory.
        @details The csv has 2 columns, full file path for audio file and extension.

        @param start_path {str} Optional, the starting point of the directory walk.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\dir_processing\directory_processing.py
        pass


    def get_ext_file_list(self, file_ext, start_path):
        '''
        @brief Wrapper for function that generates a csv containing full file path for an extension.

        @details Without a start path input, the top level directory MUST have been set.
        @details If file extension is not supplied, uses the preset audio types list.

        @param  file_ext {str} Optional, the file extension (without period prefix) want file paths for.
        @param  start_path {str} Optional, the starting point of the directory walk.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\dir_processing\directory_processing.py
        pass


    def remove_album_dir(self, start_path):
        '''
        @brief Removes empty album directories.

        @details Walks through top level directory to remove empty second level album directories contained in artist first level directories.
        @details Without a start path input, the top level directory MUST have been set.

        @param start_path {str} The starting point of the directory walk.

        @exception OSError A system related error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\dir_processing\directory_processing.py
        pass


    def remove_pattern(self, start_path, file_pattern):
        '''
        @brief Removes file matching specified pattern.

        @details Walks through top level directory and removes files matching specified file pattern.
        @details Without a start path input, the top level directory MUST have been set.

        @param start_path {str} Optional, the starting point of the directory walk.
        @param file_pattern {str} The file pattern we want to delete.

        @exception OSError A system related error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # D:\MusicProcessing\src\dir_processing\directory_processing.py
        pass
