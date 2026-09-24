'''
@class TestAudioPlaylist
@file test_audio_playlist.py
@author Gerald Manweiler

@brief Defines the test audio playlist class.

@details Tests playlist entry parsing and path-update behavior.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import inspect                                              # for test method discovery
import os                                                   # for test fixture path operations
import unittest                                             # for direct test-suite execution
from unittest import TestCase                               # for test-case assertions and lifecycle hooks
from unittest.mock import patch                             # for warning-log interception

# Local Module Constants
from src.generated_files import GENERATED_PATH              # for generated playlist output paths
from tests import TEST_M3U                                  # for playlist update tests
from tests import TEST_MP3_CRUSH                            # for invalid playlist input tests
from tests import TESTS_PATH                                # for expected playlist fixture paths
from tests import TESTS_TLD                                 # for playlist media root paths

# Local Module Errors
from src import PlaylistError                               # for expected playlist parsing errors

# Local Module Classes
from src.audio_info import AudioPlaylist                    # for playlist functionality under test

## @var playlist
# @brief AudioPlaylist instance under test.
# @details Provides access to playlist parsing and path-update functionality.
playlist = AudioPlaylist()


class TestAudioPlaylist(TestCase):
    '''
    @brief Tests AudioPlaylist class functions.

    @details Verifies playlist parsing and audio path-update behavior.
    '''


    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite.

        @details Creates shared expected and generated playlist paths for the test suite.

        @param cls {type[TestAudioPlaylist]} Test class receiving shared playlist paths.
        '''

        cls.expected_m3u = os.path.join(TESTS_PATH, "expected.m3u")
        cls.generated_m3u = os.path.join(GENERATED_PATH, "test.m3u")


    def tearDown(self):
        '''
        @brief Clean up the created playlist file.

        @details Removes the generated playlist file after each test case.

        @param self {TestAudioPlaylist} Test instance containing generated playlist paths.
        '''

        if os.path.exists(self.generated_m3u):
            os.remove(self.generated_m3u)


    def test_get_audio_name_error(self):
        '''
        @brief Test audio-name parsing without an EXTINF delimiter.

        @details Verifies malformed playlist metadata raises a playlist error.

        @test Error case.

        @param self {TestAudioPlaylist} Test instance containing playlist fixtures.

        @exception PlaylistError The EXTINF line has no filename delimiter.
        '''

        audio = None
        line = "#EXTINF:0The Eagles-Desperado.m4a"

        with self.assertRaises(PlaylistError) as cm:
            audio = playlist.get_audio_name(line)

        self.assertIsNone(audio)
        self.assertEqual(cm.exception.message, f"PlaylistError no file delimiter in {line}")



    def test_get_audio_name_m4a(self):
        '''
        @brief Test M4A audio-name parsing from an EXTINF line.

        @details Verifies M4A filenames are converted to MP3 filenames.

        @test Happy path.

        @param self {TestAudioPlaylist} Test instance containing playlist fixtures.
        '''

        line = "#EXTINF:0,The Eagles-Desperado.m4a"
        expected_audio = "The Eagles-Desperado.mp3"
        result_audio = playlist.get_audio_name(line)
        self.assertEqual(expected_audio, result_audio)


    def test_get_audio_name_mp3(self):
        '''
        @brief Test MP3 audio-name parsing from an EXTINF line.

        @details Verifies MP3 filenames are retained unchanged.

        @test Happy path.

        @param self {TestAudioPlaylist} Test instance containing playlist fixtures.
        '''

        line = "#EXTINF:0,Sawyer Fredricks - Shots Fired.mp3"
        expected_audio = "Sawyer Fredricks - Shots Fired.mp3"
        result_audio = playlist.get_audio_name(line)
        self.assertEqual(expected_audio, result_audio)


    def test_get_audio_name_wma(self):
        '''
        @brief Test WMA audio-name parsing from an EXTINF line.

        @details Verifies WMA filenames are converted to MP3 filenames.

        @test Happy path.

        @param self {TestAudioPlaylist} Test instance containing playlist fixtures.
        '''

        line = "#EXTINF:0,Creedence Clearwater Revival-Fortunate Son.wma"
        expected_audio = "Creedence Clearwater Revival-Fortunate Son.mp3"
        result_audio = playlist.get_audio_name(line)
        self.assertEqual(expected_audio, result_audio)


    @patch('src.audio_info.audio_playlist.logger.warning')
    def test_update_paths(self, mock_warning):
        '''
        @brief Test playlist path updates against expected output.

        @details Verifies existing audio paths are written and missing audio paths produce warnings.

        @test Happy path.

        @param self {TestAudioPlaylist} Test instance containing playlist fixtures.
        @param mock_warning {Mock} Patched warning logger for missing audio paths.
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
        @brief Test playlist path updates with a non-playlist file.

        @details Verifies a non-M3U input file raises a playlist error.

        @test Error case.

        @param self {TestAudioPlaylist} Test instance containing playlist fixtures.

        @exception PlaylistError The input file is not a supported playlist.
        '''

        with self.assertRaises(PlaylistError) as cm:
            playlist.update_paths(TESTS_TLD, TEST_MP3_CRUSH)

        self.assertEqual(cm.exception.message, f"PlaylistError input file {TEST_MP3_CRUSH} is not a playlist")


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
    @brief Run the AudioPlaylist test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_audio_playlist.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestAudioPlaylist)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioPlaylist(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
