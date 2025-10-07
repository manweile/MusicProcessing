
'''
@file test_directory_processing.py
@brief Defines the test directory processing class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import errno
import gc
import inspect
import os
import shutil
import unittest
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

# local module constants
from src import AUDIO_EXTS
from src import MUSIC_TLD
from src import CSV_DIR, CSV_EXT
from src import RESULT_DIR, RESULT_EXT
from src.generated_files import GENERATED_FILES
from tests import TEST_M4A_DAVIS
from tests import TESTS_PATH, TESTS_TLD
# local module classes
from src.dir_processing import DirectoryProcessing

gc.enable()

# instantiate classes here
directory = DirectoryProcessing()


class TestDirectoryProcessing(TestCase):
    '''
    @brief Tests DirectoryProcessing class functions.
    '''

    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite execution.

        @details These datums are used throughout class and only need init once.
        '''

        # dest dir for make dir and move file tests
        cls.dir_path = os.path.join(GENERATED_FILES, MUSIC_TLD, "DirOne", "DirTwo")
        cls.generated_path = os.path.join(GENERATED_FILES, MUSIC_TLD)

        # temp dirs
        cls.csv_files = os.path.join(TESTS_PATH, CSV_DIR)
        os.makedirs(cls.csv_files, exist_ok=True)

        cls.result_files = os.path.join(TESTS_PATH, RESULT_DIR)
        os.makedirs(cls.result_files, exist_ok=True)


    @classmethod
    def tearDownClass(cls):
        '''
        @brief Cleans up class level datums after test suite execution.
        '''

        if os.path.exists(cls.csv_files):
            shutil.rmtree(cls.csv_files)

        if os.path.exists(cls.result_files):
            shutil.rmtree(cls.result_files)

    def tearDown(self):
        '''
        @brief Cleans up after tests.

        @details Runs after every test definition.
        '''

        if os.path.exists(self.generated_path):
            shutil.rmtree(self.generated_path)


    def test_create_csv_alt_dir_sorted(self):
        '''
        @brief testing creating a sorted csv file in alternate directory.
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

        directory.create_csv(csv_filename, data, csv_dir, header_row, 1)

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
        @brief testing creating a text file in alternate directory.
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
        @brief Test generates a csv containing full path for all audio files.
        '''

        directory.get_audio_file_list(TESTS_TLD)

        csv_dir = os.path.join(GENERATED_FILES, CSV_DIR)
        csv_filename = "get_audio_file_list" + CSV_EXT
        csv_path = os.path.join(csv_dir, csv_filename)
        csv_exists = os.path.exists(csv_path)

        txt_dir = os.path.join(GENERATED_FILES, RESULT_DIR)
        txt_filename = "get_audio_file_list" + RESULT_EXT
        txt_path = os.path.join(txt_dir, txt_filename)
        txt_exists = os.path.exists(txt_path)

        self.assertTrue(csv_exists)
        self.assertTrue(txt_exists)


    def test_get_ext_file_list_all(self):
        '''
        @brief tests generates a csv containing full file path for an extension.
        '''

        csv_dir = os.path.join(GENERATED_FILES, CSV_DIR)
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
        @brief tests generates a csv containing full file path for an extension.
        '''

        csv_dir = os.path.join(GENERATED_FILES, CSV_DIR)
        csv_filename = "get_ext_file_list_m4a" + CSV_EXT
        csv_path = os.path.join(csv_dir, csv_filename)

        directory.get_ext_file_list(TESTS_TLD, ".m4a")

        csv_exists = os.path.exists(csv_path)
        self.assertTrue(csv_exists)

        with open(csv_path, "r") as f:
            lines = f.readlines()

        self.assertGreater(len(lines), 2)
        self.assertIn("File Path;File Ext\n", lines)


    def test_get_ext_file_list_mp3(self):
        '''
        @brief tests generates a csv containing full file path for an extension.
        '''

        csv_dir = os.path.join(GENERATED_FILES, CSV_DIR)
        csv_filename = "get_ext_file_list_mp3" + CSV_EXT
        csv_path = os.path.join(csv_dir, csv_filename)

        directory.get_ext_file_list(TESTS_TLD, ".mp3")

        csv_exists = os.path.exists(csv_path)
        self.assertTrue(csv_exists)

        with open(csv_path, "r") as f:
            lines = f.readlines()

        self.assertGreater(len(lines), 2)
        self.assertIn("File Path;File Ext\n", lines)


    def test_get_ext_file_list_wma(self):
        '''
        @brief tests generates a csv containing full file path for an extension.
        '''

        csv_dir = os.path.join(GENERATED_FILES, CSV_DIR)
        csv_filename = "get_ext_file_list_wma" + CSV_EXT
        csv_path = os.path.join(csv_dir, csv_filename)

        directory.get_ext_file_list(TESTS_TLD, ".wma")

        csv_exists = os.path.exists(csv_path)
        self.assertTrue(csv_exists)

        with open(csv_path, "r") as f:
            lines = f.readlines()

        self.assertGreater(len(lines), 2)
        self.assertIn("File Path;File Ext\n", lines)


    def test_get_file_directory_none(self):
        '''
        @brief Tests could not find the directory path of a file given its name and a starting search path.
        '''

        file_name = "Daughtry-Home.mp3"
        start_path = TESTS_TLD
        dir_path = directory.get_file_directory(start_path, file_name)
        self.assertIsNone(dir_path)


    def test_get_file_directory(self):
        '''
        @brief Tests could find the directory path of a file given its name and a starting search path.
        '''

        file_name = "Sawyer Fredricks - Shots Fired.mp3"
        start_path = TESTS_TLD
        dir_path = directory.get_file_directory(start_path, file_name)
        self.assertIsNotNone(dir_path)
        self.assertTrue(os.path.isdir(dir_path))


    def test_make_dir(self):
        '''
        @brief Tests creates a directory.
        '''

        directory.make_dir(self.dir_path)

        dir_exists = os.path.exists(self.dir_path)
        self.assertTrue(dir_exists)


    def test_make_dir_fail(self):
        '''
        @brief Tests creates a directory throws general OSError.
        '''

        bad_path = os.path.join(GENERATED_FILES, MUSIC_TLD, "?bad_path")

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
        @brief Tests creates a directory throws OSError permission error.
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
        @brief Tests getting a path info for audio file.
        '''

        path_info = directory.path_info(TEST_M4A_DAVIS)

        # successful path_info returns a mp3 file name in generated_files/Music
        expected_info = os.path.join(GENERATED_FILES, MUSIC_TLD, "Joshua Davis", "The Voice Peformance", "Joshua Davis-The Workingman's Hymn.mp3")
        self.assertEqual(path_info, expected_info)


    @patch('src.dir_processing.directory_processing.logger.warning')
    def test_path_info_not_audio(self, mock_warning):
        '''
        @brief Tests if trying to get path info for a non-audio file.
        '''

        input_path = os.path.join(TESTS_TLD, "expected.m3u")
        path_info = directory.path_info(input_path)
        self.assertIsNone(path_info)
        mock_warning.assert_called_once_with(f"File {input_path} is not in {AUDIO_EXTS}")


    @unittest.skip("complete")
    def test_remove_album_dir(self):
        '''
        @brief Tests removes empty album directories.
        '''

        pass


    @unittest.skip("complete")
    def test_remove_album_dir_fail(self):
        '''
        @brief Tests removes empty album directories cause general OSError.
        '''

        pass


    @unittest.skip("complete")
    def test_remove_album_dir_permission(self):
        '''
        @brief Tests removes empty album directories cause permission denied OSError.
        '''

        pass


    @unittest.skip("complete")
    def test_remove_pattern(self):
        '''
        @brief Test removes file matching specified pattern.
        '''

        pass


    @unittest.skip("complete")
    def test_remove_pattern_fail(self):
        '''
        @brief Test removes file matching specified pattern causes general OSError.
        '''

        pass


    @unittest.skip("complete")
    def test_remove_pattern_permission(self):
        '''
        @brief Test removes file matching specified pattern causes permission denied OSError.
        '''

        pass


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
    methods = get_method_names(TestDirectoryProcessing)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestDirectoryProcessing(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
