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
import logging
import shutil
import os
from operator import itemgetter
from pathlib import Path

# local modules
from src import AUDIO_EXTS, AUDIO_TYPES
from src import EXPORT_TLD
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8        # logging constants
from src import PLAYLIST_EXTS
from src.generated_files import GENERATED_FILES

gc.enable()

# Configure logging
basename = os.path.basename(__file__)
stem = os.path.splitext(basename)[0]
file = stem + LOG_EXT
log_filename = os.path.join(GENERATED_FILES, LOG_DIR, file)
# override the default logging level WARN to lowest level so we can log all levels
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=ERROR_LOG_FORMAT, filemode="a", encoding=UTF8)

# create logger for module and restrict to module
# use raise in exception handling if we need send something inter-module
logger = logging.getLogger(__name__)
logger.propagate = False


class DirectoryProcessing():
    '''
    @brief Defines the base directory processing used by project.
    '''

    def __init__(self, tld_path=None):
        '''
        @brief Initializes the DirectoryProcessing class.

        @param tld_path {str} Optional, the top level directory path that contains all the music files.
        @return DirectoryProcessing {instance} An instance of the class.
        @exception OSError An os error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        if tld_path is not None:
            try:
                if os.path.isdir(tld_path):
                    self._tld_path = tld_path

            except OSError as e:
                if e.errno == errno.ENOENT:
                    logger.error(f"Exception: Path {tld_path} not found", exc_info=True)
                    raise OSError
                else:
                    logger.exception(f"Exception setting path {tld_path}", stack_info=True)
                    raise
        else:
            pass


    def __ext_file_list(self, file_ext, start_path):
        '''
        @brief Generates a csv containing full file path for an audio file type.

        @details The csv file has one column that shows the filepath for files with audio file type we looked for.
        @details The csv file is sorted in directory path as found by os walk top down order.
        @details The csv file is created in the designated generated files directory.

        @param file_ext {str} The file type want file paths for.
        @param start_path {str} The starting point of the directory walk.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        csv_filename = "found_" + file_ext + ".csv"
        csv_dir = GENERATED_FILES
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
            logger.info(f"Found {type_count} {file_ext} files")

        except Exception:
            logger.exception("Exception getting files for extension {file_ext} in {start_path}", stack_info=True)
            raise


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

        @param tld_path {str} The top level directory path that contains all the music files.
        @exception OSError An os path not found or other os error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            if os.path.isdir(tld_path):
                self._tld_path = tld_path

        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error(f"OSError path {tld_path} not found", exc_info=True)
                raise OSError
            else:
                logger.error(f"OSError setting path {tld_path}", exc_info=True)
                raise OSError
        except Exception:
            logger.exception(f"Exception setting path {tld_path}", stack_info=True)
            raise


    def create_csv(self, csv_filename, data, csv_dir, header_row=None, sort_col=None):
        '''
        @brief Creates a csv file

        @details Creates a csv file in specified directory.
        @details Header row and sorting are optional.

        @param csv_filename {str} Filename for csv.
        @param data [{str}] Data to write into csv. Expected to be 1 line per element.
        @param csv_dir {str} Path for csv file.
        @param header_row [{str}] Optional, the starting row naming fields.
        @param sort_col {int} Optional, the column to sort data on.
        @exception Exception A common baseclass exception to handle unforeseen errors.
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

        except Exception:
            logger.exception("Exception writing {csv_filename}", stack_info=True)
            raise


    def create_txt(self, txt_filename, data, txt_dir):
        '''
        @brief Creates a txt file

        @details Creates a txt file in specified directory.

        @param txt_filename {str} Filename for txt.
        @param data [{str}] Data to write into txt. Expected to be 1 line per element.
        @param txt_dir {str} Path for txt file.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            txt_path = os.path.join(txt_dir, txt_filename)

            # need to append cause expecting many runs
            # txt_outfile = open(txt_path, mode='a', encoding='windows-1252', newline='')
            # txt_outfile.writelines([item + "\n" for item in data])
            # txt_outfile.close()
            txt_outfile = open(txt_path, mode='a', encoding='windows-1252', newline='')
            for item in data:
                txt_outfile.write(f"{item}\n")

            txt_outfile.close()

        except Exception:
            logger.exception("Exception writing {txt_path}", stack_info=True)
            raise


    def get_audio_file_list(self, start_path):
        '''
        @brief Generates a csv containing full path for all audio files.

        @details Without a start path input, the top level directory MUST have been set.
        @details The csv file is created in the designated generated files directory.
        @details The csv has 2 columns, full file path for audio file and extension.

        @param start_path {str} Optional, the starting point of the directory walk.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        directory_counts = {}

        audio_count = 0
        album_count = 0
        artist_count = 0
        csv_count = 0
        csv_dir = GENERATED_FILES
        csv_filename = "found_audio_files.csv"
        dir_count = 0
        file_extension = None
        header_row = ["file path", "audio file type"]
        m4a_count = 0
        mp3_count = 0
        m3u_count = 0
        other_count = 0
        not_count = 0
        tot_count = 0
        txt_count = 0
        wma_count = 0

        if start_path is None:
            start_path = self._tld_path

        try:
            initial_depth = len(start_path.split(os.sep))

            # top down walk for files of the specified extension type
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
                        data.append([audio_file_path, file_extension])
                        audio_count += 1

                        if file_extension == AUDIO_EXTS[0]:
                            mp3_count += 1
                        elif file_extension == AUDIO_EXTS[1]:
                            m4a_count += 1
                        elif file_extension == AUDIO_EXTS[2]:
                            wma_count += 1
                    else:
                        if file_extension == ".csv":
                            csv_count += 1
                        elif file_extension == PLAYLIST_EXTS[0]:
                            m3u_count += 1
                        elif file_extension == ".txt":
                            txt_count += 1
                        else:
                            not_count += 1

                    tot_count += 1

            self.create_csv(csv_filename, data, csv_dir, header_row, 1)

            artist_count = directory_counts[0]
            album_count = directory_counts[1]
            dir_count = artist_count + album_count
            other_count = csv_count + txt_count + m3u_count + not_count

            print(f"Found {artist_count} artist directories")
            print(f"Found {album_count} album directories")
            print(f"Found {dir_count} total directories")

            print(f"Found {mp3_count} {AUDIO_TYPES[0]} files")
            print(f"Found {m4a_count} {AUDIO_TYPES[1]} files")
            print(f"Found {wma_count} {AUDIO_TYPES[2]} files")
            print(f"Found {audio_count} total audio files")

            print(f"Found {csv_count} csv files")
            print(f"Found {txt_count} text files")
            print(f"Found {m3u_count} m3u files")
            print(f"Found {not_count} unknown type files")
            print(f"Found {other_count} non-audio files")

            print(f"Found {tot_count} total files")

        except Exception:
            logger.exception("Exception getting files for {start_path}", stack_info=True)
            raise


    def get_ext_file_list(self, file_ext, start_path):
        '''
        @brief Wrapper for function that generates a csv containing full file path for an extension.

        @details Without a start path input, the top level directory MUST have been set.
        @details If file extension is not supplied, uses the preset audio types list.

        @param  file_ext {str} Optional, the file extension want file paths for.
        @param  start_path {str} Optional, the starting point of the directory walk.
        '''

        try:
            if start_path is None:
                start_path = self._tld_path

            if (file_ext):
                self.__ext_file_list(file_ext, start_path)
            else:
                for file_ext in AUDIO_TYPES:
                    self.__ext_file_list(file_ext, start_path)
        except Exception:
            logger.exception(f"Exception getting file list for files with {file_ext} for {start_path}", stack_info=True)
            raise


    def get_file_directory(self, start_path, file_name):
        '''
        @brief Finds the directory path of a file given its name and a starting search path.

        @param filename (str) The name of the file to find.
        @param start_path (str) The root directory to start from.
        @return dir_path {str} The directory path for file, None if not found.
        @exception  Exception A common baseclass exception to handle unforeseen errors.
        '''

        dir_path = None
        try:
            for root, dirs, files in os.walk(start_path):
                if file_name in files:
                    dir_path = root

        except Exception:
            logger.exception("Exception getting directory path for {file_name} and starting path {start_path}", stack_info=True)
            raise
        else:
            return dir_path


    def get_file_ext(self, file_path):
        '''
        @brief Returns the file type of audio file without leading period.

        @details Returns the file type using os library as opposed to getting it from audio metadata.

        @param file_path {str} The full audio file path.
        @return file_ext {str} The file type of audio file or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        file_ext = None

        try:
            if file_path:
                # get the file extension, don't care about the file name
                _, split_extension = os.path.splitext(file_path)
                # want the type, not the full extension with the period
                file_ext = split_extension[1:]

        except Exception:
            logger.exception("Exception getting file extension", stack_info=True)
            raise
        else:
            return file_ext


    def make_album_dir(self, artist_dirpath, album_dir):
        '''
        @brief Creates an album sub-directory in an artist directory.

        @details The album name for the directory is drawn from the metadata.
        @details The audio file(s) for the created album directory will moved into the created directory by another function.

        @param artist_dirpath {str} The absolute path artist directory the new album directory will be created in.
        @param album_dir {str} The sanitized & validated name of the album for new album directory.
        @exception OSError An os permission error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            music_dir = os.path.join(artist_dirpath, album_dir)
            self.make_dir(music_dir)

        except Exception:
            logger.exception(f"Exception creating music directory {music_dir}", stack_info=True)
            raise


    def make_dir(self, dir_path):
        '''
        @brief Creates a directory.

        @param dir_path {str} The path to create.
        @exception OSError An os permission error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            else:
                logger.info(f"{dir_path} already exists")
                return

        except Exception as e:
            if e.errno == errno.EACCES:
                logger.error(f"Exception: permission denied for creating {dir_path}", exc_info=True)
                raise OSError
            else:
                logger.exception(f"Exception creating {dir_path}", stack_info=True)
                raise


    def move_audio_file(self, file_path, destination_dir):
        '''
        @brief Moves an audio file to a new directory.

        @details The destination path must exist already.

        @param file_path {str} File path for audio file.
        @param destination_path {str} New directory for audio file.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        audio_file = os.path.basename(file_path)
        destination_path = os.path.join(destination_dir, audio_file)

        try:
            shutil.move(file_path, destination_path)

        except Exception:
            logger.exception(f"Exception moving {audio_file} from {os.path.dirname(file_path)} to {destination_dir}", stack_info=True)
            raise


    def path_info(self, file_path):
        '''
        @brief Creates export path for audio file conversions and normalizations.

        @details Creates export directory if it doesn't exist.

        @param file_path {str} The full file path for audio file.
        @return export_path {str} The export path, otherwise None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            export_dir = None
            export_name = None
            export_path = None

            input_path = Path(file_path)

            input_ext = input_path.suffix
            if input_ext.lower() not in AUDIO_EXTS:
                logger.warning(f"File {input_path} is not in {AUDIO_TYPES}")
                return None

            r'''
            Ubuntu file path:
            <anchor><mount point>/<usr>/<drive label>/<tld>/<artist dir>/<album dir>/<song file.ext> = 8 elements
            <anchor><mount point>/<usr>/<tld>/<artist dir>/<album dir>/<song file.ext> = 7 elements
            anchor is drive (always an empty string) + root (always a forward slash) Eg. "" + "/" = "/"
            mount point is either "home" (a hdd) or "media" (an usb)
            if mount point is media, then usr is immediately followed by drive label, then top level directory
            if mount point is home, then usr is immediately followed by top level directory

            Ubuntu from USB stick: "/media/gerald/Lexar/Music/38 Special/Special Forces/38 Special-Caught Up in You.mp3"
            anchor = "/", mount point = "media", usr = "gerald", drive label = "Lexar", tld = "Music", artist = "38 Special", album = "Special Forces", file = '38 Special-Caught Up in You.mp3"

            Ubuntu from hdd: "/home/gerald/Music/38 Special/Special Forces/38 Special-Caught Up in You.mp3"
            anchor = "/", mount point = "home", usr = "gerald", tld = "Music", artist = "38 Special", album = "Special Forces", file = '38 Special-Caught Up in You.mp3"

            Windows file path:
            <anchor><tld>\<artist dir>\<album dir>\<song file.ext> = 5 elements
            anchor is always a drive letter + colon + backslash Eg. C:\, H:\

            Windows from USB stick: "H:\Music\38 Special\Special Forces\38 Special-Caught Up in You.mp3"
            anchor = "H:\", tld = "Music", artist = "38 Special", album = "Special Forces", file = '38 Special-Caught Up in You.mp3"

            Windows from hdd: "C:\Music\38 Special\Special Forces\38 Special-Caught Up in You.mp3"
            anchor = "C:\", tld = "Music", artist = "38 Special", album = "Special Forces", file = '38 Special-Caught Up in You.mp3"

            I don't need anchor, mount point, usr, drive label, tld
            I always need artist dir, album dir, and song file
            '''

            # get the full parent w/o filename so I can start removing unnecessary path components
            input_path_parent = input_path.parent

            # remove the anchor (ie. / or H:\), have no use for it
            input_path_parts = input_path_parent.parts[1:]

            # using fixed storage path because will always know project structure
            export_dir = os.path.join(GENERATED_FILES, EXPORT_TLD)

            full_len = len(input_path_parts)
            artist_len = full_len - 2

            # iterate over last 2 elements, which will be artist and album directories
            for i in range(artist_len, full_len):
                export_dir = os.path.join(export_dir, input_path_parts[i])

            # get mp3 audio extension from package constants
            export_ext = AUDIO_EXTS[0]

            input_name = input_path.stem

            export_name = input_name + export_ext
            export_path = os.path.join(export_dir, export_name)

        except Exception:
            logger.exception(f"Exception getting export path {file_path}", stack_info=True)
            raise
        else:
            return export_path


    def remove_album_dir(self, start_path):
        '''
        @brief Removes empty album directories.

        @details Walks through top level directory to remove empty second level album directories contained in artist first level directories.
        @details Without a start path input, the top level directory MUST have been set.

        @param start_path {str} The starting point of the directory walk.
        @exception OSError An os permission error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
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

            logger.info(f"removed {dir_count} empty album directories")

        except Exception as e:
            if e.errno == errno.EACCES:
                logger.error(f"Exception: permission denied for deleting {artist_item_path}", exc_info=True)
                raise OSError
            else:
                logger.exception(f"Exception deleting {artist_item_path}", stack_info=True)
                raise


    def remove_pattern(self, start_path, file_pattern):
        '''
        @brief Removes file matching specified pattern.

        @details Walks through top level directory and removes files matching specified file pattern.
        @details Without a start path input, the top level directory MUST have been set.

        @param start_path {str} Optional, the starting point of the directory walk.
        @param file_pattern {str} The file pattern we want to delete.
        @exception OSError An os permission error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            if start_path is None:
                start_path = self._tld_path

            # top down walk for files of the specified pattern
            # want the directory path & file names so we can get full file path
            # don't care about the sub-directory names at all

            for dir_path, dir_names, file_names in os.walk(start_path):
                for file in file_names:
                    if fnmatch.fnmatch(file, file_pattern.lower()):
                        file_path = os.path.join(dir_path, file)
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")

        except Exception as e:
            if e.errno == errno.EACCES:
                logger.error(f"Exception: permission denied for deleting {file_path}", exc_info=True)
                raise OSError
            else:
                logger.exception(f"Exception deleting file {file_path}", stack_info=True)
                raise
