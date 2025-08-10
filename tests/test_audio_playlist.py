'''
@file test_audio_playlist.py
@brief Defines the test audio playlist class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import os
import unittest

# local modules
from src import EXPORT_TLD
from src.generated_files import GENERATED_FILES
from src.audio_info import AudioPlaylist

gc.enable()

TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
TESTS_TLD = os.path.join(TESTS_PATH, EXPORT_TLD)

playlist = AudioPlaylist()


class TestAudioPlaylist(unittest.TestCase):
    '''
    @brief Tests AudioPlaylist class functions.
    '''

    # @todo improve granularity of test case; refer to test.m3u
    # may require re-write of playlist code
    def test_update_m3u(self):
        '''
        @brief Tests if the updated m3u file is equal to expected results.
        '''

        input_m3u = os.path.join(TESTS_TLD, "test.m3u")
        generated_m3u = os.path.join(GENERATED_FILES, "test.m3u")
        expected_m3u = os.path.join(TESTS_TLD, "expected.m3u")

        playlist.update_paths(TESTS_TLD, input_m3u)

        self.assertTrue(os.path.exists(generated_m3u))

        with open(generated_m3u, "r") as generated_file, open(expected_m3u, "r") as expected_file:
            generated_content = generated_file.read()
            expected_content = expected_file.read()
            self.assertEqual(generated_content, expected_content, "File contents should be equal")


if __name__ == "__main__":
    unittest.main(verbosity=2)
