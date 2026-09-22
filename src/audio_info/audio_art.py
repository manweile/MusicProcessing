'''
@class AudioArt
@file src/audio_info/audio_art.py
@author Gerald Manweiler

@brief Defines the audio art class.

@details Defines the audio art class used to handle embedded album art in supported audio file formats.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
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

# Third Party Modules
from mutagen._util import MutagenError                      # for handling Mutagen-specific errors
from mutagen.asf import ASF                                 # for handling ASF audio files
from mutagen.flac import FLAC                               # for handling FLAC audio files
from mutagen.id3 import ID3                                 # for handling ID3 tags in MP3 files
from mutagen.mp3 import MP3                                 # for handling MP3 audio files
from mutagen.mp4 import MP4                                 # for handling MP4 audio files

# Local Module Methods
from src import add_module_handler                          # for adding a module-specific handler to the logger

# Local Module Constants
from src import AUDIO_EXTS                                  # for supported audio file extensions
from src import FOLDER_ART                                  # for folder art directory
from src import FLAC_EXT                                    # for FLAC file extension
from src import M4A_EXT                                     # for M4A file extension
from src import MP3_EXT                                     # for MP3 file extension
from src import WMA_EXT                                     # for WMA file extension
from src.generated_files import GENERATED_PATH              # for generated files path

# Local Module Classes
from src.audio_info.audio_metadata import AudioMetadata     # for audio metadata handling functionality
from src.audio_normalize import AudioNormalization          # for audio normalization functionality
from src.subprocess_utils import SubprocessUtilities        # for subprocess utility functions

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

## @var metadata
# @brief Audio metadata instance.
# @details Provides audio metadata functionality.
metadata = AudioMetadata()

## @var normalization
# @brief Audio normalization instance.
# @details Provides audio normalization functionality.
normalization = AudioNormalization()

## @var subprocess_utils
# @brief Subprocess utilities instance.
# @details Provides subprocess utility functionality.
subprocess_utils = SubprocessUtilities()

## @var ALBUM_ART
# @brief Album art directory name.
# @details Identifies the generated directory that stores compilation album art.
ALBUM_ART = "AlbumArt"


class AudioArt():
    '''
    @brief Handles audio album art processing.

    @details Provides methods for extracting, processing, and managing album art associated with audio files.
    '''

    def __init__(self) -> None:
        '''
        @brief Initializes the AudioArt class.

        @details Initializes an AudioArt instance without instance-specific state.
        '''

        pass


    def __unpack_asf_image(self, data: bytearray) -> tuple:
        r'''
        @brief Unpack image data from a WM/Picture tag.

        @details Parses a WM/Picture tag with length-checked UTF-16 fields and image payload.

        @note Based on https://github.com/beetbox/mediafile/blob/master/mediafile/storage/afs.py<br>
        This function is treated as "untrusted", in particular:<br>
        requires at least 5 bytes for struct.unpack_from, or raises struct.error;<br>
        scans for UTF-16 null terminators without a bounds check;<br>
        can loop forever when a terminator is absent: once pos passes the end, data[pos:pos+2] remains b"", which never equals b"\x00\x00";<br>
        decodes arbitrary byte slices as UTF-16, which can raise UnicodeDecodeError;<br>
        reads the declared image size but does not use it to validate or bound the image payload.

        @code{.text}
        An ASF WM/Picture tag starts with a little-endian header:
        b: signed char image type (1 byte).
        i: signed int image size (4 bytes).

        The remaining fields are UTF-16-LE, null-terminated MIME type and description strings, followed by image data.
        The image type 3 identifies a front album cover.

        Example:
          |0-1|1    -     5|5                     -                        25|25 - 27|27 - 29|29                   -              29 + image size|
        b'\x03\x140\x00\x00i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00\x00\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00'

        Bytes 0-1: image type, b'\x03' (front album cover).
        Bytes 1-5: image size, b'\x140\x00\x00' = 0x00003014 little-endian = 12,308 bytes.
        Bytes 5-25: MIME type, b'i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00' = image/jpeg.
        Bytes 25-27: MIME type terminator, b'\x00\x00'.
        Bytes 27-29: empty description and its terminator, b'\x00\x00'.
        Bytes 29 through 29 + image size: image data, beginning b'\xff\xd8\xff\xe0'.
        @endcode

        @param data {bytearray} The byte attribute data from asf audio WM/Picture tag.
        @return unpacked {tuple} Contains the MIME type, raw image data, type indicator, and image description.

        @exception ValueError The WM/Picture data is malformed or truncated.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            if len(data) < 5:
                raise ValueError("WM/Picture data is missing its header")

            image_type, image_size = struct.unpack_from('<bi', data)
            if image_size < 0:
                raise ValueError("WM/Picture image size cannot be negative")

            pos = 5

            # Extract null-terminated UTF-16-LE fields without reading past the supplied data.
            mime_start = pos
            while True:
                if pos + 2 > len(data):
                    raise ValueError("WM/Picture MIME type is missing its terminator")
                if data[pos:pos + 2] == b'\x00\x00':
                    mime = data[mime_start:pos]
                    pos += 2
                    break
                pos += 2

            description_start = pos
            while True:
                if pos + 2 > len(data):
                    raise ValueError("WM/Picture description is missing its terminator")
                if data[pos:pos + 2] == b'\x00\x00':
                    description = data[description_start:pos]
                    pos += 2
                    break
                pos += 2

            image_end = pos + image_size
            if image_end > len(data):
                raise ValueError("WM/Picture image payload is truncated")
            if image_end != len(data):
                raise ValueError("WM/Picture data has unexpected trailing bytes")

            try:
                mime_type = mime.decode("utf-16-le")
                image_description = description.decode("utf-16-le")
            except UnicodeDecodeError as ud_error:
                raise ValueError("WM/Picture text fields are not valid UTF-16-LE") from ud_error

            return mime_type, data[pos:image_end], image_type, image_description

        except ValueError as v_error:
            logger.error("Invalid WM/Picture tag data", exc_info=True)
            raise v_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} unpacking asf image from tag data", stack_info=True)
            raise e_error


    def __write_data(self, file_path, image_data: bytearray):
        '''
        @brief Writes image data for audio file to separate jpeg file.

        @details Writes the extracted image data to the Folder.jpg file in the audio file's album directory.

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

        @details Extracts album art as Folder.jpg in the input audio file's album directory.<br>
        Attempts video-stream extraction first, then format-specific metadata-tag extraction.

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

        @details Uses ffmpeg to extract art from audio files of any supported format.<br>
        Requires the input file to contain a video stream.

        @code{.text}
        extract art command
        ffmpeg -hide_banner -i file_path -an -map 0:v -map_metadata -1 -update 1 output_file -y

        -hide_banner: to reduce output clutter
        -an: specifies ignore audio stream
        -map 0:v: specifies 1st input file use video stream
        -map_metadata -1: specifies discard all alphanumeric metadata from input file
        the use of -map and -map_metadata will result in smaller jpg file than vcodec copy or -c:v copy - empirically tested
        -update 1: specifies overwrite output file with 1 frame from video, the embedded art IS the 1st and only frame from video stream
        -y: to overwrite output file if needed
        @endcode

        @param file_path {str} The full path to audio file.

        @exception Exception A common baseclass exception to handle unforeseen errors.
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
        @brief Extracts cover art from m4a files.

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

        @details Processes all valid audio files when no file pattern is specified.<br>
        Requires a valid audio extension such as '.mp3', '.m4a', '.wma', or '.flac' when a pattern is specified.

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

        @details Detects a video stream that can contain embedded album art as its first frame.

        @code{.text}
        check for stream command
        ffprobe -hide_banner -select_streams v:0 -show_streams -of json file_path

        -hide_banner: reduce output clutter
        -select_streams v:0: only want video stream
        -show_streams: gets all information about each media stream in the input
        -of json: output information in json format
        @endcode

        @param file_path {str} The full path to audio file.
        @return has_stream {bool} True when a video stream is present; otherwise False.

        @exception JSONDecodeError A json decoding error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
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

        @details Skips album directories that already contain a folder-art file.<br>
        Copies a matching generated AlbumArt JPEG into the album directory when it is available.

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
