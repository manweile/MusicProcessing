
'''
@file test_audio_metadata.py
@brief Defines the test audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import copy
import gc
import inspect
import platform
import os
import shutil
import unittest
from json import JSONDecodeError
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from unittest import TestCase
from unittest.mock import patch

# third party modules
import mutagen
from mutagen._util import MutagenError

# local module constants
from src import AUDIO_EXTS, AUDIO_FILES, FOLDER_ART
from src import MP3_EXT, MUSIC_TLD
from src import PLAYLIST_EXTS
from src import RESULT_DIR, RESULT_EXT
from src.generated_files import GENERATED_FILES
from tests import TEST_M4A_EAGLES, TEST_MP3_ABBA, TEST_MP3_CRUSH, TEST_MP3_NO_TAG, TEST_WAV_NONE, TEST_WMA_CCR
from tests import TEST_M3U
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
        # the path where converted files will be created D:\MusicProcessing\src\generated_files\Music
        cls.norm_path = os.path.join(GENERATED_FILES, MUSIC_TLD)
        # directory for "walk" type tests: D:\MusicProcessing\tests\PreppedMusic
        cls.prepped = os.path.join(TESTS_PATH, "PreppedMusic")

        # test patterns
        cls.m3u_pattern = PLAYLIST_EXTS[0]
        cls.mp3_pattern = AUDIO_EXTS[0]

        # audio source files for walk tests
        cls.src_file_paths = [TEST_M4A_EAGLES, TEST_MP3_ABBA, TEST_WMA_CCR]

        # for conversion test that only needs a single mp3 file
        cls.mp3_result = os.path.join(cls.norm_path, "Abba", "Waterloo", "ABBA-Waterloo.mp3")

        # for conversion tests creating multiple mp3 files
        cls.converted_results = []
        cls.converted_results.append(os.path.join(cls.norm_path, "The Eagles", "Desperado", "The Eagles-Desperado.mp3"))
        cls.converted_results.append(os.path.join(cls.norm_path, "Abba", "Waterloo", "ABBA-Waterloo.mp3"))
        cls.converted_results.append(os.path.join(cls.norm_path, "Creedence Clearwater Revival", "Chronicle, Vol. 1", "Creedence Clearwater Revival-Fortunate Son.mp3"))

        # for create albums test
        cls.prepped_results = []
        cls.prepped_results.append(os.path.join(cls.prepped, "The Eagles", "Desperado"))
        cls.prepped_results.append(os.path.join(cls.prepped, "Abba", "Waterloo"))
        cls.prepped_results.append(os.path.join(cls.prepped, "Creedence Clearwater Revival", "Chronicle, Vol. 1"))

        # audio filenames for tag walk tests
        cls.mp3_line = os.path.join(cls.converted, "Abba", "Waterloo", "ABBA-Waterloo.mp3")
        cls.wma_line = os.path.join(cls.converted, "Creedence Clearwater Revival", "Chronicle, Vol. 1", "Creedence Clearwater Revival-Fortunate Son.wma")
        cls.m4a_line = os.path.join(cls.converted, "The Eagles", "Desperado", "The Eagles-Desperado.m4a")

        # copy input files to converted "walk" directory
        for src_converted in cls.src_file_paths:
            # get the audio file name w/o path
            # eg from D:\MusicProcessing\tests\Music\The Eagles\Desperado\The Eagles-Desperado.m4a -> The Eagles-Desperado.m4a
            file_name = os.path.basename(src_converted)

            # get audio file parent path parts
            # eg D:\MusicProcessing\tests\Music\The Eagles\Desperado
            # D:\, MusicProcessing, tests, Music, The Eagles, Desperado
            file_path = Path(src_converted)
            file_parent = file_path.parent
            path_parts = file_parent.parts

            # build up the artist & album path, from last 2 elements of file parent path parts
            # eg The Eagles, Desperado -> The Eagles\Desperado
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
            shutil.copy(src_converted, dest_path)

            # create source and destination Folder.jpg paths for audio file
            # eg D:\MusicProcessing\tests\Music\The Eagles\Desperado\Folder.jpg
            # eg D:\MusicProcessing\tests\convert_walk\The Eagles\Desperado\Folder.jpg
            src_jpg = os.path.join(TESTS_TLD, artist_album, FOLDER_ART)
            dest_jpg = os.path.join(dest_dir, FOLDER_ART)

            # and copy
            shutil.copy(src_jpg, dest_jpg)

        # copy input files to prepped "walk" directory
        for src_prepped in cls.src_file_paths:
            # get the audio file name w/o path
            # eg from D:\MusicProcessing\tests\Music\The Eagles\Desperado\The Eagles-Desperado.m4a -> The Eagles-Desperado.m4a
            file_name = os.path.basename(src_prepped)

            # get audio file parent path parts
            # eg D:\MusicProcessing\tests\Music\The Eagles\Desperado
            # D:\, MusicProcessing, tests, Music, The Eagles, Desperado
            file_path = Path(src_prepped)
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
            shutil.copy(src_prepped, dest_path)

        r'''
        ffprobe command line that is source for media info dictionary definition:
        ffprobe -v quiet -show_format -show_streams <file_path>
        where file_path points to "<linux_path>/Crush/Here/Crush-Live.mp3" or "<win_path>\Crush\Here\Crush-Live.mp3"
        Every os flavour has slight differences in the full return dict, especially the filename
        so we check the platform/environment to correct the filename value
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
            'filename': r'D:\MusicProcessing\tests\Music\Crush\Here\Crush-Live.mp3', 'nb_streams': '2', 'nb_programs': '0', 'nb_stream_groups': '0', 'format_name': 'mp3',
            'format_long_name': 'MP2/3 (MPEG audio layer 2/3)', 'size': '3970122', 'probe_score': '51'
        }

        # desktop windows: 'filename': 'D:\MusicProcessing\tests\Music\Crush\Here\Crush-Live.mp3'
        # laptop ubuntu: 'filename': '/home/gerald/MusicProcessing/tests/Music/Crush/Here/Crush-Live.mp3'
        # ci ubuntu: 'filename': '/home/runner/work/MusicProcessing/MusicProcessing/tests/Music/Crush/Here/Crush-Live.mp3'
        crush_mp3 = os.path.join(TESTS_TLD, "Crush", "Here", "Crush-Live.mp3")
        local_win = os.path.join("D:", crush_mp3)
        local_linux = os.path.join("home", "gerald", crush_mp3)
        ci_linux = os.path.join("home", "runner", "work", crush_mp3)

        os_name = platform.system()
        if os_name == "Linux":
            cls.media_dict["filename"] = local_linux
        elif os_name == "Windows":
            cls.media_dict["filename"] = local_win
        elif os.environ.get('GITHUB_ACTIONS') == 'true':
            cls.media_dict["filename"] = ci_linux

        # no matter the os/environment, inner dict TAG is always same
        cls.tag_dict = {
            'title': 'Live', 'artist': 'Crush', 'track': '1/12', 'album': 'Here', 'disc': '1/1', 'genre': 'Pop', 'TMED': 'CD', 'TORY': '2002',
            'MusicBrainz Release Track Id': '2475137d-6745-3951-a361-d4c29798f5d1', 'album_artist': 'Crush', 'TSO2': 'Crush', 'artist-sort': 'Crush', 'composer': 'Paul Lamb',
            'SCRIPT': 'Latn', 'publisher': 'Sonic Records', 'ARTISTS': 'Crush', 'ASIN': 'B000065PP6', 'originalyear': '2002', 'BARCODE': '627915092229',
            'CATALOGNUMBER': '2 50922', 'MusicBrainz Album Type': 'album', 'MusicBrainz Album Status': 'official', 'MusicBrainz Album Release Country': 'CA',
            'Acoustid Id': '4fdf7757-ba58-4a4b-a1df-1ad4d102a474', 'MusicBrainz Album Id': '18f635aa-dc20-4fbf-a3f3-d63de3bd0fb6',
            'MusicBrainz Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f', 'MusicBrainz Album Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f',
            'MusicBrainz Release Group Id': 'a7927f70-2431-3a58-b7ae-48576808cec1', 'date': '2002'
        }

        cls.id3_input_tags = {
            "TALB": "Waterloo",
            "TPE2": "ABBA",
            "TPE1": "ABBA",
            "TCOM": "Benny Andersson/Björn Ulvaeus/Stig Anderson",
            "TCON": "Pop",
            "TPUB": "Polydor",
            "TIT2": "Waterloo",
            "TRCK": "1",
            "TYER": "1900"
        }
        cls.id3_date_values = set(["1962", "1963"])

        cls.m4a_mapped = {
            'TALB': 'Desperado',
            'TPE2': 'Eagles',
            'TPE1': 'Eagles',
            'TCOM': 'Don Henley/Glenn Frey',
            'TCOP': '1973 Asylum Records',
            'TPOS': '1/1',
            'TCON': 'Rock',
            'TPUB': 'Asylum Records',
            'TIT2': 'Desperado',
            'TRCK': '5/11',
            'TYER': '1973'
        }

        cls.mp3_mapped = {
            "TALB": "Waterloo",
            "TPE2": "ABBA",
            "TPE1": "ABBA",
            "TCOM": "Benny Andersson/Björn Ulvaeus/Stig Anderson",
            "TCON": "Pop",
            "TPUB": "Polydor",
            "TIT2": "Waterloo",
            "TRCK": "1",
            "TYER": "1963",
            "TPOS": "1/1"
        }

        cls.wma_mapped = {
            'TALB': 'Chronicle, Vol. 1',
            'TPE2': 'Creedence Clearwater Revival',
            'TPE1': 'Creedence Clearwater Revival',
            'TCOM': 'John Fogerty',
            'TCON': 'Classic Rock',
            'TPUB': 'Fantasy',
            'TIT2': 'Fortunate Son',
            'TRCK': 9,
            'TYER': '1976',
            'TPOS': '1/1'
        }


    @classmethod
    def tearDownClass(cls):
        '''
        @brief Cleans up the walk type tests source audio files and directories.
        '''

        if os.path.exists(cls.converted):
            shutil.rmtree(cls.converted)

        if os.path.exists(cls.prepped):
            shutil.rmtree(cls.prepped)


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
        @details Happy path test.
        '''

        for src_file in self.src_file_paths:
            metadata.convert_file(src_file, show_spinner=False)

        for audio_file in self.converted_results:
            audio_exists = os.path.exists(audio_file)
            self.assertTrue(audio_exists)


    def test_convert_file_no_jpg(self):
        '''
        @brief Test Attempt converting a an audio file that does not have a co-located Folder.jpg file.
        '''

        input_path_parent = os.path.dirname(TEST_MP3_CRUSH)
        err_msg = f"album directory {input_path_parent} does not contain a {FOLDER_ART} file."

        with self.assertRaises(MusicProcessingError) as cm:
            metadata.convert_file(TEST_MP3_CRUSH)

        self.assertEqual(cm.exception.message, err_msg)


    def test_convert_file_wo_metadata(self):
        '''
        @brief Test Attempt converting a an audio file that does not have metadata.
        '''

        no_metadata = os.path.join(TESTS_TLD, "NoMetadata", "Here", "No_tag_Crush-Live.mp3")
        metadata.convert_file(no_metadata, show_spinner=False)

        audio_file = os.path.join(GENERATED_FILES, MUSIC_TLD, "NoMetadata", "Here", "No_tag_Crush-Live.mp3")
        audio_exists = os.path.exists(audio_file)
        self.assertTrue(audio_exists)


    def test_convert_walk(self):
        '''
        #brief Test converting all valid audio files in a top level directory to mp3 format.

        @details The audio files must have a co-located Folder.jpg file.
        @details Happy path test without a file pattern.
        '''

        metadata.convert_walk(self.converted, None, show_spinner=False)

        for audio_file in self.converted_results:
            audio_exists = os.path.exists(audio_file)
            self.assertTrue(audio_exists)


    def test_convert_walk_pattern(self):
        '''
        #brief Test converting valid audio file matching input pattern to mp3 format.

        @details The audio files must have a co-located Folder.jpg file.
        @details Happy path test with a file pattern.
        '''

        metadata.convert_walk(self.converted, self.mp3_pattern, show_spinner=False)

        audio_exists = os.path.exists(self.mp3_result)
        self.assertTrue(audio_exists)


    def test_convert_walk_pattern_invalid(self):
        '''
        #brief Test try converting invalid file pattern to mp3 format.
        '''

        log_msg = f"Pattern {self.m3u_pattern} is not for a valid audio file"

        with self.assertLogs() as captured:
            metadata.convert_walk(self.converted, self.m3u_pattern, show_spinner=False)

        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), log_msg)


    def test_create_album_dir(self):
        '''
        @brief Tests creating an album sub-directory in an artist directory.
        '''

        metadata.create_album_dir(self.prepped)

        for dir in self.prepped_results:
            dir_exists = os.path.isdir(dir)
            self.assertTrue(dir_exists)


    def test_get_any_tags(self):
        '''
        @brief Test getting tags for any type of audio file.
        '''

        for src_file in self.src_file_paths:
            tags = metadata.get_any_tags(src_file)
            tags_list = tags.values()
            if src_file == TEST_M4A_EAGLES:
                self.assertTrue(len(tags_list) == 32)
            elif src_file == TEST_MP3_ABBA:
                self.assertTrue(len(tags_list) == 9)
            elif src_file == TEST_WMA_CCR:
                self.assertTrue(len(tags_list) == 30)


    def test_get_any_tags_wo_metadata(self):
        '''
        @brief Test getting tags for any type of audio file that is without metadata.
        '''

        tags = None

        tags = metadata.get_any_tags(TEST_MP3_NO_TAG)

        self.assertIsNone(tags)


    def test_get_media_info(self):
        '''
        @brief Tests returns dictionary with media info.
        '''

        results_dict = metadata.get_media_info(TEST_MP3_CRUSH)

        self.assertDictEqual(self.media_dict, results_dict)


    @patch('src.audio_info.audio_metadata.SubprocessUtilities.popen_pipe')
    def test_get_media_info_regex_no_dict(self, mock_popen_pipe):
        '''
        @brief Tests trying to returns media info dictionary from Popen return that is missing inner dictionaries.

        @Details The SubprocessUtilities.popen_pipe return is mocked to return string that will not have any inner dictionaries for regex to match.
        '''

        results_dict = None
        mock_popen_pipe.return_value = f"[STREAM]\r\nindex=0\r\n[/STREAM]\r\n[FORMAT]\r\nfilename={TEST_MP3_ABBA}\r\n[/FORMAT]\r\n"

        results_dict = metadata.get_media_info(TEST_MP3_ABBA)
        expected_dict = {"index": "0", "filename": f"{TEST_MP3_ABBA}"}
        self.assertDictEqual(results_dict, expected_dict)


    def test_get_media_info_walk(self):
        '''
        @brief Tests getting media info (codec, duration, size, bitrate...) for audio files in top level directory.
        '''

        # use the ConvertedMusic dir
        metadata.get_media_info_walk(self.converted, None)

        txt_dir = os.path.join(GENERATED_FILES, RESULT_DIR)
        txt_filename = "get_media_info_walk" + RESULT_EXT
        txt_path = os.path.join(txt_dir, txt_filename)

        output_exists = os.path.exists(txt_path)
        self.assertTrue(output_exists)

        # check for major values in the output text file
        with open(txt_path, "r") as f:
            lines = f.readlines()

        self.assertIn(f"{self.mp3_line} has 37 keys\n", lines)
        self.assertIn(f"{self.wma_line} has 38 keys\n", lines)
        self.assertIn(f"{self.m4a_line} has 56 keys\n", lines)


    def test_get_media_info_walk_invalid_pattern(self):
        '''
        @brief Tests getting media info with an invalid pattern.
        '''

        # use the ConvertedMusic dir
        metadata.get_media_info_walk(self.converted, PLAYLIST_EXTS[0])

        txt_dir = os.path.join(GENERATED_FILES, RESULT_DIR)
        txt_filename = "get_media_info_walk" + RESULT_EXT
        txt_path = os.path.join(txt_dir, txt_filename)
        output_exists = os.path.exists(txt_path)
        file_size = os.path.getsize(txt_path)

        self.assertTrue(output_exists)
        self.assertEqual(file_size, 0)


    def test_get_media_info_walk_pattern(self):
        '''
        @brief Tests getting media info (codec, duration, size, bitrate...) for audio files pattern.
        '''

        # use the ConvertedMusic dir
        metadata.get_media_info_walk(self.converted, MP3_EXT)

        txt_dir = os.path.join(GENERATED_FILES, RESULT_DIR)
        txt_filename = "get_media_info_walk" + RESULT_EXT
        txt_path = os.path.join(txt_dir, txt_filename)
        output_exists = os.path.exists(txt_path)

        self.assertTrue(output_exists)

        # check for major values in the output text file
        with open(txt_path, "r") as f:
            lines = f.readlines()

        self.assertIn(f"{self.mp3_line} has 37 keys\n", lines)


    def test_get_media_tags(self):
        '''
        @brief Tests getting media tags.
        '''

        media_tags = metadata.get_media_tags(TEST_MP3_CRUSH)

        self.assertDictEqual(media_tags, self.tag_dict)


    @patch('src.audio_info.audio_metadata.SubprocessUtilities.subprocess_run')
    def test_get_media_tags_json_error(self, mock_subprocess_run):
        '''
        @brief Tests getting media tags from file that results in JSONDecodeError.
        '''

        mock_subprocess_run.return_value = CompletedProcess(args=['ffprobe', '-v', 'quiet', '-of', 'json', '-show_entries', 'format_tags', 'D:\\MusicProcessing\\tests\\Music\\Crush\\Here\\Crush-Live.mp3'],
                                                            returncode=0,
                                                            stdout=('{\n'
                                                                    '"format": {\n'
                                                                    '"tags": {\n'
                                                                    '"title": "Live",\n'
                                                                    '"artist": "Crush",\n'
                                                                    '"track": "1/12",\n'
                                                                    '"album": "Here",\n'
                                                                    '"disc": "1/1",\n'
                                                                    '"genre": "Pop",\n'
                                                                    '"album_artist": "Crush",\n'
                                                                    '"composer": "Paul Lamb",\n'
                                                                    '"publisher": "Sonic Records",\n'
                                                                    '"originalyear": "2002",\n'
                                                                    '"date": "2002"\n'
                                                                    '}\n'
                                                                    '}\n'
                                                                    '\n'    # should be '}\n', missing close brace causes JSONDecodeError with lineno=18
                                                                    ),
                                                            stderr='')

        media_tags = None

        with self.assertRaises(JSONDecodeError) as cm:
            media_tags = metadata.get_media_tags(TEST_MP3_CRUSH)

        self.assertIsNone(media_tags)
        self.assertEqual("JSONDecodeError", cm.exception.__class__.__name__)
        self.assertEqual(18, cm.exception.lineno)


    def test_get_media_tags_wo_metadata(self):
        '''
        @brief Tests getting media tags from audio without metadata.
        '''

        media_tags = None

        media_tags = metadata.get_media_tags(TEST_MP3_NO_TAG)

        self.assertIsNone(media_tags)


    def test_get_metadata_type(self):
        '''
        @brief Test getting metadata type of any audio file.
        '''

        # walk through ConvertedMusic files
        for file_path in self.src_file_paths:
            audio_file = mutagen.File(file_path)
            metadata_type = audio_file.__class__.__name__
            self.assertTrue(metadata_type in AUDIO_FILES)


    def test_get_metadata_type_fail(self):
        '''
        @brief Test try getting metadata type of invalid file.
        '''

        audio_file = mutagen.File(TEST_M3U)
        metadata_type = audio_file.__class__.__name__
        self.assertEqual(metadata_type, "NoneType")


    def test_get_tags_walk(self):
        '''
        @brief Tests getting tags for a input pattern
        '''

        txt_dir = os.path.join(GENERATED_FILES, RESULT_DIR)
        txt_filename = "get_tags_walk" + RESULT_EXT
        txt_path = os.path.join(txt_dir, txt_filename)

        metadata.get_tags_walk(self.converted, MP3_EXT, ffprobe=True)

        with open(txt_path, "r") as f:
            lines = f.readlines()

        self.assertIn(f"{self.mp3_line} has 9 ffprobe tags\n", lines)


    def test_get_tags_walk_ffprobe(self):
        '''
        @brief Tests getting ffprobe  tags for audio files.
        '''

        txt_dir = os.path.join(GENERATED_FILES, RESULT_DIR)
        txt_filename = "get_tags_walk" + RESULT_EXT
        txt_path = os.path.join(txt_dir, txt_filename)

        metadata.get_tags_walk(self.converted, None, ffprobe=True)

        with open(txt_path, "r") as f:
            lines = f.readlines()

        self.assertIn(f"{self.mp3_line} has 9 ffprobe tags\n", lines)
        self.assertIn(f"{self.wma_line} has 23 ffprobe tags\n", lines)
        self.assertIn(f"{self.m4a_line} has 35 ffprobe tags\n", lines)


    def test_get_tags_walk_mutagen(self):
        '''
        @brief Tests getting ffprobe  tags for audio files.
        '''

        txt_dir = os.path.join(GENERATED_FILES, RESULT_DIR)
        txt_filename = "get_tags_walk" + RESULT_EXT
        txt_path = os.path.join(txt_dir, txt_filename)

        metadata.get_tags_walk(self.converted, None)

        with open(txt_path, "r") as f:
            lines = f.readlines()

        self.assertIn(f"{self.mp3_line} has 9 MP3 tags\n", lines)
        self.assertIn(f"{self.wma_line} has 31 ASF tags\n", lines)
        self.assertIn(f"{self.m4a_line} has 32 MP4 tags\n", lines)


    def test_get_unique_media_keys(self):
        '''
        @brief Tests getting an unique set of metadata keys for audio files in specified path.
        '''

        txt_dir = os.path.join(GENERATED_FILES, RESULT_DIR)
        txt_filename = "get_unique_media_keys" + RESULT_EXT
        txt_path = os.path.join(txt_dir, txt_filename)

        metadata.get_unique_media_keys(TESTS_TLD)

        with open(txt_path, "r") as f:
            lines = f.readlines()

        self.assertGreater(len(lines), 1)
        self.assertIn(f"Unique keys for audio files in {TESTS_TLD}\n", lines)


    def test_has_art_tag_true(self):
        '''
        @brief Tests checking if an audio file has an embedded album art tag.
        '''

        has_art = metadata.has_art_tag(TEST_MP3_CRUSH)
        self.assertTrue(has_art)


    def test_has_art_tag_false(self):
        '''
        @brief Tests checking if an audio file has an embedded album art tag.
        '''

        has_art = metadata.has_art_tag(TEST_MP3_NO_TAG)
        self.assertFalse(has_art)


    def test_has_art_tag_invalid(self):
        '''
        @brief Tests checking if an audio file has an embedded album art tag.
        '''

        has_art = None

        _, file_ext = os.path.splitext(TEST_M3U)
        err_msg = f"MusicProcessingError with file: {TEST_M3U} has invalid extension: {file_ext}"

        with self.assertRaises(MusicProcessingError) as cm:
            has_art = metadata.has_art_tag(TEST_M3U)

        self.assertIsNone(has_art)
        self.assertTrue(cm.exception.args[0], err_msg)


    def test_load_any_file(self):
        '''
        @brief Tests attempt to load an audio file with mutagen.
        '''

        for src_file in self.src_file_paths:
            loaded_file = metadata.load_any_file(src_file)
            audio_class_name = loaded_file.__class__.__name__
            self.assertTrue(audio_class_name in AUDIO_FILES)


    def test_load_any_file_invalid(self):
        '''
        @brief Test loading a non-audio file with mutagen.
        '''

        audio_file = None
        file_path = TEST_M3U

        with self.assertRaises(ValueError) as cm:
            audio_file = metadata.load_any_file(file_path)

        self.assertIsNone(audio_file)
        err_msg = f"ValueError loading {TEST_M3U} returned None"
        self.assertTrue(cm.exception.args[0], err_msg)


    def test_load_any_file_non_extant(self):
        '''
        @brief Tests attempt to load a non-extant audio file with mutagen File function.
        '''

        audio_file = None
        file_path = TEST_WAV_NONE

        with self.assertRaises(MutagenError) as cm:
            audio_file = metadata.load_any_file(file_path)

        self.assertIsNone(audio_file)

        '''
        With a non-extant file, a mutagen load call will return a chained exception:
        MutagenError encapsulating a FileNotFoundError, so we check the exception context dunder,
        disable logging to prevent console clutter.
        '''
        self.assertIsInstance(cm.exception.__context__, FileNotFoundError)


    def test_map_m4a_tags(self):
        '''
        @brief Tests mapping native m4a tags to preferred id3 format.
        '''

        input_tags = metadata.get_any_tags(TEST_M4A_EAGLES)
        id3_tags = metadata.map_m4a_tags(input_tags)

        self.assertDictEqual(id3_tags, self.m4a_mapped)


    def test_map_mp3_tags(self):
        '''
        @brief Tests mapping native mp3 tags to preferred id3 format.
        '''

        input_tags = metadata.get_any_tags(TEST_MP3_ABBA)
        id3_tags = metadata.map_mp3_tags(input_tags)

        self.assertDictEqual(id3_tags, self.mp3_mapped)


    def test_map_wma_tags(self):
        '''
        @brief Tests mapping native wma tags to preferred id3 format.
        '''

        input_tags = metadata.get_any_tags(TEST_WMA_CCR)
        id3_tags = metadata.map_wma_tags(input_tags)

        self.assertDictEqual(id3_tags, self.wma_mapped)


    def test_update_id3(self):
        '''
        @brief tests updating an id3 tags dictionary with newest year and disc value.
        '''

        # need name mangling to access private method
        id3_tags = metadata._AudioMetadata__update_id3(self.id3_date_values, self.id3_input_tags)

        # add expected date and tpos to expected output
        id3_output_tags = copy.deepcopy(self.id3_input_tags)
        id3_output_tags["TYER"] = '1963'
        id3_output_tags["TPOS"] = "1/1"
        self.assertDictEqual(id3_tags, id3_output_tags)

        # change tags i/o dicts tpos values to test function NOT adding default tpos value
        self.id3_input_tags["TPOS"] = "2/3"
        id3_output_tags["TPOS"] = "2/3"
        id3_tags = metadata._AudioMetadata__update_id3(self.id3_date_values, self.id3_input_tags)
        self.assertDictEqual(id3_tags, id3_output_tags)


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
