#!/usr/bin/env python3
'''
@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.
'''

from src.dir_processing.directory_processing import DirectoryProcessing
from src.audio_info.audio_metadata import AudioMetadata

def main():
    '''
    @brief Module entry point.
    @details Takes command line arguments and executes per arguments.
    '''

    # processing = DirectoryProcessing('H', 'Music')
    # processing.ext_list_files("aac")

    metadata = AudioMetadata()

    # # get mp3
    # mp3_file_list = ["H:\\Music\\Kenny Rogers\\Daytime Friends - The Very Best of Kenny\\18 Lady.mp3",
    #                  "H:\\Music\\Various Artists\\Best of the Blues, Volume 1\\Albert Collins-Trash Talkin'.mp3",
    #                  "H:\\Music\\4 Non Blondes\\Bigger, Better, Faster, More!\\4 Non Blondes-What's Up.mp3",
    #                  "H:\\Music\\.38 Special\\.38 Special-Teacher, Teacher.mp3",
    #                  "H:\\Music\\.38 Special\\Special Forces\\.38 Special-Caught Up in You.mp3"
    #                 ]
    # for song in mp3_file_list:
    #     metadata_type = metadata.get_any_metadata_type(song)
    #     if metadata_type == "mp3":
    #         tag = metadata.get_mp3_tag_info(song)
    #         print(tag)

    # # get any tag info
    # any_tag_info_file_list = ["H:\\Music\Dolly Parton\\Blue Smoke\\Dolly Parton-Unlikely Angel.mp3",
    #                           "H:\\Music\\The Eagles\\The Eagles-Desperado.m4a",
    #                           "H:\\Music\\Elton John\\Greatest Hits, Vol. 2\\Elton John-Island Girl.wma"
    #                          ]
    # for song in any_tag_info_file_list:
    #     metadata_type = metadata.get_any_metadata_type(song)
    #     print("Song: {0} has metadata type: {1}".format(song, metadata_type))

    # conversion testing
# The commented out code block `conversion_file_list` is creating a list of file paths for audio files
# that are intended for conversion to MP3 format. The paths are specified as strings, with each string
# representing the file path of an audio file. The code block is currently disabled by commenting it
# out, so it is not being executed when the script runs.
    # conversion_file_list = ["H:\\Music\\The Eagles\\The Eagles-Desperado.m4a",
    #                         "H:\\Music\\The Eagles\\Hotel California\\The Eagles-Hotel California.wma"
    #                         ]

    conversion_file_list = [r"/media/gerald/Music/Music/The Eagles/The Eagles-Desperado.m4a",
                            r"/media/gerald/Music/Music/The Eagles/Hotel California/The Eagles-Hotel California.wma"
                            ]

    for song in conversion_file_list:
        metadata_type = metadata.get_any_metadata_type(song)

        if metadata_type.lower() != "mp3":
            metadata.convert_any_to_mp3(song)

if __name__ == "__main__":
    main()

