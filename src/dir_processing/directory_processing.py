'''
@file directory_processing.py
@brief Defines the base class for processing files and directories.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import csv
import errno
import gc
import os
import sys

from operator import itemgetter

# third party modules
import pathvalidate

# local modules
# generated files package does not have any modules,
# just a package variable the __all__ list exposes via __init__.py
from src.generated_files import generated_files
from src import _AUDIO_EXTS
from src import _AUDIO_TYPES

gc.enable()

class DirectoryProcessing():
    '''
    @brief Defines the base directory processing used by project.
    '''

    def __init__(self, tld_path):
        '''
        @brief      Initializes the DirectoryProcessing class.

        @param      tld_path {str} The top level directory path that contains all the music files.
        @return     DirectoryProcessing {instance} An instance of the class.
        @exception  OSError An os error
        @exception  Exception A generic exception
        '''

        try:
            if os.path.isdir(tld_path):
                self._tld_path = tld_path
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise OSError(f"Error: Path {tld_path} not found")
            else:
                raise Exception(f"Exception {e} setting path {tld_path}")


    @property
    def tld_path(self):
        '''
        @brief Returns the full top level directory path.

        @return tld_path {str} The top level directory path
        '''

        return self._tld_path

    @tld_path.setter
    def tld_path(self, tld_path):
        '''
        @brief Sets the top level directory.

        @details The top level directory is expected to exist already.

        @param tld_path {str} The top level directory path that contains all the music files.
        @exception OSError An os error
        @exception Exception A generic exception
        '''

        try:
            if os.path.isdir(tld_path):
                self._tld_path = tld_path
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise OSError(f"Error: Path {tld_path} not found")
            else:
                raise Exception(f"Exception {e} setting path {tld_path}")


    def get_audio_file_list(self, start_path=None):
        '''
        @brief Generates a csv containing full path for all audio files.

        @details If start_path is not supplied, uses the class top level directory path.
        @details The csv file is created in the designated generated files directory.
        @details The csv has 2 columns, full file path for audio file and extension.

        @param file_ext {str} The file extension want file paths for
        @param tld_path {str} start_path The starting point of the directory walk
        @exception Exception A generic exception
        '''

        data = []
        file_count = 0
        file_extension = None
        mp3_count = 0
        m4a_count = 0
        wma_count = 0

        if start_path == None:
            start_path = self._tld_path

        try:
            # get the generated files directory, that's where csv will be saved
            csv_dir = generated_files
            csv_filename = "found_audio_files.csv"
            csv_path = os.path.join(csv_dir, csv_filename)

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
            print(f"Found {file_count} audio files")
            print(f"{mp3_count} {_AUDIO_TYPES[0]} files")
            print(f"{m4a_count} {_AUDIO_TYPES[1]} files")
            print(f"{wma_count} {_AUDIO_TYPES[2]} files")
        except Exception as e:
            raise Exception(f"Exception {e} getting files for {start_path}")


    def get_ext_file_list(self, file_ext=None, start_path=None):
        '''
        @brief Wrapper for function that generates a csv containing full file path for an extension.

        @details If start_path is not supplied, uses the class top level directory path.
        @details If file extension is not supplied, uses the preset audio types list.

        @param file_ext {str} The file extension want file paths for.
        @param start_path {str} The starting point of the directory walk.
        '''

        if start_path == None:
            start_path = self._tld_path

        if (file_ext):
            self.__ext_file_list(file_ext, start_path)
        else:
            for file_ext in _AUDIO_TYPES:
                self.__ext_file_list(file_ext, start_path)


    def __ext_file_list(self, file_ext, start_path):
        '''
        @brief Generates a csv containing full file path for an audio file type.

        @details The csv file has one column that shows the filepath for files with audio file type we looked for.
        @details The csv file is sorted in directory path as found by os walk top down order.
        @details The csv file is created in the designated generated files directory.

        @param file_ext {str} The file type want file paths for
        @param start_path {str} The starting point of the directory walk
        @exception Exception A generic exception
        '''

        try:
            type_count = 0
            csv_filename = "found_" + file_ext + ".csv"
            # get the generated files directory, that's where csv will be saved
            csv_dir = generated_files
            csv_path = os.path.join(csv_dir, csv_filename)
            # create csv file, overwrite any existing with same name if necessary
            csv_outfile = open(csv_path, 'w', newline='')
            csv_file_writer = csv.writer(csv_outfile)

            # write the header row so we always have record of what extension we looked for
            header_row = file_ext + " file path"
            csv_file_writer.writerow([header_row])

            # top down walk for files of the specified extension type
            # want the directory path & file names so we can get full file path
            # don't care about the sub-directory names at all
            for dir_path, _, files in os.walk(start_path):
                for file in files:
                    if(file.endswith('.' + file_ext)):
                        audio_file_path = os.path.join(dir_path, file)
                        csv_file_writer.writerow([audio_file_path])
                        type_count += 1

            csv_outfile.close()
            print(f"Found {type_count} {file_ext} files")
        except Exception as e:
            raise Exception(f"Exception {e} getting files for extension {file_ext} in {start_path}")


    def get_file_ext(self, file_path):
        '''
        @brief Returns the file type of audio file without leading period.

        @details Returns the file type using os library as opposed to getting it from audio metadata.

        @param file_path {str} The full audio file path
        @return file_ext {str} The file type of audio file
        @exception Exception A generic file type exception
        '''

        split_extension = None

        try:
            if file_path:
                # get the file extension, don't care about the file name
                _, split_extension = os.path.splitext(file_path)
                # want the type, not the full extension with the period
                file_ext = split_extension[1:]
        except Exception:
            print('File type error: {} occurred'.format(sys.exec_info()[0]))

        return file_ext


    def make_album_dir(self, artist_dirpath, album_dir):
        '''
        @brief Creates an album sub-directory in an artist directory.

        @details Creates the album sub directory for the artist if needed.
        @details The album name for the directory is drawn from the metadata.
        @details The artist directory has been manually created and presumed to be valid.
        @details The audio file(s) for the created album directory will moved into the created directory by another function.

        @param artist_dirpath {str} The name of the artist for artist directory
        @param album_dir {str} The name of the album for new album directory
        @exception ValidationError Album name is unacceptable as a directory path
        @exception OSError An os permission error
        @exception Exception A generic exception
        '''

        # sanitize because the metadata might have characters invalid for directory names
        # using defaults so platform is "universal", replacement text for invalid chars is ""
        # refer to https://pathvalidate.readthedocs.io/en/latest/pages/reference/function.html#pathvalidate.sanitize_filename
        if album_dir:
            sanitized_album_dir = pathvalidate.sanitize_filepath(album_dir)
        else:
            raise pathvalidate.ValidationError(f"Album name: {album_dir} is unacceptable as a directory path")

        music_dir = os.path.join(self._tld_path, artist_dirpath, sanitized_album_dir)

        # if the album sub-directory already exists, we don't need to do anything
        if os.path.exists(music_dir):
            print(f"artist & album sub-directory: {music_dir} already exists")
        else:
            try:
                os.mkdir(music_dir)
                print(f"Created album sub-directory: {sanitized_album_dir} under artist directory: {artist_dirpath}")
            except Exception as e:
                if e.errno == errno.EACCES:
                    raise OSError(f"Error: permission denied for creating {music_dir}")
                else:
                    raise Exception(f"Exception {e} creating {music_dir}")


