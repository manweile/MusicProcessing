import os
import platform
import sys

# @todo add /home/gerald/MusicProcessing or D:\MusicProcessing to PATH??
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dir_processing import DirectoryProcessing

if platform.system() == "Linux":
    dir_processing = DirectoryProcessing(r"/media/gerald/Music/Music")
elif platform.system() == "Windows":
    dir_processing = DirectoryProcessing(r"H:\Music")

dir_processing.get_ext_file_list("aac")