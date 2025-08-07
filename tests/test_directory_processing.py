
'''
@file test_directory_processing.py
@brief Defines the test directory processing class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import os
import unittest
from unittest.mock import patch

# local modules
from src import AUDIO_TYPES
from src import EXPORT_TLD
from src.dir_processing import DirectoryProcessing

gc.enable()

# instantiate module levels vars here
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

# instantiate classes here
directory = DirectoryProcessing()


class TestDirectoryProcessing(unittest.TestCase):
    '''
    @brief Tests DirectoryProcessing class functions.
    '''

    @patch('src.dir_processing.directory_processing.logger.warning')
    def test_path_info_not_audio(self, mock_warning):
        '''
        @brief Tests if trying to get path info for a non-audio file.
        '''

        input_path = os.path.join(TESTS_PATH, EXPORT_TLD, "expected.m3u")
        path_info = directory.path_info(input_path)
        self.assertIsNone(path_info)
        mock_warning.assert_called_once_with(f"File {input_path} is not in {AUDIO_TYPES}")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestDirectoryProcessing('test_path_info_not_audio'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
