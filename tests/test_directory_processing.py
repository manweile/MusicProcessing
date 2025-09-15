
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



        # copy input files to "walk" directory
        for src_path in cls.src_file_paths:
            # get the audio file name w/o path
            # eg from D:\MusicProcessing\tests\Music\The Eagles\Desperado\The Eagles-Desperado.m4a -> The Eagles-Desperado.m4a
            file_name = os.path.basename(src_path)

            # get audio file parent path parts
            # eg D:\MusicProcessing\tests\Music\The Eagles\Desperado
            # D:\, MusicProcessing, tests, Music, The Eagles, Desperado
            file_path = Path(src_path)
            file_parent = file_path.parent
            # don't want album, tests will create those, so trim parts list
            # D:\, MusicProcessing, tests, Music, The Eagles
            path_parts = file_parent.parts[:-1]

            # build up the artist path, from last element of file parent path parts
            # eg The Eagles -> The Eagles
            full_len = len(path_parts)
            artist_len = full_len - 1
            artist = ""
            for i in range(artist_len, full_len):
                artist = os.path.join(artist, path_parts[i])

            # create the destination directory
            # D:\MusicProcessing\tests\PreppedMusic\The Eagles
            dest_dir = os.path.join(cls.prepped, artist)
            os.makedirs(dest_dir, exist_ok=True)

            # create dest: D:\MusicProcessing\tests\PreppedMusic\The Eagles\The Eagles-Desperado.m4a
            dest_path = os.path.join(dest_dir, file_name)

            # and copy
            shutil.copy(src_path, dest_path)


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


    def test_create_album_dir(self):
        '''
        @brief Tests creating an album sub-directory in an artist directory.
        '''

        directory.create_album_dir(self.prepped)

        for dir in self.results:
            dir_exists = os.path.isdir(dir)
            self.assertTrue(dir_exists)


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
