'''
@file test_audio_playlist.py
@brief Defines the test audio playlist class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import os
import unittest
from unittest import TestCase
from unittest.mock import patch

# local module constants
from src.generated_files import GENERATED_PATH
from tests import TEST_MP3_CRUSH, TEST_M3U
from tests import TESTS_PATH, TESTS_TLD
# local module errors
from src import PlaylistError
# local module classes
from src.audio_info import AudioPlaylist

gc.enable()

## @var playlist
# @brief instance of AudioPlaylist class
# @details used for accessing class functionality
playlist = AudioPlaylist()


class TestAudioPlaylist(TestCase):
    '''
    @brief Tests AudioPlaylist class functions.
    '''


    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite.

        @details These datums are used throughout class and only need init once.
        '''

        cls.expected_m3u = os.path.join(TESTS_PATH, "expected.m3u")
        cls.generated_m3u = os.path.join(GENERATED_PATH, "test.m3u")


    def tearDown(self):
        '''
        @brief Clean up the created playlist file.
        '''

        if os.path.exists(self.generated_m3u):
            os.remove(self.generated_m3u)


    def test_get_audio_name_error(self):
        '''
        @brief Tests getting audio file name from a m3u #EXTINF line without delimiter
        '''

        audio = None
        line = "#EXTINF:0The Eagles-Desperado.m4a"

        with self.assertRaises(PlaylistError) as cm:
            audio = playlist.get_audio_name(line)

        self.assertIsNone(audio)
        self.assertEqual(cm.exception.message, f"PlaylistError no file delimiter in {line}")



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


    @patch('src.audio_info.audio_playlist.logger.warning')
    def test_update_paths(self, mock_warning):
        '''
        @brief Tests if the updated m3u file is equal to expected results.
        '''

        playlist.update_paths(TESTS_TLD, TEST_M3U)
        m3u_exists = os.path.exists(self.generated_m3u)
        self.assertTrue(m3u_exists)

        # warning order will be last in first out - so 38 special then Daughtry, which is invert of order in test m3u
        mock_warning.assert_called_with(f".38 Special-Teacher, Teacher.mp3 from test.m3u not found in {TESTS_TLD}")
        mock_warning.assert_any_call(f"Daughtry-Home.mp3 from test.m3u not found in {TESTS_TLD}")

        generated_inf = []
        expected_inf = []

        with open(self.generated_m3u, "r") as generated_file, open(self.expected_m3u, "r") as expected_file:
            for generated_line, expected_line in zip(generated_file, expected_file):
                if "#EXTINF:0," in generated_line:
                    generated_inf.append(generated_line)
                if "#EXTINF:0," in expected_line:
                    expected_inf.append(expected_line)

        self.assertEqual(generated_inf, expected_inf, "List contents should be equal")


    def test_update_paths_fail(self):
        '''
        @brief Tests trying to update non-m3u file.
        '''

        with self.assertRaises(PlaylistError) as cm:
            playlist.update_paths(TESTS_TLD, TEST_MP3_CRUSH)

        self.assertEqual(cm.exception.message, f"PlaylistError input file {TEST_MP3_CRUSH} is not a playlist")


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
