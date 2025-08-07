'''
@file test_audio_playlist.py
@brief Defines the test audio playlist class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''
# standard modules
import gc
import logging
import os
import unittest

# local modules
from src import EXPORT_TLD
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging constants
from src.generated_files import GENERATED_FILES
from src.audio_info import AudioPlaylist

gc.enable()

# Configure logging
basename = os.path.basename(__file__)
stem = os.path.splitext(basename)[0]
file = stem + LOG_EXT
log_filename = os.path.join(GENERATED_FILES, LOG_DIR, file)
# override the default logging level WARN to lowest level so we can log all levels
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=ERROR_LOG_FORMAT, filemode="a", encoding=UTF8)

# create logger for module and restrict to module
# use raise in exception handling if we need send something inter-module
logger = logging.getLogger(__name__)
logger.propagate = False

TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
TESTS_TLD = os.path.join(TESTS_PATH, EXPORT_TLD)

playlist = AudioPlaylist()


class TestAudioPlaylist(unittest.TestCase):
    '''
    @brief Tests AudioPlaylist class functions.
    '''

    def test_update_m3u(self):
        '''
        @brief Tests if the updated m3u file is equal to expected results.
        '''

        input_m3u = os.path.join(TESTS_TLD, "test.m3u")
        input_tld = TESTS_TLD
        input_tld = TESTS_TLD
        generated_m3u = os.path.join(GENERATED_FILES, "test.m3u")
        expected_m3u = os.path.join(TESTS_TLD, "expected.m3u")

        # @todo how do I run AudioPlaylist.update_paths??
        playlist.update_paths(input_tld, input_m3u)

        self.assertTrue(os.path.exists(generated_m3u))

        with open(generated_m3u, "r") as generated_file, open(expected_m3u, "r") as expected_file:
            generated_content = generated_file.read()
            expected_content = expected_file.read()
            self.assertEqual(generated_content, expected_content, "File contents should be equal")


if __name__ == "__main__":
    unittest.main(verbosity=2)
