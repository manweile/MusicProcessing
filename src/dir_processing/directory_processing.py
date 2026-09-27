'''
@class DirectoryProcessing
@file directory_processing.py
@author Gerald Manweiler

@brief Defines the directory processing class.

@details Defines methods for creating files, locating media, and maintaining music directories.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import csv                                                  # for CSV file creation
import errno                                                # for operating-system error codes
import fnmatch                                              # for file-pattern matching
import gc                                                   # for garbage collection management
import inspect                                              # for current function inspection
import logging                                              # for module logging
import os                                                   # for operating-system interfaces
from operator import itemgetter                             # for CSV row sorting
from os import strerror                                     # for operating-system error messages
from pathlib import Path                                    # for object-oriented filesystem paths

# Local Module Methods
from src import add_module_handler                          # for module-specific logging handlers

# Local Module Constants
from src import AUDIO_EXTS                                  # for supported audio file extensions
from src import CSV_DIR                                     # for CSV output directory name
from src import CSV_EXT                                     # for CSV file extension
from src import M4A_EXT                                     # for M4A file extension
from src import MP3_EXT                                     # for MP3 file extension
from src import MUSIC_TLD                                   # for music top-level directory name
from src import PLAYLIST_EXTS                               # for supported playlist extensions
from src import RESULT_DIR                                  # for text result directory name
from src import RESULT_EXT                                  # for text result extension
from src import UTF8                                        # for UTF-8 text encoding
from src import WMA_EXT                                     # for WMA file extension
from src.generated_files import GENERATED_PATH              # for generated file output paths

# Local Module Errors
from src import MusicProcessingError                        # for directory processing failures

gc.enable()

## @var logger
# @brief Logger instance for the module.
# @details Sets the logger name to the current module name.
logger = logging.getLogger(__name__)

## @var basename
# @brief Base name for the logger file handler.
# @details Gets the module file name from the current file path.
basename = os.path.basename(__file__)

add_module_handler(logger, basename)


class DirectoryProcessing():
    '''
    @brief Defines the directory processing class.

    @details Provides methods to create generated files and maintain music-directory content.
    '''

    def __init__(self) -> None:
        '''
        @brief Initializes the DirectoryProcessing class.

        @details Initializes a DirectoryProcessing instance without instance-specific state.
        '''

        pass


    def create_csv(self, csv_filename: str, data: list,
                   csv_dir: str | None = None, text_mode: str | None = None, header_row: list | None = None, sort_col: int | None = None) -> None:
        '''
        @brief Creates a CSV file.

        @details Creates a CSV file in the specified or default directory.<br>
        Supports an optional file mode, header row, and sort column.

        @param csv_filename {str} Base filename without the CSV extension.
        @param data {list} Rows to write into the CSV file.
        @param csv_dir {str} Optional, path for csv file.
        @param text_mode {str} Optional file opening mode.
        @param header_row {list} Optional row naming the CSV fields.
        @param sort_col {int} Optional, the column to sort data on.

        @exception OSError A system related error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            # Determine the directory to save the CSV file, set to default if not specified
            if csv_dir is None:
                csv_dir = os.path.join(GENERATED_PATH, CSV_DIR)

            csv_path = os.path.join(csv_dir, csv_filename + CSV_EXT)

            # Set the default text mode to overwrite if not specified
            if text_mode is None:
                text_mode = 'w'

            csv_outfile = open(csv_path, mode=text_mode, encoding=UTF8, newline='')

            # using semicolon as delimiter cause have audio files with comma in dir path and/or file name
            csv_file_writer = csv.writer(csv_outfile, dialect='excel', delimiter=';')

            if header_row is not None:
                csv_file_writer.writerow(header_row)

            if sort_col is not None:
                sorted_data = sorted(data, key=itemgetter(sort_col))
            else:
                sorted_data = data

            csv_file_writer.writerows(sorted_data)
            csv_outfile.close()

        except OSError as os_error:
            logger.error(f"OSError {(strerror(os_error.errno))} writing data to {csv_path}", exc_info=True)
            raise os_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__}writing {csv_filename}", stack_info=True)
            raise e_error


    def create_txt(self, txt_filename: str, data: list, txt_dir: str | None = None) -> None:
        '''
        @brief Creates a text file.

        @details Creates a text file in the user-specified or default directory.

        @param txt_filename {str} Base filename without the text-file extension.
        @param data {list} Items to write as individual text-file lines.
        @param txt_dir {str} Optional path for txt file.

        @exception OSError A system related error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            if txt_dir is None:
                txt_dir = os.path.join(GENERATED_PATH, RESULT_DIR)

            txt_path = os.path.join(txt_dir, txt_filename + RESULT_EXT)

            # need to overwrite cause expecting many runs
            txt_outfile = open(txt_path, mode='w', encoding=UTF8, newline='')
            for item in data:
                txt_outfile.write(f"{item}\n")

            txt_outfile.close()

        except OSError as os_error:
            logger.error(f"OSError {(strerror(os_error.errno))} writing data to {txt_path}", exc_info=True)
            raise os_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} writing {txt_path}", stack_info=True)
            raise e_error


    def get_audio_file_list(self, start_path: str) -> None:
        '''
        @brief Generates a csv containing full path for all audio files.

        @details Requires a start path for the directory walk.<br>
        Creates CSV and text files in the generated-files directory.<br>
        Includes each audio file's full path and extension.

        @param start_path {str} The starting point of the directory walk.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        csv_data = []
        csv_filename = inspect.currentframe().f_code.co_name

        txt_data = []
        txt_filename = inspect.currentframe().f_code.co_name

        directory_counts = {}

        audio_count = 0
        album_count = 0
        artist_count = 0
        csv_count = 0

        dir_count = 0
        file_extension = None
        header_row = ["file path", "audio file type"]
        jpg_count = 0
        m4a_count = 0
        mp3_count = 0
        m3u_count = 0
        other_count = 0
        not_count = 0
        tot_count = 0
        txt_count = 0
        wma_count = 0

        try:
            initial_depth = len(start_path.split(os.sep))

            # top down walk for files in specified top level directory
            # want the directory path & file names so we can get full file path
            # we don't care about the sub-directory names
            for dir_path, dir_names, filenames in os.walk(start_path):
                current_depth = len(dir_path.split(os.sep)) - initial_depth

                if dir_names:
                    directory_counts[current_depth] = directory_counts.get(current_depth, 0) + len(dir_names)

                for file in filenames:
                    _, file_extension = os.path.splitext(file)

                    if (file_extension.lower() in AUDIO_EXTS):
                        audio_file_path = os.path.join(dir_path, file)
                        csv_data.append([audio_file_path, file_extension])
                        audio_count += 1

                        if file_extension == MP3_EXT:
                            mp3_count += 1
                        elif file_extension == M4A_EXT:
                            m4a_count += 1
                        elif file_extension == WMA_EXT:
                            wma_count += 1
                    else:
                        if file_extension == CSV_EXT:
                            csv_count += 1
                        elif file_extension == PLAYLIST_EXTS[0]:
                            m3u_count += 1
                        elif file_extension == RESULT_EXT:
                            txt_count += 1
                        elif file_extension == ".jpg":
                            jpg_count += 1
                        else:
                            not_count += 1

                    tot_count += 1

            self.create_csv(csv_filename, csv_data, None, None, header_row, 1)

            artist_count = directory_counts[0]
            album_count = directory_counts[1]
            dir_count = artist_count + album_count
            other_count = csv_count + jpg_count + txt_count + m3u_count + not_count

            txt_data.append(f"Found {artist_count} artist directories")
            txt_data.append(f"Found {album_count} album directories")
            txt_data.append(f"Found {dir_count} total directories")

            txt_data.append(f"Found {mp3_count} {MP3_EXT.removeprefix(".")} files")
            txt_data.append(f"Found {m4a_count} {M4A_EXT.removeprefix(".")} files")
            txt_data.append(f"Found {wma_count} {WMA_EXT.removeprefix(".")} files")
            txt_data.append(f"Found {audio_count} total audio files")

            txt_data.append(f"Found {csv_count} csv files")
            txt_data.append(f"Found {jpg_count} jpg files")
            txt_data.append(f"Found {txt_count} text files")
            txt_data.append(f"Found {m3u_count} m3u files")
            txt_data.append(f"Found {not_count} unknown type files")
            txt_data.append(f"Found {other_count} non-audio files")

            txt_data.append(f"Found {tot_count} total files")
            self.create_txt(txt_filename, txt_data, None)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting files for {start_path}", stack_info=True)
            raise e_error


    def get_ext_file_list(self, start_path: str, file_pattern: str) -> None:
        '''
        @brief Generates a csv containing full file path for audio file extension.

        @details Returns all valid audio files when no file pattern is specified.<br>
        Requires a valid extension such as '.mp3', '.m4a', '.wma', or '.flac' when a pattern is specified.

        @param start_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional file extension pattern for matching file paths.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        if file_pattern:
            csv_filename = inspect.currentframe().f_code.co_name + "_" + file_pattern.lower().removeprefix(".")
        else:
            csv_filename = inspect.currentframe().f_code.co_name + "_all"
        header_row = ["File Path", "File Ext"]

        try:
            # top down walk for files of the specified extension type
            # want the directory path & file names so we can get full file path
            # don't care about the sub-directory names at all
            for dir_path, _, filenames in os.walk(start_path):
                for file in filenames:
                    file_name, file_ext = os.path.splitext(file)

                    if file_ext.lower() not in AUDIO_EXTS:
                        # we don't touch non-audio files like jpg's, on to next
                        continue
                    elif file_pattern:
                        if not fnmatch.fnmatch(file_ext.lower(), file_pattern.lower()):
                            # no match for input pattern, on to next
                            continue

                    # have a valid file type, no pattern input or matched pattern, either can create valid file path
                    audio_file_path = os.path.join(dir_path, file_name)

                    data.append([audio_file_path, file_ext.lower().removeprefix(".")])

            self.create_csv(csv_filename, data, None, None, header_row, None)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting file list for files with {file_ext} for {start_path}", stack_info=True)
            raise e_error


    def get_file_directory(self, start_path: str, file_name: str) -> str | None:
        '''
        @brief Finds the directory path of a file given its name and a starting search path.

        @details Searches the directory tree for a file with the specified name.

        @param start_path {str} The root directory to start from.
        @param file_name {str} The name of the file to find.
        @return dir_path {str | None} The directory path for the file, or None if not found.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        dir_path = None

        try:
            for root, dirs, files in os.walk(start_path):
                if file_name in files:
                    dir_path = root

        except Exception as e_error:
            logger.exception(
                f"Exception {type(e_error).__name__} getting directory path for {file_name} "
                f"and starting path {start_path}",
                stack_info=True,
            )
            raise e_error
        else:
            return dir_path


    def make_dir(self, dir_path: str) -> None:
        '''
        @brief Creates a directory.

        @details Creates the directory and any missing parent directories when needed.

        @param dir_path {str} The path to create.

        @exception OSError A system related error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            else:
                return

        except OSError as os_error:
            if os_error.errno == errno.EACCES:
                logger.error(f"OSError permission denied for creating {dir_path}", exc_info=True)
                raise OSError(f"OSError permission denied for creating {dir_path}")
            else:
                logger.error(f"OSError {(strerror(os_error.errno))} making directory with {dir_path}", exc_info=True)
                raise os_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} creating {dir_path}", stack_info=True)
            raise e_error


    def path_info(self, file_path: str) -> str | None:
        '''
        @brief Creates export path for audio file conversions and normalizations.

        @details Requires the caller to create the export directory when needed.<br>
        Requires the input file to have a supported audio extension.

        @param file_path {str} The full file path for exported mp3 audio file.
        @return export_path {str | None} The export path, or None for unsupported audio files.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            export_dir = None
            export_name = None
            export_path = None

            input_path = Path(file_path)

            input_ext = input_path.suffix
            if input_ext.lower() not in AUDIO_EXTS:
                logger.warning(f"File {input_path} is not in {AUDIO_EXTS}")
                return None

            # The final two parent path components identify the artist and album directories
            input_path_parent = input_path.parent

            # remove the anchor (ie. / or H:\), have no use for it
            input_path_parts = input_path_parent.parts[1:]

            # using fixed storage path because will always know project structure
            export_dir = os.path.join(GENERATED_PATH, MUSIC_TLD)

            full_len = len(input_path_parts)
            artist_len = full_len - 2

            # iterate over last 2 elements, which will be artist and album directories
            for i in range(artist_len, full_len):
                export_dir = os.path.join(export_dir, input_path_parts[i])

            # get mp3 audio extension from package constants
            export_ext = MP3_EXT

            input_name = input_path.stem

            export_name = input_name + export_ext
            export_path = os.path.join(export_dir, export_name)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting export path {file_path}", stack_info=True)
            raise e_error
        else:
            return export_path


    def remove_empty_album_dir(self, start_path: str) -> None:
        '''
        @brief Removes empty album directories.

        @details Removes empty second-level album directories within artist directories.

        @param start_path {str} The starting point of the directory walk.

        @exception OSError A system related error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        dir_count = 0

        try:
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

            logger.info(f"removed {dir_count} empty album directories")

        except OSError as os_error:
            if os_error.errno == errno.EACCES:
                logger.error(f"OSError permission denied for  deleting {artist_item_path}", exc_info=True)
                raise OSError(f"OSError permission denied for  deleting {artist_item_path}")
            else:
                logger.error(f"OSError {(strerror(os_error.errno))} deleting {artist_item_path}", exc_info=True)
                raise os_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} deleting {artist_item_path}", stack_info=True)
            raise e_error


    def remove_pattern(self, start_path: str, file_pattern: str) -> None:
        '''
        @brief Removes file matching specified pattern.

        @details Removes files matching the specified pattern beneath the top-level directory.<br>
        Refuses to delete from a file-system root or mount point.<br>
        Refuses the broad *.* wildcard pattern.

        @param start_path {str} The starting point of the directory walk.
        @param file_pattern {str} The file pattern we want to delete.

        @exception OSError A system related error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            # guard against attempting root directory deletions
            resolved_path = Path(start_path).resolve()
            if resolved_path == resolved_path.parent:
                logger.error(f"{start_path} is file system root")
                raise MusicProcessingError(f"{start_path} is file system root")

            # guard against mount point deletion
            if os.path.ismount(start_path):
                logger.error(f"{start_path} is a mount point")
                raise MusicProcessingError(f"{start_path} is a mount point")

            # guard against full wildcard pattern
            if file_pattern == "*.*":
                logger.error(f"{file_pattern} is too broad")
                raise MusicProcessingError(f"{file_pattern} is too broad")

            # top down walk for files of the specified pattern
            # want the directory path & file names so we can get full file path
            # don't care about the sub-directory names at all

            for dir_path, dir_names, file_names in os.walk(start_path):
                for file in file_names:
                    if fnmatch.fnmatch(file, file_pattern.lower()):
                        file_path = os.path.join(dir_path, file)
                        os.remove(file_path)
                        logger.info(f"Deleted: {file_path}")

        except MusicProcessingError as mp_error:
            raise mp_error
        except OSError as os_error:
            if os_error.errno == errno.EACCES:
                logger.error(f"OSError permission denied for  deleting {file_path}", exc_info=True)
                raise OSError(f"OSError permission denied for  deleting {file_path}")
            else:
                logger.error(f"OSError {(strerror(os_error.errno))} deleting {file_path}", exc_info=True)
                raise os_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} deleting {file_path}", stack_info=True)
            raise e_error
