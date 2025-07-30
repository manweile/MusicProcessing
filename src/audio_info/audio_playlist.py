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
from pathlib import Path

# local modules
from src import AUDIO_EXTS
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging constants
from src import PLAYLIST_EXTS
from src.generated_files import GENERATED_FILES
from src.dir_processing import DirectoryProcessing

gc.enable()

directory = DirectoryProcessing()

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

_DELIMITER = ","


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
                if input_ext != AUDIO_EXTS[0]:
                    input_stem = os.path.splitext(os.path.basename(input_audio))[0]
                    audio = input_stem + AUDIO_EXTS[0]
                else:
                    audio = input_audio
            else:
                logger.warning(f"No file delimiter in {line}")

            return audio

        except Exception as e:
            logger.info(f"line: {line}")
            logger.critical(e, exc_info=True)


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
            export_path = GENERATED_FILES
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

        except Exception as e:
            logger.info(f"tld_path: {tld_path}, input_m3u: {input_m3u}")
            logger.critical(e, exc_info=True)


    def update_walk(self, tld_path):
        '''

        '''

        try:
            input_path = Path(tld_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # file is not mp3, m4a, or wma, so carry on to next file
                    if input_file_ext.lower() not in PLAYLIST_EXTS:
                        continue

                    input_file_path = os.path.join(dir_path, file)
                    self.update_paths(dir_path, input_file_path)

            logger.info(f"Updated m3u files in {tld_path}\n")

        except Exception as e:
            logger.info(f"tld_path: {tld_path}")
            logger.critical(e, exc_info=True)