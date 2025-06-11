'''
@file directory_processing.py
@brief Defines the base class for processing files and directories.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import csv
import errno
import fnmatch
import gc
import shutil
import os
import sys
from operator import itemgetter

# local modules
from src import _AUDIO_EXTS
from src import _AUDIO_TYPES
# generated files package does not have any modules,
# just a package variable the __all__ list exposes via __init__.py
from src.generated_files import generated_files


gc.enable()


class DirectoryProcessing():
    '''
    @brief Defines the base directory processing used by project.
    '''

    def __init__(self, tld_path=None):
        '''
        @brief      Initializes the DirectoryProcessing class.

        @param      tld_path {str} Optional, the top level directory path that contains all the music files.
        @return     DirectoryProcessing {instance} An instance of the class.
        @exception  OSError An os error.
        @exception  Exception A common baseclass exception to handle unforeseen errors.
        '''

        if tld_path != None:
            try:
                if os.path.isdir(tld_path):
                    self._tld_path = tld_path
            except OSError as e:
                if e.errno == errno.ENOENT:
                    raise OSError(f"Exception: Path {tld_path} not found")
                else:
                    raise Exception(f"Exception {e} setting path {tld_path}")
        else:
            pass


    @property
    def tld_path(self):
        '''
        @brief Returns the full top level directory path.

        @return tld_path {str} The top level directory path.
        '''

        return self._tld_path


    @tld_path.setter
    def tld_path(self, tld_path):
        '''
        @brief Sets the top level directory.

        @details The top level directory is expected to exist already.

        @param      tld_path {str} The top level directory path that contains all the music files.
        @exception  OSError An os path not found or other os error.
        @exception  Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            if os.path.isdir(tld_path):
                self._tld_path = tld_path
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise OSError(f"OSError path {tld_path} not found")
            else:
                raise OSError(f"OSError {e} setting path {tld_path}")
        except Exception as e:
            raise Exception(f"Exception {e} setting path {tld_path}")


    def create_csv(self, csv_filename, data, csv_dir, header_row=None, sort_col=None):
        '''
        @brief Creates a csv file

        @details Creates a csv file in specified directory, or default generated files directory.
        @details Header row and sorting are optional.

        @param      csv_filename {str} Filename for csv.
        @param      data [{str}] Data to write into csv.
        @param      csv_dir {str} Path for csv file.
        @param      header_row [{str}] Optional, the starting row naming fields.
        @param      sort_col {int} Optional, the column to sort data on.
        @exception  Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            csv_path = os.path.join(csv_dir, csv_filename)

            # I don't care about any previous file contents
            csv_outfile = open(csv_path, mode='w', encoding='windows-1252', newline='')
            csv_file_writer = csv.writer(csv_outfile, dialect='excel', delimiter=';')

            if header_row is not None:
                csv_file_writer.writerow(header_row)

            if sort_col is not None:
                sorted_data = sorted(data, key=itemgetter(sort_col))
            else:
                sorted_data = data

            csv_file_writer.writerows(sorted_data)
            csv_outfile.close()
        except Exception as e:
            raise Exception(f"Exception {e} writing {csv_filename}")


    def get_audio_file_list(self, start_path):
        '''
        @brief Generates a csv containing full path for all audio files.

        @details If start_path is not supplied, uses the class top level directory path.
        @details The csv file is created in the designated generated files directory.
        @details The csv has 2 columns, full file path for audio file and extension.

        @param      start_path {str} start_path Optional, the starting point of the directory walk.
        @exception  Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        csv_dir = generated_files
        csv_filename = "found_audio_files.csv"
        file_count = 0
        file_extension = None
        header_row = ["file path", "audio file type"]
        mp3_count = 0
        m4a_count = 0
        not_count = 0
        wma_count = 0
        tot_count = 0

        if start_path is None:
            start_path = self._tld_path

        try:
            # top down walk for files of the specified extension type
            # want the directory path & file names so we can get full file path
            # we don't care about the sub-directory names
            for dir_path, dir_names, filenames in os.walk(start_path):
                for file in filenames:
                    _, file_extension = os.path.splitext(file)
                    if (file_extension in _AUDIO_EXTS):
                        audio_file_path = os.path.join(dir_path, file)
                        data.append([audio_file_path, file_extension])
                        file_count += 1
                        if file_extension == _AUDIO_EXTS[0]:
                            mp3_count += 1
                        elif file_extension == _AUDIO_EXTS[1]:
                            m4a_count += 1
                        elif file_extension == _AUDIO_EXTS[2]:
                            wma_count += 1
                    else:
                        not_count += 1

                    tot_count += 1

            # sort on the extension, as the audio file path is already sorted by os walk
            self.create_csv(csv_filename, data, csv_dir, header_row, 1)
            print(f"Found {tot_count} total files")
            print(f"{not_count} non-audio files")
            print(f"Found {file_count} audio files")
            print(f"{mp3_count} {_AUDIO_TYPES[0]} files")
            print(f"{m4a_count} {_AUDIO_TYPES[1]} files")
            print(f"{wma_count} {_AUDIO_TYPES[2]} files")
        except Exception as e:
            raise Exception(f"Exception {e} getting files for {start_path}")


    def get_ext_file_list(self, file_ext, start_path):
        '''
        @brief Wrapper for function that generates a csv containing full file path for an extension.

        @details If start_path is not supplied, uses the class top level directory path.
        @details If file extension is not supplied, uses the preset audio types list.

        @param  file_ext {str} Optional, the file extension want file paths for.
        @param  start_path {str} Optional, the starting point of the directory walk.
        '''

        if start_path is None:
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

        @param      file_ext {str} The file type want file paths for.
        @param      start_path {str} The starting point of the directory walk.
        @exception  Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        csv_filename = "found_" + file_ext + ".csv"
        csv_dir = generated_files
        header_row = [file_ext + " file path"]
        type_count = 0

        try:
            # top down walk for files of the specified extension type
            # want the directory path & file names so we can get full file path
            # don't care about the sub-directory names at all
            for dir_path, dir_names, filenames in os.walk(start_path):
                for file in filenames:
                    if (file.endswith('.' + file_ext)):
                        audio_file_path = os.path.join(dir_path, file)
                        data.append([audio_file_path])
                        type_count += 1

            self.create_csv(csv_filename, data, csv_dir, header_row, None)
            print(f"Found {type_count} {file_ext} files")
        except Exception as e:
            raise Exception(f"Exception {e} getting files for extension {file_ext} in {start_path}")


    def get_file_ext(self, file_path):
        '''
        @brief Returns the file type of audio file without leading period.

        @details Returns the file type using os library as opposed to getting it from audio metadata.

        @param  file_path {str} The full audio file path.
        @return file_ext {str} The file type of audio file or None.
        '''

        file_ext = None

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

        @details The album name for the directory is drawn from the metadata.
        @details The audio file(s) for the created album directory will moved into the created directory by another function.

        @param      artist_dirpath {str} The absolute path artist directory the new album directory will be created in.
        @param      album_dir {str} The sanitized & validated name of the album for new album directory.
        @exception  OSError An os permission error.
        @exception  Exception A common baseclass exception to handle unforeseen errors.
        '''

        music_dir = os.path.join(artist_dirpath, album_dir)

        if not os.path.exists(music_dir):
            try:
                os.mkdir(music_dir)
            except Exception as e:
                if e.errno == errno.EACCES:
                    raise OSError(f"Exception: permission denied for creating {music_dir}")
                else:
                    raise Exception(f"Exception {e} creating {music_dir}")


    def move_audio_file(self, file_path, destination_dir):
        '''
        @brief Moves an audio file to a new directory.

        @details The destination path must exist already.

        @param      file_path {str} File path for audio file.
        @param      destination_path {str} New directory for audio file.
        @exception  Exception A common baseclass exception to handle unforeseen errors.
        '''

        audio_file = os.path.basename(file_path)
        destination_path = os.path.join(destination_dir, audio_file)

        try:
            shutil.move(file_path, destination_path)
        except Exception as e:
            raise Exception(f"Exception {e} moving {audio_file} from {os.path.dirname(file_path)} to {destination_dir}")


    def remove_album_dir(self, start_path):
        '''
        @brief Removes empty album directories.

        @details Walks through top level directory to remove empty second level album directories contained in artist first level directories.

        @param      start_path {str} The starting point of the directory walk.
        @exception  OSError An os permission error.
        @exception  Exception A common baseclass exception to handle unforeseen errors.
        '''

        dir_count = 0

        try:
            if start_path is None:
                start_path = self._tld_path

            # get the artist dirs under tld
            tld_content = os.listdir(start_path)

            # iterate through top level directory
            # consists of artist directories, playlist files and couple other sundry files
            for tld_item in tld_content:
                # we only want artist directories, playlist/sundry files don't count
                if os.path.isdir(os.path.join(start_path, tld_item)):
                    artist_path = os.path.join(start_path, tld_item)
                else:
                    continue

                # also don't care about empty artist directories
                if os.path.isdir(artist_path) and not os.listdir(artist_path):
                    continue

                # now we look at what's in the current artist directory
                artist_content = os.listdir(artist_path)

                for artist_item in artist_content:
                    artist_item_path = os.path.join(artist_path, artist_item)
                    if os.path.isdir(artist_item_path) and not os.listdir(artist_item_path):
                        os.rmdir(artist_item_path)
                        dir_count += 1

            print(f"removed {dir_count} empty album directories")
        except Exception as e:
            if e.errno == errno.EACCES:
                raise OSError(f"Exception: permission denied for deleting {artist_item_path}")
            else:
                raise Exception(f"Exception {e} deleting {artist_item_path}")


    def remove_pattern(self, start_path, file_pattern):
        '''
        @brief Removes specified pattern.

        @details Walks through top level directory and removes files matching specified file pattern.

        @param      start_path {str} Optional, the starting point of the directory walk.
        @param      file_pattern {str} Optional, the file pattern we want to delete.
        @exception  OSError An os permission error.
        @exception  Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            if start_path is None:
                start_path = self._tld_path

            # top down walk for files of the specified pattern
            # want the directory path & file names so we can get full file path
            # don't care about the sub-directory names at all

            for dir_path, dir_names, file_names in os.walk(start_path):
                for file in file_names:
                    if fnmatch.fnmatch(file, file_pattern):
                        file_path = os.path.join(dir_path, file)
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")

        except Exception as e:
            if e.errno == errno.EACCES:
                raise OSError(f"Exception: permission denied for deleting {file_path}")
            else:
                raise Exception(f"Exception {e} deleting file {file_path}")
