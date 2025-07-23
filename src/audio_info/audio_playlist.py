'''
@file audio_playlist.py
@brief Defines the audio playlist class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import logging
import os
from datetime import datetime
from pathlib import Path

# local modules
from src import _AUDIO_EXTS, _PLAYLIST_EXTS
from src.dir_processing import DirectoryProcessing
from src.generated_files import generated_files as _GENERATED_FILES

gc.enable()

_DELIMITER = ","

# @todo move these into src.__init__.py
# @todo figure out one time declaration for logging
# @todo the only thing that really changes is the log filename
# @tdo google search: python logging def for many modules
# @todo https://docs.python.org/3/library/logging.html
# https://docs.python.org/3/howto/logging.html#logging-advanced-tutorial
_DATETIME_FORMAT = "%Y-%m-%d_%H%M-%S"
_LOG_DIR = "logs"
_LOG_EXT = ".log"
_FILE_LOG_FORMAT = '%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s'

directory = DirectoryProcessing()

start_execution = datetime.now()
start_datetime = datetime.strftime(start_execution, _DATETIME_FORMAT)

log_filename = "playlist" + _LOG_EXT
log_filepath = os.path.join(_GENERATED_FILES, _LOG_DIR, log_filename)

logger = logging.getLogger(__name__)
# override the default logging level WARN to lowest level so we can log all level messages
logger.setLevel(logging.DEBUG)

# file handler logs debug level to log file only, no output to console
file_log_formatter = logging.Formatter(_FILE_LOG_FORMAT)
file_handler = logging.FileHandler(log_filepath, mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_log_formatter)

logger.addHandler(file_handler)


class AudioPlaylist():
    '''
    @brief Defines the base playlist processing used by project.
    '''

    def __init__(self):
        '''
        @brief Initialize the AudioPlaylist class.

        @details A basic class implementation with no instantiation parameters.

        @return AudioPlaylist {instance} An instance of the class.
        '''

        pass


    def get_audio_name(self, line):
        '''
        @brief Gets audio file name from a #EXTINF line

        @details The audio file extension may have changed from wma or m4a to mp3
        @details A  extinf tag containing line is in format: #EXTINF:N,<name>.<ext>,
        where N is length of song in seconds, or -1 or 0, and
        @details <ext> is one of mp3, m4a, or wma.
        @param line (str) Line of text read from m3u file containing a #EXTINF tag
        @return audio_file {str} Audio file name with extension, otherwise None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        audio = None

        try:
            index = line.find(_DELIMITER)
            if index != -1:
                input_audio = line[index + len(_DELIMITER):]
                # get the audio file name ext, may have to change it
                input_ext = os.path.splitext(os.path.basename(input_audio))[1]
                # wma and m4a files need mp3 extension
                if input_ext != _AUDIO_EXTS[0]:
                    input_stem = os.path.splitext(os.path.basename(input_audio))[0]
                    audio = input_stem + _AUDIO_EXTS[0]
                else:
                    audio = input_audio
            else:
                logger.warning(f"No file delimiter in {line}")

            return audio

        except Exception:
            logger.info(f"line: {line}")
            logger.critical("Exception", exc_info=True)


    def update_paths(self, tld_path, input_m3u):
        '''
        @brief Updates an old playlist relative pathing.

        @details Walks through a m3u playlist updating relative paths.
        @details The updated playlist is created in generated files directory.
        @details The new file is expected to be moved to the correct top level directory  for the relative paths.

        @param tld_path {str} The top level directory where playlist and music files are located.
        @param input_m3u {str} The full file path to playlist needing conversion.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        r'''
        see https://en.wikipedia.org/wiki/M3U
        My playlists are relative pathed (unlike windows pls files, which are absolute pathed).
        Because I use relative pathing, m3u files MUST live in the top level directory ie in Music
        So a proper relative path will be <artist>\<album>\<title>.mp3
        '''

        extheader = "#EXTM3U"
        extinf = "#EXTINF:"
        comment = "#:"

        try:
            # new m3u file gets created in generated files directory so can later be move to correct tld
            export_path = _GENERATED_FILES
            input_basename = os.path.basename(input_m3u)
            export_m3u = os.path.join(export_path, input_basename)

            with open(input_m3u, 'r') as infile, open(export_m3u, 'w') as outfile:
                for line in infile:
                    # if we dont have text, blank line is not copied to output
                    if line.strip():
                        if extheader in line:
                            # the ext header is simply copied over
                            outfile.write(line)
                        elif comment in line:
                            continue
                        elif extinf in line:
                            # get the audio file name, change ext to mp3 if needed
                            audio_file = self.get_audio_name(line.strip("\n"))
                            old_path = infile.readline().strip("\n")

                            if audio_file:
                                audio_file_path = directory.get_file_directory(tld_path, audio_file)
                            else:
                                logger.warning(f"unable to get audio file name from line: {line.strip("\n")} for relative path: {old_path} in {input_basename}")
                                continue

                            if audio_file_path:
                                found_file = Path(audio_file_path)
                                found_parts = found_file.parts
                                album = found_parts[-1]
                                artist = found_parts[-2]
                                relative_path = os.path.join(artist, album, audio_file) + "\n"
                                new_extinf = extinf + "0" + _DELIMITER + audio_file + "\n"
                                outfile.write(new_extinf)
                                outfile.write(relative_path)
                                outfile.write("\n")
                            else:
                                print(f"{audio_file} from {input_basename} not found in {tld_path}")
                                logger.info(f"{audio_file} from {input_basename} not found in {tld_path}")
                                continue

            logger.info(f"Updated {input_basename}\n")

        except Exception:
            logger.info(f"tld_path: {tld_path}, input_m3u: {input_m3u}")
            logger.critical("Exception", exc_info=True)


    def update_walk(self, tld_path):
        '''

        '''

        try:
            input_path = Path(tld_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # file is not mp3, m4a, or wma, so carry on to next file
                    if input_file_ext.lower() not in _PLAYLIST_EXTS:
                        continue

                    input_file_path = os.path.join(dir_path, file)
                    self.update_paths(dir_path, input_file_path)

            logger.info(f"Updated m3u files in {tld_path}\n")

        except Exception:
            logger.info(f"tld_path: {tld_path}")
            logger.critical("Exception", exc_info=True)