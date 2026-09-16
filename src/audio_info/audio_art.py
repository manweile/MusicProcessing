'''
@file audio_art.py
@author Gerald Manweiler

@brief Defines the audio art class.

@details Defines the audio art class used for handling embedded album art in various audio file formats.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import fnmatch                                              # for filename pattern matching
import gc                                                   # for garbage collection management
import json                                                 # for JSON parsing and handling
import logging                                              # for logging messages
import os                                                   # for operating system dependent functionality
import shutil                                               # for high-level file operations
import struct                                               # for working with C-style data structures
from json import JSONDecodeError                            # for handling JSON decode errors
from os import strerror                                     # for getting error messages corresponding to errno
from pathlib import Path                                    # for object-oriented filesystem paths

# third party modules
from mutagen.asf import ASF                                 # for handling ASF audio files
from mutagen.flac import FLAC                               # for handling FLAC audio files
from mutagen.id3 import ID3                                 # for handling ID3 tags in MP3 files
from mutagen.mp3 import MP3                                 # for handling MP3 audio files
from mutagen.mp4 import MP4                                 # for handling MP4 audio files
from mutagen._util import MutagenError                      # for handling Mutagen-specific errors

# local module methods
from src import add_module_handler                          # for adding a module-specific handler to the logger
# local module constants
from src import AUDIO_EXTS                                  # for supported audio file extensions
from src import FOLDER_ART                                  # for folder art directory
from src import FLAC_EXT                                    # for FLAC file extension
from src import M4A_EXT                                     # for M4A file extension
from src import MP3_EXT                                     # for MP3 file extension
from src import WMA_EXT                                     # for WMA file extension
from src.generated_files import GENERATED_PATH              # for generated files path
# local module classes
from src.audio_normalize import AudioNormalization          # for audio normalization functionality
from src.subprocess_utils import SubprocessUtilities        # for subprocess utility functions
# relative import so don't get circular import error
from .audio_metadata import AudioMetadata                   # for audio metadata handling functionality

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

## @var metadata
# @brief instance of AudioMetadata class
# @details used for accessing class functionality
metadata = AudioMetadata()

# @brief instance of AudioNormalization class
# @details used for accessing class functionality
normalization = AudioNormalization()

## @var subprocess_utils
# @brief instance of SubprocessUtilities class
# @details used for accessing class functionality
subprocess_utils = SubprocessUtilities()

## @var ALBUM_ART
# @brief Album art directory for compilation albums
# @details used for setting album art
ALBUM_ART = "AlbumArt"


class AudioArt():
    '''
    @brief Handles audio album art processing.

    @details Provides methods for extracting, processing, and managing album art associated with audio files.
    '''

    def __init__(self) -> None:
        '''
        @brief Initializes the AudioArt class.

        @details A basic class implementation with no instantiation parameters.

        @return AudioArt {instance} An instance of the class.
        '''

        pass


    def __unpack_asf_image(self, data: bytearray) -> tuple:
        '''
        @brief Unpack image data from a WM/Picture tag.

        @details This function is treated as "untrusted" and could throw all manner of exceptions (out-of-bounds, etc.).<br>
        From https://github.com/beetbox/mediafile/blob/master/mediafile.py#L243.

        @param data {bytearray} The byte attribute data from asf audio WM/Picture tag.
        @return (mime, image_data, type, description) ({str}, {bytes}, {int}, {str})<br>
        Tuple containing the MIME type, the raw image data, a type indicator, and the image's description.

        @exception struct.error A struct module error occurred.
        @exception UnicodeDecodeError An illegal sequence of str characters occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        r'''
        <:little-endian byte order, b: signed char (1 byte), i: signed int (4 bytes)<br>
        unpacks first 5 bytes in tuple where type is C signed char (1 byte)/Python integer and size is C signed int (4 bytes)/Python integer
        for an ASF WM/Picture, 3 = Front album cover
        eg.<br>
        b'\x03\x140\x00\x00i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00\x00\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`<br>
        image type and image size, elements 0-5: b'\x03\x140\x00\x00<br>
        image type, elements 0-1, b'\x03'<br>
        image size, elements 1-5, b'\x140\x00\x00 = 0x1403 little-endian, 0x3014 big-endian, decimal 12308<br>
        mime type, elements 5 to 25: b'i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00'<br>
        null terminator, elements 25 to 27: b'\x00\x00'<br>
        description, elements 27 to 29: b'\x00\x00'<br>
        data, elements 29 to 29 + size: b'\xff\xe0\x...'
        '''

        try:
            unpacked = None

            # Unpack the type and size from the first 5 bytes of the data.
            type, size = struct.unpack_from('<bi', data)
            pos = 5
            mime = b''

            # Extract the MIME type, which is UTF-16-LE encoded and null-terminated.
            while data[pos:pos + 2] != b'\x00\x00':
                mime += data[pos:pos + 2]
                pos += 2

            # Skip the null terminator after the MIME type.
            pos += 2
            # Extract the description, which is UTF-16-LE encoded and null-terminated.
            description = b''
            while data[pos:pos + 2] != b'\x00\x00':
                description += data[pos:pos + 2]
                pos += 2

            # Skip the null terminator after the description.
            pos += 2
            # Extract the image data based on the size.
            image_data = data[pos:pos + size]

            # Prepare the unpacked tuple with MIME type, image data, type, and description.
            unpacked = (mime.decode("utf-16-le"), image_data, type, description.decode("utf-16-le"))

        except struct.error as s_error:
            logger.error("Struct unpacking from error", exc_info=True)
            raise s_error
        except UnicodeDecodeError as ud_error:
            logger.exception("UnicodeDecodeError decoding asf image from tag data", stack_info=True)
            raise ud_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} unpacking asf image from tag data", stack_info=True)
            raise e_error
        else:
            return unpacked


    def __write_data(self, file_path, image_data: bytearray):
        '''
        @brief Writes image data for audio file to separate jpeg file.

        @ details Writes the extracted image data to a separate JPEG file named Folder.jpg in the album directory.

        @param file_path {str} The full path to audio file.
        @param image_data {bytearray} The image bytes extracted from audio file.

        @exception BlockingIOError An input/output operation was blocked.
        @exception OSError A system related error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            if image_data:
                input_path = Path(file_path)
                album_path = input_path.parent
                output_file = os.path.join(album_path, FOLDER_ART)

                with open(output_file, 'wb') as img_file:
                    img_file.write(image_data)

        except BlockingIOError as bio_error:
            logger.error(f"BlockingIOError writing image data to {file_path}", exc_info=True)
            raise bio_error
        except OSError as os_error:
            logger.error(f"OSError {(strerror(os_error.errno))} writing data with {file_path}", exc_info=True)
            raise os_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} writing image data from {file_path}", stack_info=True)
            raise e_error


    def extract_album_art(self, file_path: str) -> None:
        '''
        @brief Extract and save embedded album art.

        @details Extracts art as Folder.jpg to album directory of input audio file.<br>
        First tries extraction from video stream (audio file type agnostic), then by metadata art tag (from specific audio file type).

        @param file_path {str} The full path to audio file.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            input_path = Path(file_path)
            album_path = input_path.parent

            # don't need to waste cycles if we have a Folder.jpg from a previous execution
            album_contents = os.listdir(album_path)
            if FOLDER_ART in album_contents:
                logger.info(f"{album_path} has a {FOLDER_ART}")
                return

            # we don't touch non-audio files like m3u etc
            input_file_ext = input_path.suffix
            if input_file_ext.lower() not in AUDIO_EXTS:
                logger.warning(f"{input_path.name} is not an audio file")
                return

            # ffmpeg extraction is primary method because is file type agnostic, so long as file has a video stream
            if self.has_video_stream(input_path):
                self.extract_ffmpeg_art(input_path)
                return
            else:
                # info because mutagen check/extract methods may yet work
                logger.info(f"No video stream album art present in {file_path}")

            # mutagen extraction is secondary method, because not file type agnostic, and file must have an art metadata tag
            if metadata.has_art_tag(input_path):
                if input_file_ext.lower() == MP3_EXT:
                    self.extract_mp3_art(file_path)
                elif input_file_ext.lower() == M4A_EXT:
                    self.extract_m4a_art(file_path)
                elif input_file_ext.lower() == WMA_EXT:
                    self.extract_asf_art(file_path)
                elif input_file_ext.lower() == FLAC_EXT:
                    self.extract_flac_art(file_path)
            else:
                # warning because by this point, negative result from both art present checks, so simply can't extract any art
                logger.warning(f"No album art present in {file_path}")
                return

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} extracting album art from {file_path}", stack_info=True)
            raise e_error


    def extract_asf_art(self, file_path: str) -> None:
        '''
        @brief Extracts cover art from asf/wma files.

        @details Input file is expected to have embedded cover art.

        @param file_path {str} The full path to audio file.

        @exception MutagenError A custom exception in Mutagen occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio = ASF(file_path)
            audio_tags = audio.tags
            pic_tag = audio_tags["WM/Picture"]
            byte_attribute_array = pic_tag[0]
            picture_data = byte_attribute_array.value

            # image data is all really need for writing to the output file
            mime_type, image_data, type_indicator, image_description = self.__unpack_asf_image(picture_data)

            self.__write_data(file_path, image_data)

        except MutagenError as m_error:
            logger.error(f"MutagenError {m_error} loading {file_path}", exc_info=True)
            raise m_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} extracting asf art from {file_path}", stack_info=True)
            raise e_error


    def extract_ffmpeg_art(self, file_path: str) -> None:
        '''
        @brief Extracts and saves embedded album art.

        @details Uses ffmpeg and is audio file type agnostic.<br>
        Input file must have a video stream.

        @param file_path {str} The full path to audio file.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        '''
        extract art command explanation:<br>
        ffmpeg -hide_banner -i `file_path` -an -map 0:v -map_metadata -1 -update 1 `output_file` -y

        -hide_banner to reduce output clutter<br>
        -an specifies ignore audio stream<br>
        -map 0:v specifies 1st input file use video stream<br>
        -map_metadata -1 specifies discard all alphanumeric metadata from input file<br>
        the use of -map and -map_metadata will result in smaller jpg file than vcodec copy or -c:v copy - empirically tested<br>
        -update 1 specifies overwrite output file with 1 frame from video,
        which is all we want, the embedded art IS the 1st and only frame from video stream<br>
        -y to overwrite output file if needed
        '''

        try:
            input_path = Path(file_path)
            album_path = input_path.parent

            output_file = os.path.join(album_path, FOLDER_ART)

            command = [
                'ffmpeg', '-hide_banner',
                '-i', file_path,
                '-an',
                '-map', '0:v',
                '-map_metadata', '-1',
                '-update', '1',
                output_file, '-y'
            ]

            # don't care about the output, as subprocess_run will handle any errors and logging
            _ = subprocess_utils.subprocess_run(command)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} using ffmpeg to extract art from {input_path}", stack_info=True)
            raise e_error


    def extract_m4a_art(self, file_path: str) -> None:
        '''
        @brief Extracts cover art from m4a files

        @details Input file is expected to have cover art.

        @param file_path {str} The full path to audio file.

        @exception MutagenError A custom exception in Mutagen occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio = MP4(file_path)
            audio_tags = audio.tags
            cover_tag = audio_tags["covr"]

            # M4A files can have multiple 'covr' atoms, each containing a different image, only want the first, which is the front cover
            artwork = cover_tag[0]

            # Artwork data might be wrapped in format codes; extract the raw data.
            if isinstance(artwork, tuple):
                image_data = artwork[1]
            else:
                image_data = artwork

            self.__write_data(file_path, image_data)

        except MutagenError as m_error:
            logger.error(f"MutagenError {m_error} loading {file_path}", exc_info=True)
            raise m_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} extracting m4a art from {file_path}", stack_info=True)
            raise e_error


    def extract_flac_art(self, file_path: str) -> None:
        '''
        @brief Extracts cover art from FLAC files.

        @details Extracts the front-cover picture when present; otherwise extracts the first embedded picture.

        @param file_path {str} The full path to FLAC file.

        @exception MutagenError A custom exception in Mutagen occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio = FLAC(file_path)
            # Flac saves embedded art in the 'pictures' attribute of the FLAC object, unlike MP3/MP4(m4a)/ASF(wma) which use tags
            cover_picture = next((picture for picture in audio.pictures if picture.type == 3), None)

            if cover_picture is None and audio.pictures:
                cover_picture = audio.pictures[0]

            if cover_picture is not None:
                self.__write_data(file_path, cover_picture.data)

        except MutagenError as m_error:
            logger.error(f"MutagenError {m_error} loading {file_path}", exc_info=True)
            raise m_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} extracting FLAC art from {file_path}", stack_info=True)
            raise e_error


    def extract_mp3_art(self, file_path: str) -> None:
        '''
        @brief Extracts cover art from mp3 files.

        @details Input file is expected to have cover art.

        @param file_path {str} The full path to audio file.

        @exception MutagenError A custom exception in Mutagen occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio = MP3(file_path, ID3=ID3)
            audio_tags = audio.tags

            # technically this would have an issue if there is more than 1 embedded cover art
            for tag in audio_tags.getall('APIC'):
                image_data = tag.data

            self.__write_data(file_path, image_data)

        except MutagenError as m_error:
            logger.error(f"MutagenError {m_error} loading {file_path}", exc_info=True)
            raise m_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} extracting mp3 embedded art from {file_path}", stack_info=True)
            raise e_error


    def extract_walk(self, start_path: str, file_pattern: str) -> None:
        '''
        @brief Extracts all embedded album art from audio files.

        @details If file pattern not specified, returns all valid audio files.<br>
        Otherwise must be a valid audio file extension like '.mp3', '.m4a', '.wma', or '.flac'.

        @param start_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to transform.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        input_file_ext = None

        try:
            if file_pattern and file_pattern not in AUDIO_EXTS:
                logger.warning(f"Pattern {file_pattern} is not for a valid audio file")
                return

            input_path = Path(start_path)

            for dir_path, _, file_names in os.walk(input_path):

                # the tld Music does contain files, but not audio files w/jpg's
                if dir_path == start_path:
                    continue

                # don't need to waste cycles if we have a Folder.jpg from a previous iteration
                dir_contents = os.listdir(dir_path)
                if FOLDER_ART in dir_contents:
                    continue

                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # we don't touch non-audio files like m3u etc
                    if input_file_ext.lower() not in AUDIO_EXTS:
                        continue
                    elif file_pattern:
                        if not fnmatch.fnmatch(input_file_ext.lower(), file_pattern.lower()):
                            continue

                    input_file_path = os.path.join(dir_path, file)
                    self.extract_album_art(input_file_path)

        except Exception as e_error:
            if file_pattern:
                exc_msg = f"Exception {type(e_error).__name__} walking {start_path} to extract art from {file_pattern} audio files"
            else:
                exc_msg = f"Exception {type(e_error).__name__} walking {start_path} to extract art from audio files"

            logger.exception(exc_msg, stack_info=True)
            raise e_error


    def has_video_stream(self, file_path: str) -> bool:
        '''
        @brief Checks if an audio file has a video stream.

        @details Audio files can have embedded art in video streams, embedded art is the first frame.

        @param file_path {str} The full path to audio file.
        @return has_video {boolean} Returns true if video stream is present, false otherwise.

        @exception JSONDecodeError A json decoding error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        '''
        check for stream command explanation:<br>

        ffprobe -hide_banner -select_streams v:0 -show_streams -of json `file_path`<br>
        -hide_banner reduce output clutter<br>
        -select_streams v:0 only want video stream<br>
        -show_streams gets all information about each media stream in the input<br>
        -of json output information in json format<br>
        '''

        try:
            has_stream = False

            command = [
                'ffprobe',
                '-hide_banner',
                '-select_streams', 'v:0',
                '-show_streams',
                '-of', 'json',
                file_path
            ]

            probe_process = subprocess_utils.subprocess_run(command)

            # ffprobe outputs to stdout, unlike ffmpeg
            probe = json.loads(probe_process.stdout)

            for stream in probe['streams']:
                if stream['codec_type'] == 'video':
                    has_stream = True

        except JSONDecodeError as jd_error:
            logger.error(f"JSONDecodeError on audio file: {file_path}", exc_info=True)
            raise jd_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} extracting video stream from {file_path}", stack_info=True)
            raise e_error
        else:
            return has_stream


    def set_album_art(self, input_path: str) -> None:
        '''
        @brief Sets album art file for an album directory.

        @details First check to see a folder art file is present in album directory.<br>
        Second checks if there is a /AlbumArt/<album>.jpg cover art file, renames it to album art folder constant and moves it to album directory.

        @param input_path {str} The full path to album directory.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            for dir_path, dir_names, file_names in os.walk(input_path):
                # the tld Music does contain files, but not audio files w/jpg's
                if dir_path == input_path:
                    continue

                # first level artist directories only contain album directories, and no files
                if not file_names:
                    continue

                # Eg. "C:\Music\Albert Collins\Best Of The Blues, Vol. 1
                album_path = Path(dir_path)
                album_content = os.listdir(album_path)

                if FOLDER_ART in album_content:
                    logger.info(f"Found {FOLDER_ART} in {album_path}")
                    continue

                # check in AlbumArt folder if a jpg for album name exists
                # eg: should be "Best Of The Blues, Vol. 1"
                # eg: should be "Best Of The Blues, Vol. 1.jpg"
                album_dir_name = os.path.basename(dir_path)
                album_jpg = album_dir_name + ".jpg"

                # get the album art directory, per the project hierarchy
                # eg: D:\MusicProcessing\src\generated_files\ALbumArt
                album_art_dir = os.path.join(GENERATED_PATH, ALBUM_ART)
                album_art_dir_content = os.listdir(album_art_dir)

                if album_jpg in album_art_dir_content:
                    album_art_jpg = os.path.join(album_art_dir, album_jpg)
                    # eg: D:\MusicProcessing\src\generated_files\ALbumArt\Best Of The Blues, Vol. 1.jpg
                    # eg: C:\Music\Albert Collins\Best Of The Blues, Vol. 1\Folder.jpg
                    folder_jpg = os.path.join(album_path, FOLDER_ART)
                    shutil.copy(album_art_jpg, folder_jpg)
                else:
                    logger.warning(f"No album art set for {album_path}")

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} setting album art for {input_path}", stack_info=True)
            raise e_error
