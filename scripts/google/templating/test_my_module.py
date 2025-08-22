
'''
@file test_my_module.py
@brief Defines the test my module class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import logging
import os
import unittest
from unittest.mock import patch

# third party modules
# import ipsumlorem

# local modules
from src import AUDIO_EXTS, AUDIO_TYPES
from src import EXPORT_TLD
from src import FOLDER_ART
from src import PLAYLIST_EXTS
from src.generated_files import GENERATED_FILES
from src.errors import JSONOutputError
from src.errors import MusicProcessingError
from src.errors import PathInfoError
from src.errors import PlaylistError
from src.errors import VideoStreamError
from src.audio_info import AudioArt
from src.audio_info import AudioMetadata
from src.audio_info import AudioPlaylist
from src.audio_normalize import AudioNormalization
from src.dir_processing import DirectoryProcessing

gc.enable()

# instantiate module levels vars here
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
TESTS_TLD = os.path.join(TESTS_PATH, EXPORT_TLD)

# instantiate classes here
art = AudioArt()
directory = DirectoryProcessing()
metadata = AudioMetadata()
normalization = AudioNormalization()
playlist = AudioPlaylist()


class TestMyClass(unittest.TestCase):
    '''
    @brief Tests MyClass class functions.
    '''

    def test_my_function(self):
        '''
        @brief Tests my function purpose.
        '''

        pass


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
    methods = get_method_names(TestMyClass)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestMyClass('test_my_function'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
