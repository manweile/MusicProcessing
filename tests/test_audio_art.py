'''
@class TestAudioArt
@file test_audio_art.py
@author Gerald Manweiler

@brief Defines the test audio art class.

@details Tests AudioArt album-art extraction and writing behavior.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import errno                                                # for operating-system error numbers
import inspect                                              # for test method discovery
import os                                                   # for file-system path operations
import shutil                                               # for test-fixture copying and removal
import struct                                               # for binary ASF image fixture construction
import unittest                                             # for direct test-suite execution
from pathlib import Path                                    # for test-fixture path manipulation
from subprocess import CalledProcessError                   # for expected ffmpeg extraction failures
from unittest import TestCase                               # for test-case assertions and lifecycle hooks
from unittest.mock import patch                             # for write-operation error simulation

# Local Module Constants
from src import FOLDER_ART                                  # for album-art fixture filenames
from src import MP3_EXT                                     # for MP3 file-pattern extraction tests
from src import PLAYLIST_EXTS                               # for invalid file-pattern extraction tests
from tests import TEST_FLAC_ALANNAH_MYLES                   # for FLAC album-art extraction tests
from tests import TEST_M3U                                  # for invalid audio input tests
from tests import TEST_M4A_DAVIS                            # for M4A album-art extraction tests
from tests import TEST_MP3_ABBA                             # for existing album-art file tests
from tests import TEST_MP3_CRUSH                            # for MP3 album-art extraction tests
from tests import TEST_MP3_NO_TAG                           # for absent album-art tests
from tests import TEST_WMA_HOLIDAY                          # for WMA metadata album-art tests
from tests import TEST_WMA_JOHN                             # for WMA stream album-art tests
from tests import TESTS_PATH                                # for prepared-fixture directory paths
from tests import TESTS_TLD                                 # for test music fixture paths

# Local Module Classes
from src.audio_info import AudioArt                         # for album-art functionality under test

## @var art
# @brief AudioArt instance under test.
# @details Provides access to album-art functionality.
art = AudioArt()


class TestAudioArt(TestCase):
    '''
    @brief Tests AudioArt class functions.

    @details Verifies album-art extraction, writing, and ASF image parsing behavior.
    '''

    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite.

        @details Creates shared input, output, and cleanup paths for the test suite.

        @param cls {type[TestAudioArt]} Test class receiving shared fixtures.
        '''

        # directory for "walk" type tests: D:\MusicProcessing\tests\PreppedMusic
        cls.prepped = os.path.join(TESTS_PATH, "PreppedMusic")

        # audio source files for walk tests
        cls.src_file_paths = [TEST_M4A_DAVIS, TEST_MP3_CRUSH, TEST_WMA_JOHN]

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
        cls.flac_jpg = os.path.join(TESTS_TLD, "Alannah Myles", "A-Lan-Nah", FOLDER_ART)
        cls.mp3_jpg = os.path.join(TESTS_TLD, "Crush", "Here", FOLDER_ART)
        cls.no_stream_jpg = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", FOLDER_ART)
        cls.set_album_art_jpg = os.path.join(TESTS_TLD, "Albert Collins", "Best Of The Blues, Vol. 1", FOLDER_ART)
        cls.wma_jpg = os.path.join(TESTS_TLD, "Elton John", "Goodbye Yellow Brick Road", FOLDER_ART)
        cls.delete_jpgs = [cls.m4a_jpg, cls.flac_jpg, cls.mp3_jpg, cls.no_stream_jpg, cls.set_album_art_jpg, cls.wma_jpg]


    @classmethod
    def tearDownClass(cls):
        '''
        @brief Clean up walk-test source files and directories.

        @details Removes the prepared directory when it was created during setup.

        @param cls {type[TestAudioArt]} Test class containing shared fixtures.
        '''

        if os.path.exists(cls.prepped):
            shutil.rmtree(cls.prepped)


    def tearDown(self):
        '''
        @brief Clean up the created Folder.jpg files.

        @details Removes album-art files created by individual test cases.

        @param self {TestAudioArt} Test instance containing cleanup paths.
        '''

        for jpg in self.delete_jpgs:
            if os.path.exists(jpg):
                os.remove(jpg)

        for jpg in self.prepped_results:
            if os.path.exists(jpg):
                os.remove(jpg)


    def test_extract_album_art(self):
        '''
        @brief Test album-art extraction from an audio file.

        @details Verifies extraction creates the expected album-art file.

        @test Happy path.

        @param self {TestAudioArt} Test instance containing expected output paths.
        '''

        input_audio = TEST_WMA_JOHN
        art.extract_album_art(input_audio)
        has_jpg = os.path.exists(self.wma_jpg)
        self.assertTrue(has_jpg)


    def test_extract_album_art_folder_exists(self):
        '''
        @brief Test album-art extraction when Folder.jpg already exists.

        @details Verifies extraction logs that the co-located album-art file already exists.

        @test Edge case.

        @param self {TestAudioArt} Test instance containing test fixture paths.
        '''

        input_audio = TEST_MP3_ABBA
        album_path = Path(input_audio).parent
        log_msg = f"{album_path} has a {FOLDER_ART}"

        with self.assertLogs() as captured:
            art.extract_album_art(input_audio)

        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), log_msg)


    def test_extract_album_art_invalid_audio(self):
        '''
        @brief Test album-art extraction from an invalid audio file.

        @details Verifies extraction logs a message for a non-audio playlist file.

        @test Error case.

        @param self {TestAudioArt} Test instance containing test fixture paths.
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
        @brief Test album-art extraction without streams or metadata tags.

        @details Verifies both ffmpeg and mutagen extraction paths report absent album art.

        @test Edge case.

        @param self {TestAudioArt} Test instance containing test fixture paths.
        '''

        input_audio = TEST_MP3_NO_TAG
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
        @brief Test album-art extraction without a video stream.

        @details Verifies the mutagen fallback extracts artwork from WM/Picture metadata.

        @test Edge case.

        @param self {TestAudioArt} Test instance containing expected output paths.
        '''

        input_audio = TEST_WMA_HOLIDAY
        art.extract_album_art(input_audio)
        has_jpg = os.path.exists(self.no_stream_jpg)
        self.assertTrue(has_jpg)


    def test_extract_asf_art(self):
        '''
        @brief Test ASF album-art extraction from a WMA file.

        @details Verifies the ASF extraction method creates the expected album-art file.

        @test Happy path.

        @param self {TestAudioArt} Test instance containing expected output paths.
        '''

        input_audio = TEST_WMA_JOHN
        art.extract_asf_art(input_audio)
        art_exists = os.path.exists(self.wma_jpg)
        self.assertTrue(art_exists)


    def test_extract_flac_art(self):
        '''
        @brief Test FLAC album-art extraction.

        @details Verifies extraction creates the expected album-art file.

        @test Happy path.

        @param self {TestAudioArt} Test instance containing expected output paths.
        '''

        input_audio = TEST_FLAC_ALANNAH_MYLES
        art.extract_album_art(input_audio)
        art_exists = os.path.exists(self.flac_jpg)
        self.assertTrue(art_exists)


    def test_extract_ffmpeg_art(self):
        '''
        @brief Test ffmpeg album-art extraction.

        @details Verifies the ffmpeg extraction method creates the expected album-art file.

        @test Happy path.

        @param self {TestAudioArt} Test instance containing expected output paths.
        '''

        input_audio = TEST_MP3_CRUSH
        art.extract_ffmpeg_art(input_audio)
        art_exists = os.path.exists(self.mp3_jpg)
        self.assertTrue(art_exists)


    def test_extract_ffmpeg_art_no_stream(self):
        '''
        @brief Test ffmpeg album-art extraction without a video stream.

        @details Verifies ffmpeg reports an invalid argument when no video stream is available.

        @test Error case.

        @param self {TestAudioArt} Test instance containing expected output paths.

        @exception CalledProcessError ffmpeg fails because the input has no video stream.
        '''

        input_audio = TEST_WMA_HOLIDAY

        with self.assertRaises(CalledProcessError) as cm:
            art.extract_ffmpeg_art(input_audio)

        art_exists = os.path.exists(self.no_stream_jpg)
        self.assertFalse(art_exists)

        # Invalid argument is ffmpeg saying no video stream present
        self.assertTrue("Invalid argument" in cm.exception.stderr.strip())


    def test_extract_m4a_art(self):
        '''
        @brief Test M4A album-art extraction.

        @details Verifies the M4A extraction method creates the expected album-art file.

        @test Happy path.

        @param self {TestAudioArt} Test instance containing expected output paths.
        '''

        input_audio = TEST_M4A_DAVIS
        art.extract_m4a_art(input_audio)
        art_exists = os.path.exists(self.m4a_jpg)
        self.assertTrue(art_exists)


    def test_extract_mp3_art(self):
        '''
        @brief Test MP3 album-art extraction.

        @details Verifies the MP3 extraction method creates the expected album-art file.

        @test Happy path.

        @param self {TestAudioArt} Test instance containing expected output paths.
        '''

        input_audio = TEST_MP3_CRUSH
        art.extract_mp3_art(input_audio)
        art_exists = os.path.exists(self.mp3_jpg)
        self.assertTrue(art_exists)


    def test_extract_walk(self):
        '''
        @brief Test album-art extraction from all valid audio files.

        @details Verifies walk extraction creates artwork for prepared files without a pattern.

        @test Happy path.

        @param self {TestAudioArt} Test instance containing prepared fixture paths.
        '''

        art.extract_walk(self.prepped, None)

        for jpg_file in self.prepped_results:
            jpg_exists = os.path.exists(jpg_file)
            self.assertTrue(jpg_exists)


    def test_extract_walk_pattern(self):
        '''
        @brief Test album-art extraction with an MP3 file pattern.

        @details Verifies walk extraction creates artwork only for matching prepared MP3 files.

        @test Happy path.

        @param self {TestAudioArt} Test instance containing prepared fixture paths.
        '''

        art.extract_walk(self.prepped, MP3_EXT)

        jpg_exists = os.path.exists(self.mp3_result)
        self.assertTrue(jpg_exists)


    def test_extract_walk_pattern_invalid(self):
        '''
        @brief Test album-art extraction with an invalid file pattern.

        @details Verifies walk extraction logs an error for a playlist file extension.

        @test Error case.

        @param self {TestAudioArt} Test instance containing prepared fixture paths.
        '''

        log_msg = f"Pattern {PLAYLIST_EXTS[0]} is not for a valid audio file"

        with self.assertLogs() as captured:
            art.extract_walk(self.prepped, PLAYLIST_EXTS[0])

        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), log_msg)


    def test_has_video_stream_false(self):
        '''
        @brief Test video-stream detection when no stream exists.

        @details Verifies the method returns false for a WMA file without a video stream.

        @test Edge case.

        @param self {TestAudioArt} Test instance containing test fixture paths.
        '''

        input_audio = TEST_WMA_HOLIDAY
        has_video = art.has_video_stream(input_audio)
        self.assertFalse(has_video)


    def test_has_video_stream_true(self):
        '''
        @brief Test video-stream detection when a stream exists.

        @details Verifies the method returns true for an MP3 file with a video stream.

        @test Happy path.

        @param self {TestAudioArt} Test instance containing test fixture paths.
        '''

        input_audio = TEST_MP3_CRUSH
        has_video = art.has_video_stream(input_audio)
        self.assertTrue(has_video)


    def test_set_album_art(self):
        '''
        @brief Test setting album-art files in an audio directory.

        @details Verifies existing artwork is retained and missing artwork is created.

        @test Happy path.

        @param self {TestAudioArt} Test instance containing expected output paths.
        '''

        art.set_album_art(TESTS_TLD)

        found_art_exists = os.path.exists(self.found_album_art_jpg)
        set_art_exists = os.path.exists(self.set_album_art_jpg)

        self.assertTrue(found_art_exists)
        self.assertTrue(set_art_exists)


    def test_unpack_asf_image_invalid_utf16(self):
        '''
        @brief Test ASF image parsing with invalid UTF-16 data.

        @details Verifies malformed UTF-16 metadata raises a value error.

        @test Error case.

        @param self {TestAudioArt} Test instance used for ASF image parsing.

        @exception ValueError ASF image metadata is not valid UTF-16-LE.
        '''

        data = bytearray(struct.pack('<bi', 3, 0) + b'\x00\xdc\x00\x00\x00\x00')

        with self.assertRaisesRegex(ValueError, "not valid UTF-16-LE"):
            art._AudioArt__unpack_asf_image(data)


    def test_unpack_asf_image_malformed_data(self):
        '''
        @brief Test ASF image parsing with malformed tag data.

        @details Verifies incomplete headers, MIME types, and image payloads raise value errors.

        @test Error case.

        @param self {TestAudioArt} Test instance used for ASF image parsing.

        @exception ValueError ASF image data is malformed.
        '''

        cases = (
            (bytearray(b'\xff'), "missing its header"),
            (bytearray(struct.pack('<bi', 3, 0) + b'i\x00'), "MIME type is missing its terminator"),
            (
                bytearray(struct.pack('<bi', 3, 2) + "image/jpeg".encode("utf-16-le") + b'\x00\x00\x00\x00\xff'),
                "image payload is truncated",
            ),
        )

        for data, error_message in cases:
            with self.subTest(error_message=error_message):
                with self.assertRaisesRegex(ValueError, error_message):
                    art._AudioArt__unpack_asf_image(data)


    def test_unpack_asf_image_valid_data(self):
        '''
        @brief Test ASF image parsing with valid tag data.

        @details Verifies the parser returns MIME type, image data, picture type, and description.

        @test Happy path.

        @param self {TestAudioArt} Test instance used for ASF image parsing.
        '''

        image_data = b'\xff\xd8'
        data = bytearray(b''.join((
            struct.pack('<bi', 3, len(image_data)),
            "image/jpeg".encode("utf-16-le"),
            b'\x00\x00',
            "Front cover".encode("utf-16-le"),
            b'\x00\x00',
            image_data,
        )))

        self.assertEqual(
            ("image/jpeg", bytearray(image_data), 3, "Front cover"),
            art._AudioArt__unpack_asf_image(data),
        )


    @patch("builtins.open", side_effect=BlockingIOError(errno.EWOULDBLOCK, "Operation blocked"))
    def test_write_data_blocking_error(self, mock_open):
        '''
        @brief Test write-data handling of a blocking I/O error.

        @details Verifies the mocked writer preserves the blocking error number and message.

        @test Error case.

        @param self {TestAudioArt} Test instance used for write-data error handling.
        @param mock_open {Mock} Patched file-opening function that raises a blocking error.

        @exception BlockingIOError Mocked write operation is blocked.
        '''

        data_bytes = (b"'\x03\x140\x00\x00i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g"
                      b"\x00\x00\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00")
        data_byte_array = bytearray(data_bytes)

        with self.assertRaises(BlockingIOError) as cm:
            art._AudioArt__write_data(TEST_MP3_CRUSH, data_byte_array)

        self.assertEqual(cm.exception.errno, errno.EWOULDBLOCK)
        self.assertEqual(cm.exception.strerror, "Operation blocked")
        mock_open.assert_called_once()


    @patch("builtins.open", side_effect=OSError(errno.EACCES, "Permission denied"))
    def test_write_data_os_error(self, mock_open):
        '''
        @brief Test write-data handling of an operating-system error.

        @details Verifies the mocked writer preserves the operating-system error number and message.

        @test Error case.

        @param self {TestAudioArt} Test instance used for write-data error handling.
        @param mock_open {Mock} Patched file-opening function that raises an operating-system error.

        @exception OSError Mocked write operation is denied.
        '''

        data_bytes = (
            b"'\x03\x140\x00\x00i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g"
            b"\x00\x00\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00"
        )
        data_byte_array = bytearray(data_bytes)

        with self.assertRaises(OSError) as cm:
            art._AudioArt__write_data(TEST_MP3_CRUSH, data_byte_array)

        self.assertEqual(cm.exception.errno, errno.EACCES)
        self.assertEqual(cm.exception.strerror, "Permission denied")
        mock_open.assert_called_once()


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
    @brief Entry point for running the test suite.

    @details Collects all test methods from the TestAudioArt class and executes them using a unittest test runner.

    @note This test module can be run directly with `python tests/test_audio_art.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestAudioArt)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioArt(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
