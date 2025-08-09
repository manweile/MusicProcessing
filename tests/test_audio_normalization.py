'''
@file test_audio_normalization.py
@brief Defines the test audio normalization class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import os
import shutil
import unittest

# local modules
from src import EXPORT_TLD
from src.generated_files import GENERATED_FILES
from src.audio_normalize import AudioNormalization

gc.enable()

# D:\MusicProcessing\tests\
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

normalization = AudioNormalization()


class TestAudioNormalization(unittest.TestCase):
    '''
    @brief Tests AudioNormalization class functions.
    '''

    def tearDown(self):
        # Clean up: delete the temporary directory after each test
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


    def test_peak_normalize_file(self):
        '''
        @brief Tests peak normalize audio file level.
        '''

        # source audio file:
        audio_file = os.path.join("Crush", "Here", "Crush-Live.mp3")
        file_path = os.path.join(TESTS_PATH, EXPORT_TLD, audio_file)

        normalization.peak_normalize_file(file_path)

        r'''
        Normal operations input audio paths:
        D:\MusicCrush\Here\Crush-Live.mp3
        /home/gerald/Music/Crush/Here/Crush-Live.mp3

        Test operations input audio paths:
        D:\MusicProcessing\tests\Music\Crush\Here\Crush-Live.mp3
        /home/gerald/MusicProcessing/tests/Music/Crush/Here/Crush-Live.mp3

        peak_normalize_file will call path_info function for an export path,
        and since the source audio file has 2 extra directory levels,
        path_info will generate an export path offset by the 2 extra directories.

        So the excepted path needs to reflect the additional directory levels:
        D:\MusicProcessing\src\generated_files\Music\tests\Music\Crush\Here\Crush-Live.mp3
        /home/gerald/MusicProcessing/src/generated_files/Music/tests/Music/Crush/Here/Crush-Live.mp3
        '''
        expected_mp3 = os.path.join(GENERATED_FILES, EXPORT_TLD, audio_file)
        self.assertTrue(os.path.exists(expected_mp3))
        # @todo need to remove the generated mp3 after success


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestAudioNormalization('test_peak_normalize_file'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
