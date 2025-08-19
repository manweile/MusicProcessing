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
from subprocess import CalledProcessError

# local modules
from src import EXPORT_TLD
from src import FOLDER_ART
from src.audio_info import AudioArt

gc.enable()

# get the dir path for test location need it to find audio files
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
TESTS_TLD = os.path.join(TESTS_PATH, EXPORT_TLD)

EXPECTED_MP3_JPG = os.path.join(TESTS_TLD, "Crush", "Here", FOLDER_ART)
EXPECTED_M4A_JPG = os.path.join(TESTS_TLD, "Joshua Davis", "The Voice Peformance", FOLDER_ART)
EXPECTED_NO_STREAM_JPG = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", FOLDER_ART)
EXPECTED_WMA_JPG = os.path.join(TESTS_TLD, "Elton John", "Goodbye Yellow Brick Road", FOLDER_ART)
EXPECTED_JPGS = [EXPECTED_MP3_JPG, EXPECTED_M4A_JPG, EXPECTED_NO_STREAM_JPG, EXPECTED_WMA_JPG]

SRC_MP3 = os.path.join(TESTS_TLD, "Crush", "Here", "Crush-Live.mp3")
SRC_M4A = os.path.join(TESTS_TLD, "Joshua Davis", "The Voice Peformance", "Joshua Davis-The Workingman's Hymn.m4a")
SRC_WMA = os.path.join(TESTS_TLD, "Elton John", "Goodbye Yellow Brick Road", "Elton John-Saturday Night's Alright for Fighting.wma")
NO_STREAM_WMA = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", "Billie Holiday-Georgia On My Mind.wma")

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


    def test_extract_asf_art(self):
        '''
        @brief Tests if album art is extracted from wma/asf audio file.
        '''

        input_audio = SRC_WMA
        art.extract_asf_art(input_audio)
        art_exists = os.path.exists(EXPECTED_WMA_JPG)
        self.assertTrue(art_exists)


    def test_extract_album_art(self):
        '''
        @brief Tests if album art is extracted from audio file.

        @details Uses wma audio without a stream to ensure secondary (mutagen) extraction method is used.
        '''

        input_audio = NO_STREAM_WMA
        art.extract_album_art(input_audio)
        has_jpg = os.path.exists(EXPECTED_NO_STREAM_JPG)
        self.assertTrue(has_jpg)


    # @todo
    # def test_extract_mp3_art


    # @todo
    # def test_extract_m4a_art


    def test_has_video_stream_false(self):
        '''
        @brief Tests if audio file does not have video stream.
        '''

        input_audio = NO_STREAM_WMA
        has_video = art.has_video_stream(input_audio)
        self.assertFalse(has_video)


    def test_has_video_stream_non_extant(self):
        '''
        @brief Tests check for audio stream on non-extant file.
        '''

        '''
        subprocess_utils.subprocess_run will throw CalledProcessError,
        which is raised to it's calling functions, like has_video_stream.
        Don't want the console output cluttered up,
        so we disable the logging at & below ERROR,
        which is what subprocess_run specifies for logging.
        '''
        logging.disable(logging.ERROR)

        has_video = None
        input_audio = os.path.join(TESTS_TLD, "Non-extant.wav")

        try:
            with self.assertRaises(CalledProcessError) as cm:
                has_video = art.has_video_stream(input_audio)

            self.assertIsNone(has_video)
            stderr = cm.exception.stderr.strip()
            expected_err = f"{input_audio}: No such file or directory"
            self.assertEqual(stderr, expected_err)
        finally:
            logging.disable(original_log_level)


    def test_has_video_stream_true(self):
        '''
        @brief Tests if audio file does have video stream.
        '''

        input_audio = SRC_MP3
        has_video = art.has_video_stream(input_audio)
        self.assertTrue(has_video)


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
