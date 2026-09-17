'''
@class AudioMetadata
@file audio_metadata.py
@author Gerald Manweiler

@brief Defines the audio metadata class.

@details AudioMetadata class which encapsulates the functionality for handling and processing audio metadata across various audio file formats.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import fnmatch                                              # for filename pattern matching
import gc                                                   # for garbage collection
import inspect                                              # for inspecting live objects
import json                                                 # for JSON handling
import logging                                              # for logging
import os                                                   # for operating system interfaces
import re                                                   # for regular expressions
import shutil                                               # for high-level file operations
import sys                                                  # for system-specific parameters and functions
from json import JSONDecodeError                            # for handling JSON decode errors
from pathlib import Path                                    # for object-oriented filesystem paths
from shutil import ExecError                                # for handling shutil execution errors

# Third Party Modules
import mutagen                                              # for audio metadata handling
import pathvalidate                                         # for validating filesystem paths
from mutagen import FileType                                # for handling different audio file types
from mutagen.asf import ASF                                 # for handling ASF audio files
from mutagen.asf import ASFTags                             # for handling ASF tags
from mutagen.flac import FLAC                               # for handling FLAC audio files
from mutagen.flac import VCFLACDict                         # for handling FLAC dictionaries
from mutagen.id3 import APIC                                # for handling ID3 APIC frames
from mutagen.id3 import ID3                                 # for handling ID3 tags
from mutagen.id3 import ID3TimeStamp                        # for handling ID3 timestamps
from mutagen.mp3 import MP3                                 # for handling MP3 audio files
from mutagen.mp4 import MP4                                 # for handling MP4 audio files
from mutagen.mp4 import MP4FreeForm                         # for handling MP4 freeform atoms
from mutagen.mp4 import MP4Tags                             # for handling MP4 tags
from mutagen._util import MutagenError                      # for handling mutagen errors
from pathvalidate.error import ValidationError              # for handling path validation errors
from tqdm import tqdm                                       # for displaying progress bars

# Local Module Methods
from src import add_module_handler                          # for adding module-specific logging handlers

# Local Module Constants
from src import ASF_TYPE                                    # for ASF audio file type
from src import FLAC_TYPE                                   # for FLAC audio file type
from src import MP4_TYPE                                    # for MP4 audio file type
from src import MP3_TYPE                                    # for MP3 audio file type
from src import AUDIO_EXTS                                  # for audio file extensions
from src import AUDIO_FILES                                 # for audio file paths
from src import FOLDER_ART                                  # for folder artwork paths
from src import FLAC_EXT                                    # for FLAC file extension
from src import M4A_EXT                                     # for M4A file extension
from src import MP3_EXT                                     # for MP3 file extension
from src import WMA_EXT                                     # for WMA file extension

# Local Module Errors
from src import MetadataTypeError                           # for handling metadata type errors
from src import MusicProcessingError                        # for handling music processing errors
from src import PathInfoError                               # for handling path info errors

# Local Module Classes
from src.audio_normalize import AudioNormalization          # for audio normalization functionality
from src.dir_processing import DirectoryProcessing          # for directory processing functionality
from src.subprocess_utils import SubprocessUtilities        # for subprocess utility functionality

gc.enable()

## @var logger
# @brief the logger instance for module
# @details sets the logger name to module name
logger = logging.getLogger(__name__)

## @var basename
# @brief name for logger file handler log file
# @details gets the module file name
basename = os.path.basename(__file__)

add_module_handler(logger, basename)

## @var directory
# @brief instance of DirectoryProcessing class
# @details used for accessing class functionality
directory = DirectoryProcessing()

## @var normalization
# @brief instance of AudioNormalization class
# @details used for accessing class functionality
normalization = AudioNormalization()

## @var subprocess_utils
# @brief instance of SubprocessUtilities class
# @details used for accessing class functionality
subprocess_utils = SubprocessUtilities()

## @var TPOS
# @brief ID3 disc of set tag
# @details used to set TPOS metadata
TPOS = "TPOS"

## @var TYER
# @brief ID3 release year tag
# @details used to set TYER metadata
TYER = "TYER"

## @var GEN_KEYS
# @brief the set of ffmpeg generic metadata keys for copying to converted & normalized files
# @details these keys correspond to what Windows displays as file information in File Explorer
# @details included for reference but not actually used
GEN_KEYS = {
    'album',                # using, must have              ID3v2.3 mapping: TALB
    'album_artist',         # using, must have              ID3v2.3 mapping: TPE2
    'artist',               # using, must have              ID3v2.3 mapping: TPE1
    'comment',              # not interested                ID3v2.4 mapping: COMM   doesn't exist in ID3v2.3
    'compilation',          # not interested                ID3v2.4 mapping: TCMP   doesn't exist in ID3v2.3
    'composer',             # using, nice to have           ID3v2.3 mapping: TCOM
    'copyright',            # using, nice to have           ID3v2.3 mapping: TCOP
    'date',                 # using, must have              ID3v2.4 mapping: TDRC   doesn't exist in ID3v2.3
    'disc',                 # using, must have              ID3v2.3 mapping: TPOS
    'encoder',              # not interested                ID3v2.3 mapping: TSSE
    'encoded_by',           # not interested                ID3v2.3 mapping: TENC
    'genre',                # using, must have              ID3v2.3 mapping: TCON
    'language',             # not interested                ID3v2.3 mapping: TLAN
    'lyrics',               # not interested                ID3v2.3 mapping: USLT
    'originalyear',         # using, nice to have           ID3v2.3 mapping: TORY
    'performer',            # not interested                ID3v2.3 mapping: TPE3
    'publisher',            # using, nice to have           ID3v2.3 mapping: TPUB
    'title',                # using, must have              ID3v2.3 mapping: TIT2
    'track'                 # using, nice to have           ID3v2.3 mapping: TRCK
}

## @var FLAC_KEYS
# @brief the set of generic FLAC metadata keys
# @details the FLAC keys used for mapping to windows display compatible metadata
FLAC_KEYS = {
    'album': 'ALBUM',
    'album_artist': 'ALBUMARTIST',
    'artist': 'ARTIST',
    'composer': 'COMPOSER',
    'copyright': 'COPYRIGHT',
    'date': 'DATE',
    'disc': 'DISCNUMBER',
    'genre': 'GENRE',
    'originalyear': 'ORIGINALYEAR',
    'publisher': 'PUBLISHER',
    'title': 'TITLE',
    'track': 'TRACKNUMBER',
    'year': 'YEAR'
}

## @var FLAC_TIME_KEYS
# @brief FLAC time keys
# @details used to set TYER metadata
FLAC_TIME_KEYS = {
    'DATE',                                                # preferred key
    'YEAR',
    'ORIGINALYEAR'
}

## @var MP3_KEYS
# @brief the set of generic ID3v2.3 (mp3) metadata keys
# @details the ID3 keys used for mapping to windows display compatible metadata
MP3_KEYS = {
    'album': 'TALB',
    'album_artist': 'TPE2',
    'artist': 'TPE1',
    'composer': 'TCOM',
    'copyright': 'TCOP',
    'date': 'TYER',
    'disc': 'TPOS',
    'genre': 'TCON',
    'originalyear': 'TORY',                                 # convert to TYER
    'publisher': 'TPUB',
    'title': 'TIT2',
    'track': 'TRCK',
    'year': 'TYER',
    'originaldate': 'TDOR',                                 # ID3v2.4 field to ID3v2.3 TYER
    'release_date': 'TDRC',                                 # ID3v2.4 field convert YYYY portion to ID3v2.3 TYER
    'custom_original_year': 'TXXX=originalyear'             # ID3 user defined original year field convert to ID3v2.3 TYER
}

## @var MP3_TIME_KEYS
# @brief ID3 time keys
# @details used to set TYER metadata
MP3_TIME_KEYS = {
    'TYER',                                                 # preferred key
    'TORY',
    'TDRC',
    'TDOR',
    'TXXX=originalyear'
}

## @var M4A_KEYS
# @brief the set of generic MP4 (m4a) metadata keys
# @details the MP4 keys used for mapping to windows display compatible metadata
M4A_KEYS = {
    'album': '\xa9alb',
    'album_artist': 'aART',
    'artist': '\xa9ART',
    'composer': '\xa9wrt',
    'copyright': 'cprt',
    'date': '\xa9day',
    'disc': 'disk',
    'genre': '\xa9gen',
    'originalyear': '----:com.apple.iTunes:originalyear',   # using iTunes field, mp4 does not have \xa9ory
    'publisher': '----:com.apple.iTunes:LABEL',             # using iTunes field, mp4 does not have \xa9pub
    'title': '\xa9nam',
    'track': 'trkn'
}

## var M4A_TIME_KEYS
# @brief MP4 time keys
# @details used to set TYER metadata
M4A_TIME_KEYS = {
    '\xa9day',                                              # preferred key
    '----:com.apple.iTunes:originalyear'
}

## @var WMA_KEYS
# @brief the set of generic ASF (wma) metadata keys
# @details the ASF keys used for mapping to windows display compatible metadata
WMA_KEYS = {
    'album': 'WM/AlbumTitle',
    'album_artist': 'WM/AlbumArtist',
    'artist': 'Author',
    'composer': 'WM/Composer',
    'copyright': 'Copyright',
    'date': 'WM/Year',
    'disc': 'WM/PartOfSet',
    'genre': 'WM/Genre',
    'originalyear': 'WM/OriginalReleaseYear',
    'publisher': 'WM/Publisher',
    'title': 'Title',
    'track': 'WM/TrackNumber'
}

## var WMA_TIME_KEYS
# @brief ASF time keys
# @details used to set TYER metadata
WMA_TIME_KEYS = {

    'WM/Year',                                              # preferred key
    'WM/OriginalReleaseYear'
}


class AudioMetadata():
    '''
    @brief Metadata handling class.

    @details Provides methods for handling and updating audio file metadata across different formats.
    '''

    def __init__(self) -> None:
        '''
        @brief Initializes the AudioMetadata class.

        @details A basic class implementation with no instantiation parameters.

        @return AudioMetadata {instance} An instance of the class.
        '''

        pass


    def __update_id3(self, date_values: set[str], id3_tags: dict) -> dict:
        '''
        @brief Updates tags dictionary with newest year value and ands default disc value if needed.

        @details Updates the ID3 tags dictionary with the newest year value from the set of date strings
        and ensures a default disc value is set if not already present.

        @param date_values ({str}) Set of unique YYYY date strings.
        @param id3_tags {dict} Source ID3 tags.
        @return id3_tags {dict} Updated ID3 tags.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            # want newest date from unique dates found
            if date_values:
                max_date = max(date_values, key=int)
                id3_tags[TYER] = max_date

            if TPOS not in id3_tags:
                id3_tags[TPOS] = "1/1"

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} updating id3 tags", stack_info=True)
            raise e_error
        else:
            return id3_tags


    def convert_file(self, file_path: str, show_spinner: bool = True) -> None:
        '''
        @brief Converts a wma, m4a or mp3 audio file to mp3 audio file, using ffmpeg directly.

        @details Converts flac, m4a, mp3 & wma files to mp3 files with ID3v2.3 tags using FFMPEG.<br>
        Calling function MUST supply path to an existing valid audio file with metadata.<br>
        The supplied audio file MUST have co-located Folder.jpg album art.

        @param file_path {str} The path for audio file to be converted.
        @param show_spinner {bool} Show spinner flag.

        @exception MetadataTypeError Indicates a non-standard metadata type was encountered.
        @exception MusicProcessingError A generic music processing error occurred.
        @exception PathInfoError Indicates directory_processing.path_info function returned None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        '''
        album directories<br>
        When an artist directory does not contain album directories for all of its audio files,
        run create_album_dirs function to ensure there are album directories for every audio file.<br>
        '''

        '''
        album art<br>
        Manually review extant album art files(s), and if possible, create a Folder.jpg then move it to appropriate album directory.<br>
        If there is no extant album art file(s), but audio files have embedded art, run extract_art_function to extract it as Folder.jpg file.<br>
        Finally run set_album_art function to ensure a Folder.jpg exists in each album directory.<br>
        '''

        '''
        metadata transfer<br>
        I dont want every possible tag, just the subset that Windows will display AND are ID3v2.3 format.<br>
        Comments are ASF/FLAC/ID3v2.3/MP4, but MusicBrainz/MP3Tag/puddletag have difficulty displaying comments properly,
        so passing on transferring comment metadata.<br>
        Compilation is not ID3v2.3, so passing on transferring compilation metadata too.<br>
        Date info is most problematic part of metadata.<br>
        ASF/FLAC/ID3v2.3/MP4 have multiple date type tags, the data types could be a full ISO date, or could just be a 4 digit year string.<br>
        Format any found date values to YYYY and map them to ID3v2.3 TYER field. Refer to the `map_*_tags` functions for details.<br>
        I have manually edited all audio files without date to have 1963 as default.
        '''

        '''
        This ffmpeg cli command is for converting audio files to mp3 format, wiping out any existing metadata.

        ffmpeg -hide_banner -i `file_path` -vn -map_metadata -1 -codec:a libmp3lame -id3v2_version 3 -b:a 128198<br>
        -hide_banner                                        reduce output clutter<br>
        -i file_path                                        the path to the audio file<br>
        -vn -map_metadata -1                                -vn drops video stream and -map_metadata -1 drops all text metadata<br>
        -codec:a libmp3lame                                 -codec:a libmp3lame sets audio codec for mp3<br>
        -id3v2_version 3                                    known bug, MUST specify id3v2 version, else will get ID3v2.4<br>
        -b:a 128198                                         ffmpeg will downgrade bitrate if you don't set it
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            # get export path for converted files, will return None for an invalid audio extension
            export_path = directory.path_info(file_path)

            if export_path is None:
                logger.exception(f"PathInfoError with file {file_path} returned None", stack_info=True)
                raise PathInfoError(f"PathInfoError with file {file_path} returned None")
            else:
                directory.make_dir(os.path.dirname(export_path))

            input_path_parent = os.path.dirname(file_path)
            cover = os.path.join(input_path_parent, FOLDER_ART)

            if not os.path.exists(cover):
                logger.warning(f"album directory {input_path_parent} does not contain a {FOLDER_ART} file.")
                raise MusicProcessingError(f"album directory {input_path_parent} does not contain a {FOLDER_ART} file.")

            # export format is always mp3
            export_format = MP3_EXT.removeprefix(".")

            input_format = os.path.splitext(file_path)[1].lower()[1:]
            input_path_stem = os.path.splitext(os.path.basename(file_path))[0]
            data.append(f"Beginning conversion on {input_path_stem} from {input_format} to {export_format}")
            data.append(f"Source directory path: {input_path_parent}")

            metadata_type = self.get_metadata_type(file_path)

            if metadata_type is None:
                logger.error(f"MetadataTypeError with file: {os.path.basename(file_path)} returned None", exc_info=True)
                raise MetadataTypeError(f"MetadataTypeError with file: {os.path.basename(file_path)} returned None")

            input_tags = self.get_any_tags(file_path)

            if input_tags:
                if metadata_type == FLAC_TYPE:
                    tags = self.map_flac_tags(input_tags)
                elif metadata_type == MP3_TYPE:
                    tags = self.map_mp3_tags(input_tags)
                elif metadata_type == MP4_TYPE:
                    tags = self.map_m4a_tags(input_tags)
                elif metadata_type == ASF_TYPE:
                    tags = self.map_wma_tags(input_tags)
            else:
                tags = None

            # get the input file info - want bitrate so can preserve the quality in exported file
            media_info = self.get_media_info(file_path)
            bitrate = media_info['bit_rate']

            command = [
                "ffmpeg",
                "-hide_banner",
                "-i", file_path,
                "-vn", "-map_metadata", "-1",
                "-codec:a", "libmp3lame",
                "-id3v2_version", "3",
                "-b:a", str(bitrate)
            ]

            # cycle through tags dictionary and add metadata directly to command string
            if tags is not None:
                if not isinstance(tags, dict):
                    logger.exception("Tags must be a dictionary.", stack_info=True)
                    raise MusicProcessingError("Tags must be a dictionary.")
                else:
                    for key, value in tags.items():
                        command.extend(['-metadata', '{0}={1}'.format(key, value)])

            # specify the output with overwrite flag, always want clean output
            command.extend([export_path, '-y'])

            success_msg = None
            success_msg = subprocess_utils.spinner_popen_pipe(export_path, command, show_spinner)
            if success_msg is not None:
                data.append(success_msg)

            # Add album art
            mp3_file = MP3(export_path, ID3=ID3, v2_version=3)
            # encoding & type = 3 specifies UTF-8 & front cover
            with open(cover, "rb") as album_art_file:
                mp3_file.tags.add(
                    APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,
                        desc="Cover",
                        data=album_art_file.read()
                    )
                )
            mp3_file.save(v2_version=3)

            directory.create_txt(txt_filename, data)

        except MetadataTypeError as mt_error:
            raise mt_error
        except MusicProcessingError as mp_error:
            raise mp_error
        except PathInfoError as pi_error:
            raise pi_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} converting {file_path} to {export_path}", stack_info=True)
            raise e_error


    def convert_walk(self, start_path: str, file_pattern: str, show_spinner: bool = True) -> None:
        '''
        @brief Converts all audio files found in specified path to mp3 format.

        @details Calling functions MUST verify valid start path.<br>
        If file pattern not specified, processes all valid audio files.<br>
        Otherwise must be a valid audio file extension like '.mp3', '.m4a', '.wma', or '.flac'.

        @param start_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to transform.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        input_file_ext = None

        try:
            # calling function is NOT responsible for pattern validity
            if file_pattern and file_pattern not in AUDIO_EXTS:
                logger.warning(f"Pattern {file_pattern} is not for a valid audio file")
                return

            input_path = Path(start_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # file is not flac, mp3, m4a, or wma, so carry on to next file
                    if input_file_ext.lower() not in AUDIO_EXTS:
                        continue
                    elif file_pattern:
                        if not fnmatch.fnmatch(input_file_ext.lower(), file_pattern.lower()):
                            continue

                    input_file_path = os.path.join(dir_path, file)
                    self.convert_file(input_file_path, show_spinner)

        except Exception as e_error:
            if file_pattern:
                exc_msg = f"Exception {type(e_error).__name__} walking {start_path} to convert {file_pattern} audio files to mp3"
            else:
                exc_msg = f"Exception {type(e_error).__name__} walking {start_path} to convert audio files to mp3"

            logger.exception(exc_msg, stack_info=True)
            raise e_error


    def create_album_dirs(self, start_path: str) -> None:
        '''
        @brief Creates a album sub-directories in artist directories.

        @details Calling functions MUST verify valid start path.<br>
        Creates the album sub directory for the artist if needed.<br>
        The album name for the directory is drawn from the album metadata field, and will be sanitized to Windows OS values.<br>
        Audio files will be moved into their respective album directories.<br>
        A csv report named after the function (`create_album_dirs`) containing all audio file paths,
        album metadata values and sanitized album directory names will be created.<br>

        @param start_path {str} The tld holding music files.

        @exception ValidationError A pathlib module validation error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        csv_filename = inspect.currentframe().f_code.co_name
        header_row = ["audio file path", "album metadata", "sanitized album directory"]

        try:
            # get the artist dirs under tld
            tld_content = os.listdir(start_path)
            len_tld_content = len(tld_content)

            tld_bar = tqdm(desc=f'Processing {start_path} content', total=len_tld_content, unit=' items')

            # top level directory consists of artist directories, playlist files and couple other sundry files
            for tld_item in tld_content:
                # update the progress bar before processing artist directory
                # else we will have a mismatch in the bar processed/total display
                # we only want artist directories, playlist/sundry files don't count
                tld_item_path = os.path.join(start_path, tld_item)
                if os.path.isfile(tld_item_path):
                    tld_bar.update(1)
                    continue

                # since we skip tld items that are files,
                # now we need to check tld items that are directories
                artist_content = os.listdir(tld_item_path)
                # want to know if we have any empty artist directories so we can deal with them later
                if os.path.isdir(tld_item_path) and not artist_content:
                    logger.info(f"{tld_item_path} is an empty artist directory")
                    tld_bar.update(1)
                    continue

                # now we can look at what's in the current artist 1st level directory
                for artist_item in artist_content:

                    # we don't care about existing album 2nd level dirs
                    artist_item_path = os.path.join(tld_item_path, artist_item)
                    if os.path.isdir(artist_item_path):
                        continue

                    # if we find an audio file, we need a album sub-directory for it
                    # as artist dirs are supposed to only contain album sub dirs
                    if os.path.isfile(artist_item_path):
                        _, file_ext = os.path.splitext(artist_item)

                    # audio files are supposed to be in an album sub dir
                    if file_ext.lower() in AUDIO_EXTS:
                        audio_file = artist_item_path
                        # using ffprobe function cause it is audio file type agnostic
                        file_media_tags = self.get_media_tags(audio_file)
                    else:
                        # we found a non audio file
                        continue

                    if file_media_tags and 'album' in file_media_tags.keys():
                        # the album metadata should have had all / removed manually,
                        # but do replace anyways, it would wreak havoc by creating nested dirs
                        album = file_media_tags['album'].replace("/", "-")

                        # sanitize because the metadata might have characters invalid for directory names
                        # platform is "Windows" because it is more restrictive (therefore os universal),
                        # the characters \, :, *, ?, ", <, >, | will be replaced by "-"
                        # refer to https://pathvalidate.readthedocs.io/en/latest/pages/reference/function.html#pathvalidate.sanitize_filename
                        sanitized_album_name = pathvalidate.sanitize_filepath(album, replacement_text="-", platform="Windows", validate_after_sanitize=True)

                        data.append([audio_file, file_media_tags['album'], sanitized_album_name])

                        # make the album sub directory is REQUIRED before moving the audio file
                        album_path = os.path.join(tld_item_path, sanitized_album_name)
                        directory.make_dir(album_path)

                        # now transfer the audio file to new album directory
                        file_path = os.path.basename(audio_file)
                        destination_path = os.path.join(album_path, file_path)
                        shutil.move(audio_file, destination_path)

                    else:
                        logger.warning(f"{audio_file} is missing album metadata")
                        continue

                tld_bar.update(1)

            tld_bar.close()
            directory.create_csv(csv_filename, data, None, None, header_row, 0)

        except ExecError as exc_error:
            logger.exception(f"ExecError moving {file_path} to {destination_path}", exc_info=True)
            raise exc_error
        except ValidationError as v_error:
            logger.exception(f"ValidationError sanitizing album metadata {album}", stack_info=True)
            raise v_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} creating sub-dirs for {start_path}", stack_info=True)
            raise e_error


    def get_any_tags(self, file_path: str) -> ASFTags | ID3 | MP4Tags | VCFLACDict:
        '''
        @brief Gets tags for any type of audio file.

        @details Any type means flac, m4a, mp3, or wma files.

        @param file_path {str} The full path to audio file.
        @return tags {object} Tag object (one of ASFTags, ID3, MP4Tags, or VCFLACDict) holding audio file tags or None.

        @exception ValueError A function or operation received an argument of correct type but inappropriate value.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            tags = None
            audio_file = self.load_any_file(file_path)

            if audio_file is not None:
                tags = audio_file.tags

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting metadata type for file: {file_path}", stack_info=True)
            raise e_error
        else:
            return tags


    def get_media_info(self, file_path: str) -> dict:
        '''
        @brief Returns dictionary with media info.

        @details Uses ffprobe to get all media info from any valid audio file.<br>
        This def replaces the native pydub mediainfo function.<br>
        The file_path MUST be for a valid audio file.

        @param file_path {str} The full path to audio file.
        @return media_info {dict} Media info (codec, duration, size, bitrate...) from filepath.

        @exception re.error An error occurred processing a regular expression with re module.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        r'''
        This ffprobe cli WILL include 'comment' = 'Cover (front)' if the file has embedded album art in the TAG inner dict.<br>
        A mutagen call to ASF/FLAC/ID3/MP4, would place WM\Picture, METADATA_BLOCK_PICTURE, APIC, or covr AND include the byte data for the art.<br>
        This is because show_streams means ffprobe sees the art data as the video stream metadata instead.

        ffprobe -v error -show_format -show_streams `file_path`<br>
        -v quiet          reduce output clutter<br>
        -show_format      get high level details of media file<br>
        -show_streams     gets all information about each media stream in the input<br>
        '''

        r'''
        output format from popen_pipe<br>
        Note that on Windows, the line endings are \r\n, whereas on Linux it is just \n)<br>
        DISPOSITION: and TAG: are inner dicts

        [STREAM]\r\nkey=value\r\n...\r\nDISPOSITION:key=value\r\n...\r\nDISPOSITION:key=value\r\n[/STREAM]\r\n<br>
        [FORMAT]\r\nkey=value\r\n...\r\nTAG:key=value\r\n...\r\nTAG:key=value\r\n[/FORMAT]<br>

        regex command to parse out data:<br>
        `rgx = re.compile(r"(?:(?P<inner_dict>.*?):)?(?P<key>.*?)\=(?P<value>.*?)$")`

        r - so don't have to use escaping (\\)

        1st RE (Regular Expression) - to get an inner dict<br>
        (?:(?P<inner_dict>.*?):)<br>
        Question mark colon is a non-capturing version of regular parentheses.<br>
        Matches whatever regular expression is inside the parentheses - in this case, the (?P<inner_dict>.*?).<br>
        The substring matched by the group cannot be retrieved after performing a match or referenced later in the pattern.<br>
        [STREAM], [/STREAM], [FORMAT], and [/FORMAT] never match, so they get ignored.

        (?P<inner_dict>.*?):<br>
        inner_dict is symbolic group name, must be valid python identifier.<br>
        Period asterisk question mark means match any char except newline, as few as possible characters will be matched.<br>
        The colon matches the token after a inner_dict name (as in DISPOSITION:)<br>
        DISPOSITION: and TAG: are inner dicts, they get returned.

        2nd RE - get the key<br>
        ?(?P<key>.*?)<br>
        question mark causes the resulting RE to match 0 or 1 repetitions of the preceding RE

        (?P<key>.*?):<br>
        Question mark P <key> where key is the symbolic group name.<br>
        Period asterisk question mark means match any char except newline, as few as possible characters will be matched<br>

        3rd RE - get the value<br>
        \=(?P<value>.*?)<br>
        slash equal escapes the equal sign, which is the token used in key/value pairs<br>
        period asterisk question mark means match any char except newline, as few as possible characters will be matched

        $<br>
        Dollar anchors a match to end of search string.
        '''

        try:
            media_info = None

            command = [
                "ffprobe",
                "-v", "error",
                "-show_format",
                "-show_streams",
                file_path
            ]

            output = subprocess_utils.popen_pipe(command)

            rgx = re.compile(r"(?:(?P<inner_dict>.*?):)?(?P<key>.*?)\=(?P<value>.*?)$")
            media_info = {}

            # Remove carriage return characters on Windows to normalize line endings
            if sys.platform == 'win32':
                output = output.replace("\r", "")

            # Split the output into lines and process each line individually
            for line in output.split("\n"):
                mobj = rgx.match(line)

                if mobj:
                    # Extract the inner dictionary, key, and value tokens specified in the regex pattern from the regex match object
                    inner_dict, key, value = mobj.groups()

                    if inner_dict:
                        try:
                            media_info[inner_dict]
                        except KeyError:
                            media_info[inner_dict] = {}
                        media_info[inner_dict][key] = value
                    else:
                        media_info[key] = value

        except re.error as re_error:
            logger.error(f"Regex error processing {output}", exc_info=True)
            raise re_error
        except Exception as e_error:
            logger.exception(f"Exception getting media info for file {file_path}")
            raise e_error
        else:
            return media_info


    def get_media_info_walk(self, start_path: str, file_pattern: str) -> None:
        '''
        @brief Gets media info (codec, duration, size, bitrate...) for audio files and saves to file.

        @details Wrapper function that uses ffprobe call in `get_media_info` to walk through the directory tree
        and get media information for audio files.<br>
        The collected information is stored in a list and can be saved to a file.

        @param start_path {str} The starting point of the directory walk.
        @param file_pattern {str} The audio file pattern we want to get tags from.

        @exception ValueError A function or operation received an argument of correct type but inappropriate value.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            for dir_path, _, file_names in os.walk(start_path):
                # the tld Music does contain files, but not audio files
                if dir_path == start_path:
                    continue

                for file in file_names:
                    input_file, input_file_ext = os.path.splitext(file)

                    # file is not mp3, m4a, or wma, so carry on to next file
                    if input_file_ext.lower() not in AUDIO_EXTS:
                        continue
                    elif file_pattern:
                        if not fnmatch.fnmatch(input_file_ext.lower(), file_pattern.lower()):
                            continue

                    input_file_path = os.path.join(dir_path, file)

                    media_info = self.get_media_info(input_file_path)
                    if media_info:
                        file_msg = f"\n{input_file_path} has {len(media_info)} keys"
                        data.append(file_msg)
                        for key, value in media_info.items():
                            if isinstance(value, dict):
                                continue
                            else:
                                data.append(f"key: {key}, value: {value}")
                    else:
                        logger.error(f"ValueError getting info for audio file: {input_file_path} returned None", exc_info=True)
                        raise ValueError(f"ValueError getting info for audio file: {input_file_path} returned None")

            directory.create_txt(txt_filename, data)

        except ValueError as v_error:
            raise v_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting media info for file {input_file_path}")
            raise e_error


    def get_media_tags(self, file_path: str) -> dict:
        '''
        @brief Gets media tags.

        @details Uses ffprobe to get tags from any valid audio file.

        @param file_path {str} The full path to audio file.
        @return media_tags {dict} Media tags from filepath.

        @exception ValueError A function or operation received an argument of correct type but inappropriate value.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        '''
        Note that this ffprobe cli, unlike the general media info cli: ffprobe -v quiet -show_format -show_streams file_path,
        will NOT insert 'comment' = 'Cover (front)' in the tags dictionary if the audio file has embedded art.<br>
        This cli will only return textual audio metadata.

        ffprobe -v -of json -show_entries format_tags `file_path`<br>
        -v quiet reduce console clutter<br>
        -of json output in json format<br>
        -show_entries format_tags we only care about tags<br>
        `file_path` the path to the audio file<br>
        '''

        try:
            media_tags = None

            command = [
                "ffprobe",
                "-v", "error",
                "-of", "json",
                "-show_entries", "format_tags",
                file_path
            ]
            result = subprocess_utils.subprocess_run(command)
            data = json.loads(result.stdout)

            if "format" in data and "tags" in data["format"]:
                media_tags = data["format"]["tags"]

        except JSONDecodeError as jd_error:
            logger.error("JSONDecodeError decoding JSON output from ffprobe", exc_info=True)
            raise jd_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting media tags for file {file_path}", stack_info=True)
            raise e_error
        else:
            return media_tags


    def get_metadata_type(self, file_path: str) -> str:
        '''
        @brief Returns the metadata type of any audio file.

        @param file_path {str} The full path to audio file.
        @return metadata_type {str} The type of the audio file class or None.

        @exception ValueError A function or operation received an argument of correct type but inappropriate value.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            metadata_type = None

            audio_file = self.load_any_file(file_path)

            if audio_file is not None:
                # the built in class name of the filetype returned shows what metadata type
                # Eg flac = FLAC, mp3 = MP3, m4a = MP4, wma = ASF
                metadata_type = audio_file.__class__.__name__
            else:
                logger.error(f"ValueError getting metadata type: {file_path} returned None", exc_info=True)
                raise ValueError(f"ValueError getting metadata type: {file_path} returned None")

        except ValueError as v_error:
            raise v_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting metadata type for file: {file_path}", stack_info=True)
            raise e_error
        else:
            return metadata_type


    def get_tags_walk(self, file_path: str, file_pattern: str, ffprobe: bool = False) -> None:
        '''
        @brief Gets tags for audio files and saves to file.

        @details File walk will skip any non-audio files like playlists, jpgs, etc. Therefore a non-audio ext input will never have a pattern match.

        @param file_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to get tags from.
        @param ffprobe {bool} Optional, return ffprobe tags instead of mutagen tags.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            input_tags = None
            for dir_path, _, file_names in os.walk(file_path):
                # the tld Music does contain files, but not audio files
                if dir_path == file_path:
                    continue

                for file in file_names:
                    input_file, input_file_ext = os.path.splitext(file)

                    # we don't touch non-audio files like jpg's
                    if input_file_ext.lower() not in AUDIO_EXTS:
                        continue

                    if file_pattern and not fnmatch.fnmatch(input_file_ext.lower(), file_pattern.lower()):
                        continue
                    else:
                        tag_file_path = os.path.join(dir_path, file)

                        if ffprobe:
                            input_tags = self.get_media_tags(tag_file_path)
                        else:
                            metadata_type = self.get_metadata_type(tag_file_path)
                            if metadata_type in AUDIO_FILES:
                                input_tags = self.get_any_tags(tag_file_path)

                        if input_tags:
                            if ffprobe:
                                data.append(f"\n{tag_file_path} has {len(input_tags)} ffprobe tags")
                            else:
                                data.append(f"\n{tag_file_path} has {len(input_tags)} {metadata_type} tags")

                            tag_items = input_tags.items()
                            for key, value in tag_items:
                                data.append(f"{key}: {value}")
                        else:
                            data.append(f"\n{tag_file_path} has no metadata")

            directory.create_txt(txt_filename, data)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting tags for file {file_path}", stack_info=True)
            raise e_error


    def get_unique_media_keys(self, file_path: str) -> None:
        '''
        @brief Gets set of ffprobe keys and saves to file.

        @details Walks from starting path and saves set of unique metadata keys found by ffprobe.

        @param file_path {str} The starting point of the directory walk.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            input_tags = None
            unique_keys = set()
            for dir_path, _, file_names in os.walk(file_path):
                # the tld Music does contain files, but not audio files
                if dir_path == file_path:
                    continue

                for file in file_names:
                    input_file, input_file_ext = os.path.splitext(file)

                    # we don't touch non-audio files like jpg's
                    if input_file_ext.lower() not in AUDIO_EXTS:
                        continue

                    tag_file_path = os.path.join(dir_path, file)
                    input_tags = self.get_media_tags(tag_file_path)

                    if input_tags:
                        file_keys = input_tags.keys()
                        unique_keys.update(file_keys)

            data.append(f"Unique keys for audio files in {file_path}")

            if len(unique_keys) > 0:
                sorted_list = sorted(unique_keys)
                for key in sorted_list:
                    data.append(key)

            directory.create_txt(txt_filename, data)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting tags for file {file_path}", stack_info=True)
            raise e_error


    def has_art_tag(self, file_path: str) -> bool:
        '''
        @brief Checks if an audio file has the embedded album art tag.

        @details Checks for the presence of an embedded album art tag in the audio file.

        @param file_path {str} The full path to audio file.
        @return has_art {boolean} Returns true if art tag is present, false otherwise.

        @exception MusicProcessingError A generic music processing error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            has_art = False

            file_name, file_ext = os.path.splitext(file_path)
            if file_ext.lower() not in AUDIO_EXTS:
                logger.error(f"MusicProcessingError with file: {file_name} has invalid extension: {file_ext}", exc_info=True)
                raise MusicProcessingError(f"MusicProcessingError with file: {file_name} has invalid extension: {file_ext}")

            audio_tags = self.get_any_tags(file_path)

            #  FLAC files store album art in the 'pictures' attribute of the FLAC object, unlike other formats where it may be stored in tags.
            if file_ext.lower() == FLAC_EXT:
                audio_file = self.load_any_file(file_path)
                has_art = isinstance(audio_file, FLAC) and bool(audio_file.pictures)
            elif audio_tags is not None:
                if 'APIC:' in audio_tags:
                    has_art = True          # ID3/mp3
                elif 'covr' in audio_tags:
                    has_art = True          # MP4/m4a
                elif 'WM/Picture' in audio_tags:
                    has_art = True          # ASF/wma
                else:
                    return False
            else:
                return False

        except MusicProcessingError as mp_error:
            raise mp_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} checking for album art tag in file {file_path}", stack_info=True)
            raise e_error
        else:
            return has_art


    def load_any_file(self, file_path: str) -> FileType:
        '''
        @brief Loads any valid audio file type.

        @details Expects a valid filepath to an acceptable audio file.

        @param file_path {str} The full file path for audio file.
        @return audio_file {FileType} Mutagen instance for the input audio file type or None.

        @exception MutagenError A custom exception in Mutagen occurred.
        @exception ValueError A function or operation received an argument of correct type but inappropriate value.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio_file = None
            audio_file = mutagen.File(file_path)

            # mutagen did not throw an exception, but didn't load file either
            if audio_file is None:
                logger.error(f"ValueError loading {file_path} returned None", exc_info=True)
                raise ValueError(f"ValueError loading {file_path} returned None")

        except MutagenError as m_error:
            logger.error(f"MutagenError {m_error} loading {file_path}", exc_info=True)
            raise m_error
        except ValueError as v_error:
            raise v_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} loading audio file: {file_path}", stack_info=True)
            raise e_error
        else:
            return audio_file

    def map_flac_tags(self, input_tags: VCFLACDict) -> dict:
        '''
        @brief Converts FLAC metadata to generic metadata

        @details Converts subset of tags (the ones that Window will display) from FLAC.

        @param input_tags {VCFLACDict} The FLAC tags source.
        @return id3_tags {dict} The tags converted from FLAC tags.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            id3_tags = {}
            date_values = set()

            # Ensure DISCNUMBER is present in the input tags, defaulting to '1' if missing.
            if 'DISCNUMBER' not in input_tags:
                input_tags['DISCNUMBER'] = ['1']

            for metadata_field, flac_value in FLAC_KEYS.items():
                flac_tag = input_tags.get(flac_value)

                if flac_tag:
                    mp3_key = MP3_KEYS[metadata_field]
                    metadata_value = flac_tag[0]

                    if isinstance(metadata_value, str) and flac_value in FLAC_TIME_KEYS:
                        # just in case string is "YYYY-MM-DD"
                        date_value = metadata_value[0:4]
                        date_values.add(date_value)
                        continue

                    # FLAC/Vorbis metadata is string
                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    id3_tags[mp3_key] = tag_value

            id3_tags = self.__update_id3(date_values, id3_tags)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} mapping FLAC tags", stack_info=True)
            raise e_error
        else:
            return id3_tags


    def map_m4a_tags(self, input_tags: MP4Tags) -> dict:
        '''
        @brief Converts m4a (MP4) metadata to generic metadata

        @details Converts subset of tags (the ones that Window will display) from wma.

        @param input_tags {MP4Tags} The m4a tags source.
        @return id3_tags {dict} The tags converted from wma tags.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            id3_tags = {}
            date_values = set()

            for metadata_field, m4a_value in M4A_KEYS.items():
                m4a_tag = input_tags.get(m4a_value)

                if m4a_tag:
                    mp3_key = MP3_KEYS[metadata_field]
                    metadata_value = input_tags[m4a_value][0]

                    # for '\xa9day', ----:com.apple.iTunes:originalyear requires different handling
                    if isinstance(metadata_value, str) and m4a_value in M4A_TIME_KEYS:
                        # just in case string is "YYYY-MM-DD"
                        date_value = metadata_value[0:4]
                        date_values.add(date_value)
                        continue

                    # m4a doesn't have a "native" original year field like "\xa9ory",
                    # relies on the iTunes field ----:com.apple.iTunes:originalyear,
                    # so need additional step to decode from MP4FreeForm
                    if isinstance(metadata_value, MP4FreeForm) and m4a_value in M4A_TIME_KEYS:
                        decode_value = input_tags[m4a_value][0].decode()
                        # just in case string is "YYYY-MM-DD"
                        date_value = decode_value[0:4]
                        date_values.add(date_value)
                        continue

                    # m4a tag metadata values are usually strings, except for track and disc numbers which are tuples of ints
                    if isinstance(metadata_value, tuple) and m4a_value == "trkn":
                        track_num = input_tags[m4a_value][0][0]
                        total_tracks = input_tags[m4a_value][0][1]
                        tag_value = f"{track_num}/{total_tracks}"

                    if isinstance(metadata_value, tuple) and m4a_value == "disk":
                        disc_num = input_tags[m4a_value][0][0]
                        total_discs = input_tags[m4a_value][0][1]
                        tag_value = f"{disc_num}/{total_discs}"

                    # m4a supposedly has native publisher "\xa9pub", but not seen in my collection
                    # I do have iTunes "----:com.apple.iTunes:LABEL" field
                    if isinstance(metadata_value, MP4FreeForm) and m4a_value == "----:com.apple.iTunes:LABEL":
                        tag_value = input_tags[m4a_value][0].decode()

                    # rest of m4a/mp4 metadata I care about is string
                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    id3_tags[mp3_key] = tag_value

            id3_tags = self.__update_id3(date_values, id3_tags)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} converting m4a tags", stack_info=True)
            raise e_error
        else:
            return id3_tags


    def map_mp3_tags(self, input_tags: ID3) -> dict:
        '''
        @brief Converts mp3 metadata to id3 metadata

        @details Converts subset of tags (the ones that Window will display) from mp3 to id3.

        @param input_tags {ID3} The mp3 tags source.
        @return id3_tags {dict} The tags converted from mp3 tags.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            id3_tags = {}
            date_values = set()

            for metadata_field, mp3_value in MP3_KEYS.items():
                mp3_tag = input_tags.get(mp3_value)

                if mp3_tag:
                    mp3_key = MP3_KEYS[metadata_field]
                    metadata_value = input_tags[mp3_value].text[0]

                    # need to get all possible date years into set, but not add to output dict just yet
                    if isinstance(metadata_value, ID3TimeStamp) and (mp3_value in MP3_TIME_KEYS):
                        # just in case string is "YYYY-MM-DD"
                        date_value = metadata_value.text[0:4]
                        date_values.add(date_value)
                        continue

                    # ID3v2.3 tag metadata values are strings
                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    id3_tags[mp3_key] = tag_value

            id3_tags = self.__update_id3(date_values, id3_tags)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} converting mp3 tags to id3 tags", stack_info=True)
            raise e_error
        else:
            return id3_tags


    def map_wma_tags(self, input_tags: ASFTags) -> dict:
        '''
        @brief Converts wma (ASF) metadata to id3 metadata

        @details Converts subset of tags (the ones that Window will display) from wma to id3.

        @param input_tags {ASFTags} The wma tags source.
        @return tags {dict} The tags converted from wma tags.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            id3_tags = {}
            date_values = set()

            for metadata_field, wma_value in WMA_KEYS.items():
                wma_tag = input_tags.get(wma_value)

                if wma_tag:
                    mp3_key = MP3_KEYS[metadata_field]
                    metadata_value = input_tags[wma_value][0].value

                    # need to get all possible date years into set, but not add to output dict just yet
                    if isinstance(metadata_value, str) and (wma_value in WMA_TIME_KEYS):
                        # just in case string is "YYYY-MM-DD"
                        date_value = metadata_value[0:4]
                        date_values.add(date_value)
                        continue

                    # most tags are strings except for track num, which is int
                    if isinstance(metadata_value, int):
                        tag_value = metadata_value

                    #  rest of the ASF/WMA metadata I care about is string
                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    id3_tags[mp3_key] = tag_value

            id3_tags = self.__update_id3(date_values, id3_tags)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} converting wma tags to id3 tags", stack_info=True)
            raise e_error
        else:
            return id3_tags


    def normalize_flac_filename(self, file_path: str) -> None:
        '''
        @brief Renames a FLAC using its album artist and title metadata.

        @details Calling function MUST supply path to an existing FLAC file.<br>
        The FLAC MUST contain ALBUMARTIST and TITLE Vorbis comment tags.<br>
        A csv report named after the function (`normalize_flac_filename.csv`) is created after the file is renamed.

        @param file_path {str} The path for the FLAC file to rename.

        @exception ValueError Indicates invalid input or missing required metadata.
        @exception ValidationError Indicates the created filename is invalid.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        csv_filename = inspect.currentframe().f_code.co_name

        try:
            _, file_ext = os.path.splitext(file_path)
            if file_ext.lower() != FLAC_EXT:
                logger.error(f"ValueError with file: {file_path} has invalid extension: {file_ext}", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} has invalid extension: {file_ext}")

            audio_file = self.load_any_file(file_path)

            if not isinstance(audio_file, FLAC) or audio_file.tags is None:
                logger.error(f"ValueError loading FLAC metadata from {file_path}", exc_info=True)
                raise ValueError(f"ValueError loading FLAC metadata from {file_path}")

            album_artist_tag = audio_file.tags.get('albumartist')
            title_tag = audio_file.tags.get('title')

            if album_artist_tag is None or not album_artist_tag:
                logger.error(f"ValueError with file: {file_path} missing album artist metadata", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} missing album artist metadata")

            if title_tag is None or not title_tag:
                logger.error(f"ValueError with file: {file_path} missing title metadata", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} missing title metadata")

            album_artist = album_artist_tag[0]
            title = title_tag[0]

            file_stem = os.path.splitext(os.path.basename(file_path))[0]
            if re.fullmatch(rf"{re.escape(album_artist)}\s*-\s*{re.escape(title)}", file_stem):
                return

            normalized_name = f"{album_artist}-{title}{FLAC_EXT}"
            normalized_name = pathvalidate.sanitize_filename(
                normalized_name,
                replacement_text="",
                platform="Windows",
                validate_after_sanitize=True,
            )

            normalized_path = os.path.join(os.path.dirname(file_path), normalized_name)
            del audio_file
            os.rename(file_path, normalized_path)

            data.append([file_path, album_artist, title, normalized_path])
            header_row = ["original file path", "album artist", "title", "normalized file path"]
            directory.create_csv(csv_filename, data, None, None, header_row, 0)

        except ValidationError as validation_error:
            logger.exception(f"ValidationError creating normalized filename for {file_path}", stack_info=True)
            raise validation_error
        except ValueError as v_error:
            raise v_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} normalizing filename for {file_path}", stack_info=True)
            raise e_error


    def normalize_mp3_filename(self, file_path: str) -> None:
        '''
        @brief Renames an ID3v2.3 MP3 using its album artist and title metadata.

        @details Calling function MUST supply path to an existing valid MP3 file.<br>
        The MP3 MUST contain ID3v2.3 metadata with TPE2 and TIT2 frames.<br>
        The metadata values are assumed to be sanitized already.<br>
        A CSV report named after the function (`normalize_mp3_filename.csv`) is created after the file is renamed.

        @param file_path {str} The path for the MP3 file to rename.

        @exception ValueError Indicates invalid input or missing required metadata.
        @exception ValidationError Indicates the created filename is invalid.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        csv_filename = inspect.currentframe().f_code.co_name

        try:
            _, file_ext = os.path.splitext(file_path)
            if file_ext.lower() != MP3_EXT:
                logger.error(f"ValueError with file: {file_path} has invalid extension: {file_ext}", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} has invalid extension: {file_ext}")

            audio_file = self.load_any_file(file_path)

            if not isinstance(audio_file, MP3) or audio_file.tags is None:
                logger.error(f"ValueError loading ID3v2.3 metadata from {file_path}", exc_info=True)
                raise ValueError(f"ValueError loading ID3v2.3 metadata from {file_path}")

            if audio_file.tags.version != (2, 3, 0):
                logger.error(f"ValueError with file: {file_path} metadata is not ID3v2.3", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} metadata is not ID3v2.3")

            album_artist_tag = audio_file.tags.get('TPE2')
            title_tag = audio_file.tags.get('TIT2')

            if album_artist_tag is None or not album_artist_tag.text:
                logger.error(f"ValueError with file: {file_path} missing album artist metadata", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} missing album artist metadata")

            if title_tag is None or not title_tag.text:
                logger.error(f"ValueError with file: {file_path} missing title metadata", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} missing title metadata")

            album_artist = album_artist_tag.text[0]
            title = title_tag.text[0]

            file_stem = os.path.splitext(os.path.basename(file_path))[0]
            if re.fullmatch(rf"{re.escape(album_artist)}\s*-\s*{re.escape(title)}", file_stem):
                return

            normalized_name = f"{album_artist}-{title}{MP3_EXT}"
            normalized_name = pathvalidate.sanitize_filename(
                normalized_name,
                replacement_text="",
                platform="Windows",
                validate_after_sanitize=True,
            )

            normalized_path = os.path.join(os.path.dirname(file_path), normalized_name)
            os.rename(file_path, normalized_path)

            data.append([file_path, album_artist, title, normalized_path])
            header_row = ["original file path", "album artist", "title", "normalized file path"]
            directory.create_csv(csv_filename, data, None, None, header_row, 0)

        except ValidationError as validation_error:
            logger.exception(f"ValidationError creating normalized filename for {file_path}", stack_info=True)
            raise validation_error
        except ValueError as v_error:
            raise v_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} normalizing filename for {file_path}", stack_info=True)
            raise e_error


    def normalize_mp4_filename(self, file_path: str) -> None:
        '''
        @brief Renames an M4A using its album artist and title metadata.

        @details Calling function MUST supply path to an existing M4A file.<br>
        The M4A MUST contain aART and title MP4 tags.<br>
        A CSV report named after the function (`normalize_mp4_filename.csv`) is created after the file is renamed.

        @param file_path {str} The path for the M4A file to rename.

        @exception ValueError Indicates invalid input or missing required metadata.
        @exception ValidationError Indicates the created filename is invalid.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        csv_filename = inspect.currentframe().f_code.co_name

        try:
            _, file_ext = os.path.splitext(file_path)
            if file_ext.lower() != M4A_EXT:
                logger.error(f"ValueError with file: {file_path} has invalid extension: {file_ext}", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} has invalid extension: {file_ext}")

            audio_file = self.load_any_file(file_path)

            if not isinstance(audio_file, MP4) or audio_file.tags is None:
                logger.error(f"ValueError loading MP4 metadata from {file_path}", exc_info=True)
                raise ValueError(f"ValueError loading MP4 metadata from {file_path}")

            album_artist_tag = audio_file.tags.get('aART')
            title_tag = audio_file.tags.get('\xa9nam')

            if album_artist_tag is None or not album_artist_tag:
                logger.error(f"ValueError with file: {file_path} missing album artist metadata", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} missing album artist metadata")

            if title_tag is None or not title_tag:
                logger.error(f"ValueError with file: {file_path} missing title metadata", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} missing title metadata")

            album_artist = album_artist_tag[0]
            title = title_tag[0]

            file_stem = os.path.splitext(os.path.basename(file_path))[0]
            if re.fullmatch(rf"{re.escape(album_artist)}\s*-\s*{re.escape(title)}", file_stem):
                return

            normalized_name = f"{album_artist}-{title}{M4A_EXT}"
            normalized_name = pathvalidate.sanitize_filename(
                normalized_name,
                replacement_text="",
                platform="Windows",
                validate_after_sanitize=True,
            )

            normalized_path = os.path.join(os.path.dirname(file_path), normalized_name)
            os.rename(file_path, normalized_path)

            data.append([file_path, album_artist, title, normalized_path])
            header_row = ["original file path", "album artist", "title", "normalized file path"]
            directory.create_csv(csv_filename, data, None, None, header_row, 0)

        except ValidationError as validation_error:
            logger.exception(f"ValidationError creating normalized filename for {file_path}", stack_info=True)
            raise validation_error
        except ValueError as v_error:
            raise v_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} normalizing filename for {file_path}", stack_info=True)
            raise e_error


    def normalize_wma_filename(self, file_path: str) -> None:
        '''
        @brief Renames a WMA file using album artist and title metadata.

        @details Calling function MUST supply path to an existing WMA file.<br>
        The WMA MUST contain 'WM/AlbumArtist' and 'Title' tags.<br>
        A CSV report named after the function (`normalize_wma_filename.csv`) is created after the file is renamed.

        @param file_path {str} The path for the WMA file to rename.

        @exception ValueError Indicates invalid input or missing required metadata.
        @exception ValidationError Indicates the created filename is invalid.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        csv_filename = inspect.currentframe().f_code.co_name

        try:
            _, file_ext = os.path.splitext(file_path)
            if file_ext.lower() != WMA_EXT:
                logger.error(f"ValueError with file: {file_path} has invalid extension: {file_ext}", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} has invalid extension: {file_ext}")

            audio_file = self.load_any_file(file_path)

            if not isinstance(audio_file, ASF) or audio_file.tags is None:
                logger.error(f"ValueError loading WMA metadata from {file_path}", exc_info=True)
                raise ValueError(f"ValueError loading WMA metadata from {file_path}")

            album_artist_tag = audio_file.tags.get('albumartist')
            title_tag = audio_file.tags.get('title')

            if album_artist_tag is None or not album_artist_tag:
                logger.error(f"ValueError with file: {file_path} missing album artist metadata", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} missing album artist metadata")

            if title_tag is None or not title_tag:
                logger.error(f"ValueError with file: {file_path} missing title metadata", exc_info=True)
                raise ValueError(f"ValueError with file: {file_path} missing title metadata")

            album_artist = album_artist_tag[0]
            title = title_tag[0]

            file_stem = os.path.splitext(os.path.basename(file_path))[0]
            if re.fullmatch(rf"{re.escape(album_artist)}\s*-\s*{re.escape(title)}", file_stem):
                return

            normalized_name = f"{album_artist}-{title}{WMA_EXT}"
            normalized_name = pathvalidate.sanitize_filename(
                normalized_name,
                replacement_text="",
                platform="Windows",
                validate_after_sanitize=True,
            )

            normalized_path = os.path.join(os.path.dirname(file_path), normalized_name)
            del audio_file
            os.rename(file_path, normalized_path)

            data.append([file_path, album_artist, title, normalized_path])
            header_row = ["original file path", "album artist", "title", "normalized file path"]
            directory.create_csv(csv_filename, data, None, None, header_row, 0)

        except ValidationError as validation_error:
            logger.exception(f"ValidationError creating normalized filename for {file_path}", stack_info=True)
            raise validation_error
        except ValueError as v_error:
            raise v_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} normalizing filename for {file_path}", stack_info=True)
            raise e_error


    def normalize_flac_filename_walk(self, start_path: str) -> None:
        '''
        @brief Renames FLAC files found in specified path using album artist and title metadata.

        @details Calling functions MUST verify valid start path.

        @param start_path {str} The starting point of the directory walk.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        input_file_ext = None

        try:
            input_path = Path(start_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # only process FLAC files
                    if input_file_ext.lower() != FLAC_EXT:
                        continue

                    input_file_path = os.path.join(dir_path, file)
                    self.normalize_flac_filename(input_file_path)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} walking {start_path} to normalize FLAC files", stack_info=True)
            raise e_error


    def normalize_mp3_filename_walk(self, start_path: str) -> None:
        '''
        @brief Renames ID3v2.3 MP3 files found in specified path using album artist and title metadata.

        @details Calling functions MUST verify valid start path.

        @param start_path {str} The starting point of the directory walk.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        input_file_ext = None

        try:
            input_path = Path(start_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # only process MP3 files
                    if input_file_ext.lower() != MP3_EXT:
                        continue

                    input_file_path = os.path.join(dir_path, file)
                    self.normalize_mp3_filename(input_file_path)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} walking {start_path} to normalize audio files", stack_info=True)
            raise e_error


    def normalize_mp4_filename_walk(self, start_path: str) -> None:
        '''
        @brief Renames M4A files found in specified path using album artist and title metadata.

        @details Calling functions MUST verify valid start path.

        @param start_path {str} The starting point of the directory walk.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        input_file_ext = None

        try:
            input_path = Path(start_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # only process M4A files
                    if input_file_ext.lower() != M4A_EXT:
                        continue

                    input_file_path = os.path.join(dir_path, file)
                    self.normalize_mp4_filename(input_file_path)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} walking {start_path} to normalize MP4 files", stack_info=True)
            raise e_error


    def normalize_wma_filename_walk(self, start_path: str) -> None:
        '''
        @brief Renames WMA files found in specified path using album artist and title metadata.

        @details Calling functions MUST verify valid start path.

        @param start_path {str} The starting point of the directory walk.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        input_file_ext = None

        try:
            input_path = Path(start_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # only process WMA files
                    if input_file_ext.lower() != WMA_EXT:
                        continue

                    input_file_path = os.path.join(dir_path, file)
                    self.normalize_wma_filename(input_file_path)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} walking {start_path} to normalize WMA files", stack_info=True)
            raise e_error
