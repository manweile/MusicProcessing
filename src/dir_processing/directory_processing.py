'''!@brief Defines the directory processing class.'''

##
# @file directory_processing.py
# @brief Defines the directory processing class
#
# @section description_directory_processing Description
# Defines the base class for directory processing
# - DirectoryProcessing (base class)

# @section libraries_directory_processing Libraries/Modules
# - os standard library (https://docs.python.org/3/library/os.html)
# - pathvalidate 3rd party library (https://pathvalidate.readthedocs.io/en/latest/index.html#)
#     - access to is_valid_filename, sanitize_filepath, ValidationError

# @section author_directory_processing Authour(s)
# - Created by Gerald Manweiler on April 8, 2025

# @copyright 2025 GWN Software. All rights reserved.

# standard modules
import csv
import gc
import os
import sys

from operator import itemgetter

# third party modules
# from pathvalidate import is_valid_filename, sanitize_filepath, ValidationError
import pathvalidate

# local modules
from generated_files import script_directory as generated_files

# from Mp3Tag program, I know I have these audio file extensions and types:
_AUDIO_EXTS = [ ".mp3", ".m4a", ".wma" ]
_AUDIO_TYPES = ["mp3", "m4a", "wma"]

gc.enable()

class DirectoryProcessing():
    '''!
    @brief Contains directory processing functionality.
    @details Defines the base directory processing used by project.
    '''

    def __init__(self, drive, tld):
        '''!
        @private
        @brief      Initializes the DirectoryProcessing class.
        @details    The drive letter is expected to be valid and the top level directory is expected to exist.
        @details    We set the values for convenience, and do not expect to change them.
        @param      self {instance} The class reference.
        @param      drive {str} The drive letter for top level directory.
        @param      tld {str} The top level directory that contains all the music files.
        @return     DirectoryProcessing {instance} An instance of the class.
        '''

        if drive.isalpha() and drive:
            self._drive = drive + ":\\"
        else:
            raise ValueError("alphabetic character A-Z or a-z expected")

        # remove any invalid directory path characters
        # using defaults so platform is "universal", replacement text for invalid chars is ""
        # refer to https://pathvalidate.readthedocs.io/en/latest/pages/reference/function.html#pathvalidate.sanitize_filename
        if tld:
            # sanitized_tld = sanitize_filepath(tld)
            sanitized_tld = pathvalidate.sanitize_filepath(tld)
        else:
            # raise ValidationError("directory path required")
            raise pathvalidate.ValidationError("directory path required")

        # if is_valid_filename(sanitized_tld):
        #     self._tld = sanitized_tld
        # else:
        #     raise ValidationError("invalid directory path {0}".format(tld))
        if pathvalidate.is_valid_filename(sanitized_tld):
            self._tld = sanitized_tld
        else:
            raise pathvalidate.ValidationError("invalid directory path {0}".format(tld))

        self._tld_path = self._drive + self._tld


    @property
    def drive(self):
        '''!
        @public
        @brief Returns the drive letter.
        @param self {instance} The class reference.
        @return drive {str} The drive letter for top level directory.
        '''

        drive = None
        # slice out the drive letter, don't need the :\
        drive = self._drive[:1]
        return drive


    @drive.setter
    def drive(self, value):
        '''!
        @public
        @brief Sets the drive letter.
        @param self {instance} The class reference.
        @param value {str} The drive letter.
        '''

        if value.isalpha():
            self._drive = value + ":\\"
        else:
            raise ValueError("alphabetic character A-Z or a-z expected")


    @property
    def tld(self):
        '''!
        @public
        @brief Returns the top level directory.
        @param {instance} self The class reference
        @return {str} tld The top level directory
        '''

        return self._tld


    @tld.setter
    def tld(self, value):
        '''!
        @public
        @brief Sets the top level directory.
        @details The top level directory is expected to exist already.
        @param self {instance} The class reference.
        @param value {str} The top level directory.
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
        @public
        @brief Returns the full top level directory path.
        @param self {instance} The class reference.
        @return tld_path {str} The top level directory path
        '''

        return self._tld_path


    def audio_list_files(self, start_path=None):
        '''!
        @public
        @brief Generates a csv containing full path for all audio files.
        @details If start_path is not supplied, uses the class top level directory path.
        @details The csv file is created in the designated generated files directory.
        @details The csv has 2 columns, full file path for audio file and extension.
        @param self {instance} The class reference.
        @param file_ext {str} The file extension want file paths for.
        @param tld_path {str} start_path The starting point of the directory walk.
        '''

        data = []
        file_count = 0
        file_extension = None
        mp3_count = 0
        m4a_count = 0
        wma_count = 0

        if start_path == None:
            start_path = self._tld_path

        # get the generated files directory, that's where csv will be saved
        cwd = generated_files
        csv_filename = "found_audio_files.csv"
        csv_path = os.path.join(cwd, csv_filename)

        # create csv file, overwrite any existing with same name
        csv_outfile = open(csv_path, 'w', newline='')
        csv_file_writer = csv.writer(csv_outfile, delimiter=',')
        header_row = ["file path","audio file type"]
        csv_file_writer.writerow(header_row)

        # top down walk for files of the specified extension type
        # want the directory path & file names so we can get full file path
        # we don't care about the sub-directory names
        for dir_path, _, files in os.walk(start_path):
            for file in files:
                _, file_extension = os.path.splitext(file)
                if(file_extension in _AUDIO_EXTS):
                    audio_file_path = os.path.join(dir_path, file)
                    data.append([audio_file_path, file_extension])
                    file_count += 1
                    if file_extension == _AUDIO_EXTS[0]:
                        mp3_count += 1
                    elif file_extension == _AUDIO_EXTS[1]:
                        m4a_count += 1
                    elif file_extension == _AUDIO_EXTS[2]:
                        wma_count += 1

        # sort on the extension, as the audio file path is already sorted by os walk
        sorted_data = sorted(data, key=itemgetter(1))
        csv_file_writer.writerows(sorted_data)
        csv_outfile.close()
        print("Found {0} audio files, with {1} {2} files, {3} {4} files, and {5} {6} files".format(
            file_count, mp3_count, _AUDIO_TYPES[0], m4a_count, _AUDIO_TYPES[1], wma_count, _AUDIO_TYPES[2]))


    def ext_list_files(self, file_ext=None, start_path=None):
        '''!
        @public
        @brief Wrapper for function that generates a csv containing full file path for an extension.
        @details If start_path is not supplied, uses the class top level directory path.
        @details If file extension is not supplied, uses the preset audio types module list.
        @param self {instance} The class reference.
        @param file_ext {str} The file extension want file paths for.
        @param start_path {str} The starting point of the directory walk.
        '''

        if start_path == None:
            start_path = self._tld_path

        if (file_ext):
            self._ext_list_files(file_ext, start_path)
        else:
            for file_type in _AUDIO_TYPES:
                self._ext_list_files(file_type, start_path)


    def _ext_list_files(self, file_type, start_path):
        '''!
        @private
        @brief Generates a csv containing full file path for an audio file type.
        @details The csv file has one column that shows the filepath for files with audio file type we looked for.
        @details The csv file is sorted in directory path as found by os walk top down order.
        @details The csv file is created in the designated generated files directory.
        @param self {instance} The class reference.
        @param file_type {str} The file type want file paths for.
        @param start_path {str} The starting point of the directory walk.
        '''

        type_count = 0
        csv_filename = "found_" + file_type + ".csv"
        # get the generated files directory, that's where csv will be saved
        cwd = generated_files
        csv_path = os.path.join(cwd, csv_filename)
        # create csv file, overwrite any existing with same name if necessary
        csv_outfile = open(csv_path, 'w', newline='')
        csv_file_writer = csv.writer(csv_outfile)

        # write the header row so we always have record of what extension we looked for
        header_row = file_type + " file path"
        csv_file_writer.writerow([header_row])

        # top down walk for files of the specified extension type
        # want the directory path & file names so we can get full file path
        # don't care about the sub-directory names at all
        for dir_path, _, files in os.walk(start_path):
            for file in files:
                if(file.endswith('.' + file_type)):
                    audio_file_path = os.path.join(dir_path, file)
                    csv_file_writer.writerow([audio_file_path])
                    type_count += 1

        csv_outfile.close()
        print("Found {0} {1} files".format(type_count, file_type))


    def get_file_type(self, file_path):
        '''!
        @public
        @brief Returns the file type of audio file without leading period.
        @param self {instance} The class reference.
        @param file_path {str} The full audio file path.
        @return file_type {str} The file type of audio file.
        '''

        split_extension = None

        try:
            if file_path:
                # get the file extension, don't care about the file name
                _, split_extension = os.path.splitext(file_path)
                # want the type, not the full extension with the period
                file_type = split_extension[1:]
        except Exception:
            print('File type error: {} occurred'.format(sys.exec_info()[0]))

        return file_type


    def make_album_dir(self, artist_dirpath, album_dir):
        '''!
        @brief Creates an album sub-directory in an artist directory.
        @details Creates the album sub directory for the artist if needed.
        @details The album name for the directory is drawn from the metadata.
        @details The artist directory has been manually created and presumed to be valid.
        @details The audio file(s) for the created album directory will moved into the created directory by another function.
        @param self {instance} The class reference.
        @param artist_dirpath {str} The name of the artist for artist directory.
        @param album_dir {str} The name of the album for new album directory.
        '''

        # sanitize because the metadata might have characters invalid for directory names
        album_dir = pathvalidate.sanitize_filepath(album_dir)

        music_dir = os.path.join(self._tld_path, artist_dirpath, album_dir)

        # if the album sub-directory already exists, we don't need to do anything
        if not os.path.exists(music_dir):
            os.mkdir(music_dir)

