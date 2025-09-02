
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
import unittest
from unittest import TestCase

# third party modules
from mutagen._util import MutagenError

# local module constants
from src import MUSIC_TLD
from src.generated_files import GENERATED_FILES
from tests import TEST_MP3_ABBA, TEST_MP3_CRUSH, TEST_WAV_NONE
from tests import TESTS_TLD
# local module errors
from src import MusicProcessingError
# local module classes
from src.audio_info import AudioMetadata

gc.enable()

# r'''
# ffprobe command line that is source for media info dictionary definition:
# ffprobe -v quiet -show_format -show_streams <file_path>
# where file_path points to "<linux_path>/Crush/Here/Crush-Live.mp3" or "<win_path>\Crush\Here\Crush-Live.mp3"
# Every os flavour has slight differences in the full return dict, especially the filename,
# so we actually compare on the TAG inner dict, as it is invariant across operating systems.
# '''
# EXPECTED_INFO = {
#     'comment': 'Cover (front)', 'title': 'Live', 'artist': 'Crush', 'track': '1/12', 'album': 'Here', 'disc': '1/1', 'genre': 'Pop', 'TMED': 'CD', 'TORY': '2002',
#     'MusicBrainz Release Track Id': '2475137d-6745-3951-a361-d4c29798f5d1', 'album_artist': 'Crush', 'TSO2': 'Crush', 'artist-sort': 'Crush', 'composer': 'Paul Lamb',
#     'SCRIPT': 'Latn', 'publisher': 'Sonic Records', 'ARTISTS': 'Crush', 'ASIN': 'B000065PP6', 'originalyear': '2002', 'BARCODE': '627915092229',
#     'CATALOGNUMBER': '2 50922', 'MusicBrainz Album Type': 'album', 'MusicBrainz Album Status': 'official', 'MusicBrainz Album Release Country': 'CA',
#     'Acoustid Id': '4fdf7757-ba58-4a4b-a1df-1ad4d102a474', 'MusicBrainz Album Id': '18f635aa-dc20-4fbf-a3f3-d63de3bd0fb6',
#     'MusicBrainz Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f', 'MusicBrainz Album Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f',
#     'MusicBrainz Release Group Id': 'a7927f70-2431-3a58-b7ae-48576808cec1', 'date': '2002'
# }

# instantiate classes here
metadata = AudioMetadata()


class TestAudioMetadata(TestCase):
    '''
    @brief Tests AudioMetadata class functions.
    '''

    def setUp(self):
        '''
        @brief Initialize data for tests.
        '''

        r'''
        ffprobe command line that is source for media info dictionary definition:
        ffprobe -v quiet -show_format -show_streams <file_path>
        where file_path points to "<linux_path>/Crush/Here/Crush-Live.mp3" or "<win_path>\Crush\Here\Crush-Live.mp3"
        Every os flavour has slight differences in the full return dict, especially the filename,
        so we actually compare on the TAG inner dict, as it is invariant across operating systems.
        '''

        self.expected_info = {
            'comment': 'Cover (front)', 'title': 'Live', 'artist': 'Crush', 'track': '1/12', 'album': 'Here', 'disc': '1/1', 'genre': 'Pop', 'TMED': 'CD', 'TORY': '2002',
            'MusicBrainz Release Track Id': '2475137d-6745-3951-a361-d4c29798f5d1', 'album_artist': 'Crush', 'TSO2': 'Crush', 'artist-sort': 'Crush', 'composer': 'Paul Lamb',
            'SCRIPT': 'Latn', 'publisher': 'Sonic Records', 'ARTISTS': 'Crush', 'ASIN': 'B000065PP6', 'originalyear': '2002', 'BARCODE': '627915092229',
            'CATALOGNUMBER': '2 50922', 'MusicBrainz Album Type': 'album', 'MusicBrainz Album Status': 'official', 'MusicBrainz Album Release Country': 'CA',
            'Acoustid Id': '4fdf7757-ba58-4a4b-a1df-1ad4d102a474', 'MusicBrainz Album Id': '18f635aa-dc20-4fbf-a3f3-d63de3bd0fb6',
            'MusicBrainz Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f', 'MusicBrainz Album Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f',
            'MusicBrainz Release Group Id': 'a7927f70-2431-3a58-b7ae-48576808cec1', 'date': '2002'
        }


    def test_convert_file(self):
        '''
        @brief Test converting a valid audio file to mp3 format.
        '''

        metadata.convert_file(TEST_MP3_ABBA)
        mp3_result = os.path.join(GENERATED_FILES, MUSIC_TLD, "Abba", "Waterloo", "ABBA-Waterloo.mp3")
        mp3_exists = os.path.exists(mp3_result)
        self.assertTrue(mp3_exists)
        # @todo add CCR Fortunate Son.wma and Eagles Desperado.m4a


    def test_get_media_info_dict(self):
        '''
        @brief Tests returns dictionary with media info.
        '''

        results_info = metadata.get_media_info_dict(TEST_MP3_CRUSH)

        self.maxDiff = None
        self.assertDictEqual(self.expected_info, results_info['TAG'])


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

