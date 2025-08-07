
'''
@file test_audio_normalization.py
@brief Defines the test audio normalization class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import os
import unittest

# third party modules
# import ipsumlorem

# local modules
# from src import AUDIO_EXTS, AUDIO_TYPES
from src import EXPORT_TLD
# from src import FOLDER_ART
# from src import HOME, MEDIA                                     # ubuntu mount points
# from src import PLAYLIST_EXTS
from src.generated_files import GENERATED_FILES
# from src.audio_info import AudioArt
# from src.audio_info import AudioPlaylist
from src.audio_normalize import AudioNormalization
# from src.dir_processing import DirectoryProcessing

gc.enable()

# instantiate module levels vars here
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
TESTS_TLD = os.path.join(TESTS_PATH, EXPORT_TLD)

# instantiate classes here
# art = AudioArt()
# directory = DirectoryProcessing()
normalization = AudioNormalization()
# playlist = AudioPlaylist()


class TestAudioNormalization(unittest.TestCase):
    '''
    @brief Tests AudioNormalization class functions.
    '''

    def test_peak_normalize_file(self):
        '''
        @brief Tests peak normalize audio file level.
        '''

        file_path = os.path.join(TESTS_TLD, "Crush", "Here", "Crush-Live.mp3")
        normalization.peak_normalize_file(file_path)
        generated_mp3 = os.path.join(GENERATED_FILES, EXPORT_TLD, "tests", EXPORT_TLD, "Crush", "Here", "Crush-Live.mp3")
        self.assertTrue(os.path.exists(generated_mp3))
        # @todo need to remove the generated mp3 after success


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestAudioNormalization('test_peak_normalize_file'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
