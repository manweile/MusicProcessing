
'''
@file test_directory_processing.py
@brief Defines the test directory processing class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import logging
import os
import unittest

# third party modules
# import ipsumlorem

# local modules
from src import EXPORT_TLD
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging constants
from src.generated_files import GENERATED_FILES
from src.dir_processing import DirectoryProcessing

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

# instantiate module levels vars here
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

# instantiate classes here
directory = DirectoryProcessing()


class TestDirectoryProcessing(unittest.TestCase):
    '''
    @brief Tests DirectoryProcessing class functions.
    '''

    def test_path_info_not_audio(self):
        '''
        @brief Tests if trying to get path info for a non-audio file.
        '''

        m3u_file = os.path.join(TESTS_PATH, EXPORT_TLD, "expected.m3u")
        path_info = directory.path_info(m3u_file)
        self.assertIsNone(path_info)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestDirectoryProcessing('test_path_info_not_audio'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
