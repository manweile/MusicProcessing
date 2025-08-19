'''
@file test_audio_normalization.py
@brief Defines the test audio normalization class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import os
import shutil
import unittest

# local modules
from src import EXPORT_TLD
from src.generated_files import GENERATED_FILES
from src.audio_normalize import AudioNormalization

gc.enable()

TESTS_TLD = os.path.dirname(os.path.abspath(__file__))
MP3_FILE = os.path.join("Crush", "Here", "Crush-Live.mp3")
NORM_FILE = os.path.join(GENERATED_FILES, EXPORT_TLD, MP3_FILE)
SRC_FILE = os.path.join(TESTS_TLD, EXPORT_TLD, MP3_FILE)

normalization = AudioNormalization()


class TestAudioNormalization(unittest.TestCase):
    '''
    @brief Tests AudioNormalization class functions.
    '''

    def tearDown(self):
        '''
        @brief Clean up the created audio file and directory.
        '''

        expected_tld = os.path.join(GENERATED_FILES, EXPORT_TLD)
        if os.path.exists(expected_tld):
            shutil.rmtree(expected_tld)


    # @todo add ebu normalize
    # @todo add rms normalize
    # @todo add a PathInfoError from one of the normalize defs test
    # @todo add a mp3 only error from one of the normalize defs test


    def test_peak_normalize_file(self):
        '''
        @brief Tests peak normalize audio file level.
        '''

        normalization.peak_normalize_file(SRC_FILE)
        self.assertTrue(os.path.exists(NORM_FILE))


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
