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
import os
import shutil
import unittest

# local modules
from src import EXPORT_TLD
from src.generated_files import GENERATED_FILES
from src.audio_normalize import AudioNormalization

gc.enable()

NORM_PATH = os.path.join(GENERATED_FILES, EXPORT_TLD)
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

EBU_DYNAMIC_SRC = SAMPLE_RATE_SRC = os.path.join(TESTS_PATH, EXPORT_TLD, "Abba", "Waterloo", "ABBA-Waterloo.mp3")
EBU_DYNAMIC_RES = os.path.join(NORM_PATH, "Abba", "Waterloo", "ABBA-Waterloo.mp3")

SAMPLE_RATE_RES = 44100

EBU_LINEAR_SRC = LOUDNORM_SRC = PEAK_SRC = RMS_CLIPPING_SRC = os.path.join(TESTS_PATH, EXPORT_TLD, "Crush", "Here", "Crush-Live.mp3")
EBU_LINEAR_RES = PEAK_RES = RMS_CLIPPING_RES = os.path.join(NORM_PATH, "Crush", "Here", "Crush-Live.mp3")

SRC_FILE = os.path.join(TESTS_PATH, EXPORT_TLD, "Crush", "Here", "Crush-Live.mp3")

BIT_SRC = VOL_SRC = os.path.join(TESTS_PATH, EXPORT_TLD, "Bear McCreary", "Battlestar Galactica", "Bear McCreary - BSG Gayatri Mantra Theme Song.mp3")
BIT_RES = 128959

VOLUME_INFO_RES = {'mean_volume': -15.8, 'max_volume': -0.1}

normalization = AudioNormalization()


class TestAudioNormalization(unittest.TestCase):
    '''
    @brief Tests AudioNormalization class functions.
    '''

    def tearDown(self):
        '''
        @brief Clean up the created audio file and directory.
        '''

        if os.path.exists(NORM_PATH):
            shutil.rmtree(NORM_PATH)


    # @todo add __loudnorn_json_parse tests
    # can have JSONDecodeError
    # can have JSONOutputError


    # @todo add get_sample_rate tests
    # can have IndexError
    # can have JSONDecodeError


    def test_ebu_normalize_linear(self):
        '''
        @brief Tests linear ebu normalize audio file level.
        '''

        normalization.ebu_normalize_file(EBU_LINEAR_SRC, show_spinner=False)
        self.assertTrue(os.path.exists(EBU_LINEAR_RES))


    def test_ebu_normalize_dynamic(self):
        '''
        @brief Tests dynamic ebu normalize audio file level.
        '''

        normalization.ebu_normalize_file(EBU_DYNAMIC_SRC, show_spinner=False)
        self.assertTrue(os.path.exists(EBU_DYNAMIC_RES))


    # @todo need a peak clipping test
    # @todo need a peak max volume test


    def test_peak_normalize_file(self):
        '''
        @brief Tests peak normalize audio file level.
        '''

        normalization.peak_normalize_file(PEAK_SRC, show_spinner=False)
        self.assertTrue(os.path.exists(PEAK_RES))


    # @todo need a passing rms test
    # @todo need a rms max volume test


    def test_rms_normalize_file_clipping(self):
        '''
        @brief Tests rms normalize audio file level would clip.

        @details This test will fail if ran with pytest.
        '''

        module = f"{normalization.__module__}"
        logger = logging.getLogger(module)
        with self.assertLogs(logger, level=logging.WARNING) as cm:
            normalization.rms_normalize_file(RMS_CLIPPING_SRC, show_spinner=False)

        self.assertIn(RMS_CLIPPING_RES, cm.output[0])


    def test_get_bit_rate(self):
        '''
        @brief Tests getting bit rate.
        '''

        bit_rate = normalization.get_bit_rate(BIT_SRC)
        self.assertEqual(BIT_RES, bit_rate)


    def test_get_sample_rate(self):
        '''
        @brief Tests getting sample rate.
        '''

        sample_rate = normalization.get_sample_rate(SAMPLE_RATE_SRC)
        self.assertEqual(SAMPLE_RATE_RES, sample_rate)


    def test_get_volume_info(self):
        '''
        @brief Tests getting volume info.
        '''

        volumes = normalization.get_volume_info(VOL_SRC)
        self.maxDiff = None
        self.assertDictEqual(volumes, VOLUME_INFO_RES)


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
