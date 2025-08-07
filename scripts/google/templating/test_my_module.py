
'''
@file test_my_module.py
@brief Defines the test my module class.

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
from src import EXPORT_TLD

gc.enable()

# instantiate module levels vars here
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

# instantiate classes here



class TestMyClass(unittest.TestCase):
    '''
    @brief Tests MyClass class functions.
    '''

    def test_my_function(self):
        '''
        @brief Tests my function purpose.
        '''

        pass


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestMyClass('test_my_function'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
