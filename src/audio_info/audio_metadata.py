'''
@file audio_metadata.py
@brief Defines the audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import fnmatch
import gc
import inspect
import json
import logging
import os
import re
import sys
from json import JSONDecodeError
from pathlib import Path

# third party modules
import mutagen
import pathvalidate
from mutagen import FileType
from mutagen.asf import ASFTags
from mutagen.id3 import APIC, ID3, ID3TimeStamp
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4FreeForm, MP4Tags
from mutagen._util import MutagenError
from pathvalidate.error import ValidationError
from tqdm import tqdm

# local module methods
from src import add_module_handler
# local module constants
from src import ASF_TYPE, AUDIO_EXTS, AUDIO_FILES
from src import FOLDER_ART
from src import MP4_TYPE, MP3_EXT, MP3_TYPE
# local module errors
from src import MetadataTypeError
from src import MusicProcessingError
from src import PathInfoError
# local module classes
from src.audio_normalize import AudioNormalization
from src.dir_processing import DirectoryProcessing
from src.subprocess_utils import SubprocessUtilities

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
    'album',                # must have                     ffmpeg mapping: TALB
    'album_artist',         # must have                     ffmpeg mapping: TPE2
    'artist',               # must have                     ffmpeg mapping: TPE1
    'comment',              # PITA, handled as ID3v2.4      ffmpeg mapping: COMM
    'compilation',          # PITA, is ID3v2.4              ffmpeg mapping: TCMP
    'composer',             # nice to have                  ffmpeg mapping: TCOM
    'copyright',            # nice to have                  ffmpeg mapping: TCOP
    'date',                 # must have                     ffmpeg mapping: TDRC    is ID3v2.4
    'disc',                 # nice to have                  ffmpeg mapping: TPOS
    'encoder',              # not interested                ffmpeg mapping: TSSE
    'encoded_by',           # not interested                ffmpeg mapping: TENC
    'genre',                # must have                     ffmpeg mapping: TCON
    'language'              # not interested                ffmpeg mapping: TLAN
    'lyrics',               # not interested                ffmpeg mapping: USLT
    'originalyear',         # nice to have                  ffmpeg mapping: TORY
    'performer',            # not interested                ffmpeg mapping: TPE3
    'publisher',            # nice to have                  ffmpeg mapping: TPUB
    'title',                # must have                     ffmpeg mapping: TIT2
    'track'                 # nice to have                  ffmpeg mapping: TRCK
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
    @brief Defines the base metadata processing used by project.
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

        @param date_values ({str}) Set of unique YYYY date strings.
        @param id3_tags {dict} Source ID3 tags.
        @return output_tags {dict} Updated ID3 tags.

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


    def convert_file(self, file_path: str, show_spinner=True) -> None:
        '''
        @brief Converts a wma, m4a or mp3 audio file to mp3 audio file, using ffmpeg directly.

        @details Calling function MUST supply an existing file path.
        @details Converts m4a, mp3 & wma files to mp3 files with ID3v2.3 tags using FFMPEG.
        @details Only the Windows displayable subset of metadata key/values is preserved.
        @details Run create_album_dir function to ensure there are album directories for every audio file.
        @details Then manually review extant album art and create and/or move Folder.jpg, if possible, to each album directory.
        @details Next run extract_art_function to extract embedded art as Folder.jpg if needed, into each album directory.
        @details Finally run set_album_art function to ensure a Folder.jpg exists in each album directory.

        @param file_path {str} The path for audio file to be converted.
        @param show_spinner {bool} Show spinner flag.

        @exception MetadataTypeError Indicates a non-standard metadata type was encountered.
        @exception MusicProcessingError A generic music processing error occurred.
        @exception PathInfoError Indicates directory_processing.path_info function returned None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
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

            '''
            metadata transfer
            I dont want every possible tag, just the subset that Windows will display AND are ID3v2.3
            Comments are ASF/ID3v2.3/MP4, but MusicBrainz/MP3Tag/puddletag have difficulty displaying,
            so passing on transferring comment metadata
            Compilation is not ID3v2.3, so passing on transferring compilation metadata
            Date info is most problematic part of metadata, ASF/ID3v2.3/MP4 multiple date type tags,
            the data types could be a full ISO date, or could just be a 4 digit year string,
            so I am formatting any found date values to YYYY and mapping to ID3v2.3 TYER field
            I have manually edited all audio files without date to have 1963 as default
            '''
            metadata_type = self.get_metadata_type(file_path)

            if metadata_type is None:
                logger.error(f"MetadataTypeError with file: {os.path.basename(file_path)} returned None", exc_info=True)
                raise MetadataTypeError(f"MetadataTypeError with file: {os.path.basename(file_path)} returned None")

            input_tags = self.get_any_tags(file_path)

            if metadata_type == MP3_TYPE:
                tags = self.map_mp3_tags(input_tags)
            elif metadata_type == MP4_TYPE:
                tags = self.map_m4a_tags(input_tags)
            elif metadata_type == ASF_TYPE:
                tags = self.map_wma_tags(input_tags)

            # get the input file info - want bitrate so can preserve the quality in exported file
            # @todo look at using get_bit_rate instead
            media_info = self.get_media_info(file_path)
            bitrate = media_info['bit_rate']

            # ffmpeg
            # -hide_banner            # reduce output clutter
            # -i file_path            # specify input file D:\MusicProcessing\tests\Music\Crush\Here\Crush-Live.mp3
            # -vn -map_metadata -1    # -vn drops video stream and -map_metadata -1 drops all text metadata
            # -codec:a libmp3lame     # -codec:a libmp3lame sets audio codec for mp3
            # -id3v2_version 3        # known bug have to specify id3v2 version
            # -b:a 128198             # ffmpeg will downgrade bitrate if you don't set it
            command = [
                "ffmpeg", "-hide_banner",
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

            # export_path -y        # specify the output with overwrite flag D:\MusicProcessing\src\generated_files\Music\Crush\Here\Crush-Live.mp3
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


    def convert_walk(self, start_path: str, file_pattern: str, show_spinner=True) -> None:
        '''
        @brief Converts all audio files found in specified path to mp3 format.

        @details Calling functions MUST verify valid start path.

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

                    # file is not mp3, m4a, or wma, so carry on to next file
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


    def create_album_dir(self, start_path: str) -> None:
        '''
        @brief Creates an album sub-directory in an artist directory.

        @details Calling functions MUST verify valid start path.
        @details Creates the album sub directory for the artist if needed.
        @details The album name for the directory is drawn from the album metadata field.
        @details Also creates csv of all audio file paths, album metadata values and sanitized album directory names.

        @param start_path {str} The tld holding music files.

        @exception ValidationError A pathlib module validation error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        album_dirs = set()
        data = []
        csv_filename = inspect.currentframe().f_code.co_name
        header_row = ["audio file path", "album metadata", "album directory"]

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

                    if 'album' in file_media_tags.keys():
                        # the album metadata should have had all / removed manually,
                        # but do replace anyways, it would wreak havoc by creating nested dirs
                        album = file_media_tags['album'].replace("/", "-")

                        # sanitize because the metadata might have characters invalid for directory names
                        # platform is "Windows" because it is more restrictive (therefore os universal),
                        # the characters \, :, *, ?, ", <, >, | will be replaced by "-"
                        # refer to https://pathvalidate.readthedocs.io/en/latest/pages/reference/function.html#pathvalidate.sanitize_filename
                        album_dir = pathvalidate.sanitize_filepath(album, replacement_text="-", platform="Windows", validate_after_sanitize=True)

                        data.append([audio_file, album, album_dir])
                        album_dirs.add(album_dir)

                        # make the album sub directory is REQUIRED before moving the audio file
                        directory.make_album_dir(tld_item_path, album_dir)

                        # now transfer the audio file to new album directory
                        destination_dir = os.path.join(tld_item_path, album_dir)
                        directory.move_audio_file(audio_file, destination_dir)
                    else:
                        logger.warning(f"{audio_file} is missing album metadata")
                        continue

                tld_bar.update(1)

            tld_bar.close()
            directory.create_csv(csv_filename, data, None, header_row, 0)

        except ValidationError as v_error:
            logger.exception(f"ValidationError sanitizing album metadata {album}", stack_info=True)
            raise v_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} creating sub-dirs for {start_path}", stack_info=True)
            raise e_error


    def get_any_tags(self, file_path: str) -> ASFTags | ID3 | MP4Tags:
        '''
        @brief Gets tags for any type of audio file.

        @details Any type means m4a, mp3, or wma files.

        @param file_path {str} The full path to audio file.
        @return tags {object} Tag object (one of ID3, MP4Tags, or ASFTags) holding audio file tags or None.

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

        @details Uses ffprobe to get all media info from any valid audio file.
        @details This def replaces the native pydub mediainfo function.
        @details The file_path MUST be for a valid audio file.

        @param file_path {str} The full path to audio file.
        @return media_info {dict} Media info (codec, duration, size, bitrate...) from filepath.

        @exception re.error An error occurred processing a regular expression with re module.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            media_info = None

            '''
            this cli WILL include 'comment' = 'Cover (front)' if the file has embedded album art in the TAG inner dict,
            whereas ASF/ID3/MP4, would place WM\Picture, APIC, or covr AND include the byte data for the art,
            This is because show_streams means ffprobe sees the art data as the video stream metadata instead.
            '''
            # -v quiet reduce output clutter
            # -show_format get high level details of media file
            # -show_streams gets all information about each media stream in the input
            command = [
                "ffprobe",
                "-v", "quiet",
                "-show_format",
                "-show_streams",
                file_path
            ]

            output = subprocess_utils.popen_pipe(command)

            rgx = re.compile(r"(?:(?P<inner_dict>.*?):)?(?P<key>.*?)\=(?P<value>.*?)$")
            media_info = {}

            if sys.platform == 'win32':
                output = output.replace("\r", "")

            for line in output.split("\n"):
                mobj = rgx.match(line)

                if mobj:
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

        @param file_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to get tags from.

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

        try:
            media_tags = None

            '''
            Note that this cli, unlike the general media info cli: ffprobe -v quiet -show_format -show_streams file_path,
            will NOT insert 'comment' = 'Cover (front)' in the tags dictionary if the audio file has embedded art.
            This cli will only return textual audio metadata.
            '''
            # -v quiet reduce console clutter
            # -of json output in json format
            # -show_entries format_tags we only care about tags
            command = [
                "ffprobe",
                "-v", "quiet",
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
                # Eg mp3 = MP3, m4a = MP4, wma = ASF
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


    def get_tags_walk(self, file_path: str, file_pattern: str, ffprobe=False) -> None:
        '''
        @brief Gets tags for audio files and saves to file.

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

                    if file_pattern and not fnmatch.fnmatch(file, file_pattern.lower()):
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
                                tag_items = input_tags.items()
                                for key, value in tag_items:
                                    data.append(f"{key}: {value}")
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

                    file_keys = input_tags.keys()
                    if file_keys:
                        unique_keys.update(file_keys)

            data.append(unique_keys)
            directory.create_txt(txt_filename, data)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting tags for file {file_path}", stack_info=True)
            raise e_error


    def has_art_tag(self, file_path: str) -> bool:
        '''
        @brief Checks if an audio file has the embedded album art tag.

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

            if audio_tags is not None:
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

                    if isinstance(metadata_value, tuple) and m4a_value == "trkn":
                        track_num = input_tags[m4a_value][0][0]
                        total_tracks = input_tags[m4a_value][0][1]
                        tag_value = f"{track_num}/{total_tracks}"

                    if isinstance(metadata_value, tuple) and m4a_value == "disk":
                        disc_num = input_tags[m4a_value][0][0]
                        total_discs = input_tags[m4a_value][0][1]
                        tag_value = f"{disc_num}/{total_discs}"

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

                    # m4a supposedly has native publisher "\xa9pub", but not seen in my collection
                    # I do have iTunes "----:com.apple.iTunes:LABEL" field
                    if isinstance(metadata_value, MP4FreeForm) and m4a_value == "----:com.apple.iTunes:LABEL":
                        tag_value = input_tags[m4a_value][0].decode()

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

                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    # track num is int
                    if isinstance(metadata_value, int):
                        tag_value = metadata_value

                    id3_tags[mp3_key] = tag_value

            id3_tags = self.__update_id3(date_values, id3_tags)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} converting wma tags to id3 tags", stack_info=True)
            raise e_error
        else:
            return id3_tags
