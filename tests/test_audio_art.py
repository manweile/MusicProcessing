'''
@file test_audio_art.py
@brief Defines the test audio art class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import os
import unittest

# local modules
from src import EXPORT_TLD
from src.generated_files import GENERATED_FILES
from src.audio_info import AudioArt

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

    def test_has_video_stream_false(self):
        '''
        @brief Tests if audio file does not have video stream.
        '''

        input_audio = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", "Billie Holiday-Georgia On My Mind.wma")
        self.assertFalse(art.has_video_stream(input_audio))


    def test_has_video_stream_true(self):
        '''
        @brief Tests if audio file does have video stream.
        '''

        input_audio = os.path.join(TESTS_TLD, "Crush", "Here", "Crush-Live.mp3")
        self.assertTrue(art.has_video_stream(input_audio))


    def test_has_video_stream_non_extant(self):
        '''
        @brief Tests check for audio stream on non-extant file.
        '''

        input_audio = os.path.join(TESTS_TLD, "Non-extant.wav")
        # subprocess_utils.subprocess_run throws CalledProcessError
        # raised to has_video_stream throws Exception

        self.assertTrue(art.has_video_stream(input_audio))


    def test_extract_asf_art(self):
        '''

        '''

        input_audio = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", "Billie Holiday-Georgia On My Mind.wma")
        art.extract_asf_art(input_audio)
        # @todo
        # assert exists Folder.jpg in Album dir
        # add teardown to remove folder jpg in album dir


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
    methods = get_method_names(TestAudioArt)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioArt(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
