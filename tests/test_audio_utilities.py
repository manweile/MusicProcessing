'''
@file test_audio_utilities.py one off functions.

@brief Defines the test audio utilities class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import unittest
from unittest import TestCase

# local module classes
from src.audio_info import AudioUtilities

gc.enable()

# normalization = AudioNormalization()
utilities = AudioUtilities()


class TestAudioUtilities(TestCase):
    '''
    @brief Tests AudioUtilities class functions.
    '''

    def test_clip_vol_check_walk(self):
        '''
        @brief Tests walking tld to get clipping and max volume amounts.
        '''

        converted_tld = r"F:\ConvertedMusic"
        utilities.clip_vol_check_walk(converted_tld)


def get_method_names(cls):
    '''
    @brief Returns a list of names of methods defined within a given class.

    @param cls {Class} The name of the class to get methods list from.
    @return method_names [{str}] The names of the methods defined in class.
    '''

    method_names = []
    for name, obj in inspect.getmembers(cls):
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            if name.startswith('test_'):
                method_names.append(name)
    return method_names


if __name__ == "__main__":
    methods = get_method_names(TestAudioUtilities)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioUtilities(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
