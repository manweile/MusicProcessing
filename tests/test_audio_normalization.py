'''
@file test_audio_normalization.py
@brief Defines the test audio normalization class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import logging
import math
import os
import shutil
import unittest
from json import JSONDecodeError
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

# local module constants
from src import ILT, LRA, MUSIC_TLD, TP
from src.generated_files import GENERATED_PATH
from tests import TEST_M3U, TEST_MP3_ABBA, TEST_MP3_CRUSH, TEST_MP3_SMEAGOL, TEST_MP3_X
from tests import TESTS_PATH
# local module errors
from src.errors import JSONOutputError
# local module classes
from src.audio_normalize import AudioNormalization

gc.enable()

## @var normalization
# @brief instance of AudioNormalization class
# @details used for accessing class functionality
normalization = AudioNormalization()


class TestAudioNormalization(TestCase):
    '''
    @brief Tests AudioNormalization class functions.
    '''

    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite.

        @details These datums are used throughout class and only need init once.
        '''

        # directory for "walk" type tests: D:\MusicProcessing\tests\NormalizedMusic
        cls.normalized = os.path.join(TESTS_PATH, "NormalizedMusic")
        # the path where converted files will be created D:\MusicProcessing\src\generated_files\Music
        cls.norm_path = os.path.join(GENERATED_PATH, MUSIC_TLD)

        # audio source files for walk tests
        cls.src_file_paths = [TEST_MP3_ABBA, TEST_MP3_CRUSH, TEST_MP3_SMEAGOL]

        #  for ebu normalization walk top level directory test
        cls.normalized_results = []
        cls.normalized_results.append(os.path.join(cls.norm_path, "Abba", "Waterloo", "ABBA-Waterloo.mp3"))
        cls.normalized_results.append(os.path.join(cls.norm_path, "Crush", "Here", "Crush-Live.mp3"))
        cls.normalized_results.append(os.path.join(cls.norm_path, "The Lord of the Rings", "The Two Towers", "Howard Shore-The Taming Of Smeagol.mp3"))

        # copy input files to converted "walk" directory
        for src_normalized in cls.src_file_paths:
            # get the audio file name w/o path
            # eg from D:\MusicProcessing\tests\Music\Abba\Waterloo\ABBA-Waterloo.mp3 -> ABBA-Waterloo.mp3
            file_name = os.path.basename(src_normalized)

            # get audio file parent path parts
            # eg D:\MusicProcessing\tests\Music\Abba\Waterloo
            # D:\, MusicProcessing, tests, Music, Abba, Waterloo
            file_path = Path(src_normalized)
            file_parent = file_path.parent
            path_parts = file_parent.parts

            # build up the artist & album path, from last 2 elements of file parent path parts
            # eg Abba, Waterloo -> Abba\Waterloo
            full_len = len(path_parts)
            artist_len = full_len - 2
            artist_album = ""
            for i in range(artist_len, full_len):
                artist_album = os.path.join(artist_album, path_parts[i])

            # create the destination directory
            # D:\MusicProcessing\tests\NormalizedMusic\Abba\Waterloo\
            dest_dir = os.path.join(cls.normalized, artist_album)
            os.makedirs(dest_dir, exist_ok=True)

            # create dest: D:\MusicProcessing\tests\NormalizedMusic\Abba\Waterloo\ABBA-Waterloo.mp3
            dest_path = os.path.join(dest_dir, file_name)

            # and copy
            shutil.copy(src_normalized, dest_path)

        cls.bit_src = TEST_MP3_CRUSH
        cls.bit_res = 129156

        cls.ebu_dynamic_src = TEST_MP3_ABBA
        cls.ebu_dynamic_res = os.path.join(cls.norm_path, "Abba", "Waterloo", "ABBA-Waterloo.mp3")

        cls.ebu_linear_src = TEST_MP3_CRUSH
        cls.ebu_linear_res = os.path.join(cls.norm_path, "Crush", "Here", "Crush-Live.mp3")

        cls.json_decode_msg = "Expecting ',' delimiter"

        cls.max_vol_src = TEST_MP3_X
        cls.max_vol_res = "X Ambassadors-Renegades.mp3 has max volume: 0.00 dB, peak normalization not needed"

        cls.peak_src = TEST_MP3_CRUSH
        cls.peak_res = os.path.join(cls.norm_path, "Crush", "Here", "Crush-Live.mp3")

        cls.rms_clipping_src = TEST_MP3_CRUSH
        cls.rms_clipping_res = os.path.join(cls.norm_path, "Crush", "Here", "Crush-Live.mp3")

        cls.rms_src = TEST_MP3_SMEAGOL
        cls.rms_res = os.path.join(cls.norm_path, "The Lord of the Rings", "The Two Towers", "Howard Shore-The Taming Of Smeagol.mp3")

        cls.sample_rate_src = TEST_MP3_ABBA
        cls.sample_rate_res = 44100

        cls.vol_err_src = TEST_M3U

        cls.vol_info_src = TEST_MP3_CRUSH
        cls.vol_info_res = {'mean_volume': -19.9, 'max_volume': -6.7}

        cls.input_process = CompletedProcess(
            args=[
                'ffmpeg',
                '-hide_banner',
                '-i', f'{TEST_MP3_ABBA}',
                '-vn',
                '-af', (f"loudnorm=I={ILT}:TP={TP}:LRA={LRA}:print_format=json"),
                '-f', 'null', '-'
            ],
            returncode=0,
            stdout='',
            # tests using stderr are expected to fill in needed values
            stderr=""
        )


    @classmethod
    def tearDownClass(cls):
        '''
        @brief Cleans up the walk type tests source audio files and directories.
        '''

        if os.path.exists(cls.normalized):
            shutil.rmtree(cls.normalized)


    def tearDown(self):
        '''
        @brief Clean up the created audio file and directory.
        '''

        if os.path.exists(self.norm_path):
            shutil.rmtree(self.norm_path)


    def test_ebu_normalize_dynamic(self):
        '''
        @brief Tests dynamic ebu normalize audio file level.
        '''

        normalization.ebu_normalize_file(self.ebu_dynamic_src, show_spinner=False)
        self.assertTrue(os.path.exists(self.ebu_dynamic_res))


    def test_ebu_normalize_linear(self):
        '''
        @brief Tests linear ebu normalize audio file level.
        '''

        normalization.ebu_normalize_file(self.ebu_linear_src, show_spinner=False)
        self.assertTrue(os.path.exists(self.ebu_linear_res))


    def test_get_bit_rate(self):
        '''
        @brief Tests getting bit rate.
        '''

        bit_rate = normalization.get_bit_rate(self.bit_src)

        res_bitrate = math.floor(bit_rate / 1000)
        exp_bitrate = math.floor(self.bit_res / 1000)

        self.assertEqual(res_bitrate, exp_bitrate)


    @patch('src.audio_normalize.audio_normalization.SubprocessUtilities.subprocess_run')
    def test_get_bit_rate_decode_error(self, mock_subprocess_run):
        '''
        @brief Tests getting bit rate throws JSONDecodeError.
        '''

        bit_rate = None
        # missing close brace in stdout causes JSONDecodeError
        mock_subprocess_run.return_value = CompletedProcess(
            args=['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_entries', 'format=bit_rate', f'{self.bit_src}'],
            returncode=0,
            stdout='{"format": {"bit_rate": "129156"}',
            stderr=''
        )

        with self.assertRaises(JSONDecodeError) as cm:
            bit_rate = normalization.get_bit_rate(self.bit_src)

        self.assertIsNone(bit_rate)
        self.assertEqual("JSONDecodeError", cm.exception.__class__.__name__)
        self.assertEqual(self.json_decode_msg, cm.exception.msg)

        mock_subprocess_run.reset_mock(return_value=True, side_effect=True)


    def test_get_bit_rate_index_error(self):
        '''
        @brief Tests getting sample rate throws IndexError.
        '''

        bit_rate = None
        bit_rate_normalization = AudioNormalization()

        mock_get_bit_rate = Mock(spec=bit_rate_normalization)
        mock_get_bit_rate.side_effect = IndexError()

        bit_rate_normalization.get_bit_rate = mock_get_bit_rate

        with self.assertRaises(IndexError) as cm:
            bit_rate = bit_rate_normalization.get_bit_rate(self.bit_src)

        self.assertIsNone(bit_rate)
        self.assertEqual("IndexError", cm.exception.__class__.__name__)

        mock_get_bit_rate.reset_mock(return_value=True, side_effect=True)


    def test_get_sample_rate(self):
        '''
        @brief Tests getting sample rate.
        '''

        sample_rate = normalization.get_sample_rate(self.sample_rate_src)
        self.assertEqual(self.sample_rate_res, sample_rate)


    @patch('src.audio_normalize.audio_normalization.SubprocessUtilities.subprocess_run')
    def test_get_sample_rate_decode_error(self, mock_subprocess_run):
        '''
        @brief Tests getting sample rate throws JSONDecodeError.
        '''

        sample_rate = None
        # missing close brace in stdout causes JSONDecodeError
        mock_subprocess_run.return_value = CompletedProcess(
            args=[
                'ffprobe',
                '-v', 'quiet',
                '-select_streams', 'a:0',
                '-show_entries', 'stream=sample_rate',
                '-of', 'json',
                f'{self.sample_rate_src}'
            ],
            returncode=0,
            stdout='{"programs": [], "stream_groups": [], "streams": [{"sample_rate": "44100"}]',
            stderr=''
        )

        with self.assertRaises(JSONDecodeError) as cm:
            sample_rate = normalization.get_sample_rate(self.sample_rate_src)

        self.assertIsNone(sample_rate)
        self.assertEqual("JSONDecodeError", cm.exception.__class__.__name__)
        self.assertEqual(self.json_decode_msg, cm.exception.msg)

        mock_subprocess_run.reset_mock(return_value=True, side_effect=True)


    def test_get_sample_rate_index_error(self):
        '''
        @brief Tests getting sample rate throws IndexError.
        '''

        sample_rate = None
        sample_rate_normalization = AudioNormalization()

        mock_get_sample_rate = Mock(spec=sample_rate_normalization)
        mock_get_sample_rate.side_effect = IndexError()

        sample_rate_normalization.get_sample_rate = mock_get_sample_rate

        with self.assertRaises(IndexError) as cm:
            sample_rate = sample_rate_normalization.get_sample_rate(self.sample_rate_src)

        self.assertIsNone(sample_rate)
        self.assertEqual("IndexError", cm.exception.__class__.__name__)

        mock_get_sample_rate.reset_mock(return_value=True, side_effect=True)


    def test_get_volume_info(self):
        '''
        @brief Tests getting volume info.
        '''

        volumes = normalization.get_volume_info(self.vol_info_src)
        self.maxDiff = None
        self.assertDictEqual(volumes, self.vol_info_res)


    def test_loudnorm_json_parse(self):
        '''
        @brief Tests parsing json element out of ffmpeg loudnorm subprocess stderr output.
        '''

        test_process = self.input_process
        test_process.stderr = (
            '{\n'
            '\t"input_i" : "-16.52",\n'
            '\t"input_tp" : "-3.42",\n'
            '\t"input_lra" : "2.20",\n'
            '\t"input_thresh" : "-26.93",\n'
            '\t"output_i" : "-15.83",\n'
            '\t"output_tp" : "-2.00",\n'
            '\t"output_lra" : "1.40",\n'
            '\t"output_thresh" : "-26.03",\n'
            '\t"normalization_type" : "dynamic",\n'
            '\t"target_offset" : "-0.17"\n'
            '}\n'
        )

        # need name mangling to access private method
        output_data = normalization._AudioNormalization__loudnorm_json_parse(test_process)
        expected_data = {
            "input_i": "-16.52",
            "input_tp": "-3.42",
            "input_lra": "2.20",
            "input_thresh": "-26.93",
            "output_i": "-15.83",
            "output_tp": "-2.00",
            "output_lra": "1.40",
            "output_thresh": "-26.03",
            "normalization_type": "dynamic",
            "target_offset": "-0.17"
        }
        self.assertDictEqual(output_data, expected_data)


    def test_loudnorm_json_parse_decode_error(self):
        '''
        @brief Tests parsing json element out of ffmpeg loudnorm subprocess stderr output with JSONDecodeError.
        '''

        # the input_process.stderr json string has extra closing curly to trigger a JSONDecodeError
        test_process = self.input_process
        test_process.stderr = (
            '{\n'
            '\t"input_i" : "-16.52",\n'
            '\t"input_tp" : "-3.42",\n'
            '\t"input_lra" : "2.20",\n'
            '\t"input_thresh" : "-26.93",\n'
            '\t"output_i" : "-15.83",\n'
            '\t"output_tp" : "-2.00",\n'
            '\t"output_lra" : "1.40",\n'
            '\t"output_thresh" : "-26.03",\n'
            '\t"normalization_type" : "dynamic",\n'
            '\t"target_offset" : "-0.17"\n'
            '}\n}'
        )

        output_data = None
        with self.assertRaises(JSONDecodeError) as cm:
            # need name mangling to access private method
            output_data = normalization._AudioNormalization__loudnorm_json_parse(test_process)

        self.assertIsNone(output_data)
        self.assertEqual("JSONDecodeError", cm.exception.__class__.__name__)
        self.assertEqual("Extra data", cm.exception.msg)


    def test_loudnorm_json_parse_find_error(self):
        '''
        @brief Tests parsing json element out of ffmpeg loudnorm subprocess stderr output with JSONOutputError.
        '''

        # the input_process.stderr json string must be missing 1 of the curly braces {},
        # to trigger a JSONOutputError, doesn't matter which one.
        test_process = self.input_process
        test_process.stderr = (
            '{\n'
            '\t"input_i" : "-16.52",\n'
            '\t"input_tp" : "-3.42",\n'
            '\t"input_lra" : "2.20",\n'
            '\t"input_thresh" : "-26.93",\n'
            '\t"output_i" : "-15.83",\n'
            '\t"output_tp" : "-2.00",\n'
            '\t"output_lra" : "1.40",\n'
            '\t"output_thresh" : "-26.03",\n'
            '\t"normalization_type" : "dynamic",\n'
            '\t"target_offset" : "-0.17"\n'
            '\n'
        )

        output_data = None
        with self.assertRaises(JSONOutputError) as cm:
            # need name mangling to access private method
            output_data = normalization._AudioNormalization__loudnorm_json_parse(test_process)

        self.assertIsNone(output_data)
        self.assertEqual("JSONOutputError", cm.exception.__class__.__name__)
        err_msg = f"JSONOutputError could not find JSON output in subprocess stderr\n{test_process.stderr}"
        self.assertEqual(err_msg, cm.exception.message)


    def test_normalize_walk_ebu(self):
        '''
        @brief Tests ebu normalizes all audio files in specified top level directory.
        '''

        normalization.normalize_walk(self.normalized, "ebu", show_spinner=False)

        for audio_file in self.normalized_results:
            audio_exists = os.path.exists(audio_file)
            self.assertTrue(audio_exists)


    def test_normalize_walk_peak(self):
        '''
        @brief Tests peak normalizes all audio files in specified top level directory.
        '''

        normalization.normalize_walk(self.normalized, "peak", show_spinner=False)

        audio_exists = os.path.exists(self.peak_res)
        self.assertTrue(audio_exists)


    def test_normalize_walk_rms(self):
        '''
        @brief Tests rms normalizes all audio files in specified top level directory.
        '''

        normalization.normalize_walk(self.normalized, "rms", show_spinner=False)

        audio_exists = os.path.exists(self.rms_res)
        self.assertTrue(audio_exists)


    def test_peak_normalize_file(self):
        '''
        @brief Tests peak normalize audio file level.
        '''

        normalization.peak_normalize_file(self.peak_src, show_spinner=False)
        self.assertTrue(os.path.exists(self.peak_res))


    def test_peak_normalize_file_max_volume(self):
        '''
        @brief Tests peak normalize audio file level would have max volume.
        '''

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.peak_normalize_file(self.max_vol_src, show_spinner=False)

        self.assertIn(self.max_vol_res, cm.output[0])


    def test_rms_normalize_file(self):
        '''
        @brief Tests rms normalize audio file level.
        '''

        normalization.rms_normalize_file(self.rms_src, show_spinner=False)
        self.assertTrue(os.path.exists(self.rms_res))


    def test_rms_normalize_file_clipping(self):
        '''
        @brief Tests rms normalize audio file level would clip.
        '''

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.rms_normalize_file(self.rms_clipping_src, show_spinner=False)

        self.assertIn(self.rms_clipping_res, cm.output[0])


    def test_rms_normalize_max_volume(self):
        '''
        @brief Tests rms normalize audio file level would have max volume.
        '''

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.peak_normalize_file(self.max_vol_src, show_spinner=False)

        self.assertIn(self.max_vol_res, cm.output[0])


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
    methods = get_method_names(TestAudioNormalization)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioNormalization(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
