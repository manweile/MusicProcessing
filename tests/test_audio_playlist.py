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
from src.audio_info import AudioPlaylist

# third party modules
# import ipsumlorem

# local modules
from src import _EXPORT_TLD
from src.generated_files import generated_files

gc.enable()

_TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

playlist = AudioPlaylist()


class TestAudioPlaylist(unittest.TestCase):
    '''
    @brief Tests AudioPlaylist class functions.
    '''

    def test_update_m3u(self):
        '''
        @brief Tests if the updated m3u file is equal to expected results.
        '''

        input_m3u = os.path.join(_TESTS_PATH, _EXPORT_TLD, "test.m3u")
        input_tld = os.path.join(_TESTS_PATH, _EXPORT_TLD)
        generated_m3u = os.path.join(generated_files, "test.m3u")
        expected_m3u = os.path.join(_TESTS_PATH, _EXPORT_TLD, "expected.m3u")

        # @todo how do I run AudioPlaylist.update_paths??
        playlist.update_paths(input_tld, input_m3u)

        self.assertTrue(os.path.exists(generated_m3u))

        with open(generated_m3u, "r") as generated_file, open(expected_m3u, "r") as expected_file:
            generated_content = generated_file.read()
            expected_content = expected_file.read()
            self.assertEqual(generated_content, expected_content, "File contents should be equal")


if __name__ == "__main__":
    unittest.main(verbosity=2)
