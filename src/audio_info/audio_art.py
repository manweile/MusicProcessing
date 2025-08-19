'''
@file audio_art.py
@brief Defines the audio art class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import fnmatch
import gc
import json
import logging
import os
import shutil
import struct
from json import JSONDecodeError
from os import strerror
from pathlib import Path

# third party modules
from mutagen.asf import ASF
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen._util import MutagenError

# local modules
from src import AUDIO_EXTS
from src import FOLDER_ART
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging constants
from src.generated_files import GENERATED_FILES
from src.audio_normalize import AudioNormalization
from src.subprocess_utils import SubprocessUtilities
# relative import so don't get circular import error
from .audio_metadata import AudioMetadata

gc.enable()

metadata = AudioMetadata()
normalization = AudioNormalization()
subprocess_utils = SubprocessUtilities()

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

ALBUM_ART = "AlbumArt"


class AudioArt():
    '''
    @brief Defines the base art processing class used by project.
    '''

    def __init__(self):
        '''
        @brief Initializes the AudioArt class.

        @details A basic class implementation with no instantiation parameters.

        @return AudioArt {instance} An instance of the class.
        '''

        pass


    def __unpack_asf_image(self, data):
        '''
        @brief Unpack image data from a WM/Picture tag.

        @details https://github.com/beetbox/mediafile/blob/master/mediafile.py#L243.
        @details This function is treated as "untrusted" and could throw all manner of exceptions (out-of-bounds, etc.).

        @param data {bytearray} The byte attribute data from asf audio WM/Picture tag.
        @return (mime, image_data, type, description) ({str}, {bytes}, {int}, {str}) Tuple containing the MIME type, the raw image data, a type indicator, and
        the image's description.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            r'''
            <:little-endian byte order, b: signed char (1 byte), i: signed int (4 bytes)
            unpacks first 5 bytes in tuple where type is C signed char (1 byte)/Python integer and size is C signed int (4 bytes)/Python integer
            for an ASF WM/Picture, 3 = Front album cover
            eg. b'\x03\x140\x00\x00i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00\x00\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`
            image type and image size, elements 0-5: b'\x03\x140\x00\x00
            image type, elements 0-1, b'\x03'
            image size, elements 1-5, b'\x140\x00\x00 = 0x1403 little-endian, 0x3014 big-endian, decimal 12308
            mime type, elements 5 to 25: b'i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00'
            null terminator, elements 25 to 27: b'\x00\x00'
            description, elements 27 to 29: b'\x00\x00'
            data, elements 29 to 29 + size: b'\xff\xe0\x...'
            '''
            type, size = struct.unpack_from('<bi', data)
            pos = 5
            mime = b''

            while data[pos:pos + 2] != b'\x00\x00':
                mime += data[pos:pos + 2]
                pos += 2

            pos += 2
            description = b''
            while data[pos:pos + 2] != b'\x00\x00':
                description += data[pos:pos + 2]
                pos += 2

            pos += 2
            image_data = data[pos:pos + size]

            return (mime.decode("utf-16-le"), image_data, type, description.decode("utf-16-le"))

        except struct.error as s_error:
            logger.error("Struct unpacking from error", exc_info=True)
            raise s_error
        except UnicodeDecodeError as ud_error:
            logger.exception("UnicodeDecodeError decoding asf image from tag data", stack_info=True)
            raise ud_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} unpacking asf image from tag data", stack_info=True)
            raise e_error


    def __write_data(self, file_path, image_data):
        '''
        @brief Writes image data for audio file to separate jpeg file.

        @param file_path {str} The full path to audio file.
        @param image_data {bytearray} The image bytes extracted from audio file.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            if image_data:
                input_path = Path(file_path)
                album_path = input_path.parent
                output_file = os.path.join(album_path, FOLDER_ART)

                with open(output_file, 'wb') as img_file:
                    img_file.write(image_data)

                logger.info(f"Album art written from {input_path.name} and saved to {album_path}")

        except BlockingIOError as bio_error:
            logger.error(f"BlockingIOError writing image data to {file_path}", exc_info=True)
            raise bio_error
        except OSError as os_error:
            logger.error(f"OSError {(strerror(os_error.errno))} writing data with {file_path}", exc_info=True)
            raise os_error
        except Exception as e_error:
            logger.exception(f"Exception writing image data from {file_path}", stack_info=True)
            raise e_error


    def extract_album_art(self, file_path):
        '''
        @brief Extract and save embedded album art.

        @details Extracts art as Folder.jpg to album directory of input audio file.
        @details First tries extraction from video stream (audio file type agnostic),
        then by metadata art tag (from specific audio file type).

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
                logger.info(f"{input_path.name} is not an audio file")
                return

            # primary extraction method because it is is file type agnostic
            # file with video stream can use audio type agnostic extraction
            if self.has_video_stream(input_path):
                self.extract_ffmpeg_art(input_path)
                return
            else:
                logger.info(f"No video stream album art present in {file_path}")

            # secondary extraction method because it is dependent on file type
            # and file must have an art metadata tag
            if metadata.has_art_tag(input_path):
                if input_file_ext.lower() == AUDIO_EXTS[0]:
                    self.extract_mp3_art(file_path)
                elif input_file_ext.lower() == AUDIO_EXTS[1]:
                    self.extract_m4a_art(file_path)
                elif input_file_ext.lower() == AUDIO_EXTS[2]:
                    self.extract_asf_art(file_path)
            else:
                logger.warning(f"No metadata tag album art present in {file_path}")
                return

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} extracting album art from {file_path}", stack_info=True)
            raise e_error


    def extract_asf_art(self, file_path):
        '''
        @brief Extracts cover art from wma files.

        @details Input file is expected to have embedded cover art.

        @param file_path {str} The full path to audio file.
        @exception OSError An os path not found or other os error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio = ASF(file_path)
            audio_tags = audio.tags
            pic_tag = audio_tags["WM/Picture"]
            byte_attribute_array = pic_tag[0]
            picture_data = byte_attribute_array.value
            mime_type, image_data, type_indicator, image_description = self.__unpack_asf_image(picture_data)

            self.__write_data(file_path, image_data)

        except MutagenError as m_error:
            # handle mutagen ASF error
            logger.error(f"MutagenError {m_error} loading {file_path}", exc_info=True)
            raise m_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} extracting asf art from {file_path}", stack_info=True)
            raise e_error


    def extract_ffmpeg_art(self, file_path):
        '''
        @brief Extracts and saves embedded album art.

        @details Uses ffmpeg and is audio file type agnostic.
        @details Input file must have a video stream and an art tag.

        @param file_path {str} The full path to audio file.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            input_path = Path(file_path)
            album_path = input_path.parent

            output_file = os.path.join(album_path, FOLDER_ART)

            # -hide_banner to reduce output clutter
            # -an specifies ignore audio stream
            # -map 0:v specifies 1st input file use video stream
            # -map_metadata -1 specifies discard all alphanumeric metadata from input file
            # the use of -map and -map_metadata will result in smaller jpg file than vcodec copy or -c:v copy - empirically tested
            # -update 1 specifies overwrite output file with 1 frame from video
            # (which is all we want, the embedded art IS the 1st and only frame from video stream)
            # -y to overwrite output file if needed
            command = [
                'ffmpeg', '-hide_banner',
                '-i', file_path,
                '-an',
                '-map', '0:v',
                '-map_metadata', '-1',
                '-update', '1',
                output_file, '-y'
            ]

            _ = subprocess_utils.subprocess_run(command)
            logger.info(f"FFMPEG extracted album art from {input_path.name} and saved to {album_path}")

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} using ffmpeg to extract art from {input_path}", stack_info=True)
            raise e_error


    def extract_m4a_art(self, file_path):
        '''
        @brief Extracts cover art from m4a files

        @details Input file is expected to have cover art.

        @param file_path {str} The full path to audio file.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio = MP4(file_path)
            audio_tags = audio.tags
            cover_tag = audio_tags["covr"]
            # M4A files can have multiple 'covr' atoms, each containing a different image.
            # I only want the first, which is the front cover.
            artwork = cover_tag[0]

            # Artwork data might be wrapped in format codes; extract the raw data.
            if isinstance(artwork, tuple):
                image_data = artwork[1]
            else:
                image_data = artwork

            self.__write_data(file_path, image_data)

        except MutagenError as m_error:
            # handle mutagen ASF error
            logger.error(f"MutagenError {m_error} loading {file_path}", exc_info=True)
            raise m_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} extracting m4a art from {file_path}", stack_info=True)
            raise


    def extract_mp3_art(self, file_path):
        '''
        @brief Extracts cover art from wma files.

        @details Input file is expected to have cover art.

        @param file_path {str} The full path to audio file.
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
            # handle mutagen ASF error
            logger.error(f"MutagenError {m_error} loading {file_path}", exc_info=True)
            raise m_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} extracting mp3 embedded art from {file_path}", stack_info=True)
            raise


    def extract_walk(self, start_path, file_pattern):
        '''
        @brief Extracts all embedded album art from audio files.

        @details Extracts embedded art from m4a, mp3, and wma files.

        @param start_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to transform.
        '''

        input_file_ext = None

        try:
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

                    if file_pattern and not fnmatch.fnmatch(file, file_pattern.lower()):
                        continue
                    else:
                        input_file_path = os.path.join(dir_path, file)
                        self.extract_album_art(input_file_path)

        except Exception as e_error:
            if file_pattern:
                exc_msg = f"Exception {type(e_error).__name__} walking {start_path} to extract art from {file_pattern} audio files"
            else:
                exc_msg = f"Exception {type(e_error).__name__} walking {start_path} to extract art from audio files"

            logger.exception(exc_msg, stack_info=True)
            raise


    def has_video_stream(self, file_path):
        '''
        @brief Checks if an audio file has a video stream.

        @details Audio files can have embedded art in video streams.
        @details Embedded art is the first frame.

        @param file_path {str} The full path to audio file.
        @return has_video {boolean} Returns true if video stream is present, false otherwise.
        @exception JSONDecodeError A json decoding error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            has_stream = False

            # -hide_banner reduce output clutter
            # -select_streams v:0 only want video stream
            # -show_streams gets all information about each media stream in the input
            # -of json output information in json format
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


    def set_album_art(self, input_path):
        '''
        @brief Sets album art file for an album directory.

        @details First check to see a folder art file is present in album directory.
        @details Second checks if there is a /AlbumArt/<album>.jpg cover art file,
        renames it to album art folder constant and moves it to album directory.

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

                album_path = Path(dir_path)                                     # Eg. "C:\Music\Albert Collins\Best Of The Blues, Vol. 1
                album_content = os.listdir(album_path)

                if FOLDER_ART in album_content:
                    continue

                # check in AlbumArt folder if a jpg for album name exists
                album_dir_name = os.path.basename(dir_path)                     # should be "Best Of The Blues, Vol. 1"
                album_jpg = album_dir_name + ".jpg"                             # should be "Best Of The Blues, Vol. 1.jpg"

                # get the album art directory, per the project hierarchy
                album_art_dir = os.path.join(GENERATED_FILES, ALBUM_ART)       # D:\MusicProcessing\src\generated_files\ALbumArt
                album_art_dir_content = os.listdir(album_art_dir)

                if album_jpg in album_art_dir_content:
                    album_art_jpg = os.path.join(album_art_dir, album_jpg)     # D:\MusicProcessing\src\generated_files\ALbumArt\Best Of The Blues, Vol. 1.jpg
                    folder_jpg = os.path.join(album_path, FOLDER_ART)          # C:\Music\Albert Collins\Best Of The Blues, Vol. 1\Folder.jpg
                    shutil.copy(album_art_jpg, folder_jpg)
                    logger.info(f"Set {album_art_jpg} as {FOLDER_ART} for {album_path}")
                else:
                    logger.warning(f"No album art set for {album_path}")

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} setting album art for {input_path}", stack_info=True)
            raise
