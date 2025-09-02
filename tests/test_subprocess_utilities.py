
'''
@file test_subprocess_utilities.py
@brief Defines the test subprocess_utilities class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import logging
import unittest
from subprocess import CalledProcessError
from unittest import TestCase

# local modules
from tests import TEST_WAV_NONE
from src.subprocess_utils import SubprocessUtilities

gc.enable()

# instantiate classes here
subprocess_utils = SubprocessUtilities()

'''
Get the effective level so we can disable logging when necessary.
In tests that use assertRaises, disable the logger at or below the log level of the tested function,
encapsulate the assertRaises in a try block, and use a finally to restore the original log level.
'''
original_log_level = logging.getLogger().getEffectiveLevel()


class TestSubprocessUtilities(TestCase):
    '''
    @brief Tests SubprocessUtilities class functions.
    '''

    # @todo add a subprocess_run(command) test that has a jsondecoderror


    # def test_subprocess_run_non_extant(self):
    #     '''
    #     @brief Tests Tries to run ffprobe video stream check for non-extant file.

    #     @details This test is a due diligence expected failure test.
    #     SubprocessUtilities.subprocess_run is 4th level, called by AudioArt.has_video_stream function.
    #     AudioArt.has_video_stream has its own tests, which are not an appropriate location for subprocess_run testing.
    #     '''

    #     # Don't want the console output cluttered up
    #     logging.disable(logging.ERROR)

    #     input_audio = TEST_WAV_NONE

    #     # -hide_banner reduce output clutter
    #     # -select_streams v:0 only want video stream
    #     # -show_streams gets all information about each media stream in the input
    #     # -of json output information in json format
    #     probe_command = [
    #         'ffprobe',
    #         '-hide_banner',
    #         '-select_streams', 'v:0',
    #         '-show_streams',
    #         '-of', 'json',
    #         input_audio
    #     ]
    #     probe_process = None

    #     try:
    #         with self.assertRaises(CalledProcessError) as cm:
    #             probe_process = subprocess_utils.subprocess_run(probe_command)

    #         self.assertIsNone(probe_process)
    #         stderr = cm.exception.stderr.strip()
    #         expected_err = f"{input_audio}: No such file or directory"
    #         self.assertEqual(stderr, expected_err)
    #     finally:
    #         logging.disable(original_log_level)

    def test_subprocess_run_non_extant(self):
        '''
        @brief Tests Tries to run ffprobe video stream check for non-extant file.

        @details This test is a due diligence expected failure test.
        SubprocessUtilities.subprocess_run is 4th level, called by AudioArt.has_video_stream function.
        AudioArt.has_video_stream has its own tests, which are not an appropriate location for subprocess_run testing.
        '''

        input_audio = TEST_WAV_NONE

        # -hide_banner reduce output clutter
        # -select_streams v:0 only want video stream
        # -show_streams gets all information about each media stream in the input
        # -of json output information in json format
        probe_command = [
            'ffprobe',
            '-hide_banner',
            '-select_streams', 'v:0',
            '-show_streams',
            '-of', 'json',
            input_audio
        ]
        probe_process = None

        with self.assertRaises(CalledProcessError) as cm:
            probe_process = subprocess_utils.subprocess_run(probe_command)

        self.assertIsNone(probe_process)
        stderr = cm.exception.stderr.strip()
        expected_err = f"{input_audio}: No such file or directory"
        self.assertEqual(stderr, expected_err)


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
    methods = get_method_names(TestSubprocessUtilities)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestSubprocessUtilities(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
