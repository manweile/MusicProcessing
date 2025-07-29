'''
@file test_audio_art.py
@brief Defines the test audio art class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import os
import unittest

# local modules
from src.audio_info import AudioArt

# local modules
from src import EXPORT_TLD, FOLDER_ART
from src.generated_files import GENERATED_FILES

gc.enable()

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

    def test_extract_album_art(self):
        '''
        @brief Tests if album art is extracted from audio file.
        '''

        pass


    # def test_update_m3u(self):
    #     '''
    #     @brief Tests if the updated m3u file is equal to expected results.
    #     '''

    #     input_m3u = os.path.join(_TESTS_PATH, EXPORT_TLD, "test.m3u")
    #     input_tld = os.path.join(_TESTS_PATH, EXPORT_TLD)
    #     generated_m3u = os.path.join(GENERATED_FILES, "test.m3u")
    #     expected_m3u = os.path.join(_TESTS_PATH, EXPORT_TLD, "expected.m3u")

    #     playlist.update_paths(input_tld, input_m3u)

    #     self.assertTrue(os.path.exists(generated_m3u))

    #     with open(generated_m3u, "r") as generated_file, open(expected_m3u, "r") as expected_file:
    #         generated_content = generated_file.read()
    #         expected_content = expected_file.read()
    #         self.assertEqual(generated_content, expected_content, "File contents should be equal")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestAudioArt('test_extract_album_art'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
