
'''
@file test_directory_processing.py
@brief Defines the test directory processing class.

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
from src import AUDIO_EXTS
from src import MUSIC_TLD
from src.generated_files import GENERATED_FILES
from tests import TEST_M4A_DAVIS
from tests import TESTS_TLD
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

        pass


    @classmethod
    def tearDownClass(cls):
        '''
        @brief Cleans up class level datums after test suite execution.
        '''

        pass


    def tearDown(self):
        '''
        @brief Cleans up after tests.

        @details Runs after every test definition.
        '''

        pass

    @unittest.skip("complete")
    def test_create_csv(self):
        '''
        @brief testing creating a csv file.
        '''

        pass


    @unittest.skip("complete")
    def test_create_txt(self):
        '''
        @brief testing creating a text file.
        '''

        pass


    @unittest.skip("complete")
    def test_get_audio_file(self):
        '''
        @brief Test generates a csv containing full path for all audio files.
        '''

        pass


    @unittest.skip("complete")
    def test_get_ext_file_list(self):
        '''
        @brief tests generates a csv containing full file path for an extension.
        '''

        pass


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


    @unittest.skip("complete")
    def test_make_album_dir(self):
        '''
        @brief tests creates an album sub-directory in an artist directory.
        '''

        pass


    @unittest.skip("complete")
    def test_make_dir(self):
        '''
        @brief Tests creates a directory.
        '''

        pass


    @unittest.skip("complete")
    def test_audio_file(self):
        '''
        @brief Test moves audio file to a new directory.

        @details The destination path must exist already.

        @param file_path {str} File path for audio file.
        @param destination_path {str} New directory for audio file.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        pass


    @patch('src.dir_processing.directory_processing.logger.warning')
    def test_path_info_not_audio(self, mock_warning):
        '''
        @brief Tests if trying to get path info for a non-audio file.
        '''

        input_path = os.path.join(TESTS_TLD, "expected.m3u")
        path_info = directory.path_info(input_path)
        self.assertIsNone(path_info)
        mock_warning.assert_called_once_with(f"File {input_path} is not in {AUDIO_EXTS}")


    def test_path_info(self):
        '''
        @brief Tests getting a path info for audio file.
        '''

        path_info = directory.path_info(TEST_M4A_DAVIS)

        # successful path_info returns a mp3 file name in generated_files/Music
        expected_info = os.path.join(GENERATED_FILES, MUSIC_TLD, "Joshua Davis", "The Voice Peformance", "Joshua Davis-The Workingman's Hymn.mp3")
        self.assertEqual(path_info, expected_info)


    @unittest.skip("complete")
    def test_remove_album_dir(self):
        '''
        @brief Tests removes empty album directories.
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
