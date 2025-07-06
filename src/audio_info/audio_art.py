'''
@file audio_art.py
@brief Defines the audio art class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import ffmpeg
import fnmatch
import gc
import os
import shutil
import struct
import subprocess
from ffmpeg import Error
from pathlib import Path
from subprocess import CalledProcessError

# third party modules
from mutagen.asf import ASF
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4

# local modules
from src import _AUDIO_EXTS
from src.generated_files import generated_files

gc.enable()

_ALBUM_ART = "AlbumArt"
_ASF = "ASF"
_FOLDER_ART = "Folder.jpg"
_MP3 = "MP3"
_MP4 = "MP4"


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

        @details https://github.com/beetbox/mediafile/blob/master/mediafile.py#L243
        @details This function is treated as "untrusted" and could throw all manner of exceptions (out-of-bounds, etc.).

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
        except Exception as e:
            raise Exception(f"Exception {e} extracting embedded art from tag data")


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
                output_file = os.path.join(album_path, _FOLDER_ART)
                with open(output_file, 'wb') as img_file:
                    img_file.write(image_data)
                print(f"Album art written from {input_path.name} and saved to {album_path}")
        except Exception as e:
            raise Exception(f"Exception: {e} writing embedded art from {file_path}")


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
            if _FOLDER_ART in album_contents:
                return

            # we don't touch non-audio files like m3u etc
            input_file_ext = input_path.suffix
            if input_file_ext.lower() not in _AUDIO_EXTS:
                return

            # file with video stream can use audio type agnostic extraction
            if self.has_video_stream(input_path):
                self.extract_ffmpeg_art(input_path)
                return
            else:
                print(f"No video stream album art present in {file_path}")

            # no matter what extraction method, file must have an art tag
            if self.has_art_tag(input_path):
                # each audio file type has different extraction method
                metadata_type = self.get_metadata_type(input_path)
                if metadata_type == _ASF:
                    self.extract_asf_art(file_path)
                elif metadata_type == _MP3:
                    self.extract_mp3_art(file_path)
                elif metadata_type == _MP4:
                    self.extract_m4a_art(file_path)
            else:
                print(f"No album art present in {file_path}")
                return
        except Exception as e:
            raise Exception(f"Exception {e} extracting art from {file_path}")


    def extract_asf_art(self, file_path):
        '''
        @brief Extracts cover art from wma files

        @details Input file is expected to have embedded cover art.

        @param file_path {str} The full path to audio file.
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
        except Exception as e:
            raise Exception(f"Exception: {e} extracting embedded art from {file_path}")


    def extract_ffmpeg_art(self, file_path):
        '''
        @brief Extracts and saves embedded album art.

        @details Uses ffmpeg and is audio file type agnostic.
        @details Input file must have a video stream and an art tag.

        @param file_path {str} The full path to audio file.
        @exception CalledProcessError A subprocess error from ffmpeg command execution.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            input_path = Path(file_path)
            album_path = input_path.parent

            output_file = os.path.join(album_path, _FOLDER_ART)

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

            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Album art extracted from {input_path.name} and saved to {album_path}")
        except CalledProcessError as e:
            raise CalledProcessError(f"Error extracting album art: {e}\n\nFFmpeg output: {e.stderr}")
        except Exception as e:
            raise Exception(f"Exception {e} extracting art from {input_path}")


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
        except Exception as e:
            raise Exception(f"Exception: {e} extracting embedded art from {file_path}")


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
        except Exception as e:
            raise Exception(f"Exception: {e} extracting embedded art from {file_path}")


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
                if _FOLDER_ART in dir_contents:
                    continue

                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)
                    # we don't touch non-audio files like m3u etc
                    if input_file_ext.lower() not in _AUDIO_EXTS:
                        continue

                    if file_pattern and not fnmatch.fnmatch(file, file_pattern.lower()):
                        continue
                    else:
                        input_file_path = os.path.join(dir_path, file)
                        self.extract_album_art(input_file_path)
        except Exception as e:
            if file_pattern:
                raise Exception(f"Exception {e} walking {start_path} to convert {file_pattern} audio files to mp3")
            else:
                raise Exception(f"Exception {e} walking {start_path} to convert audio files to mp3")


    def has_video_stream(self, file_path):
        r'''
        @todo write own ffmpeg.probe
        @todo refer to C:\Users\gmanw\AppData\Local\Programs\Python\Python312\Lib\site-packages\ffmpeg\_probe.py
        @brief Checks if an audio file has a video stream.

        @details Audio files can have embedded art in video streams.
        @details Embedded art is the first frame.

        @param file_path {str} The full path to audio file.
        @return has_video {boolean} Returns true if video stream is present, false otherwise.
        @exception Error A ffmpeg-python module error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            has_stream = False
            probe = ffmpeg.probe(file_path)
            for stream in probe['streams']:
                if stream['codec_type'] == 'video':
                    has_stream = True
        except Error as e:
            print(f"An ffmpeg error occurred: {e.stderr.decode()}")
        except Exception as e:
            raise Exception(f"Exception {e} extracting art from {file_path}")

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

                album_path = Path(dir_path)                     # Eg. "C:\Music\Albert Collins\Best Of The Blues, Vol. 1
                album_content = os.listdir(album_path)

                if _FOLDER_ART in album_content:
                    continue

                # check in AlbumArt folder if a jpg for album name exists
                album_dir_name = os.path.basename(dir_path)     # should be "Best Of The Blues, Vol. 1"
                album_jpg = album_dir_name + ".jpg"             # should be "Best Of The Blues, Vol. 1.jpg"

                # get the album art directory, per the project hierarchy
                album_art_dir = os.path.join(generated_files, _ALBUM_ART)
                album_art_dir_content = os.listdir(album_art_dir)

                if album_jpg in album_art_dir_content:
                    album_art_jpg = os.path.join(album_art_dir, album_jpg)
                    folder_jpg = os.path.join(album_path, _FOLDER_ART)
                    shutil.copy(album_art_jpg, folder_jpg)
                    print(f"Set {album_art_jpg} as {_FOLDER_ART} for {album_path}")
                else:
                    print(f"No album art set for {album_path}")
        except Exception as e:
            raise Exception(f"Exception {e} setting album art for {album_path}")
