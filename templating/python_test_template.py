import os
from string import Template

template_string = """
\'\'\'
@file ${file_name}.py
@brief Defines the ${file_brief} class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
\'\'\'

# standard modules
import gc
import inspect
# import logging
import os
import unittest
from unittest import TestCase
# from unittest.mock import patch

# third party modules
# import ipsumlorem

# local module constants
# from src import AUDIO_EXTS
from src import MUSIC_TLD
# from src import FOLDER_ART
# from src import PLAYLIST_EXTS
# from src.generated_files import GENERATED_FILES
from tests import TESTS_PATH, TESTS_TLD
# local module errors
# from src.errors import JSONOutputError
# from src.errors import MusicProcessingError
# from src.errors import PathInfoError
# from src.errors import PlaylistError
# from src.errors import VideoStreamError
# local module classes
# from src.audio_info import AudioArt
# from src.audio_info import AudioMetadata
# from src.audio_info import AudioPlaylist
# from src.audio_normalize import AudioNormalization
# from src.dir_processing import DirectoryProcessing

gc.enable()

# instantiate classes here

## @var art
# @brief instance of AudioArt class
# @details used for accessing class functionality
# art = AudioArt()

## @var directory
# @brief instance of DirectoryProcessing class
# @details used for accessing class functionality
# directory = DirectoryProcessing()

## @var metadata
# @brief instance of AudioMetadata class
# @details used for accessing class functionality
# metadata = AudioMetadata()

## @var normalization
# @brief instance of AudioNormalization class
# @details used for accessing class functionality
# normalization = AudioNormalization()

## @var playlist
# @brief instance of AudioPlaylist class
# @details used for accessing class functionality
# playlist = AudioPlaylist()

## @var utilities
# @brief instance of AudioUtilities class
# @details used for accessing class functionality
# utilities = AudioUtilities()

## @var subprocess_utils
# @brief instance of SubprocessUtilities class
# @details used for accessing class functionality
# subprocess_utils = SubprocessUtilities()


class ${class_name}(TestCase):
    \'\'\'
    @brief Tests ${class_brief} class functions.
    \'\'\'

    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite.

        @details These datums are used throughout class and only need init once.
        '''


    @classmethod
    def tearDownClass(cls):
        '''
        @brief Cleans up class datums.
        '''

        pass


    def setUp(self):
        '''
        @brief Sets up before individual tests.

        @details Does setup that is required before individual tests.
        '''

        pass


    def tearDown(self):
        '''
        @brief Cleans up after individual tests.

        @details Does clean that is required after every test.
        '''

        pass


    def ${def_name}(self):
        \'\'\'
        @brief Tests ${def_brief}.
        \'\'\'

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



if __name__ == \"__main__\":
    methods = get_method_names(${class_name})

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(${class_name}(name))

    runner = unittest.TextTestRunner(verbosity=${verbosity})
    runner.run(suite)
"""

if __name__ == "__main__":
    '''
    @brief Top level script environment entry point.
    '''

    # @todo use argparse or some other cli param entry paradigm
    data = {
        "file_name": "test_my_module",
        "file_brief": "test my module",
        "class_name": "TestMyClass",
        "class_brief": "MyClass",
        "def_name": "test_my_function",
        "def_brief": "my function purpose",
        "verbosity": 2
    }

    template = Template(template_string)
    output_content = template.substitute(data)

    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path, f"{data['file_name']}.py")

    with open(file, "w") as new_file:
        new_file.write(output_content)
