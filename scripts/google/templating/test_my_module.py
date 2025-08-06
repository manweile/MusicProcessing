
'''
@file test_my_module.py
@brief Defines the test my module class.

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
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging constants
from src.generated_files import GENERATED_FILES

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


# instantiate classes here



class TestMyClass(unittest.TestCase):
    '''
    @brief Tests MyClass class functions.
    '''

    def test_my_function(self):
        '''
        @brief Tests ipsum lorem
        '''

        pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
