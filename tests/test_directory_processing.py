'''
@class TestDirectoryProcessing
@file test_directory_processing.py
@brief Defines the test directory processing class.

@details Tests directory creation, listing, path resolution, and safe removal behavior.

@version 1.0.0
@date 2026-09-22

@author Gerald Manweiler

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import errno                                                # for operating-system error number assertions
import inspect                                              # for test method discovery
import os                                                   # for file-system path operations
import shutil                                               # for test-fixture copying and removal
import sys                                                  # for file-system root-path tests
import unittest                                             # for direct test-suite execution
from pathlib import Path                                    # for test-fixture path manipulation
from unittest import TestCase                               # for test-case assertions and lifecycle hooks
from unittest.mock import Mock                              # for directory operation test doubles
from unittest.mock import patch                             # for warning-log interception

# Local Module Constants
from src import AUDIO_EXTS                                  # for non-audio path assertions
from src import CSV_DIR                                     # for generated CSV fixture directories
from src import CSV_EXT                                     # for generated CSV filename extensions
from src import M4A_EXT                                     # for M4A file-list filtering tests
from src import MP3_EXT                                     # for MP3 file-list filtering tests
from src import MUSIC_TLD                                   # for generated music directory paths
from src import RESULT_DIR                                  # for generated text fixture directories
from src import RESULT_EXT                                  # for generated text filename extensions
from src import WMA_EXT                                     # for WMA file-list filtering tests
from src.generated_files import GENERATED_PATH              # for generated test output paths
from tests import TEST_M3U                                  # for non-audio fixture tests
from tests import TEST_M4A_DAVIS                            # for M4A fixture path tests
from tests import TEST_MP3_ABBA                             # for MP3 fixture path tests
from tests import TEST_WMA_JOHN                             # for WMA fixture path tests
from tests import TESTS_PATH                                # for expected file fixture paths
from tests import TESTS_TLD                                 # for test music directory paths

# Local Module Errors
from src import MusicProcessingError                        # for safe-removal error assertions

# Local Module Classes
from src.dir_processing import DirectoryProcessing          # for directory functionality under test

## @var directory
# @brief DirectoryProcessing instance under test.
# @details Provides access to directory processing functionality.
directory = DirectoryProcessing()


class TestDirectoryProcessing(TestCase):
    '''
    @brief Tests DirectoryProcessing class functions.

    @details Verifies directory creation, discovery, reporting, and removal behavior.
    '''

    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite execution.

        @details Creates shared generated directory paths and temporary report directories.

        @param cls {type[TestDirectoryProcessing]} Test class receiving shared fixtures.
        '''

        # dest dir for make dir and move file tests
        cls.dir_path = os.path.join(GENERATED_PATH, MUSIC_TLD, "ArtistDir", "AlbumDir")
        cls.generated_tld = os.path.join(GENERATED_PATH, MUSIC_TLD)

        # temp dirs
        cls.csv_files = os.path.join(TESTS_PATH, CSV_DIR)
        os.makedirs(cls.csv_files, exist_ok=True)

        cls.result_files = os.path.join(TESTS_PATH, RESULT_DIR)
        os.makedirs(cls.result_files, exist_ok=True)


    @classmethod
    def tearDownClass(cls):
        '''
        @brief Clean up class-level test fixtures.

        @details Removes temporary CSV and result directories after the test suite completes.

        @param cls {type[TestDirectoryProcessing]} Test class containing shared fixture paths.
        '''

        if os.path.exists(cls.csv_files):
            shutil.rmtree(cls.csv_files)

        if os.path.exists(cls.result_files):
            shutil.rmtree(cls.result_files)


    def tearDown(self):
        '''
        @brief Clean up generated test output.

        @details Removes the generated music directory after each test case.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.
        '''

        if os.path.exists(self.generated_tld):
            shutil.rmtree(self.generated_tld)


    def test_create_csv_alt_dir_sorted(self):
        '''
        @brief Test sorted CSV creation in an alternate directory.

        @details Verifies generated CSV content is sorted and matches the expected fixture.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing CSV fixture paths.
        '''

        csv_dir = self.csv_files
        csv_filename = "alt_dir_sorted"

        # add datums in descending row order so we can test sort functionality
        data = []
        data.append(["Row4 Col1", "Row4 Col2"])
        data.append(["Row3 Col1", "Row3 Col2"])
        data.append(["Row2 Col1", "Row2 Col2"])
        data.append(["Row1 Col1", "Row1 Col2"])

        header_row = ["Col1", "Col2"]

        directory.create_csv(csv_filename, data, csv_dir, None, header_row, 1)

        created_csv = os.path.join(self.csv_files, csv_filename + CSV_EXT)
        created_exists = os.path.exists(created_csv)
        self.assertTrue(created_exists)

        expected_csv = os.path.join(TESTS_PATH, "expected.csv")

        with open(created_csv, "r") as f1, open(expected_csv, "r") as f2:
            content1 = f1.read()
            content2 = f2.read()
            self.assertEqual(content1, content2)


    def test_create_txt_alt_dir(self):
        '''
        @brief Test text-file creation in an alternate directory.

        @details Verifies generated text content matches the expected fixture.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing result fixture paths.
        '''

        result_dir = self.result_files
        result_filename = "alt_dir"

        data = []
        data.append("first text line")
        data.append("second text line")
        data.append("third text line")

        directory.create_txt(result_filename, data, result_dir)

        created_txt = os.path.join(self.result_files, result_filename + RESULT_EXT)
        created_exists = os.path.exists(created_txt)
        self.assertTrue(created_exists)

        expected_txt = os.path.join(TESTS_PATH, "expected.txt")

        with open(created_txt, "r") as f1, open(expected_txt, "r") as f2:
            content1 = f1.read()
            content2 = f2.read()
            self.assertEqual(content1, content2)


    def test_get_audio_file(self):
        '''
        @brief Test audio-file listing generation.

        @details Verifies CSV and text reports are created for all audio fixtures.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.
        '''

        directory.get_audio_file_list(TESTS_TLD)

        csv_dir = os.path.join(GENERATED_PATH, CSV_DIR)
        csv_filename = "get_audio_file_list" + CSV_EXT
        csv_path = os.path.join(csv_dir, csv_filename)
        csv_exists = os.path.exists(csv_path)

        txt_dir = os.path.join(GENERATED_PATH, RESULT_DIR)
        txt_filename = "get_audio_file_list" + RESULT_EXT
        txt_path = os.path.join(txt_dir, txt_filename)
        txt_exists = os.path.exists(txt_path)

        self.assertTrue(csv_exists)
        self.assertTrue(txt_exists)


    def test_get_ext_file_list_all(self):
        '''
        @brief Test file-list generation for all extensions.

        @details Verifies the generated CSV contains file-path and extension headers.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.
        '''

        csv_dir = os.path.join(GENERATED_PATH, CSV_DIR)
        csv_filename = "get_ext_file_list_all" + CSV_EXT
        csv_path = os.path.join(csv_dir, csv_filename)

        directory.get_ext_file_list(TESTS_TLD, None)

        csv_exists = os.path.exists(csv_path)
        self.assertTrue(csv_exists)

        with open(csv_path, "r") as f:
            lines = f.readlines()

        self.assertGreater(len(lines), 2)
        self.assertIn("File Path;File Ext\n", lines)


    def test_get_ext_file_list_m4a(self):
        '''
        @brief Test file-list generation for M4A files.

        @details Verifies an M4A-filtered CSV report is created with expected headers.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.
        '''

        csv_dir = os.path.join(GENERATED_PATH, CSV_DIR)
        csv_filename = "get_ext_file_list_m4a" + CSV_EXT
        csv_path = os.path.join(csv_dir, csv_filename)

        directory.get_ext_file_list(TESTS_TLD, M4A_EXT)

        csv_exists = os.path.exists(csv_path)
        self.assertTrue(csv_exists)

        with open(csv_path, "r") as f:
            lines = f.readlines()

        self.assertGreater(len(lines), 2)
        self.assertIn("File Path;File Ext\n", lines)


    def test_get_ext_file_list_mp3(self):
        '''
        @brief Test file-list generation for MP3 files.

        @details Verifies an MP3-filtered CSV report is created with expected headers.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.
        '''

        csv_dir = os.path.join(GENERATED_PATH, CSV_DIR)
        csv_filename = "get_ext_file_list_mp3" + CSV_EXT
        csv_path = os.path.join(csv_dir, csv_filename)

        directory.get_ext_file_list(TESTS_TLD, MP3_EXT)

        csv_exists = os.path.exists(csv_path)
        self.assertTrue(csv_exists)

        with open(csv_path, "r") as f:
            lines = f.readlines()

        self.assertGreater(len(lines), 2)
        self.assertIn("File Path;File Ext\n", lines)


    def test_get_ext_file_list_wma(self):
        '''
        @brief Test file-list generation for WMA files.

        @details Verifies a WMA-filtered CSV report is created with expected headers.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.
        '''

        csv_dir = os.path.join(GENERATED_PATH, CSV_DIR)
        csv_filename = "get_ext_file_list_wma" + CSV_EXT
        csv_path = os.path.join(csv_dir, csv_filename)

        directory.get_ext_file_list(TESTS_TLD, WMA_EXT)

        csv_exists = os.path.exists(csv_path)
        self.assertTrue(csv_exists)

        with open(csv_path, "r") as f:
            lines = f.readlines()

        self.assertGreater(len(lines), 2)
        self.assertIn("File Path;File Ext\n", lines)


    def test_get_file_directory(self):
        '''
        @brief Test directory lookup for an existing audio file.

        @details Verifies the search returns the containing directory for a known audio file.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing audio fixture paths.
        '''

        file_name = "Sawyer Fredricks - Shots Fired.mp3"
        start_path = TESTS_TLD

        dir_path = directory.get_file_directory(start_path, file_name)

        self.assertIsNotNone(dir_path)
        self.assertTrue(os.path.isdir(dir_path))


    def test_get_file_directory_none(self):
        '''
        @brief Test directory lookup for a missing audio file.

        @details Verifies the search returns none when the requested file is absent.

        @test Edge case.

        @param self {TestDirectoryProcessing} Test instance containing audio fixture paths.
        '''

        file_name = "Daughtry-Home.mp3"
        start_path = TESTS_TLD

        dir_path = directory.get_file_directory(start_path, file_name)

        self.assertIsNone(dir_path)


    def test_make_dir(self):
        '''
        @brief Test directory creation.

        @details Verifies a nested directory is created at the requested path.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.
        '''

        directory.make_dir(self.dir_path)

        dir_exists = os.path.exists(self.dir_path)
        self.assertTrue(dir_exists)


    def test_make_dir_fail(self):
        '''
        @brief Test directory creation with an operating-system error.

        @details Verifies the mocked directory method propagates an invalid-argument error.

        @test Error case.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.

        @exception OSError Mocked directory creation receives an invalid argument.
        '''

        bad_path = os.path.join(GENERATED_PATH, MUSIC_TLD, "?bad_path")

        make_dir_directory = DirectoryProcessing()

        mock_make_dir = Mock(spec=make_dir_directory)
        mock_make_dir.side_effect = OSError(errno.EINVAL, "Invalid argument")

        make_dir_directory.make_dir = mock_make_dir

        with self.assertRaises(OSError) as cm:
            make_dir_directory.make_dir(bad_path)

        dir_exists = os.path.exists(bad_path)

        self.assertFalse(dir_exists)
        self.assertEqual("OSError", cm.exception.__class__.__name__)
        self.assertEqual(cm.exception.errno, 22)

        mock_make_dir.reset_mock(return_value=True, side_effect=True)


    def test_make_dir_permission(self):
        '''
        @brief Test directory creation with a permission error.

        @details Verifies the mocked directory method propagates a permission-denied error.

        @test Error case.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.

        @exception OSError Mocked directory creation is denied permission.
        '''

        make_dir_directory = DirectoryProcessing()

        mock_make_dir = Mock(spec=make_dir_directory)
        mock_make_dir.side_effect = OSError(errno.EACCES, "Permission denied")

        make_dir_directory.make_dir = mock_make_dir

        with self.assertRaises(OSError) as cm:
            make_dir_directory.make_dir(self.dir_path)

        dir_exists = os.path.exists(self.dir_path)

        self.assertFalse(dir_exists)
        self.assertEqual(cm.exception.errno, errno.EACCES)

        mock_make_dir.reset_mock(return_value=True, side_effect=True)


    def test_path_info(self):
        '''
        @brief Test generated output path resolution for an audio file.

        @details Verifies path information maps an M4A fixture to its generated MP3 path.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing audio fixture paths.
        '''

        path_info = directory.path_info(TEST_M4A_DAVIS)

        # successful path_info returns a mp3 file name in generated_files/Music
        expected_info = os.path.join(GENERATED_PATH, MUSIC_TLD, "Joshua Davis", "The Voice Peformance", "Joshua Davis-The Workingman's Hymn.mp3")
        self.assertEqual(path_info, expected_info)


    @patch('src.dir_processing.directory_processing.logger.warning')
    def test_path_info_not_audio(self, mock_warning):
        '''
        @brief Test path information for a non-audio file.

        @details Verifies a playlist input returns none and logs a warning.

        @test Error case.

        @param self {TestDirectoryProcessing} Test instance containing audio fixture paths.
        @param mock_warning {Mock} Patched warning logger for non-audio input.
        '''

        input_path = os.path.join(TESTS_TLD, "expected.m3u")

        path_info = directory.path_info(input_path)

        self.assertIsNone(path_info)
        mock_warning.assert_called_once_with(f"File {input_path} is not in {AUDIO_EXTS}")


    def test_remove_album_dir(self):
        '''
        @brief Test removal of empty album directories.

        @details Verifies empty album directories are removed while non-empty paths remain.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.
        '''

        # need a non-audio file in tld
        m3u_base = os.path.basename(TEST_M3U)
        m3u_file = os.path.join(self.generated_tld, m3u_base)
        os.makedirs(self.generated_tld)
        shutil.copy(TEST_M3U, m3u_file)

        # need an empty album dir
        davis_file_path = Path(TEST_M4A_DAVIS)
        davis_file_parent = davis_file_path.parent
        davis_path_parts = davis_file_parent.parts
        davis_full_len = len(davis_path_parts)
        davis_artist_len = davis_full_len - 2
        davis_artist_album = ""
        for i in range(davis_artist_len, davis_full_len):
            davis_artist_album = os.path.join(davis_artist_album, davis_path_parts[i])

        empty_album_dir = os.path.join(self.generated_tld, davis_artist_album)
        os.makedirs(empty_album_dir)

        # need and empty artist dir
        abba_file_path = Path(TEST_MP3_ABBA)
        abba_file_parent = abba_file_path.parent
        abba_path_parts = abba_file_parent.parts[:-1]
        abba_full_len = len(abba_path_parts)
        abba_artist_len = abba_full_len - 1
        abba_artist = ""
        for i in range(abba_artist_len, abba_full_len):
            abba_artist = os.path.join(abba_artist, abba_path_parts[i])

        empty_artist_dir = os.path.join(self.generated_tld, abba_artist)
        os.makedirs(empty_artist_dir)

        # need a full album dir
        john_file_path = Path(TEST_WMA_JOHN)
        john_file_parent = john_file_path.parent
        john_path_parts = john_file_parent.parts
        john_full_len = len(john_path_parts)
        john_artist_len = john_full_len - 2
        john_artist_album = ""
        for i in range(john_artist_len, john_full_len):
            john_artist_album = os.path.join(john_artist_album, john_path_parts[i])

        full_album_dir = os.path.join(self.generated_tld, john_artist_album)
        john_file_name = os.path.basename(TEST_WMA_JOHN)
        full_album_path = os.path.join(full_album_dir, john_file_name)
        os.makedirs(full_album_dir)
        shutil.copy(TEST_WMA_JOHN, full_album_path)

        r'''
        expected dir contents
        /generated_files/Music
            test.m3u
            /Abba
            /Elton John
                /Goodbye Yellow Brick Road
                    Elton John-Saturday Night's Alright for Fighting.wma
        '''
        directory.remove_empty_album_dir(self.generated_tld)

        m3u_exists = os.path.exists(m3u_file)
        empty_album_exists = os.path.exists(empty_album_dir)
        # check is empty
        empty_artist_exists = os.path.isdir(empty_artist_dir) and not os.listdir(empty_artist_dir)
        full_album_exists = os.path.exists(full_album_path)

        self.assertTrue(m3u_exists)
        self.assertFalse(empty_album_exists)
        self.assertTrue(empty_artist_exists)
        self.assertTrue(full_album_exists)


    def test_remove_album_dir_fail(self):
        '''
        @brief Test album-directory removal with an operating-system error.

        @details Verifies the mocked removal method propagates an invalid-argument error.

        @test Error case.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.

        @exception OSError Mocked album-directory removal receives an invalid argument.
        '''

        remove_album_dir_directory = DirectoryProcessing()

        mock_remove_album_dir = Mock(spec=remove_album_dir_directory)
        mock_remove_album_dir.side_effect = OSError(errno.EINVAL, "Invalid argument")

        remove_album_dir_directory.remove_empty_album_dir = mock_remove_album_dir

        with self.assertRaises(OSError) as cm:
            remove_album_dir_directory.remove_empty_album_dir(self.generated_tld)

        self.assertEqual("OSError", cm.exception.__class__.__name__)
        self.assertEqual(cm.exception.errno, 22)

        mock_remove_album_dir.reset_mock(return_value=True, side_effect=True)


    def test_remove_album_dir_permission(self):
        '''
        @brief Test album-directory removal with a permission error.

        @details Verifies the mocked removal method propagates a permission-denied error.

        @test Error case.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.

        @exception OSError Mocked album-directory removal is denied permission.
        '''

        remove_album_dir_directory = DirectoryProcessing()

        mock_remove_album_dir = Mock(spec=remove_album_dir_directory)
        mock_remove_album_dir.side_effect = OSError(errno.EACCES, "Permission denied")

        remove_album_dir_directory.remove_empty_album_dir = mock_remove_album_dir

        with self.assertRaises(OSError) as cm:
            remove_album_dir_directory.remove_empty_album_dir(self.generated_tld)

        self.assertEqual(cm.exception.errno, errno.EACCES)

        mock_remove_album_dir.reset_mock(return_value=True, side_effect=True)


    def test_remove_pattern(self):
        '''
        @brief Test removal of a file matching a specified pattern.

        @details Verifies a matching playlist file is removed from the generated music directory.

        @test Happy path.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.
        '''

        os.makedirs(self.generated_tld)

        m3u_base = os.path.basename(TEST_M3U)
        m3u_file = os.path.join(self.generated_tld, m3u_base)
        shutil.copy(TEST_M3U, m3u_file)

        directory.remove_pattern(self.generated_tld, m3u_base)

        m3u_exists = os.path.exists(m3u_file)
        self.assertFalse(m3u_exists)


    def test_remove_pattern_fail(self):
        '''
        @brief Test pattern removal with an operating-system error.

        @details Verifies the mocked removal method propagates an invalid-argument error.

        @test Error case.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.

        @exception OSError Mocked pattern removal receives an invalid argument.
        '''

        remove_pattern_directory = DirectoryProcessing()

        mock_remove_pattern = Mock(spec=remove_pattern_directory)
        mock_remove_pattern.side_effect = OSError(errno.EINVAL, "Invalid argument")

        remove_pattern_directory.remove_pattern = mock_remove_pattern

        with self.assertRaises(OSError) as cm:
            remove_pattern_directory.remove_pattern(self.generated_tld, "blah.blah")

        self.assertEqual("OSError", cm.exception.__class__.__name__)
        self.assertEqual(cm.exception.errno, 22)

        mock_remove_pattern.reset_mock(return_value=True, side_effect=True)


    def test_remove_pattern_permission(self):
        '''
        @brief Test pattern removal with a permission error.

        @details Verifies the mocked removal method propagates a permission-denied error.

        @test Error case.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.

        @exception OSError Mocked pattern removal is denied permission.
        '''

        remove_pattern_directory = DirectoryProcessing()

        mock_remove_pattern = Mock(spec=remove_pattern_directory)
        mock_remove_pattern.side_effect = OSError(errno.EACCES, "Permission denied")

        remove_pattern_directory.remove_pattern = mock_remove_pattern

        with self.assertRaises(OSError) as cm:
            remove_pattern_directory.remove_pattern(self.generated_tld, "blah.blah")

        self.assertEqual(cm.exception.errno, errno.EACCES)

        mock_remove_pattern.reset_mock(return_value=True, side_effect=True)


    def test_remove_pattern_mount(self):
        '''
        @brief Test pattern removal from a mount point.

        @details Verifies a mount-point path raises a music processing error.

        @test Error case.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.

        @exception MusicProcessingError The requested path is a mount point.
        '''

        err_msg = f"{self.generated_tld} is a mount point"

        remove_pattern_directory = DirectoryProcessing()

        mock_remove_pattern = Mock(spec=remove_pattern_directory)
        mock_remove_pattern.side_effect = MusicProcessingError(err_msg)

        remove_pattern_directory.remove_pattern = mock_remove_pattern

        with self.assertRaises(MusicProcessingError) as cm:
            remove_pattern_directory.remove_pattern(self.generated_tld, "blah.blah")

        self.assertEqual("MusicProcessingError", cm.exception.__class__.__name__)
        self.assertEqual(cm.exception.message, err_msg)

        mock_remove_pattern.reset_mock(return_value=True, side_effect=True)


    def test_remove_pattern_root(self):
        '''
        @brief Test pattern removal from the file-system root.

        @details Verifies a root path raises a music processing error.

        @test Error case.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.

        @exception MusicProcessingError The requested path is the file-system root.
        '''

        sys_executable = Path(sys.executable)
        root_path = sys_executable.anchor

        pattern = "blah.blah"

        with self.assertRaises(MusicProcessingError) as cm:
            directory.remove_pattern(root_path, pattern)

        self.assertEqual("MusicProcessingError", cm.exception.__class__.__name__)
        self.assertEqual(cm.exception.message, f"{root_path} is file system root")


    def test_remove_pattern_wildcard(self):
        '''
        @brief Test pattern removal with a full wildcard.

        @details Verifies an overly broad wildcard raises a music processing error.

        @test Error case.

        @param self {TestDirectoryProcessing} Test instance containing generated output paths.

        @exception MusicProcessingError The supplied wildcard pattern is too broad.
        '''

        pattern = "*.*"

        with self.assertRaises(MusicProcessingError) as cm:
            directory.remove_pattern(self.generated_tld, pattern)

        self.assertEqual("MusicProcessingError", cm.exception.__class__.__name__)
        self.assertEqual(cm.exception.message, f"{pattern} is too broad")


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
    @brief Run the DirectoryProcessing test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.
    '''
    methods = get_method_names(TestDirectoryProcessing)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestDirectoryProcessing(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
