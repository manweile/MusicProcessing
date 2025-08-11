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
import os
import unittest

# third party modules
# import ipsumlorem

# local modules
# from src import AUDIO_EXTS, AUDIO_TYPES
# from src import EXPORT_TLD
# from src import FOLDER_ART
# from src import PLAYLIST_EXTS
# from src.generated_files import GENERATED_FILES
# from src.audio_info import AudioArt
# from src.audio_info import AudioMetadata
# from src.audio_info import AudioPlaylist
# from src.audio_normalize import AudioNormalization
# from src.dir_processing import DirectoryProcessing

gc.enable()

# instantiate module levels vars here
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

# instantiate classes here
# art = AudioArt()
# directory = DirectoryProcessing()
# metadata = AudioMetadata()
# normalization = AudioNormalization()
# playlist = AudioPlaylist()


class ${class_name}(unittest.TestCase):
    \'\'\'
    @brief Tests ${class_brief} class functions.
    \'\'\'

    def ${def_name}(self):
        \'\'\'
        @brief Tests ${def_brief}.
        \'\'\'

        pass


if __name__ == \"__main__\":
    suite = unittest.TestSuite()
    suite.addTest(${class_name}(\'${def_name}\'))

    runner = unittest.TextTestRunner(verbosity=${verbosity})
    runner.run(suite)
"""

# @todo argparse this
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

with open(f"{data['file_name']}.py", "w") as f:
    f.write(output_content)
