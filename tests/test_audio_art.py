'''
@file test_audio_art.py
@brief Defines the test audio art class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import logging
import os
import unittest
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import patch

# local modules
from src import EXPORT_TLD
from src import FOLDER_ART
from src.audio_info import AudioArt

gc.enable()

# get the dir path for test location need it to find audio files
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
TESTS_TLD = os.path.join(TESTS_PATH, EXPORT_TLD)

EXPECTED_M4A_JPG = os.path.join(TESTS_TLD, "Joshua Davis", "The Voice Peformance", FOLDER_ART)
EXPECTED_MP3_JPG = os.path.join(TESTS_TLD, "Crush", "Here", FOLDER_ART)
EXPECTED_NO_STREAM_JPG = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", FOLDER_ART)
EXPECTED_NO_TAG_MP3_JPG = os.path.join(TESTS_TLD, FOLDER_ART)
EXPECTED_WMA_JPG = os.path.join(TESTS_TLD, "Elton John", "Goodbye Yellow Brick Road", FOLDER_ART)

EXPECTED_JPGS = [EXPECTED_MP3_JPG, EXPECTED_M4A_JPG, EXPECTED_NO_STREAM_JPG, EXPECTED_WMA_JPG]

INPUT_M3U = os.path.join(TESTS_TLD, "test.m3u")

SRC_HAS_JPG_AUDIO = os.path.join(TESTS_TLD, "Abba", "Waterloo", "ABBA-Waterloo.mp3")
SRC_HAS_JPG_PATH = os.path.join(TESTS_TLD, "Abba", "Waterloo")
SRC_MP3 = os.path.join(TESTS_TLD, "Crush", "Here", "Crush-Live.mp3")
SRC_M4A = os.path.join(TESTS_TLD, "Joshua Davis", "The Voice Peformance", "Joshua Davis-The Workingman's Hymn.m4a")
SRC_NO_STREAM_WMA = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", "Billie Holiday-Georgia On My Mind.wma")
SRC_NO_TAG_MP3 = os.path.join(TESTS_TLD, "No_tag_Crush-Live.mp3")
SRC_WMA = os.path.join(TESTS_TLD, "Elton John", "Goodbye Yellow Brick Road", "Elton John-Saturday Night's Alright for Fighting.wma")

art = AudioArt()

'''
Get the effective level so we can disable logging when necessary.
In tests that use assertRaises, disable the logger at or below the log level of the tested function,
encapsulate the assertRaises in a try block, and use a finally to restore the original log level.
'''
original_log_level = logging.getLogger().getEffectiveLevel()


class TestAudioArt(unittest.TestCase):
    '''
    @brief Tests AudioArt class functions.
    '''

    def tearDown(self):
        '''
        @brief Clean up the created Folder.jpg files.
        '''

        for jpg in EXPECTED_JPGS:
            if os.path.exists(jpg):
                os.remove(jpg)


    @patch('src.audio_info.audio_art.logger.info')
    def test_extract_album_art_folder_exists(self, mock_warning):
        '''
        brief Test Try to extract album art from file that already has co-located Folder.jpg file.
        '''

        input_audio = SRC_HAS_JPG_AUDIO
        album_path = Path(input_audio).parent
        art.extract_album_art(input_audio)
        mock_warning.assert_called_once_with(f"{album_path} has a {FOLDER_ART}")


    @patch('src.audio_info.audio_art.logger.info')
    def test_extract_album_art_invalid_audio(self, mock_warning):
        '''
        @brief Tests Try to extract album art from non-valid file.
        '''

        input_audio = INPUT_M3U
        input_path = Path(input_audio)
        art.extract_album_art(input_audio)
        mock_warning.assert_called_once_with(f"{input_path.name} is not an audio file")

    # per https://stackoverflow.com/questions/15763394/mocking-two-functions-with-patch-for-a-unit-test
    # the order of stacked patch decorators and calls to the matching assert_called_once_with matter,
    # and its FILO (first in, last out)
    # so if a warning is 1st patch, then the same warning has to be last assert
    # the declaration order in signature doesn't matter though


    @patch('src.audio_info.audio_art.logger.warning')
    @patch('src.audio_info.audio_art.logger.info')
    def test_extract_album_art_no_tag_or_stream(self, mock_info, mock_warning):
        '''
        @brief Test try to extract art from audio file with no stream or metadata tags at all.

        @details This a complete no result test, as the function has 2 possible extraction methods,
        ffmpeg (first), mutagen (backup).
        '''

        input_audio = SRC_NO_TAG_MP3
        art.extract_album_art(input_audio)
        art_exists = os.path.exists(EXPECTED_NO_TAG_MP3_JPG)
        self.assertFalse(art_exists)
        mock_info.assert_called_once_with(f"No video stream album art present in {input_audio}")
        mock_warning.assert_called_once_with(f"No album art present in {input_audio}")


    def test_extract_album_art_with_stream_and_tag(self):
        '''
        @brief Tests if album art is extracted from audio file.

        @details Happy path test case.
        '''

        input_audio = SRC_WMA
        art.extract_album_art(input_audio)
        has_jpg = os.path.exists(EXPECTED_WMA_JPG)
        self.assertTrue(has_jpg)


    def test_extract_album_art_without_stream_with_tag(self):
        '''
        @brief Tests if album art is extracted from audio file.

        @details Uses wma audio without a stream to ensure secondary (mutagen) extraction method is used.
        '''

        input_audio = SRC_NO_STREAM_WMA
        art.extract_album_art(input_audio)
        has_jpg = os.path.exists(EXPECTED_NO_STREAM_JPG)
        self.assertTrue(has_jpg)


    def test_extract_asf_art(self):
        '''
        @brief Tests if album art is extracted from wma/asf audio file.
        '''

        input_audio = SRC_WMA
        art.extract_asf_art(input_audio)
        art_exists = os.path.exists(EXPECTED_WMA_JPG)
        self.assertTrue(art_exists)


    def test_extract_ffmpeg_art(self):
        '''
        @brief Tests if album art is extracted from m4a audio file.
        '''

        input_audio = SRC_MP3
        art.extract_ffmpeg_art(input_audio)
        art_exists = os.path.exists(EXPECTED_MP3_JPG)
        self.assertTrue(art_exists)


    def test_extract_ffmpeg_art_no_stream(self):
        '''
        @brief Tests if album art is extracted from audio file without video stream.

        @details Expected to throw CalledProcessError.
        '''

        input_audio = SRC_NO_STREAM_WMA

        logging.disable(logging.ERROR)

        try:
            with self.assertRaises(CalledProcessError) as cm:
                art.extract_ffmpeg_art(input_audio)

            art_exists = os.path.exists(EXPECTED_NO_STREAM_JPG)
            self.assertFalse(art_exists)
            # Invalid argument is ffmpeg saying no video stream present
            self.assertTrue("Invalid argument" in cm.exception.stderr.strip())
        finally:
            logging.disable(original_log_level)


    def test_extract_m4a_art(self):
        '''
        @brief Tests if album art is extracted from m4a audio file.
        '''

        input_audio = SRC_M4A
        art.extract_m4a_art(input_audio)
        art_exists = os.path.exists(EXPECTED_M4A_JPG)
        self.assertTrue(art_exists)


    def test_extract_mp3_art(self):
        '''
        @brief Tests if album art is extracted from mp3 audio file.
        '''

        input_audio = SRC_MP3
        art.extract_mp3_art(input_audio)
        art_exists = os.path.exists(EXPECTED_MP3_JPG)
        self.assertTrue(art_exists)


    def test_has_video_stream_false(self):
        '''
        @brief Tests if audio file does not have video stream.
        '''

        input_audio = SRC_NO_STREAM_WMA
        has_video = art.has_video_stream(input_audio)
        self.assertFalse(has_video)


    def test_has_video_stream_true(self):
        '''
        @brief Tests if audio file does have video stream.
        '''

        input_audio = SRC_MP3
        has_video = art.has_video_stream(input_audio)
        self.assertTrue(has_video)


    # @unittest.skip("Skip until code written")
    # def test_has_video_stream_json_fail(self):
    #     '''
    #     @brief Tests if audio file with album art video stream fails json decoding.
    #     '''

    #     pass


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
    methods = get_method_names(TestAudioArt)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioArt(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
