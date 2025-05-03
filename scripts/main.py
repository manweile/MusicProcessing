#!/usr/bin/env python3
from src.dir_processing.directory_processing import DirectoryProcessing

def main():
    processing = DirectoryProcessing('H', 'Music')
    processing.get_ext_list_files("aac")

if __name__ == "__main__":
    main()