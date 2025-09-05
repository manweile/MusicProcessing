
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
from src import AUDIO_EXTS, FOLDER_ART, MUSIC_TLD, PLAYLIST_EXTS
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

        # directory for "walk" type tests: D:\MusicProcessing\tests\ConvertedMusic
        cls.converted = os.path.join(TESTS_PATH, "ConvertedMusic")

        # the path where converted file will be created
        cls.norm_path = os.path.join(GENERATED_FILES, MUSIC_TLD)

        # test patterns
        cls.m3u_pattern = PLAYLIST_EXTS[0]
        cls.mp3_pattern = AUDIO_EXTS[0]

        # source files
        cls.src_file_paths = [TEST_M4A_EAGLES, TEST_MP3_ABBA, TEST_WMA_CCR]

        # conversion results
        m4a_result = os.path.join(cls.norm_path, "The Eagles", "Desperado", "The Eagles-Desperado.mp3")
        mp3_result = os.path.join(cls.norm_path, "Abba", "Waterloo", "ABBA-Waterloo.mp3")
        wma_result = os.path.join(cls.norm_path, "Creedence Clearwater Revival", "Chronicle, Vol. 1", "Creedence Clearwater Revival-Fortunate Son.mp3")
        cls.mp3_result = os.path.join(cls.norm_path, "Abba", "Waterloo", "ABBA-Waterloo.mp3")
        cls.results = [m4a_result, mp3_result, wma_result]

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
            dest_dir = os.path.join(cls.converted, artist_album)
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


        r'''
        ffprobe command line that is source for media info dictionary definition:
        ffprobe -v quiet -show_format -show_streams <file_path>
        where file_path points to "<linux_path>/Crush/Here/Crush-Live.mp3" or "<win_path>\Crush\Here\Crush-Live.mp3"
        Every os flavour has slight differences in the full return dict, especially the filename
        so we use self.maxDiff = 2
        '''

        cls.media_dict = {
            'index': '1', 'codec_name': 'mjpeg', 'codec_long_name': 'Motion JPEG', 'profile': 'Baseline', 'codec_type': 'video', 'codec_tag_string': '[0][0][0][0]',
            'codec_tag': '0x0000', 'sample_fmt': 'fltp', 'sample_rate': '44100', 'channels': '2', 'channel_layout': 'stereo', 'bits_per_sample': '0', 'initial_padding': '0',
            'id': 'N/A', 'r_frame_rate': '90000/1', 'avg_frame_rate': '0/0', 'time_base': '1/90000', 'start_pts': 'N/A', 'start_time': '0.000000', 'duration_ts': '22131951',
            'duration': '245.910567', 'bit_rate': '129156', 'max_bit_rate': 'N/A', 'bits_per_raw_sample': '8', 'nb_frames': 'N/A', 'nb_read_frames': 'N/A', 'nb_read_packets': 'N/A',
            'DISPOSITION': {
                'default': '0', 'dub': '0', 'original': '0', 'comment': '0', 'lyrics': '0', 'karaoke': '0', 'forced': '0', 'hearing_impaired': '0', 'visual_impaired': '0',
                'clean_effects': '0', 'attached_pic': '1', 'timed_thumbnails': '0', 'non_diegetic': '0', 'captions': '0', 'descriptions': '0', 'metadata': '0', 'dependent': '0',
                'still_image': '0', 'multilayer': '0'},
            'width': '500', 'height': '490', 'coded_width': '500', 'coded_height': '490', 'closed_captions': '0', 'film_grain': '0', 'has_b_frames': '0', 'sample_aspect_ratio': '1:1', 'display_aspect_ratio': '50:49',
            'pix_fmt': 'yuvj420p', 'level': '-99', 'color_range': 'pc', 'color_space': 'bt470bg', 'color_transfer': 'unknown', 'color_primaries': 'unknown',
            'chroma_location': 'center', 'field_order': 'unknown', 'refs': '1',
            'TAG': {
                'comment': 'Cover (front)', 'title': 'Live', 'artist': 'Crush', 'track': '1/12', 'album': 'Here', 'disc': '1/1', 'genre': 'Pop', 'TMED': 'CD', 'TORY': '2002',
                'MusicBrainz Release Track Id': '2475137d-6745-3951-a361-d4c29798f5d1', 'album_artist': 'Crush', 'TSO2': 'Crush', 'artist-sort': 'Crush', 'composer': 'Paul Lamb',
                'SCRIPT': 'Latn', 'publisher': 'Sonic Records', 'ARTISTS': 'Crush', 'ASIN': 'B000065PP6', 'originalyear': '2002', 'BARCODE': '627915092229',
                'CATALOGNUMBER': '2 50922', 'MusicBrainz Album Type': 'album', 'MusicBrainz Album Status': 'official','MusicBrainz Album Release Country': 'CA',
                'Acoustid Id': '4fdf7757-ba58-4a4b-a1df-1ad4d102a474', 'MusicBrainz Album Id': '18f635aa-dc20-4fbf-a3f3-d63de3bd0fb6',
                'MusicBrainz Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f', 'MusicBrainz Album Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f',
                'MusicBrainz Release Group Id': 'a7927f70-2431-3a58-b7ae-48576808cec1', 'date': '2002'},
            'filename': 'D:\\MusicProcessing\\tests\\Music\\Crush\\Here\\Crush-Live.mp3', 'nb_streams': '2', 'nb_programs': '0', 'nb_stream_groups': '0', 'format_name': 'mp3',
            'format_long_name': 'MP2/3 (MPEG audio layer 2/3)', 'size': '3970122', 'probe_score': '51'
        }

        # @todo change the filename value to match OS.

        # no matter the os, inner dict TAG is always same
        cls.tag_dict = {
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

        if os.path.exists(cls.converted):
            shutil.rmtree(cls.converted)


    def tearDown(self):
        '''
        @brief Cleans up the created audio files and directories.

        @details These audio files are created by multiple tests and need deletion after every test.
        '''

        if os.path.exists(self.norm_path):
            shutil.rmtree(self.norm_path)


    def test_convert_file(self):
        '''
        @brief Test converting a valid audio file to mp3 format.

        @details The audio files must have a co-located Folder.jpg file.
        '''

        for src_file in self.src_file_paths:
            metadata.convert_file(src_file)

        for audio_file in self.results:
            audio_exists = os.path.exists(audio_file)
            self.assertTrue(audio_exists)


    # @todo add test try to convert file w/o colocated Folder.jpg


    def test_convert_walk(self):
        '''
        #brief Test converting all valid audio files in a top level directory to mp3 format.

        @details The audio files must have a co-located Folder.jpg file.
        @details Happy path test without a file pattern.
        '''

        metadata.convert_walk(self.converted, None)

        for audio_file in self.results:
            audio_exists = os.path.exists(audio_file)
            self.assertTrue(audio_exists)


    def test_convert_walk_pattern(self):
        '''
        #brief Test converting valid audio file matching input pattern to mp3 format.

        @details The audio files must have a co-located Folder.jpg file.
        @details Happy path test with a file pattern.
        '''

        metadata.convert_walk(self.converted, self.mp3_pattern)

        audio_exists = os.path.exists(self.mp3_result)
        self.assertTrue(audio_exists)


    def test_convert_walk_invalid_pattern(self):
        '''
        #brief Test try converting invalid file pattern to mp3 format.
        '''

        log_msg = f"Pattern {self.m3u_pattern} is not for a valid audio file"

        with self.assertLogs() as captured:
            metadata.convert_walk(self.converted, self.m3u_pattern)

        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), log_msg)


    # @todo copy/edit to get tags test
    # @todo add full expected media dict, specify maxDiff = 1 (the file path)


    def test_get_media_info_dict(self):
        '''
        @brief Tests returns dictionary with media info.
        '''

        results_dict = metadata.get_media_info_dict(TEST_MP3_CRUSH)

        self.maxDiff = None
        self.assertDictEqual(self.media_dict, results_dict)


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
