'''
@file test_audio_art.py
@brief Defines the test audio art class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import os
import unittest
from pathlib import Path
from subprocess import CalledProcessError
from unittest import TestCase

# local module constants
from src import FOLDER_ART
from tests import TEST_M3U
from tests import TEST_M4A_DAVIS, TEST_MP3_ABBA, TEST_MP3_CRUSH, TEST_WMA_HOLIDAY, TEST_WMA_JOHN
from tests import TESTS_TLD
# local module classes
from src.audio_info import AudioArt

gc.enable()

art = AudioArt()


class TestAudioArt(TestCase):
    '''
    @brief Tests AudioArt class functions.
    '''

    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite.

        @details These datums are used throughout class and only need init once.
        '''

        # don't add this one to delete list in tearDown, need it for an error test
        cls.found_album_art_jpg = os.path.join(TESTS_TLD, "Abba", "Waterloo", FOLDER_ART)

        cls.m4a_jpg = os.path.join(TESTS_TLD, "Joshua Davis", "The Voice Peformance", FOLDER_ART)
        cls.mp3_jpg = os.path.join(TESTS_TLD, "Crush", "Here", FOLDER_ART)
        cls.no_stream_jpg = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", FOLDER_ART)
        cls.set_album_art_jpg = os.path.join(TESTS_TLD, "Albert Collins", "Best Of The Blues, Vol. 1", FOLDER_ART)
        cls.wma_jpg = os.path.join(TESTS_TLD, "Elton John", "Goodbye Yellow Brick Road", FOLDER_ART)

        cls.src_has_jpg_path = os.path.join(TESTS_TLD, "Abba", "Waterloo")
        cls.src_no_tag_mp3 = os.path.join(TESTS_TLD, "Crush", "Here", "No_tag_Crush-Live.mp3")

        cls.src_has_jpg_audio = TEST_MP3_ABBA
        cls.src_m4a = TEST_M4A_DAVIS
        cls.src_mp3 = TEST_MP3_CRUSH
        cls.src_no_stream_wma = TEST_WMA_HOLIDAY
        cls.src_wma = TEST_WMA_JOHN


    def tearDown(self):
        '''
        @brief Clean up the created Folder.jpg files.
        '''

        delete_jpgs = [
            self.m4a_jpg,
            self.mp3_jpg,
            self.no_stream_jpg,
            self.set_album_art_jpg,
            self.wma_jpg
        ]

        for jpg in delete_jpgs:
            if os.path.exists(jpg):
                os.remove(jpg)


    def test_extract_album_art(self):
        '''
        @brief Tests if album art is extracted from audio file.

        @details Happy path test case.
        '''

        input_audio = self.src_wma
        art.extract_album_art(input_audio)
        has_jpg = os.path.exists(self.wma_jpg)
        self.assertTrue(has_jpg)


    def test_extract_album_art_folder_exists(self):
        '''
        brief Tests try to extract album art from file that already has co-located Folder.jpg file.
        '''

        input_audio = self.src_has_jpg_audio
        album_path = Path(input_audio).parent
        log_msg = f"{album_path} has a {FOLDER_ART}"

        with self.assertLogs() as captured:
            art.extract_album_art(input_audio)

        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), log_msg)


    def test_extract_album_art_invalid_audio(self):
        '''
        @brief Tests try to extract album art from non-valid file.
        '''

        input_audio = TEST_M3U
        input_path = Path(input_audio)
        log_msg = f"{input_path.name} is not an audio file"

        with self.assertLogs() as captured:
            art.extract_album_art(input_audio)

        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), log_msg)


    def test_extract_album_art_no_tag_or_stream(self):
        '''
        @brief Test try to extract art from audio file with no stream or metadata tags at all.

        @details This a complete no result test, as the function has 2 possible extraction methods,
        ffmpeg (primary), mutagen (secondary).
        '''

        input_audio = self.src_no_tag_mp3
        no_jpg = os.path.join(TESTS_TLD, FOLDER_ART)
        info_msg = f"No video stream album art present in {input_audio}"
        warning_msg = f"No album art present in {input_audio}"

        with self.assertLogs() as captured:
            art.extract_album_art(input_audio)

        art_exists = os.path.exists(no_jpg)
        self.assertFalse(art_exists)

        self.assertEqual(len(captured.records), 2)
        self.assertEqual(captured.records[0].getMessage(), info_msg)
        self.assertEqual(captured.records[1].getMessage(), warning_msg)


    def test_extract_album_art_without_stream_with_tag(self):
        '''
        @brief Tests if album art is extracted from audio file.

        @details Uses wma audio without a stream to ensure mutagen (secondary) extraction method is used.
        '''

        input_audio = self.src_no_stream_wma
        art.extract_album_art(input_audio)
        has_jpg = os.path.exists(self.no_stream_jpg)
        self.assertTrue(has_jpg)


    def test_extract_asf_art(self):
        '''
        @brief Tests if album art is extracted from wma/asf audio file.
        '''

        input_audio = self.src_wma
        art.extract_asf_art(input_audio)
        art_exists = os.path.exists(self.wma_jpg)
        self.assertTrue(art_exists)


    def test_extract_ffmpeg_art(self):
        '''
        @brief Tests if album art is extracted from an audio file.
        '''

        input_audio = self.src_mp3
        art.extract_ffmpeg_art(input_audio)
        art_exists = os.path.exists(self.mp3_jpg)
        self.assertTrue(art_exists)


    def test_extract_ffmpeg_art_no_stream(self):
        '''
        @brief Tests if album art is extracted from audio file without video stream.

        @details Expected to throw CalledProcessError.
        '''

        input_audio = self.src_no_stream_wma

        with self.assertRaises(CalledProcessError) as cm:
            art.extract_ffmpeg_art(input_audio)

        art_exists = os.path.exists(self.no_stream_jpg)
        self.assertFalse(art_exists)
        # Invalid argument is ffmpeg saying no video stream present
        self.assertTrue("Invalid argument" in cm.exception.stderr.strip())


    def test_extract_m4a_art(self):
        '''
        @brief Tests if album art is extracted from m4a audio file.
        '''

        input_audio = self.src_m4a
        art.extract_m4a_art(input_audio)
        art_exists = os.path.exists(self.m4a_jpg)
        self.assertTrue(art_exists)


    def test_extract_mp3_art(self):
        '''
        @brief Tests if album art is extracted from mp3 audio file.
        '''

        input_audio = self.src_mp3
        art.extract_mp3_art(input_audio)
        art_exists = os.path.exists(self.mp3_jpg)
        self.assertTrue(art_exists)


    def test_has_video_stream_false(self):
        '''
        @brief Tests if audio file does not have video stream.
        '''

        input_audio = self.src_no_stream_wma
        has_video = art.has_video_stream(input_audio)
        self.assertFalse(has_video)


    def test_has_video_stream_true(self):
        '''
        @brief Tests if audio file does have video stream.
        '''

        input_audio = self.src_mp3
        has_video = art.has_video_stream(input_audio)
        self.assertTrue(has_video)


    def test_set_album_art(self):
        '''
        @brief Tests setting album art file.
        '''

        art.set_album_art(TESTS_TLD)

        found_art_exists = os.path.exists(self.found_album_art_jpg)
        set_art_exists = os.path.exists(self.set_album_art_jpg)

        self.assertTrue(found_art_exists)
        self.assertTrue(set_art_exists)


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
