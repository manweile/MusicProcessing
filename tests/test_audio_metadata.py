
'''
@file test_audio_metadata.py
@brief Defines the test audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import os
import unittest

# third party modules
from pydub.utils import mediainfo

# local modules
from src import EXPORT_TLD
from src.audio_info import AudioMetadata

gc.enable()

# instantiate module levels vars here
TESTS_TLD = os.path.dirname(os.path.abspath(__file__))
MP3_FILE = os.path.join("Crush", "Here", "Crush-Live.mp3")
SRC_FILE = os.path.join(TESTS_TLD, EXPORT_TLD, MP3_FILE)

# instantiate classes here
metadata = AudioMetadata()


class TestAudioMetadata(unittest.TestCase):
    '''
    @brief Tests AudioMetadata class functions.
    '''

    def test_get_media_info_dict(self):
        '''
        @brief Tests Returns dictionary with media info.

        @details Tests my replacement for pydub.utils mediainfo
        '''

        results_info = metadata.get_media_info_dict(SRC_FILE)
        expected_info = mediainfo(SRC_FILE)
        self.assertDictEqual(results_info, expected_info)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestAudioMetadata('test_get_media_info_dict'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
