
'''
@file test_audio_metadata.py
@brief Defines the test audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import os
import shutil
import unittest
from pathlib import Path
from unittest import TestCase

# third party modules
from mutagen._util import MutagenError

# local module constants
from src import FOLDER_ART, MUSIC_TLD
from src.generated_files import GENERATED_FILES
from tests import TEST_M4A_EAGLES, TEST_MP3_ABBA, TEST_MP3_CRUSH, TEST_WAV_NONE, TEST_WMA_CCR
from tests import TESTS_PATH, TESTS_TLD
# local module errors
from src import MusicProcessingError
# local module classes
from src.audio_info import AudioMetadata

gc.enable()

# instantiate classes here
metadata = AudioMetadata()


class TestAudioMetadata(TestCase):
    '''
    @brief Tests AudioMetadata class functions.
    '''

    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite.

        @details These datums are used throughout class and only need init once.
        '''

        # directory for "walk" type tests: D:\MusicProcessing\tests\convert_walk
        cls.convert_walk = os.path.join(TESTS_PATH, "convert_walk")
        # source files
        cls.src_file_paths = [TEST_M4A_EAGLES, TEST_MP3_ABBA, TEST_WMA_CCR]

        for src_path in cls.src_file_paths:
            # get the audio file name w/o path
            # eg from D:\MusicProcessing\tests\Music\The Eagles\Desperado\The Eagles-Desperado.m4a -> The Eagles-Desperado.m4a
            file_name = os.path.basename(src_path)

            # get audio file parent path parts
            # eg D:\MusicProcessing\tests\MusicThe Eagles\Desperado
            # D:\, MusicProcessing, tests, Music, The Eagles, Desperado
            file_path = Path(src_path)
            file_parent = file_path.parent
            path_parts = file_parent.parts

            # build up the artist & album path, from last 2 elements of file parent path parts
            # eg Abba, Desperado -> The Eagles\Desperado
            full_len = len(path_parts)
            artist_len = full_len - 2
            artist_album = ""
            for i in range(artist_len, full_len):
                artist_album = os.path.join(artist_album, path_parts[i])

            # create the destination directory
            # D:\MusicProcessing\tests\convert_walk\The Eagles\Desperado\
            dest_dir = os.path.join(cls.convert_walk, artist_album)
            os.makedirs(dest_dir, exist_ok=True)

            # create dest: D:\MusicProcessing\tests\convert_walk\The Eagles\Desperado\The Eagles-Desperado.m4a
            dest_path = os.path.join(dest_dir, file_name)

            # and copy
            shutil.copy(src_path, dest_path)

            # create source and destination Folder.jpg paths for audio file
            # eg D:\MusicProcessing\tests\Music\The Eagles\Desperado\Folder.jpg
            # eg D:\MusicProcessing\tests\convert_walk\The Eagles\Desperado\Folder.jpg
            src_jpg = os.path.join(TESTS_TLD, artist_album, FOLDER_ART)
            dest_jpg = os.path.join(dest_dir, FOLDER_ART)

            # and copy
            shutil.copy(src_jpg, dest_jpg)


        # the path where converted file will be created
        cls.norm_path = os.path.join(GENERATED_FILES, MUSIC_TLD)

        r'''
        ffprobe command line that is source for media info dictionary definition:
        ffprobe -v quiet -show_format -show_streams <file_path>
        where file_path points to "<linux_path>/Crush/Here/Crush-Live.mp3" or "<win_path>\Crush\Here\Crush-Live.mp3"
        Every os flavour has slight differences in the full return dict, especially the filename,
        so we actually compare on the TAG inner dict, as it is invariant across operating systems.
        '''
        cls.expected_tag = {
            'comment': 'Cover (front)', 'title': 'Live', 'artist': 'Crush', 'track': '1/12', 'album': 'Here', 'disc': '1/1', 'genre': 'Pop', 'TMED': 'CD', 'TORY': '2002',
            'MusicBrainz Release Track Id': '2475137d-6745-3951-a361-d4c29798f5d1', 'album_artist': 'Crush', 'TSO2': 'Crush', 'artist-sort': 'Crush', 'composer': 'Paul Lamb',
            'SCRIPT': 'Latn', 'publisher': 'Sonic Records', 'ARTISTS': 'Crush', 'ASIN': 'B000065PP6', 'originalyear': '2002', 'BARCODE': '627915092229',
            'CATALOGNUMBER': '2 50922', 'MusicBrainz Album Type': 'album', 'MusicBrainz Album Status': 'official', 'MusicBrainz Album Release Country': 'CA',
            'Acoustid Id': '4fdf7757-ba58-4a4b-a1df-1ad4d102a474', 'MusicBrainz Album Id': '18f635aa-dc20-4fbf-a3f3-d63de3bd0fb6',
            'MusicBrainz Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f', 'MusicBrainz Album Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f',
            'MusicBrainz Release Group Id': 'a7927f70-2431-3a58-b7ae-48576808cec1', 'date': '2002'
        }


    @classmethod
    def tearDownClass(cls):
        '''
        @brief Cleans up the walk type tests source audio files and directories.
        '''

        if os.path.exists(cls.convert_walk):
            shutil.rmtree(cls.convert_walk)


    def tearDown(self):
        '''
        @brief Cleans up the created audio files and directories.

        @details These audio files are created by multiple tests and need deletion after every test.
        '''

        if os.path.exists(self.norm_path):
            shutil.rmtree(self.norm_path)

    @unittest.skip("debug ci failure")
    def test_convert_file(self):
        '''
        @brief Test converting a valid audio file to mp3 format.

        @details The audio files must have a co-located Folder.jpg file.
        '''

        for src_file in self.src_file_paths:
            metadata.convert_file(src_file)

        m4a_result = os.path.join(self.norm_path, "The Eagles", "Desperado", "The Eagles-Desperado.mp3")
        mp3_result = os.path.join(self.norm_path, "Abba", "Waterloo", "ABBA-Waterloo.mp3")
        wma_result = os.path.join(self.norm_path, "Creedence Clearwater Revival", "Chronicle, Vol. 1", "Creedence Clearwater Revival-Fortunate Son.mp3")

        results = [m4a_result, mp3_result, wma_result]

        for audio_file in results:
            audio_exists = os.path.exists(audio_file)
            self.assertTrue(audio_exists)

    @unittest.skip("debug ci failure")
    def test_convert_walk_all(self):
        '''
        #brief Test converting all valid audio files in a top level directory to mp3 format.

        @details The audio files must have a co-located Folder.jpg file.
        @details Happy path test without a file pattern.
        '''

        m4a_result = os.path.join(GENERATED_FILES, MUSIC_TLD, "The Eagles", "Desperado", "The Eagles-Desperado.mp3")
        mp3_result = os.path.join(GENERATED_FILES, MUSIC_TLD, "Abba", "Waterloo", "ABBA-Waterloo.mp3")
        wma_result = os.path.join(GENERATED_FILES, MUSIC_TLD, "Creedence Clearwater Revival", "Chronicle, Vol. 1", "Creedence Clearwater Revival-Fortunate Son.mp3")

        results = [m4a_result, mp3_result, wma_result]

        metadata.convert_walk(self.convert_walk, None)

        for audio_file in results:
            audio_exists = os.path.exists(audio_file)
            self.assertTrue(audio_exists)


    def test_get_media_info_dict(self):
        '''
        @brief Tests returns dictionary with media info.
        '''

        results_dict = metadata.get_media_info_dict(TEST_MP3_CRUSH)

        self.maxDiff = None
        self.assertDictEqual(self.expected_tag, results_dict['TAG'])


    def test_load_any_file(self):
        '''
        @brief Tests attempt to load an audio file with mutagen.
        '''

        loaded_file = metadata.load_any_file(TEST_MP3_CRUSH)
        audio_class_name = loaded_file.__class__.__name__
        self.assertEqual(audio_class_name, "MP3")
        # @todo need m4a and mp3 too


    '''
    With a non-extant file, a mutagen load call will return a chained exception:
    MutagenError encapsulating a FileNotFoundError, so we check the exception context dunder,
    disable logging to prevent console clutter.
    '''


    def test_load_any_file_non_extant(self):
        '''
        @brief Tests attempt to load a non-extant audio file with mutagen File function.
        '''

        audio_file = None
        file_path = TEST_WAV_NONE

        with self.assertRaises(MutagenError) as cm:
            audio_file = metadata.load_any_file(file_path)

        self.assertIsNone(audio_file)
        self.assertIsInstance(cm.exception.__context__, FileNotFoundError)


    # @todo test_load_m4a


    def test_load_m4a_file_non_extant(self):
        '''
        @brief Tests attempt to load a non-extant audio file with mutagen MP4 class.
        '''

        audio_file = None
        file_path = os.path.join(TESTS_TLD, "Non-extant.m4a")

        with self.assertRaises(MutagenError) as cm:
            audio_file = metadata.load_m4a_file(file_path)

        self.assertIsNone(audio_file)
        self.assertIsInstance(cm.exception.__context__, FileNotFoundError)


    # @todo test_load_mp3


    def test_load_mp3_file_non_extant(self):
        '''
        @brief Tests attempt to load a non-extant audio file with mutagen MP3 class.
        '''

        audio_file = None
        file_path = os.path.join(TESTS_TLD, "Non-extant.mp3")

        with self.assertRaises(MutagenError) as cm:
            audio_file = metadata.load_mp3_file(file_path)

        self.assertIsNone(audio_file)
        self.assertIsInstance(cm.exception.__context__, FileNotFoundError)


    # @todo test_load_wma


    def test_load_wma_file_non_extant(self):
        '''
        @brief Tests attempt to load a non-extant audio file with mutagen ASF class.
        '''

        audio_file = None
        file_path = os.path.join(TESTS_TLD, "Non-extant.wma")

        with self.assertRaises(MutagenError) as cm:
            audio_file = metadata.load_wma_file(file_path)

        self.assertIsNone(audio_file)
        self.assertIsInstance(cm.exception.__context__, FileNotFoundError)


    def test_load_wma_file_with_mp3(self):
        '''
        @brief Attempt to load a mp3 as wma with mutagen ASF class.

        @details Expected to throw custom exception.
        '''

        audio_file = None

        with self.assertRaises(MusicProcessingError) as cm:
            audio_file = metadata.load_wma_file(TEST_MP3_CRUSH)

        self.assertIsNone(audio_file)
        self.assertEqual(cm.exception.message, f"MusicProcessingError {TEST_MP3_CRUSH} not wma")


def get_method_names(cls):
    '''
    @brief Returns a list of methods defined within a given class.

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
    methods = get_method_names(TestAudioMetadata)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioMetadata(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
