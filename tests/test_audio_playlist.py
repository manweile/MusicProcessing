'''
@file test_audio_playlist.py
@brief Defines the test audio playlist class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import logging
import os
import unittest

# local modules
from src import EXPORT_TLD
from src.generated_files import GENERATED_FILES
from src import PlaylistError
from src.audio_info import AudioPlaylist

gc.enable()

TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
TESTS_TLD = os.path.join(TESTS_PATH, EXPORT_TLD)
EXPECTED_M3U = os.path.join(TESTS_TLD, "expected.m3u")
INPUT_M3U = os.path.join(TESTS_TLD, "test.m3u")
GENERATED_M3U = os.path.join(GENERATED_FILES, "test.m3u")

playlist = AudioPlaylist()

'''
Get the effective level so we can disable logging when necessary.
In tests that use assertRaises, disable the logger at or below the log level of the tested function,
encapsulate the assertRaises in a try block, and use a finally to restore the original log level.
'''
original_log_level = logging.getLogger().getEffectiveLevel()


class TestAudioPlaylist(unittest.TestCase):
    '''
    @brief Tests AudioPlaylist class functions.
    '''

    # def tearDown(self):
    #     '''
    #     @brief Clean up the created playlist file.
    #     '''

    #     if os.path.exists(GENERATED_M3U):
    #         os.path.remove(GENERATED_M3U)


    def test_get_audio_name_error(self):
        '''
        @brief Tests getting audio file name from a m3u #EXTINF line without delimiter
        '''

        logging.disable(logging.ERROR)

        audio = None
        line = "#EXTINF:0The Eagles-Desperado.m4a"

        try:
            with self.assertRaises(PlaylistError) as cm:
                audio = playlist.get_audio_name(line)

            self.assertIsNone(audio)
            self.assertEqual(cm.exception.message, f"PlaylistError no file delimiter in {line}")
        finally:
            logging.disable(original_log_level)


    def test_get_audio_name_m4a(self):
        '''
        @brief Tests getting m4a audio file name from a m3u #EXTINF line
        '''

        line = "#EXTINF:0,The Eagles-Desperado.m4a"
        expected_audio = "The Eagles-Desperado.mp3"
        result_audio = playlist.get_audio_name(line)
        self.assertEqual(expected_audio, result_audio)


    def test_get_audio_name_mp3(self):
        '''
        @brief Tests getting mp3 audio file name from a m3u #EXTINF line
        '''

        line = "#EXTINF:0,Sawyer Fredricks - Shots Fired.mp3"
        expected_audio = "Sawyer Fredricks - Shots Fired.mp3"
        result_audio = playlist.get_audio_name(line)
        self.assertEqual(expected_audio, result_audio)


    def test_get_audio_name_wma(self):
        '''
        @brief Tests getting wma audio file name from a m3u #EXTINF line
        '''

        line = "#EXTINF:0,Creedence Clearwater Revival-Fortunate Son.wma"
        expected_audio = "Creedence Clearwater Revival-Fortunate Son.mp3"
        result_audio = playlist.get_audio_name(line)
        self.assertEqual(expected_audio, result_audio)

    # @unittest.skip("Skip until figure out ci issue")
    def test_update_m3u(self):
        '''
        @brief Tests if the updated m3u file is equal to expected results.
        '''

        playlist.update_paths(TESTS_TLD, INPUT_M3U)

        self.assertTrue(os.path.exists(GENERATED_M3U))

        with open(GENERATED_M3U, "r") as generated_file, open(EXPECTED_M3U, "r") as expected_file:
            generated_content = generated_file.read()
            expected_content = expected_file.read()
            self.maxDiff = None
            self.assertEqual(generated_content, expected_content, "File contents should be equal")


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
    methods = get_method_names(TestAudioPlaylist)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioPlaylist(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
