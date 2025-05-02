#!/usr/bin/env python3
'''
@file main.py
@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.
'''

from src.dir_processing.directory_processing import DirectoryProcessing

def main():
    '''
    @brief Module entry point.
    @details Takes command line arguments and executes per arguments.
    '''

    processing = DirectoryProcessing('H', 'Music')
    processing.ext_list_files("aac")

if __name__ == "__main__":
    '''
    @brief Top level script environment entry point
    '''

    main()

