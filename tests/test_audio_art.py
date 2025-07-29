'''
@file test_audio_art.py
@brief Defines the test audio art class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import logging
import os
import unittest

# local modules
from src import EXPORT_TLD
from src import FILE_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging modules
from src.audio_info import AudioArt
from src.generated_files import GENERATED_FILES

gc.enable()

# Configure logging
basename = os.path.basename(__file__)
stem = os.path.splitext(basename)[0]
file = stem + LOG_EXT
log_filename = os.path.join(GENERATED_FILES, LOG_DIR, file)

logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=FILE_LOG_FORMAT, filemode="a", encoding=UTF8)
logger = logging.getLogger(__name__)
# override the default logging level WARN to lowest level so we can log all level messages
logger.setLevel(logging.DEBUG)

# get the dir path for test location need it to find audio files
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
TESTS_TLD = os.path.join(TESTS_PATH, EXPORT_TLD)

art = AudioArt()


class TestAudioArt(unittest.TestCase):
    '''
    @brief Tests AudioArt class functions.
    '''

    '''
    # has embedded art
    /home/gerald/Music/Crush/Here/Crush-Live.mp3"
    /home/gerald/Music/Joshua Davis/The Voice Peformance/Joshau Davis-The Workingman's Hym.m4a
    /home/gerald/Music/Elton John/Goodbye Yellow Brick Road/Elton John-Saturday Night's Alright for Fighting.wma"

    # has embedded, but not in a video stream, so will fail with ffmpeg
    /home/gerald/Music/Billie Holiday/Georgia On My Mind/Billie Holiday-Georgia On My Mind.wma"

    # no embedded art
    /home/gerald/Music/38 Special/Special Forces/38 Special-Caught Up in You.mp3
    /home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a
    /home/gerald/Music/Alejandro Escovedo/More Miles Than Money- Live 1994-1996/Alejandro Escovedo-Broken Bottle.wma"

    test_has_folder_art
        pass
        fail
    test_is_audio_file
        pass
        fail
    test_has_video_stream
        pass
        fail
    test_has_art_tag
        pass
        fail
    test_extract_album_art
        doesn't really need a test if test the support functions
    test_extract_asf_art
    test_extract_ffmpeg-art
    test_extract_mp3_art
    test_extract_m4a_art
    test_extract_walk
        test with valid pattern
        test with invalid pattern
    test_set_album_art
        not sure how to test
    '''

    def test_has_video_stream_false(self):
        '''
        @brief Tests if audio file does not have video stream.
        '''

        try:
            # input_audio = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", "Billie Holiday-Georgia On My Mind.wma")
            input_audio = os.path.join(TESTS_TLD, "Billie Holiday", "Billie Holiday-Georgia On My Mind.wma")
            self.assertFalse(art.has_video_stream(input_audio))
        except Exception:
            logger.exception("Exception", stackInfo=True)


    def test_has_video_stream_true(self):
        '''
        @brief Tests if audio file does have video stream.
        '''

        input_audio = os.path.join(TESTS_TLD, "Crush", "Here", "Crush-Live.mp3")
        self.assertTrue(art.has_video_stream(input_audio))


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestAudioArt('test_has_video_stream_false'))
    suite.addTest(TestAudioArt('test_has_video_stream_true'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
