'''
@class TestAudioNormalization
@file test_audio_normalization.py
@brief Defines the test audio normalization class.

@details Tests audio normalization levels, volume analysis, and loudnorm JSON parsing behavior.

@version 1.0.0
@date 2026-09-22

@author Gerald Manweiler

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import inspect                                              # for test method discovery
import logging                                              # for warning-log assertions
import math                                                 # for bitrate comparison rounding
import os                                                   # for file-system path operations
import shutil                                               # for test-fixture copying and removal
import unittest                                             # for direct test-suite execution
from json import JSONDecodeError                            # for JSON parsing error assertions
from pathlib import Path                                    # for test-fixture path manipulation
from subprocess import CompletedProcess                     # for subprocess result fixtures
from unittest import TestCase                               # for test-case assertions and lifecycle hooks
from unittest.mock import Mock                              # for mock test doubles
from unittest.mock import patch                             # for patched subprocess calls

# Local Module Constants
from src import ILT                                         # for loudness normalization targets
from src import LRA                                         # for loudness-range normalization target
from src import MUSIC_TLD                                   # for generated music directory paths
from src import TP                                          # for true-peak normalization target
from src.generated_files import GENERATED_PATH              # for generated output paths
from tests import TEST_M3U                                  # for invalid audio input tests
from tests import TEST_MP3_ABBA                             # for dynamic normalization tests
from tests import TEST_MP3_CRUSH                            # for linear normalization tests
from tests import TEST_MP3_SMEAGOL                          # for RMS normalization tests
from tests import TEST_MP3_X                                # for max-volume tests
from tests import TESTS_PATH                                # for normalized test-fixture paths

# Local Module Errors
from src.errors import JSONOutputError                      # for loudnorm output parsing errors

# Local Module Classes
from src.audio_normalize import AudioNormalization          # for normalization functionality under test

## @var normalization
# @brief AudioNormalization instance under test.
# @details Provides access to normalization functionality.
normalization = AudioNormalization()


class TestAudioNormalization(TestCase):
    '''
    @brief Tests AudioNormalization class functions.

    @details Verifies normalization, volume analysis, and error handling for audio fixtures.
    '''

    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite.

        @details Creates shared fixture paths, expected results, and subprocess values for the test suite.

        @code{.text}
        loudnorm command line
        ffmpeg -hide_banner -i TEST_MP3_ABBA -vn -af loudnorm=I={ILT}:TP={TP}:LRA={LRA}:print_format=json -f null -

        -hide_banner; reduce output clutter
        -i TEST_MP3_ABBA; the input audio file
        -vn; disable video streams
        -af loudnorm=I={ILT}:TP={TP}:LRA={LRA}:print_format=json; apply loudnorm filter with specified targets and output in json format
        -f null -; output to null format (don't create a file)
        @endcode

        @param cls {type[TestAudioNormalization]} Test class receiving shared fixtures.
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
        cls.normalized_results.append(
            os.path.join(
                cls.norm_path,
                "The Lord of the Rings",
                "The Two Towers",
                "Howard Shore-The Taming Of Smeagol.mp3",
            )
        )

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
        @brief Clean up normalized test-fixture directories.

        @details Removes the prepared normalization directory after the test suite completes.

        @param cls {type[TestAudioNormalization]} Test class containing shared fixture paths.
        '''

        if os.path.exists(cls.normalized):
            shutil.rmtree(cls.normalized)


    def tearDown(self):
        '''
        @brief Clean up generated audio files and directories.

        @details Removes generated normalization output after each test case.

        @param self {TestAudioNormalization} Test instance containing generated output paths.
        '''

        if os.path.exists(self.norm_path):
            shutil.rmtree(self.norm_path)


    def test_ebu_normalize_dynamic(self):
        '''
        @brief Test dynamic EBU normalization for an audio file.

        @details Verifies dynamic EBU normalization creates the expected output file.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing expected output paths.
        '''

        normalization.ebu_normalize_file(self.ebu_dynamic_src, show_spinner=False)
        self.assertTrue(os.path.exists(self.ebu_dynamic_res))


    def test_ebu_normalize_linear(self):
        '''
        @brief Test linear EBU normalization for an audio file.

        @details Verifies linear EBU normalization creates the expected output file.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing expected output paths.
        '''

        normalization.ebu_normalize_file(self.ebu_linear_src, show_spinner=False)
        self.assertTrue(os.path.exists(self.ebu_linear_res))


    def test_get_bit_rate(self):
        '''
        @brief Test audio bitrate retrieval.

        @details Verifies the retrieved bitrate matches the expected fixture bitrate.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing bitrate fixtures.
        '''

        bit_rate = normalization.get_bit_rate(self.bit_src)

        res_bitrate = math.floor(bit_rate / 1000)
        exp_bitrate = math.floor(self.bit_res / 1000)

        self.assertEqual(res_bitrate, exp_bitrate)


    @patch('src.audio_normalize.audio_normalization.SubprocessUtilities.subprocess_run')
    def test_get_bit_rate_decode_error(self, mock_subprocess_run):
        '''
        @brief Test bitrate retrieval with invalid JSON output.

        @details Verifies malformed mocked ffprobe output raises a JSON decode error.

        @code{.text}
        get bit rate command
        ffprobe -v quiet -print_format json -show_entries format=bit_rate self.bit_src

        -v quiet; reduce clutter
        -print_format json; output in json format
        -show_entries format=bit_rate; get just the bit rate
        self.bit_src; the path to the media file to be analyzed.
        @endcode

        @test Error case.

        @param self {TestAudioNormalization} Test instance containing bitrate fixtures.
        @param mock_subprocess_run {Mock} Patched subprocess runner returning invalid JSON.

        @exception JSONDecodeError Mocked ffprobe output is not valid JSON.
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
        @brief Test bitrate retrieval with an index error.

        @details Verifies the mocked bitrate method propagates an index error.

        @test Error case.

        @param self {TestAudioNormalization} Test instance containing bitrate fixtures.

        @exception IndexError Mocked bitrate retrieval has no indexed result.
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
        @brief Test audio sample-rate retrieval.

        @details Verifies the retrieved sample rate matches the expected fixture value.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing sample-rate fixtures.
        '''

        sample_rate = normalization.get_sample_rate(self.sample_rate_src)
        self.assertEqual(self.sample_rate_res, sample_rate)


    @patch('src.audio_normalize.audio_normalization.SubprocessUtilities.subprocess_run')
    def test_get_sample_rate_decode_error(self, mock_subprocess_run):
        '''
        @brief Test sample-rate retrieval with invalid JSON output.

        @details Verifies malformed mocked ffprobe output raises a JSON decode error.

        @code{.text}
        get sample rate command
        ffprobe -v quiet -select_streams a:0 -show_entries stream=sample_rate -of json self.sample_rate_src

        -v quiet: reduce clutter
        -select_streams a:0; only want audio stream
        -show_entries stream=sample_rate; we only get the one entry specified
        -of json; to output in json format
        self.sample_rate_src; the path to the audio file to be analyzed.
        @endcode

        @test Error case.

        @param self {TestAudioNormalization} Test instance containing sample-rate fixtures.
        @param mock_subprocess_run {Mock} Patched subprocess runner returning invalid JSON.

        @exception JSONDecodeError Mocked ffprobe output is not valid JSON.
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
        @brief Test sample-rate retrieval with an index error.

        @details Verifies the mocked sample-rate method propagates an index error.

        @test Error case.

        @param self {TestAudioNormalization} Test instance containing sample-rate fixtures.

        @exception IndexError Mocked sample-rate retrieval has no indexed result.
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
        @brief Test audio volume information retrieval.

        @details Verifies the mean and maximum volume values match the expected fixture data.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing volume fixtures.
        '''

        volumes = normalization.get_volume_info(self.vol_info_src)
        self.maxDiff = None
        self.assertDictEqual(volumes, self.vol_info_res)


    def test_loudnorm_json_parse(self):
        '''
        @brief Test parsing loudnorm JSON from ffmpeg stderr.

        @details Verifies valid loudnorm stderr JSON is converted to the expected dictionary.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing subprocess fixtures.
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
        @brief Test loudnorm JSON parsing with malformed JSON.

        @details Verifies malformed loudnorm stderr JSON raises a JSON decode error.

        @test Error case.

        @param self {TestAudioNormalization} Test instance containing subprocess fixtures.

        @exception JSONDecodeError Loudnorm stderr contains malformed JSON.
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
        @brief Test loudnorm JSON parsing without a complete JSON object.

        @details Verifies incomplete loudnorm stderr output raises a JSON output error.

        @test Error case.

        @param self {TestAudioNormalization} Test instance containing subprocess fixtures.

        @exception JSONOutputError Loudnorm stderr has no complete JSON object.
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
        @brief Test EBU normalization for all audio files in a directory.

        @details Verifies directory-walk EBU normalization creates every expected output file.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing normalized output paths.
        '''

        normalization.level_normalize_walk(self.normalized, "ebu", show_spinner=False)

        for audio_file in self.normalized_results:
            audio_exists = os.path.exists(audio_file)
            self.assertTrue(audio_exists)


    def test_normalize_walk_peak(self):
        '''
        @brief Test peak normalization for all audio files in a directory.

        @details Verifies directory-walk peak normalization creates the expected output file.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing normalized output paths.
        '''

        normalization.level_normalize_walk(self.normalized, "peak", show_spinner=False)

        audio_exists = os.path.exists(self.peak_res)
        self.assertTrue(audio_exists)


    def test_normalize_walk_rms(self):
        '''
        @brief Test RMS normalization for all audio files in a directory.

        @details Verifies directory-walk RMS normalization creates the expected output file.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing normalized output paths.
        '''

        normalization.level_normalize_walk(self.normalized, "rms", show_spinner=False)

        audio_exists = os.path.exists(self.rms_res)
        self.assertTrue(audio_exists)


    def test_peak_normalize_file(self):
        '''
        @brief Test peak normalization for an audio file.

        @details Verifies peak normalization creates the expected output file.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing normalized output paths.
        '''

        normalization.peak_normalize_file(self.peak_src, show_spinner=False)
        self.assertTrue(os.path.exists(self.peak_res))


    def test_peak_normalize_file_max_volume(self):
        '''
        @brief Test peak normalization when maximum volume is already reached.

        @details Verifies peak normalization logs that no further adjustment is needed.

        @test Edge case.

        @param self {TestAudioNormalization} Test instance containing volume fixtures.
        '''

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.peak_normalize_file(self.max_vol_src, show_spinner=False)

        self.assertIn(self.max_vol_res, cm.output[0])


    def test_rms_normalize_file(self):
        '''
        @brief Test RMS normalization for an audio file.

        @details Verifies RMS normalization creates the expected output file.

        @test Happy path.

        @param self {TestAudioNormalization} Test instance containing normalized output paths.
        '''

        normalization.rms_normalize_file(self.rms_src, show_spinner=False)
        self.assertTrue(os.path.exists(self.rms_res))


    def test_rms_normalize_file_clipping(self):
        '''
        @brief Test RMS normalization when output would clip.

        @details Verifies RMS normalization logs a clipping warning.

        @test Edge case.

        @param self {TestAudioNormalization} Test instance containing RMS fixtures.
        '''

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.rms_normalize_file(self.rms_clipping_src, show_spinner=False)

        self.assertIn(self.rms_clipping_res, cm.output[0])


    def test_rms_normalize_max_volume(self):
        '''
        @brief Test RMS normalization when maximum volume is already reached.

        @details Verifies normalization logs that no further peak adjustment is needed.

        @test Edge case.

        @param self {TestAudioNormalization} Test instance containing volume fixtures.
        '''

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.peak_normalize_file(self.max_vol_src, show_spinner=False)

        self.assertIn(self.max_vol_res, cm.output[0])


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
    @brief Run the AudioNormalization test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.
    '''
    methods = get_method_names(TestAudioNormalization)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioNormalization(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
