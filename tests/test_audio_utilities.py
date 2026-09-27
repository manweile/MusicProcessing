'''
@class TestAudioUtilities
@file test_audio_utilities.py
@author Gerald Manweiler

@brief Defines the test audio utilities class.

@details Tests utility behavior that checks audio clipping and volume levels.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import inspect                                              # for test method discovery
import unittest                                             # for direct test-suite execution
from unittest import TestCase                               # for test-case assertions

# Local Module Constants
from tests import TESTS_TLD                                 # for audio utility walk input

# Local Module Classes
from src.audio_info import AudioUtilities                   # for utility functionality under test

## @var utilities
# @brief AudioUtilities instance under test.
# @details Provides access to audio utility functionality.
utilities = AudioUtilities()


class TestAudioUtilities(TestCase):
    '''
    @brief Tests AudioUtilities class functions.

    @details Verifies audio utility behavior using music test fixtures.
    '''


    def test_clip_vol_check_walk(self):
        '''
        @brief Test clipping and maximum-volume analysis over a directory walk.

        @details Verifies the utility processes all audio fixtures in the top-level music directory.

        @test Happy path.

        @param self {TestAudioUtilities} Test instance containing utility fixtures.
        '''

        converted_tld = TESTS_TLD
        utilities.clip_vol_check_walk(converted_tld)


def get_method_names(cls):
    '''
    @brief Get names of test methods defined by a class.

    @details Filters class methods to names that begin with the test prefix.

    @param cls {type} Class containing test methods.

    @return method_names {list[str]} Names of test methods defined by the class.
    '''

    method_names = []
    for name, obj in inspect.getmembers(cls):
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            if name.startswith('test_'):
                method_names.append(name)
    return method_names


if __name__ == "__main__":
    '''
    @brief Run the AudioUtilities test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_audio_utilities.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestAudioUtilities)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioUtilities(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
