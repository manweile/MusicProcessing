'''!
@file directory_processing.py
@brief Defines the directory processing class

@section description_directory_processing Description
Defines the base class for directory processing
- DirectoryProcessing (base class)

@section libraries_directory_processing Libraries/Modules
- os standard library (https://docs.python.org/3/library/os.html)
- pathvalidate 3rd party library (https://pathvalidate.readthedocs.io/en/latest/index.html#)
    - access to is_valid_filename, sanitize_filepath, ValidationError

@section author_directory_processing Authour(s)
- Created by Gerald Manweiler on April 8, 2025

@copyright 2025 GWN Software. All rights reserved.
'''

# standard
import csv
import gc
import glob
import logging
import os
import sys

# third party
from pathvalidate import is_valid_filename, sanitize_filepath, ValidationError

_AUDIO_EXT = ["mp3", "m4a", "wma"]

gc.enable()

class DirectoryProcessing():
    '''!
    @brief Contains directory processing functionality

    @details Defines the base directory processing used by project

    '''

    def __init__(self, drive, tld):
        '''!
        @brief Initializes the DirectoryProcessing class

        @details The drive letter is expected to be valid and the top level directory is expected to exist
        We set the values for convenience, and do not expect to change them

        @param {instance} self The class reference
        @param {str} drive The drive letter for top level directory
        @param {str} tld The top level directory that contains all the music files
        @return {object} DirectoryProcessing An instance of the class
        '''

        if drive.isalpha():
            self._drive = drive + ":\\"
        else:
            raise ValueError("alphabetic character A-Z or a-z expected")

        # remove any invalid directory path characters
        # using defaults so platform is "universal", replacement text for invalid chars is ""
        # refer to https://pathvalidate.readthedocs.io/en/latest/pages/reference/function.html#pathvalidate.sanitize_filename
        sanitized_tld = sanitize_filepath(tld)
        if is_valid_filename(sanitized_tld):
            self._tld = sanitized_tld
        else:
            raise ValidationError("invalid directory path {0}".format(tld))

        self._tld_path = self._drive + self._tld


    @property
    def drive(self):
        '''!
        @brief Returns the drive letter

        @param {instance} self The class reference
        @return {str} The drive letter for top level directory
        '''

        drive = None
        # slice out the drive letter, don't need the :\
        drive = self._drive[:1]
        return drive


    @drive.setter
    def drive(self, value):
        '''!
        @brief Sets the drive letter

        @param {str} value The drive letter
        '''

        if value.isalpha():
            self._drive = value + ":\\"
        else:
            raise ValueError("alphabetic character A-Z or a-z expected")


    @property
    def tld(self):
        '''!
        @brief Returns the top level directory

        @param {instance} self The class reference
        @return {str} tld The top level directory
        '''

        return self._tld


    @tld.setter
    def tld(self, value):
        '''!
        @brief Sets the top level directory

        @details The top level directory is expected to exist already

        @param {instance} self The class reference
        @param {str} value The top level directory
        '''

        # check if input directory does exist
        tld_path = self._drive() + value
        if(os.path.isdir(tld_path)):
            self._tld = value
        else:
            raise IOError("Top level directory {0} not found".format(tld_path))


    @property
    def tld_path(self):
        '''!
        @brief Returns the full top level directory path

        @param {instance} self The class reference
        @return {str} tld_path The top level directory path
        '''

        return self._tld_path


    def get_file_type(self, file_path):
        '''!
        @brief Returns the file type of audio file without leading period

        @param {str} file_path The full audio file path
        @return {str} file_extension The file extension of audio file
        '''

        split_extension = None

        try:
            if file_path:
                # get the file type, don't care about the file name
                _, split_extension = os.path.splitext(file_path)
                file_extension = split_extension[1:]
        except Exception:
            print('File extension error: {} occurred'.format(sys.exec_info()[0]))

        return file_extension

    def list_files(self, file_ext, start_path=None):
        '''!
        @brief Generates a csv containing full file path for an extension

        @details Generates a csv containing full file path for an extension
        If start_path is not supplied, uses the class top level directory path
        The csv file is created in the current working directory

        @param {str} file_ext The file extension want file paths for
        @param tld_path {str} start_path The starting point of the directory walk
        '''

        if start_path == None:
            start_path = self._tld_path

        # get the current working directory, that's where csv will be saved
        cwd = os.getcwd()
        csv_filename = "found_" + file_ext + ".csv"
        csv_path = os.path.join(cwd, csv_filename)
        # create csv file, overwrite any existing with same name
        csv_outfile = open(csv_path, 'w', newline='')
        csv_file_writer = csv.writer(csv_outfile)
        #  write the header row so we always have record of what extension we looked for
        csv_file_writer.writerow([file_ext + " file path"])

        # top down walk for files of the specified extension type
        # want the directory path so can get full file path
        # so don't care about the sub-directories
        for dir_path, _, files in os.walk(start_path):
            for file in files:
                if(file.endswith('.' + file_ext)):
                    audio_file_path = os.path.join(dir_path, file)
                    csv_file_writer.writerow([audio_file_path])

        csv_outfile.close()


    def make_album_dir(self, artist_dirpath, album_dir):
        '''!
        @brief Creates an album sub-directory in an artist directory

        @details Creates the album sub directory for the artist if needed
        The album name for the directory is drawn from the metadata and may need sanitization
        because there is no guarantee it can be used as is from the metadata
        The artist directory has been manually created and presumed to be valid
        The audio file(s) for the created album directory will moved into the created directory by another function

        @param {instance} self The class reference
        @param {str} artist_dirpath The name of the artist for artist directory
        @param {str} album_dir The name of the album for new album directory
        '''

        # using all defaults
        album_dir = sanitize_filepath(album_dir)

        music_dir = os.path.join(self._tld_path, artist_dirpath, album_dir)

        # if the album sub-directory already exists, we don't need to do anything
        if not os.path.exists(music_dir):
            os.mkdir(music_dir)

