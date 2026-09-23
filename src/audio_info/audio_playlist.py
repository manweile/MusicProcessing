'''
@class AudioPlaylist
@file audio_playlist.py
@author Gerald Manweiler

@brief Defines the audio playlist class.

@details Defines methods for reading and updating M3U playlists for the MusicProcessing project.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import gc                                                   # for garbage collection management
import logging                                              # for module logging
import os                                                   # for operating-system interfaces
from os import strerror                                     # for operating-system error messages
from pathlib import Path                                    # for object-oriented filesystem paths

# Local Module Methods
from src import add_module_handler                          # for module-specific logging handlers

# Local Module Constants
from src import AUDIO_EXTS                                  # for supported audio file extensions
from src import MP3_EXT                                     # for MP3 file extension
from src import PLAYLIST_EXTS                               # for supported playlist file extensions
from src.generated_files import GENERATED_PATH              # for generated file output paths

# Local Module Errors
from src import PlaylistError                               # for playlist processing failures

# Local Module Classes
from src.dir_processing import DirectoryProcessing          # for directory processing functionality

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

## @var directory
# @brief Directory processing instance.
# @details Provides directory processing functionality.
directory = DirectoryProcessing()

## @var DELIMITER
# @brief M3U field delimiter.
# @details Separates duration and file name values in EXTINF playlist entries.
DELIMITER = ","


class AudioPlaylist():
    '''
    @brief Defines the audio playlist processing class.

    @details Provides methods that update M3U playlist entries for the project's music collection.
    '''

    def __init__(self) -> None:
        '''
        @brief Initializes the AudioPlaylist class.

        @details Initializes an AudioPlaylist instance without instance-specific state.
        '''

        pass


    def get_audio_name(self, line: str) -> str:
        '''
        @brief Gets an audio file name from an EXTINF line.

        @details Converts WMA and M4A file extensions to MP3.<br>
        @details Parses EXTINF entries in the form `#EXTINF:N,<name>.<ext>`, where N is a song duration, -1, or 0.<br>
        @details Supports MP3, M4A, and WMA file extensions.

        @param line {str} Line of text read from an M3U file containing an EXTINF tag.
        @return audio {str} Audio file name with extension.

        @exception PlaylistError Indicates an error occurred in playlist class.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            index = line.find(DELIMITER)

            if index != -1:
                input_audio = line[index + len(DELIMITER):]

                # get the audio file name ext, may have to change it
                input_ext = os.path.splitext(os.path.basename(input_audio))[1]

                # wma and m4a files need mp3 extension
                if input_ext != AUDIO_EXTS[0]:
                    input_stem = os.path.splitext(os.path.basename(input_audio))[0]
                    audio = input_stem + MP3_EXT
                else:
                    audio = input_audio
            else:
                logger.exception(f"PlaylistError no file delimiter in {line}", stack_info=True)
                raise PlaylistError(f"PlaylistError no file delimiter in {line}")

        except PlaylistError as p_error:
            raise p_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting audio name from {line}", stack_info=True)
            raise e_error
        else:
            return audio


    def update_paths(self, tld_path: str, input_m3u: str) -> None:
        '''
        @brief Updates an old playlist relative pathing.

        @details Updates relative paths in an M3U playlist.<br>
        Creates the updated playlist in the generated-files directory.<br>
        Expects the updated playlist to be moved to the music top-level directory.

        @note see https://en.wikipedia.org/wiki/M3U<br>
        My playlists are relative pathed (unlike windows pls files, which are absolute pathed).<br>
        Because I use relative pathing, m3u files MUST live in the top level directory ie in Music<br>
        So a proper relative path will be artist/album/title.mp3

        @param tld_path {str} The top level directory where playlist and music files are located.
        @param input_m3u {str} The full file path to playlist needing conversion.

        @exception OSError A system related error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        extheader = "#EXTM3U"
        extinf = "#EXTINF:"
        comment = "#:"

        try:
            # verify m3u input
            _, input_file_ext = os.path.splitext(input_m3u)
            if input_file_ext.lower() not in PLAYLIST_EXTS:
                logger.exception(f"PlaylistError input file {input_m3u} is not a playlist", stack_info=True)
                raise PlaylistError(f"PlaylistError input file {input_m3u} is not a playlist")

            # new m3u file gets created in generated files directory so can later be move to correct tld
            export_path = GENERATED_PATH
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
                            audio_file_path = directory.get_file_directory(tld_path, audio_file)

                            if audio_file_path:
                                found_file = Path(audio_file_path)
                                found_parts = found_file.parts
                                album = found_parts[-1]
                                artist = found_parts[-2]
                                relative_path = os.path.join(artist, album, audio_file) + "\n"
                                new_extinf = extinf + "0" + DELIMITER + audio_file + "\n"
                                outfile.write(new_extinf)
                                outfile.write(relative_path)
                                outfile.write("\n")
                            else:
                                logger.warning(f"{audio_file} from {input_basename} not found in {tld_path}")
                                continue

        except OSError as os_error:
            logger.error(f"OSError {(strerror(os_error.errno))} writing data from {input_m3u} to {export_m3u}", exc_info=True)
            raise os_error
        except PlaylistError as p_error:
            raise p_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} updating playlist tld_path: {tld_path}, input_m3u: {input_m3u}", stack_info=True)
            raise e_error
        else:
            logger.info(f"Updated {input_basename}\n")


    def update_walk(self, tld_path: str) -> None:
        '''
        @brief Updates playlists relative pathing.

        @details Finds M3U playlists beneath the top-level directory and updates their relative paths.

        @param tld_path {str} The top level directory where playlist and music files are located.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            input_path = Path(tld_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # file is not m3u, carry on to next file
                    if input_file_ext.lower() not in PLAYLIST_EXTS:
                        continue

                    input_file_path = os.path.join(dir_path, file)
                    self.update_paths(dir_path, input_file_path)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} updating m3u files in tld_path: {tld_path}", stack_info=True)
            raise e_error
