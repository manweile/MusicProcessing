'''
@file test_audio_normalization.py one off functions.
@brief Defines the test audio normalization class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import unittest
# from json import JSONDecodeError
# from pathlib import Path
# from subprocess import CalledProcessError, CompletedProcess
from unittest import TestCase
# from unittest.mock import Mock
# from unittest.mock import patch

# local module constants
# from src import ILT, LRA, MUSIC_TLD, TP
# from src.generated_files import GENERATED_FILES
# from tests import TEST_M3U, TEST_MP3_ABBA, TEST_MP3_CRUSH, TEST_MP3_SMEAGOL, TEST_MP3_X
# from tests import TESTS_PATH
# local module errors
# from src.errors import JSONOutputError
# local module classes
from src.audio_normalize import AudioNormalization

gc.enable()

normalization = AudioNormalization()


class TestAudioNormalization(TestCase):
    '''
    @brief Tests AudioNormalization class functions.
    '''

    def test_peak_clip_check_walk(self):
        '''
        @brief Tests walking tld to get peak adjustment amount.
        '''

        converted_tld = r"F:\ConvertedMusic"
        normalization.peak_clip_check_walk(converted_tld)


    def test_rms_clip_check_walk(self):
        '''
        @brief Tests walking tld to get rms adjustment amount.
        '''

        converted_tld = r"F:\ConvertedMusic"
        normalization.rms_clip_check_walk(converted_tld)


    @unittest.skip("one off")
    def test_normalize_max_vol_check_walk(self):
        '''
        @brief Tests walking tld to get normalization max volume amount.
        '''

        converted_tld = r"F:\ConvertedMusic"
        normalization.normalize_max_vol_check_walk(converted_tld)


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
    methods = get_method_names(TestAudioNormalization)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioNormalization(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
