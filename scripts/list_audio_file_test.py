import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dir_processing import DirectoryProcessing

dir_processing = DirectoryProcessing(r"H:\Music")

dir_processing.get_audio_list_files()