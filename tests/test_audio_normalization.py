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
from unittest import TestCase

# local module constants
from src import MUSIC_TLD
from src.generated_files import GENERATED_FILES
from tests import TEST_M3U, TEST_MP3_ABBA, TEST_MP3_CRUSH, TEST_SMEAGOL_MP3, TEST_MP3_X
# local module classes
from src.audio_normalize import AudioNormalization

gc.enable()

NORM_PATH = os.path.join(GENERATED_FILES, MUSIC_TLD)

BIT_SRC = TEST_MP3_CRUSH
BIT_RES = 129156

EBU_DYNAMIC_SRC = TEST_MP3_ABBA
EBU_DYNAMIC_RES = os.path.join(NORM_PATH, "Abba", "Waterloo", "ABBA-Waterloo.mp3")

EBU_LINEAR_SRC = TEST_MP3_CRUSH
EBU_LINEAR_RES = os.path.join(NORM_PATH, "Crush", "Here", "Crush-Live.mp3")

# @todo find a audio file that will peak clip (can't be X Ambassadors - that vol fails first)
PEAK_CLIP_SRC = ""
PEAK_CLIP_RES = ""

MAX_VOL_SRC = TEST_MP3_X
MAX_VOL_RES = "X Ambassadors-Renegades.mp3 has max volume: 0.00 dB, peak normalization not needed"

PEAK_SRC = TEST_MP3_CRUSH
PEAK_RES = os.path.join(NORM_PATH, "Crush", "Here", "Crush-Live.mp3")

RMS_CLIPPING_SRC = TEST_MP3_CRUSH
RMS_CLIPPING_RES = os.path.join(NORM_PATH, "Crush", "Here", "Crush-Live.mp3")

RMS_SRC = TEST_SMEAGOL_MP3
RMS_RES = os.path.join(NORM_PATH, "The Lord of the Rings", "The Two Towers", "Howard Shore-The Taming Of Smeagol.mp3")

SAMPLE_RATE_SRC = TEST_MP3_ABBA
SAMPLE_RATE_RES = 44100

VOL_ERR_SRC = TEST_M3U

VOL_INFO_SRC = TEST_MP3_CRUSH
VOL_INFO_RES = {'mean_volume': -19.9, 'max_volume': -6.7}


normalization = AudioNormalization()


class TestAudioNormalization(TestCase):
    '''
    @brief Tests AudioNormalization class functions.
    '''

    def tearDown(self):
        '''
        @brief Clean up the created audio file and directory.
        '''

        if os.path.exists(NORM_PATH):
            shutil.rmtree(NORM_PATH)


    def test_ebu_normalize_dynamic(self):
        '''
        @brief Tests dynamic ebu normalize audio file level.
        '''

        normalization.ebu_normalize_file(EBU_DYNAMIC_SRC, show_spinner=False)
        self.assertTrue(os.path.exists(EBU_DYNAMIC_RES))


    def test_ebu_normalize_linear(self):
        '''
        @brief Tests linear ebu normalize audio file level.
        '''

        normalization.ebu_normalize_file(EBU_LINEAR_SRC, show_spinner=False)
        self.assertTrue(os.path.exists(EBU_LINEAR_RES))


    def test_get_bit_rate(self):
        '''
        @brief Tests getting bit rate.
        '''

        bit_rate = normalization.get_bit_rate(BIT_SRC)

        res_bitrate = math.floor(bit_rate / 1000)
        exp_bitrate = math.floor(BIT_RES / 1000)

        self.assertEqual(res_bitrate, exp_bitrate)


    @unittest.skip("complete, needs mocking")
    def test_get_bit_rate_decode_error(self):
        '''
        @brief Tests getting bit rate throws JSONDecodeError.
        '''

        # @todo mock the subprocess_run ret val

        bit_rate = normalization.get_bit_rate(BIT_SRC)

        res_bitrate = math.floor(bit_rate / 1000)
        exp_bitrate = math.floor(BIT_RES / 1000)

        self.assertEqual(res_bitrate, exp_bitrate)


    def test_get_sample_rate(self):
        '''
        @brief Tests getting sample rate.
        '''

        sample_rate = normalization.get_sample_rate(SAMPLE_RATE_SRC)
        self.assertEqual(SAMPLE_RATE_RES, sample_rate)


    @unittest.skip("complete, needs mocking")
    def test_get_sample_rate_decode_error(self):
        '''
        @brief Tests getting sample rate throws JSONDecodeError.
        '''

        # @todo mock the subprocess_run ret val
        sample_rate = normalization.get_sample_rate(SAMPLE_RATE_SRC)
        self.assertEqual(SAMPLE_RATE_RES, sample_rate)


    @unittest.skip("complete, needs mocking")
    def test_get_sample_rate_index_error(self):
        '''
        @brief Tests getting sample rate throws IndexError.
        '''

        # @todo mock the subprocess_run ret val
        sample_rate = normalization.get_sample_rate(SAMPLE_RATE_SRC)
        self.assertEqual(SAMPLE_RATE_RES, sample_rate)


    def test_get_volume_info(self):
        '''
        @brief Tests getting volume info.
        '''

        volumes = normalization.get_volume_info(VOL_INFO_SRC)
        self.maxDiff = None
        self.assertDictEqual(volumes, VOL_INFO_RES)


    @unittest.skip("complete, look for CalledProcessError in other tests")
    def test_get_volume_info_invalid_file(self):
        '''
        @brief Tests getting volume info failing.
        '''

        volumes = None
        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.CRITICAL) as cm:
            volumes = normalization.get_volume_info(VOL_ERR_SRC)

        self.assertIsNone(volumes)
        # @todo need to check if there will logging output


    @unittest.skip("complete")
    def test_loudnorm_json_parse(self):
        '''
        @brief Tests parsing json element out of ffmpeg loudnorm subprocess stderr output.
        '''

        # need name mangling to access private method
        input_data = normalization._AudioNormalization__loudnorm_json_parse(self.input_process)
        pass


    @unittest.skip("complete")
    def test_loudnorm_json_parse_decode_error(self):
        '''
        @brief Tests parsing json element out of ffmpeg loudnorm subprocess stderr output.
        '''

        pass


    @unittest.skip("complete")
    def test_loudnorm_json_parse_output_error(self):
        '''
        @brief Tests parsing json element out of ffmpeg loudnorm subprocess stderr output.
        '''

        pass


    @unittest.skip('complete')
    def test_normalize_walk_ebu(self):
        '''
        @brief Tests ebu normalizes all audio files in specified top level directory.
        '''

        pass


    @unittest.skip('complete')
    def test_normalize_walk_peak(self):
        '''
        @brief Tests peak normalizes all audio files in specified top level directory.
        '''

        pass


    @unittest.skip('complete')
    def test_normalize_walk_rms(self):
        '''
        @brief Tests rms normalizes all audio files in specified top level directory.
        '''

        pass


    def test_peak_normalize_file(self):
        '''
        @brief Tests peak normalize audio file level.
        '''

        normalization.peak_normalize_file(PEAK_SRC, show_spinner=False)
        self.assertTrue(os.path.exists(PEAK_RES))


    @unittest.skip("Need a file that will peak clip")
    def test_peak_normalize_file_clipping(self):
        '''
        @brief Tests rms normalize audio file level would clip.
        '''

        # PEAK_CLIP_SRC = os.path.join("F:", "ConvertedMusic", "3 Doors Down", "3 Doors Down", "3 Doors Down-It's Not My Time.mp3")
        PEAK_CLIP_SRC = RMS_SRC
        PEAK_CLIP_RES = os.path.join(NORM_PATH, "3 Doors Down", "3 Doors Down", "3 Doors Down-It's Not My Time.mp3")

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.peak_normalize_file(PEAK_CLIP_SRC, show_spinner=False)

        self.assertIn(PEAK_CLIP_RES, cm.output[0])


    def test_peak_normalize_file_max_volume(self):
        '''
        @brief Tests peak normalize audio file level would have max volume.
        '''

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.peak_normalize_file(MAX_VOL_SRC, show_spinner=False)

        self.assertIn(MAX_VOL_RES, cm.output[0])


    # @unittest.skip("one off")
    def test_peak_clip_check_walk(self):
        '''
        @brief Tests walking tld to get peak adjustment amount.
        '''

        converted_tld = r"F:\ConvertedMusic"
        normalization.peak_clip_check_walk(converted_tld)


    # @unittest.skip("one off")
    def test_rms_clip_check_walk(self):
        '''
        @brief Tests walking tld to get rms adjustment amount.
        '''

        converted_tld = r"F:\ConvertedMusic"
        normalization.rms_clip_check_walk(converted_tld)


    @unittest.skip("one off")
    def test_normalize_max_vol_check_walk(self):
        '''
        @brief Tests walking tld to get normalization max volume amount.
        '''

        converted_tld = r"F:\ConvertedMusic"
        normalization.normalize_max_vol_check_walk(converted_tld)


    def test_rms_normalize_file(self):
        '''
        @brief Tests rms normalize audio file level.
        '''

        normalization.rms_normalize_file(RMS_SRC, show_spinner=False)
        self.assertTrue(os.path.exists(RMS_RES))


    def test_rms_normalize_file_clipping(self):
        '''
        @brief Tests rms normalize audio file level would clip.
        '''

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.rms_normalize_file(RMS_CLIPPING_SRC, show_spinner=False)

        self.assertIn(RMS_CLIPPING_RES, cm.output[0])


    def test_rms_normalize_max_volume(self):
        '''
        @brief Tests rms normalize audio file level would have mav volume.
        '''

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)

        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.peak_normalize_file(MAX_VOL_SRC, show_spinner=False)

        self.assertIn(MAX_VOL_RES, cm.output[0])


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
