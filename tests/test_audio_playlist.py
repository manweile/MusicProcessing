'''
@file test_audio_playlist.py
@brief Defines the test audio playlist class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import os
import unittest
from unittest.mock import patch

# local modules
from src import EXPORT_TLD
from src.generated_files import GENERATED_FILES
from src.audio_info import AudioPlaylist

gc.enable()

TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
TESTS_TLD = os.path.join(TESTS_PATH, EXPORT_TLD)
EXPECTED_M3U = os.path.join(TESTS_TLD, "expected.m3u")
INPUT_M3U = os.path.join(TESTS_TLD, "test.m3u")
GENERATED_M3U = os.path.join(GENERATED_FILES, "test.m3u")

playlist = AudioPlaylist()


class TestAudioPlaylist(unittest.TestCase):
    '''
    @brief Tests AudioPlaylist class functions.
    '''

    def tearDown(self):
        '''
        @brief Clean up the created playlist file.
        '''

        if os.path.exists(GENERATED_M3U):
            os.path.remove(GENERATED_M3U)


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


    def test_get_audio_name_m4a(self):
        '''
        @brief Tests getting m4a audio file name from a m3u #EXTINF line
        '''

        line = "#EXTINF:0,The Eagles-Desperado.m4a"
        expected_audio = "The Eagles-Desperado.mp3"
        result_audio = playlist.get_audio_name(line)
        self.assertEqual(expected_audio, result_audio)


    @patch('src.audio_info.audio_playlist.logger.exception')
    def test_get_audio_name_error(self, mock_warning):
        '''
        @brief Tests getting audio file name from a m3u #EXTINF line without delimiter
        '''

        line = "#EXTINF:0The Eagles-Desperado.m4a"
        playlist.get_audio_name(line)
        mock_warning.assert_called_once_with(f"No file delimiter in {line}")


    def test_update_m3u(self):
        '''
        @brief Tests if the updated m3u file is equal to expected results.
        '''

        playlist.update_paths(TESTS_TLD, INPUT_M3U)

        self.assertTrue(os.path.exists(GENERATED_M3U))

        with open(GENERATED_M3U, "r") as generated_file, open(EXPECTED_M3U, "r") as expected_file:
            generated_content = generated_file.read()
            expected_content = expected_file.read()
            self.assertEqual(generated_content, expected_content, "File contents should be equal")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestAudioPlaylist('test_update_m3u'))
    suite.addTest(TestAudioPlaylist('test_get_audio_name_mp3'))
    suite.addTest(TestAudioPlaylist('test_get_audio_name_wma'))
    suite.addTest(TestAudioPlaylist('test_get_audio_name_m4a'))
    suite.addTest(TestAudioPlaylist('test_get_audio_name_error'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
