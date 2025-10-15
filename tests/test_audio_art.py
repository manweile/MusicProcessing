'''
@file test_audio_art.py
@brief Defines the test audio art class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import errno
import gc
import inspect
import os
import shutil
import struct
import unittest
from pathlib import Path

from subprocess import CalledProcessError
from unittest import TestCase
from unittest.mock import Mock, patch
# local module constants
from src import AUDIO_EXTS, FOLDER_ART, PLAYLIST_EXTS
from src import UTF8
from tests import TEST_M3U
from tests import TEST_M4A_DAVIS, TEST_MP3_ABBA, TEST_MP3_CRUSH, TEST_MP3_NO_TAG, TEST_WMA_HOLIDAY, TEST_WMA_JOHN
from tests import TESTS_PATH, TESTS_TLD
# local module classes
from src.audio_info import AudioArt

gc.enable()

## @var art
# @brief instance of AudioArt class
# @details used for accessing class functionality
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

        # directory for "walk" type tests: D:\MusicProcessing\tests\PreppedMusic
        cls.prepped = os.path.join(TESTS_PATH, "PreppedMusic")

        # audio source files for walk tests
        cls.src_file_paths = [TEST_M4A_DAVIS, TEST_MP3_CRUSH, TEST_WMA_JOHN]

        # test patterns
        cls.m3u_pattern = PLAYLIST_EXTS[0]
        cls.mp3_pattern = AUDIO_EXTS[0]

        # results files
        cls.mp3_result = os.path.join(cls.prepped, "Crush", "Here", FOLDER_ART)

        cls.prepped_results = []
        cls.prepped_results.append(os.path.join(cls.prepped, "Joshua Davis", "The Voice Peformance", FOLDER_ART))
        cls.prepped_results.append(cls.mp3_result)
        cls.prepped_results.append(os.path.join(cls.prepped, "Elton John", "Goodbye Yellow Brick Road", FOLDER_ART))

        # copy input files to "walk" directory
        for src_path in cls.src_file_paths:
            # get the audio file name w/o path
            file_name = os.path.basename(src_path)

            # get audio file parent path parts
            file_path = Path(src_path)
            file_parent = file_path.parent
            path_parts = file_parent.parts

            # build up the artist & album path, from last 2 elements of file parent path parts
            full_len = len(path_parts)
            artist_len = full_len - 2
            artist_album = ""
            for i in range(artist_len, full_len):
                artist_album = os.path.join(artist_album, path_parts[i])

            # create the destination directory and copy file
            dest_dir = os.path.join(cls.prepped, artist_album)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, file_name)
            shutil.copy(src_path, dest_path)

        # don't add this one to delete list used by tearDown, need it for an error test
        cls.found_album_art_jpg = os.path.join(TESTS_TLD, "Abba", "Waterloo", FOLDER_ART)

        cls.m4a_jpg = os.path.join(TESTS_TLD, "Joshua Davis", "The Voice Peformance", FOLDER_ART)
        cls.mp3_jpg = os.path.join(TESTS_TLD, "Crush", "Here", FOLDER_ART)
        cls.no_stream_jpg = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", FOLDER_ART)
        cls.set_album_art_jpg = os.path.join(TESTS_TLD, "Albert Collins", "Best Of The Blues, Vol. 1", FOLDER_ART)
        cls.wma_jpg = os.path.join(TESTS_TLD, "Elton John", "Goodbye Yellow Brick Road", FOLDER_ART)
        cls.delete_jpgs = [cls.m4a_jpg, cls.mp3_jpg, cls.no_stream_jpg, cls.set_album_art_jpg, cls.wma_jpg]

        cls.src_has_jpg_path = os.path.join(TESTS_TLD, "Abba", "Waterloo")
        cls.src_no_tag_mp3 = TEST_MP3_NO_TAG

        cls.src_has_jpg_audio = TEST_MP3_ABBA
        cls.src_m4a = TEST_M4A_DAVIS
        cls.src_mp3 = TEST_MP3_CRUSH
        cls.src_no_stream_wma = TEST_WMA_HOLIDAY
        cls.src_wma = TEST_WMA_JOHN


    @classmethod
    def tearDownClass(cls):
        '''
        @brief Cleans up the walk type tests source audio files and directories.
        '''

        if os.path.exists(cls.prepped):
            shutil.rmtree(cls.prepped)


    def tearDown(self):
        '''
        @brief Clean up the created Folder.jpg files.
        '''

        for jpg in self.delete_jpgs:
            if os.path.exists(jpg):
                os.remove(jpg)

        for jpg in self.prepped_results:
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


    def test_extract_walk(self):
        '''
        #brief Test extracting album art from all valid audio files in a top level directory.

        @details Audio files must not have a co-located Folder.jpg file.
        @details Happy path test without a file pattern.
        '''

        art.extract_walk(self.prepped, None)

        for jpg_file in self.prepped_results:
            jpg_exists = os.path.exists(jpg_file)
            self.assertTrue(jpg_exists)


    def test_extract_walk_pattern(self):
        '''
        #brief Test extracting album art from mp3 audio files in a top level directory.

        @details Audio files must not have a co-located Folder.jpg file.
        @details Happy path test with a file pattern.
        '''

        art.extract_walk(self.prepped, self.mp3_pattern)

        jpg_exists = os.path.exists(self.mp3_result)
        self.assertTrue(jpg_exists)


    def test_extract_walk_pattern_invalid(self):
        '''
        #brief Test try extracting album art with invalid file pattern.
        '''

        log_msg = f"Pattern {self.m3u_pattern} is not for a valid audio file"

        with self.assertLogs() as captured:
            art.extract_walk(self.prepped, self.m3u_pattern)

        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), log_msg)


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


    @patch.object(AudioArt, '_AudioArt__unpack_asf_image')
    def test_unpack_asf_image_decode_error(self, mock_unpack_asf_image):
        '''
        @brief Tests unpack_asf_image throws UnicodeDecodeError.
        '''

        data_bytes = b"'\x03\x140\x00\x00i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00\x00\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00"
        data_byte_array = bytearray(data_bytes)
        unpacked_art = None

        mock_unpack_asf_image.side_effect = UnicodeDecodeError(UTF8, b'\xff', 0, 1, 'invalid start byte')

        with self.assertRaises(UnicodeDecodeError) as cm:
            unpacked_art = art._AudioArt__unpack_asf_image(data_byte_array)

        self.assertIsNone(unpacked_art)
        self.assertEqual("UnicodeDecodeError", cm.exception.__class__.__name__)
        self.assertEqual("invalid start byte", cm.exception.reason)

        mock_unpack_asf_image.reset_mock(return_value=True, side_effect=True)


    def test_unpack_asf_image_struct_error(self):
        '''
        @brief Tests unpack_asf_image throws struct error.
        '''

        data_bytes = b'\xff'
        data_byte_array = bytearray(data_bytes)
        unpacked_art = None

        with self.assertRaises(struct.error) as cm:
            unpacked_art = art._AudioArt__unpack_asf_image(data_byte_array)

        self.assertIsNone(unpacked_art)
        self.assertEqual("error", cm.exception.__class__.__name__)

        err_msg = "unpack_from requires a buffer of at least 5 bytes for unpacking 5 bytes at offset 0 (actual buffer size is 1)"
        self.assertEqual(err_msg, cm.exception.args[0])


    def test_write_data_blocking_error(self):
        '''
        @brief Tests write_data throws BlockingIOError.
        '''

        data_bytes = b"'\x03\x140\x00\x00i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00\x00\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00"
        data_byte_array = bytearray(data_bytes)

        write_data_art = AudioArt()

        mock_write_data = Mock(spec=write_data_art)
        mock_write_data.side_effect = BlockingIOError(errno.EWOULDBLOCK, "Operation blocked")

        write_data_art.__write_data = mock_write_data

        with self.assertRaises(BlockingIOError) as cm:
            write_data_art.__write_data(TEST_MP3_CRUSH, data_byte_array)

        self.assertEqual(cm.exception.errno, errno.EWOULDBLOCK)
        self.assertEqual(cm.exception.strerror, "Operation blocked")

        mock_write_data.reset_mock(return_value=True, side_effect=True)


    def test_write_data_os_error(self):
        '''
        @brief Tests write_data throws OSError.
        '''

        data_bytes = b"'\x03\x140\x00\x00i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00\x00\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00"
        data_byte_array = bytearray(data_bytes)

        write_data_art = AudioArt()

        mock_write_data = Mock(spec=write_data_art)
        mock_write_data.side_effect = OSError(errno.EACCES, "Permission denied")

        write_data_art.__write_data = mock_write_data

        with self.assertRaises(OSError) as cm:
            write_data_art.__write_data(TEST_MP3_CRUSH, data_byte_array)

        self.assertEqual(cm.exception.errno, errno.EACCES)
        self.assertEqual(cm.exception.strerror, "Permission denied")

        mock_write_data.reset_mock(return_value=True, side_effect=True)


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
