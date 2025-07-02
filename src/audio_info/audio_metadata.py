'''
@file audio_metadata.py
@brief Defines the audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import ffmpeg
import fnmatch
import gc
import os
import pprint
import shutil
import struct
from pathlib import Path

# third party modules
import mutagen
import pathvalidate
from mutagen.asf import ASF
from mutagen.id3 import APIC, error, ID3, ID3TimeStamp
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4FreeForm
from pydub import AudioSegment
from pydub.utils import mediainfo
from tqdm import tqdm

# local modules
from src import _AUDIO_EXTS, _AUDIO_TYPES
from src.dir_processing import DirectoryProcessing
from src.generated_files import generated_files

gc.enable()

_ALBUM_ART = "AlbumArt"
_ASF = "ASF"
_FOLDER_ART = "Folder.jpg"
_MP3 = "MP3"
_MP4 = "MP4"
_TPOS = "TPOS"
_TYER = "TYER"

# the set of pydub generic metadata keys I want to copy to converted & normalized files
# these keys also correspond to what Windows displays as file information in File Explorer
_GEN_KEYS = {
    'album',                    # must have
    'album_artist',             # nice to have
    'artist',                   # must have
    'comment',                  # nice to have, but a PITA to parse/add
    'compilation',              # nice to have, but not ID3v2.3
    'composer',                 # nice to have
    'copyright',                # nice to have
    'date',                     # must have
    'disc',                     # nice to have
    'genre',                    # must have
    'originalyear'              # nice to have
    'publisher',                # nice to have
    'title',                    # must have
    'track',                    # nice to have
}

# dict of generic to ID3v2.3 (MP3)
_MP3_KEYS = {
    'album': 'TALB',
    'album_artist': 'TPE2',
    'artist': 'TPE1',
    'composer': 'TCOM',
    'copyright': 'TCOP',
    'date': 'TYER',
    'disc': 'TPOS',
    'genre': 'TCON',
    'originalyear': 'TORY',                         # convert to TYER
    'publisher': 'TPUB',
    'title': 'TIT2',
    'track': 'TRCK',
    'originaldate': 'TDOR',                         # ID3v2.4 field to ID3v2.3 TYER
    'release_date': 'TDRC',                         # ID3v2.4 field convert YYYY portion to ID3v2.3 TYER
    'custom_original_year': 'TXXX=originalyear'     # ID3 user defined original year field convert to ID3v2.3 TYER
}

_MP3_TIME_KEYS = {
    'TYER',                                 # preferred key
    'TORY',
    'TDRC',
    'TDOR',
    'TXXX=originalyear'
}

# dict of possible m4a (MP4)
_M4A_KEYS = {
    'album': '\xa9alb',
    'album_artist': 'aART',
    'artist': '\xa9ART',
    'composer': '\xa9wrt',
    'copyright': 'cprt',
    'date': '\xa9day',
    'disc': 'disk',
    'genre': '\xa9gen',
    'originalyear': '----:com.apple.iTunes:originalyear',   # using iTunes filed, mp4 does not have \xa9ory
    'publisher': '----:com.apple.iTunes:LABEL',             # using iTunes field, mp4 does not have \xa9pub
    'title': '\xa9nam',
    'track': 'trkn'
}

_M4A_TIME_KEYS = {
    '\xa9day',                              # preferred key
    '----:com.apple.iTunes:originalyear'
}

# dict of possible wma (ASF)
_WMA_KEYS = {
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

_WMA_TIME_KEYS = {

    'WM/Year',                              # preferred key
    'WM/OriginalReleaseYear'
}


class AudioMetadata():
    '''
    @brief Defines the base metadata processing used by project.
    '''

    def __init__(self):
        '''
        @brief Initializes the AudioMetadata class.

        @details A basic class implementation with no instantiation parameters.

        @return AudioMetadata {instance} An instance of the class.
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


    def __update_id3(self, date_values, id3_tags):
        '''
        @brief Updates tags dictionary with newest year value and ands default disc value if needed.

        @param id3_tags {dict} Source ID3 tags.
        @return output_tags {dict} Updated ID3 tags.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            # want newest date from unique dates found
            if date_values:
                max_date = max(date_values, key=int)
                id3_tags[_TYER] = max_date

            if "TPOS" not in id3_tags:
                id3_tags[_TPOS] = "1/1"

            for key, value in id3_tags.items():
                print(f"key: {key}, value: {value}")

        except Exception as e:
            raise Exception(f"Exception: {e} updating tags")

        return id3_tags


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


    def convert_file(self, file_path):
        '''
        @brief Converts a wma, m4a or mp3 audio file to mp3 audio file.

        @details Converts m4a, mp3 & wma files to mp3 files with ID3v2.3 tags using FFMPEG.
        @details Only the Windows displayable subset of metadata key/values is preserved.
        @details Run create_album_dir function to ensure there are album directories for every audio file.
        @details Then manually review extant album art and create and/or move Folder.jpg, if possible, to each album directory.
        @details Next run extract_art_function to extract embedded art as Folder.jpg if needed, into each album directory.
        @details Finally run set_album_art function to ensure a Folder.jpg exists in each album directory.

        @param file_path {str} The path for audio file to be converted.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            # export_dir = None
            # export_name = None
            # export_path = None

            # input_path = Path(file_path)

            # input_ext = input_path.suffix
            # if input_ext.lower() != _AUDIO_EXTS[0]:
            #     raise Exception(f"File {input_path} is not an {_AUDIO_TYPES[0]}")

            # r'''
            # Ubuntu file path:
            # <anchor><mount point>/<usr>/<drive label>/<tld>/<artist dir>/<album dir>/<song file.ext> = 8 elements
            # <anchor><mount point>/<usr>/<tld>/<artist dir>/<album dir>/<song file.ext> = 7 elements
            # anchor is drive (always an empty string) + root (always a forward slash) Eg. "" + "/" = "/"
            # mount point is either "home" (a hdd) or "media" (an usb)
            # if mount point is media, then usr is immediately followed by drive label, then top level directory
            # if mount point is home, then usr is immediately followed by top level directory

            # Ubuntu from USB stick: "/media/gerald/Lexar/Music/38 Special/Special Forces/38 Special-Caught Up in You.mp3"
            # anchor = "/", mount point = "media", usr = "gerald", drive label = "Lexar", tld = "Music", artist = "38 Special", album = "Special Forces", file = '38 Special-Caught Up in You.mp3"

            # Ubuntu from hdd: "/home/gerald/Music/38 Special/Special Forces/38 Special-Caught Up in You.mp3"
            # anchor = "/", mount point = "home", usr = "gerald", tld = "Music", artist = "38 Special", album = "Special Forces", file = '38 Special-Caught Up in You.mp3"

            # Windows file path:
            # <anchor><tld>\<artist dir>\<album dir>\<song file.ext> = 5 elements
            # anchor is always a drive letter + colon + backslash Eg. C:\, H:\

            # Windows from USB stick: "H:\Music\38 Special\Special Forces\38 Special-Caught Up in You.mp3"
            # anchor = "H:\", tld = "Music", artist = "38 Special", album = "Special Forces", file = '38 Special-Caught Up in You.mp3"

            # Windows from hdd: "C:\Music\38 Special\Special Forces\38 Special-Caught Up in You.mp3"
            # anchor = "C:\", tld = "Music", artist = "38 Special", album = "Special Forces", file = '38 Special-Caught Up in You.mp3"

            # I don't need anchor, mount point, usr, drive label, tld
            # I always need artist dir, album dir, and song file
            # '''
            # # get the full parent w/o filename so I can start removing unnecessary path components
            # input_path_parent = input_path.parent

            # # remove the anchor (ie. / or H:\), have no use for it
            # input_path_parts = input_path_parent.parts[1:]

            # # platform module doesn't help us here, ubuntu has differing paths for hdd (home) vs usb (media), unlike windows
            # # to keep the artist dir and album dir we need to look at the 1st element of our anchor trimmed path parts
            # if input_path_parts[0] == _MEDIA:
            #     # Ubuntu usb is going to have <mount point>/<usr>/<drive label>/<tld>/<artist dir>/<album dir>
            #     # so 6 elements, we don't want elements 0 to 3: 'media', 'gerald', 'Lexar', 'Music'
            #     input_path_components = input_path_parts[4:]
            # elif input_path_parts[0] == _HOME:
            #     # Ubuntu hdd is going to have <mount point>/<usr>/<tld>/<artist dir>/<album dir>
            #     # so 5 elements, we don't want  elements 0 to 2: 'home', 'gerald', 'Music'
            #     input_path_components = input_path_parts[3:]
            # else:
            #     # Windows is going to have <tld>/<artist dir>/<album dir>
            #     # so 3 elements, we don't want element 1: 'Music'
            #     input_path_components = input_path_parts[1:]

            # # using fixed storage path because will always know project structure
            # export_dir = os.path.join(generated_files, _EXPORT_TLD)

            # for component in input_path_components:
            #     export_dir = os.path.join(export_dir, component)

            # # directory is already extant if we are processing multiple songs for the same artist & album
            # if not os.path.exists(export_dir):
            #     os.makedirs(export_dir)

            # # get mp3 extension from package constants
            # export_ext = _AUDIO_EXTS[0]

            # input_name = input_path.stem
            # export_name = input_name + export_ext
            # export_path = os.path.join(export_dir, export_name)
            export_path = DirectoryProcessing.path_info(file_path)

            export_format = _AUDIO_TYPES[0]
            input_format = os.path.splitext(file_path)[1].lower()[1:]
            input_path_stem = os.path.splitext(os.path.basename(file_path))[0]
            input_path_parent = os.path.dirname(file_path)
            print(f"Beginning conversion on {input_path_stem} from {input_format} to {export_format}")
            print(f"Source directory path: {input_path_parent}")
            # input_format = input_path.suffix[1:].lower()
            # print(f"Beginning conversion on {input_path.stem} from {input_format} to {export_format}")
            # print(f"Source directory path: {input_path_parent}")

            '''
            metadata transfer
            I dont want every possible tag, just the subset that Windows will display AND are ID3v2.3

            Comments are ASF/ID3v2.3/MP4, MusicBrainz/MP3Tag/puddletag have difficulty displaying,
            so passing on transferring comment metadata

            Compilation is not ID3v2.3, so passing on transferring compilation metadata

            Date info is most problematic part of metadata, ASF/ID3v2.3/MP4 multiple date type tags,
            the data types could be a full ISO date, or could just be a 4 digit year string,
            so I am formatting any found date values to YYYY and mapping to ID3v2.3 TYER field

            I have manually edited all audio files without date to have 1963 as default
            '''
            metadata_type = self.get_metadata_type(file_path)
            if metadata_type == _ASF:
                format = _ASF
                input_tags = self.get_wma_tags(file_path)
                tags = self.map_wma_tags(input_tags)
            elif metadata_type == _MP3:
                format = _MP3
                input_tags = self.get_mp3_tags(file_path)
                tags = self.map_mp3_tags(input_tags)
            elif metadata_type == _MP4:
                format = _MP4
                input_tags = self.get_m4a_tags(file_path)
                tags = self.map_m4a_tags(input_tags)

            # get the input file info - want bitrate so can preserve the quality in exported file
            media_info = self.get_media_info(file_path)
            bitrate = media_info['bit_rate']

            '''
            If a song has does have embedded art, ffmpeg will NOT auto transfer it.
            Therefore all audio files must have co-located cover art.
            '''
            cover = os.path.join(input_path_parent, _FOLDER_ART)

            if metadata_type == _MP3:
                audio_segment = AudioSegment.from_mp3(file_path)
            elif metadata_type == _MP4:
                audio_segment = AudioSegment.from_file(file_path, format=format)
            elif metadata_type == _ASF:
                # pydub doesn't know about wma/asf, so no format forces an autodetect
                audio_segment = AudioSegment.from_file(file_path)

            # the id3v2 version = 3 is important!
            # both pydub (AudioSegment) and mutagen (MP3) need it
            # and both documentations don't really mention it
            audio_segment.export(export_path, export_format, bitrate=bitrate, tags=tags, id3v2_version='3')

            # Add or update album art
            try:
                audio_tags = MP3(export_path, ID3=ID3, v2_version=3)
                audio_tags.add_tags()
            except error:
                pass                        # Tags already exist

            with open(cover, "rb") as album_art_file:
                audio_tags.tags.add(
                    APIC(
                        encoding=3,         # UTF-8
                        mime="image/jpeg",
                        type=3,             # Front Cover
                        desc="Cover",
                        data=album_art_file.read()
                    )
                )
            audio_tags.save(v2_version=3)

        except Exception as e:
            raise Exception(f"Exception {e} converting {file_path} to {export_path}")


    def convert_walk(self, start_path, file_pattern):
        '''
        @brief Converts all audio files found in specified path to mp3 format.

        @details Converts m4a, mp3 & wma files to mp3 files with ID3v2.3 tags using FFMPEG.
        @details Only the Windows displayable subset of metadata key/values is preserved.

        @param start_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to transform.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        input_file_ext = None

        try:
            input_path = Path(start_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # file is not mp3, m4a, or wma, so carry on to next file
                    if input_file_ext.lower() not in _AUDIO_EXTS:
                        continue
                    elif file_pattern:
                        if not fnmatch.fnmatch(file, file_pattern.lower()):
                            continue

                    input_file_path = os.path.join(dir_path, file)
                    self.convert_file(input_file_path)

        except Exception as e:
            if file_pattern:
                raise Exception(f"Exception {e} walking {start_path} to convert {file_pattern} audio files to mp3")
            else:
                raise Exception(f"Exception {e} walking {start_path} to convert audio files to mp3")


    def create_album_dir(self, start_path):
        '''
        @brief Creates an album sub-directory in an artist directory.

        @details Creates the album sub directory for the artist if needed.
        @details The album name for the directory is drawn from the album metadata field.
        @details Also creates csv of all audio file paths, album metadata values and sanitized album directory names.

        @param start_path {str} The tld holding music files.
        @param file_path {str} The full path to audio file.
        @exception ValueError An inappropriate argument value of correct type error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        album_dirs = set()
        data = []
        csv_filename = "created_album_dirs.csv"
        header_row = ["audio file path", "album metadata", "album directory"]

        try:
            dir_processing = DirectoryProcessing(start_path)

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
                    print(f"{tld_item_path} is an empty artist directory")
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
                    if file_ext.lower() in _AUDIO_EXTS:
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
                        dir_processing.make_album_dir(tld_item_path, album_dir)

                        # now transfer the audio file to new album directory
                        destination_dir = os.path.join(tld_item_path, album_dir)
                        dir_processing.move_audio_file(audio_file, destination_dir)
                    else:
                        print(f"{audio_file} is missing album metadata")
                        continue

                tld_bar.update(1)

            tld_bar.close()
            dir_processing.create_csv(csv_filename, data, generated_files, header_row, 0)
            print(f"Created {len(album_dirs)} album dirs")
        except ValueError as e:
            raise Exception(f"ValueError {e} sanitizing album metadata {album}")
        except Exception as e:
            raise Exception(f"Exception {e} creating sub-dirs for {start_path}")


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
        @exception Error A ffmpeg error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # map argument specifies which input stream(s) should be included in the output.
        # by default, the covert art is the first (and only frame) of the of the (only) video stream.
        # 0: Refers to the first input file (index 0).
        # v: Refers to the video stream within that input file.
        # results in only including the video stream from the first input file in the output,
        # discarding any other streams (audio or video).
        map = '0:v'

        # map_metadata controls how metadata is handled.
        # -1: discard all alphanumeric metadata from the input.
        # results in no copying of metadata from input file to output image.
        map_metadata = '-1'

        try:
            input_path = Path(file_path)
            album_path = input_path.parent

            input_stream = ffmpeg.input(input_path)
            output_file = os.path.join(album_path, _FOLDER_ART)
            output_stream = ffmpeg.output(input_stream, output_file, map=map, map_metadata=map_metadata)

            # run executes the ffmpeg command
            # quiet prevents output to terminal and captures stdout & stderr for debugging purposes
            # overwrite_output since won't be able to respond to an overwrite y/n prompt
            out, err = ffmpeg.run(output_stream, quiet=True, overwrite_output=True)
            print(f"Album art written from {input_path.name} and saved to {album_path}")
        except ffmpeg.Error as e:
            print(f"An ffmpeg error occurred: {e.stderr.decode()}")
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


    def get_any_tags(self, file_path):
        '''
        @brief gets tags for any type of audio file.

        @details Any type means m4a, mp3, or wma files.

        @param file_path {str} The full path to audio file.
        @return tags {object} Tag object (one of ID3, MP4Tags, or ASFTags) holding audio file tags or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            tags = None
            audio_file = self.load_any_file(file_path)
            if audio_file is not None and audio_file.tags:
                tags = audio_file.tags
            else:
                raise ValueError(f"Returned None loading audio file: {file_path}")
        except Exception as e:
            raise Exception(f"Exception: {e} getting metadata type for file: {file_path}")

        return tags


    def get_m4a_tags(self, file_path):
        '''
        @brief gets tag information for an m4a audio file.

        @param file_path {str} The full path to m4a audio file.
        @return tag_info {MP4Tags} Tag object holding audio file tag info or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            tag_info = None
            audio_file = self.load_m4a_file(file_path)
            if audio_file is not None:
                tag_info = audio_file.tags
            else:
                raise ValueError(f"Returned None loading audio file: {file_path} ")
        except Exception as e:
            raise Exception(f"Exception {e} getting tags for file {file_path}")

        return tag_info


    def get_media_info(self, file_path):
        '''
        @brief Gets media info.

        @details Uses ffmpeg to get all media info from any valid audio file.

        @param file_path {str} The full path to audio file.
        @return media_info {dict} Media info (codec, duration, size, bitrate...) from filepath.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            media_info = None
            media_info = mediainfo(file_path)
        except Exception as e:
            raise Exception(f"Exception {e} getting media info for file {file_path}")

        return media_info


    def get_media_info_walk(self, start_path, file_pattern):
        '''
        @brief Pretty prints tags for audio files.

        @param file_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to get tags from.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            for dir_path, _, file_names in os.walk(start_path):
                # the tld Music does contain files, but not audio files
                if dir_path == start_path:
                    continue

                for file in file_names:
                    input_file, input_file_ext = os.path.splitext(file)

                    # file is not mp3, m4a, or wma, so carry on to next file
                    if input_file_ext.lower() not in _AUDIO_EXTS:
                        continue
                    elif file_pattern:
                        if not fnmatch.fnmatch(file, file_pattern.lower()):
                            continue

                    input_file_path = os.path.join(dir_path, file)

                    media_info = self.get_media_info(input_file_path)
                    if media_info:
                        for key, value in media_info.items():
                            if isinstance(value, dict):
                                continue
                            else:
                                print(f"key: {key}, value: {value}")
                    else:
                        raise ValueError(f"Returned None getting info for audio file: {input_file_path} ")

                    print("\r\n")

        except Exception as e:
            raise Exception(f"Exception {e} getting media info for file {input_file_path}")


    def get_media_tags(self, file_path):
        '''
        @brief Gets media tags.

        @details Uses ffmpeg to get tags from any valid audio file.

        @param file_path {str} The full path to audio file.
        @return media_tags {dict} Media tags from filepath.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            media_tags = None
            media_info = mediainfo(file_path)
            if media_info:
                media_tags = media_info['TAG']
        except Exception as e:
            raise Exception(f"Exception {e} getting media tags for file {file_path}")

        return media_tags


    def get_metadata_type(self, file_path):
        '''
        @brief Returns the metadata type of any audio file.

        @param file_path {str} The full path to audio file.
        @return metadata_type {str} The type of the audio file metadata tags or None.
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
                return None
        except Exception as e:
            raise Exception(f"Exception: {e} getting metadata type for file: {file_path}")

        return metadata_type


    def get_mp3_tags(self, file_path):
        '''
        @brief Gets tag information for an mp3 audio file.

        @param file_path {str} The full path to mp3 audio file.
        @return tag_info {ID3} Tag object holding audio file tag info or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            tag_info = None
            audio_file = self.load_mp3_file(file_path)
            if audio_file is not None:
                tag_info = audio_file.tags
            else:
                raise ValueError(f"Returned None loading audio file: {file_path}")
        except Exception as e:
            raise Exception(f"Exception {e} getting tags for file {file_path}")

        return tag_info


    # def get_sample_rate(self, file_path):
    #     '''
    #     @brief Gets the sample rate from audio file.

    #     @param file_path {str} The full path to audio file.
    #     @return sample_rate {int} The sample rate in Hz, otherwise None.
    #     @exception Exception A common baseclass exception to handle unforeseen errors.
    #     '''

    #     try:
    #         sample_rate = None
    #         probe = ffmpeg.probe(file_path)
    #         audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)

    #         if audio_stream and 'sample_rate' in audio_stream:
    #             sample_rate = int(audio_stream['sample_rate'])

    #     except ffmpeg.Error as e:
    #         raise Exception(f"An ffmpeg error occurred: {e.stderr.decode()}")
    #     except Exception as e:
    #         raise Exception(f"Exception {e} getting sample rate for file {file_path}")

    #     return sample_rate


    def get_tags_walk(self, file_path, file_pattern, ffprobe=False):
        '''
        @brief Pretty prints tags for audio files.

        @param file_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to get tags from.
        @param ffprobe {bool} Optional, return ffprobe tags instead of mutagen tags.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            input_tags = None
            for dir_path, _, file_names in os.walk(file_path):
                # the tld Music does contain files, but not audio files
                if dir_path == file_path:
                    continue

                for file in file_names:
                    input_file, input_file_ext = os.path.splitext(file)

                    # we don't touch non-audio files like jpg's
                    if input_file_ext.lower() not in _AUDIO_EXTS:
                        continue

                    if file_pattern and not fnmatch.fnmatch(file, file_pattern.lower()):
                        continue
                    else:
                        tag_file_path = os.path.join(dir_path, file)

                        if ffprobe:
                            input_tags = self.get_media_tags(tag_file_path)
                        else:
                            metadata_type = self.get_metadata_type(tag_file_path)
                            if metadata_type == _ASF:
                                input_tags = self.get_wma_tags(tag_file_path)
                            elif metadata_type == _MP3:
                                input_tags = self.get_mp3_tags(tag_file_path)
                            elif metadata_type == _MP4:
                                input_tags = self.get_m4a_tags(tag_file_path)

                        if input_tags:
                            if ffprobe:
                                print(f"{tag_file_path} has {len(input_tags)} ffprobe tags")
                                # want one key/value pair per line
                                pprint.pprint(input_tags)
                                print()
                            else:
                                print(f"{tag_file_path} has {len(input_tags)} {metadata_type} tags")
                                # mutagen returns tags as ASFTags, ID3Tags, MP4Tags objects
                                # not as a simple dict of string key/value
                                # so need mutagen pprint and splitlines to "format" into simple dict
                                pprint.pprint(input_tags.pprint().splitlines())
                                print()
                        else:
                            print(f"{tag_file_path} has no metadata")
        except Exception as e:
            raise Exception(f"Exception {e} getting tags for file {file_path}")


    # def get_volume_info(self, file_path):
    #     '''
    #     @brief Gets mean and max volume from audio file using ffmpeg.

    #     @param file_path {str} The full path to audio file.
    #     @return volumes {dict} The mean and max
    #     @exception Exception A common baseclass exception to handle unforeseen errors.
    #     '''

    #     try:
    #         volumes = dict()

    #         command = [
    #             'ffmpeg',
    #             '-i', file_path,
    #             '-hide_banner',
    #             '-filter:a', 'volumedetect',
    #             '-f', 'null',
    #             '-'                             # Send output to stdout
    #         ]

    #         # Run FFmpeg and capture stderr (where volumedetect output goes)
    #         process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #         stdout, stderr = process.communicate()

    #         # Decode stderr to string and search for volume information
    #         output_str = stderr.decode('utf-8')

    #         mean_volume_match = re.search(r'mean_volume: ([-]?\d+\.\d+) dB', output_str)
    #         max_volume_match = re.search(r'max_volume: ([-]?\d+\.\d+) dB', output_str)

    #         if mean_volume_match and max_volume_match:
    #             mean_volume = float(mean_volume_match.group(1))
    #             max_volume = float(max_volume_match.group(1))
    #             volumes['mean_volume'] = mean_volume
    #             volumes['max_volume'] = max_volume

    #     except Exception as e:
    #         raise Exception(f"Exception {e} getting volume for file {file_path}")

    #     return volumes


    def get_wma_tags(self, file_path):
        '''
        @brief gets tag information for an wma audio file.

        @param file_path {str} The full path to wma audio file.
        @return tag_info {ASFTags} Tag object holding audio file tag info or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            tag_info = None
            audio_file = self.load_wma_file(file_path)
            if audio_file is not None:
                tag_info = audio_file.tags
            else:
                raise ValueError(f"Returned None loading audio file: {file_path}")
        except Exception as e:
            raise Exception(f"Exception {e} getting tags for file {file_path}")

        return tag_info


    def get_unique_media_keys(self, file_path):
        '''
        @brief Gets set of ffprobe keys.

        @details Walks from starting path and saves set of unique metadata keys found by ffprobe.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

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
                    if input_file_ext.lower() not in _AUDIO_EXTS:
                        continue

                    tag_file_path = os.path.join(dir_path, file)
                    input_tags = self.get_media_tags(tag_file_path)
                    file_keys = input_tags.keys()
                    if file_keys:
                        unique_keys.update(file_keys)

            print(sorted(unique_keys))
        except Exception as e:
            raise Exception(f"Exception {e} getting tags for file {file_path}")


    def has_art_tag(self, file_path):
        '''
        @brief Checks if an audio file has the embedded album art tag.

        @param file_path {str} The full path to audio file.
        @return has_art {boolean} Returns true if art tag is present, false otherwise.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            has_art = False
            file_name, file_ext = os.path.splitext(file_path)

            if file_ext.lower() not in _AUDIO_EXTS:
                raise Exception(f"File: {file_name} has invalid extension: {file_ext}")

            audio_tags = self.get_any_tags(file_path)

            if audio_tags is None:
                raise Exception(f"File: {file_name} has no metadata")

            if 'WM/Picture' in audio_tags:
                has_art = True
            elif 'covr' in audio_tags:
                has_art = True
            elif 'APIC:' in audio_tags:
                has_art = True
        except Exception as e:
            raise Exception(f"Exception {e} checking for album art tag in file {file_path}")

        return has_art


    def has_video_stream(self, file_path):
        '''
        @brief Checks if an audio file has a video stream.

        @details Audio files can have embedded art in video streams.
        @details Embedded art is the first frame.

        @param file_path {str} The full path to audio file.
        @return has_video {boolean} Returns true if video stream is present, false otherwise.
        @exception Error A ffmpeg error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            has_stream = False
            probe = ffmpeg.probe(file_path)
            for stream in probe['streams']:
                if stream['codec_type'] == 'video':
                    has_stream = True
        except ffmpeg.Error as e:
            print(f"An ffmpeg error occurred: {e.stderr.decode()}")
        except Exception as e:
            raise Exception(f"Exception {e} extracting art from {file_path}")

        return has_stream


    def load_any_file(self, file_path):
        '''
        @brief loads any valid audio file type.

        @details Expects a valid filepath to an acceptable audio file.

        @param file_path {str} The full file path for audio file.
        @return audio_file {FileType} Instance for the input audio file type or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio_file = None
            audio_file = mutagen.File(file_path)
            if audio_file is None:
                return None
        except Exception as e:
            raise Exception(f"Exception {e} loading audio file: {file_path}")

        return audio_file


    def load_m4a_file(self, file_path):
        '''
        @brief Loads an m4a audio file.

        @details Expects a valid filepath to a m4a type audio file.

        @param file_path {str} The full file path for audio file.
        @return audio_file {FileType} Instance for the input audio file type or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio_file = None
            if file_path.lower().endswith('.m4a'):
                audio_file = MP4(file_path)
                if audio_file is None:
                    return None
        except Exception as e:
            raise Exception(f"Exception {e} loading audio file: {file_path}")

        return audio_file


    def load_mp3_file(self, file_path):
        '''
        @brief Loads an mp3 audio file.

        @details Expects a valid filepath to a mp3 type audio file.

        @param file_path {str} The full file path for audio file.
        @return audio_file {FileType} Instance for the input audio file type or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio_file = None
            if file_path.lower().endswith('.mp3'):
                audio_file = MP3(file_path)
                if audio_file is None:
                    return None
        except Exception as e:
            raise Exception(f"Exception {e} loading audio file: {file_path}")

        return audio_file


    def load_wma_file(self, file_path):
        '''
        @brief Loads an wma audio file.

        @details Expects a valid filepath to a wma type audio file.

        @param file_path {str} The full file path for audio file.
        @return audio_file {FileType} Instance for the input audio file type or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            audio_file = None
            if file_path.lower().endswith('.wma'):
                audio_file = ASF(file_path)
                if audio_file is None:
                    return None
        except Exception as e:
            raise Exception(f"Exception {e} loading audio file: {file_path}")

        return audio_file


    # def loudness_normalize_file(self, file_path):
    #     '''
    #     @todo complete or abandon
    #     @brief Normalizes audio file level.

    #     @details

    #     @param file_path {str} The full file path for audio file.
    #     @param target_dbfs {float} The target loudness.
    #     @exception Exception A common baseclass exception to handle unforeseen errors.
    #     '''

    #     try:
    #         # 1st pass to get loudnorm statistics

    #         # 2nd pass to apply loudnorm statistics

    #         pass
    #     except Exception as e:
    #         raise Exception(f"Exception {e} normalizing audio file: {file_path}")


    def map_m4a_tags(self, input_tags):
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
            for metadata_field, m4a_value in _M4A_KEYS.items():
                m4a_tag = input_tags.get(m4a_value)

                if m4a_tag:
                    mp3_key = _MP3_KEYS[metadata_field]
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
                    if isinstance(metadata_value, str) and m4a_value in _M4A_TIME_KEYS:
                        # just in case string is "YYYY-MM-DD"
                        date_value = metadata_value[0:4]
                        date_values.add(date_value)
                        print(f"metadata: {metadata_field:<20} - m4a key: {m4a_value:<35} - id3 key: {mp3_key} - value: {date_value}")
                        continue

                    # m4a doesn't have a "native" original year field like "\xa9ory",
                    # relies on the iTunes field ----:com.apple.iTunes:originalyear,
                    # so need additional step to decode from MP4FreeForm
                    if isinstance(metadata_value, MP4FreeForm) and m4a_value in _M4A_TIME_KEYS:
                        decode_value = input_tags[m4a_value][0].decode()
                        # just in case string is "YYYY-MM-DD"
                        date_value = decode_value[0:4]
                        date_values.add(date_value)
                        print(f"metadata: {metadata_field:<20} - m4a key: {m4a_value:<35} - id3 key: {mp3_key} - value: {date_value}")
                        continue

                    # m4a supposedly has native publisher "\xa9pub", but not seen in my collection
                    # I do have iTunes "----:com.apple.iTunes:LABEL" field
                    if isinstance(metadata_value, MP4FreeForm) and m4a_value == "----:com.apple.iTunes:LABEL":
                        tag_value = input_tags[m4a_value][0].decode()

                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    print(f"metadata: {metadata_field:<20} - m4a key: {m4a_value:<35} - id3 key: {mp3_key} - value: {tag_value}")
                    id3_tags[mp3_key] = tag_value

            id3_tags = self.__update_id3(date_values, id3_tags)

        except Exception as e:
            raise Exception(f"Exception {e} converting m4a tags")

        return id3_tags


    def map_mp3_tags(self, input_tags):
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
            for metadata_field, mp3_value in _MP3_KEYS.items():

                mp3_tag = input_tags.get(mp3_value)
                if mp3_tag:
                    mp3_key = _MP3_KEYS[metadata_field]
                    metadata_value = input_tags[mp3_value].text[0]

                    # need to get all possible date years into set, but not add to output dict just yet
                    if isinstance(metadata_value, ID3TimeStamp) and (mp3_value in _MP3_TIME_KEYS):
                        # just in case string is "YYYY-MM-DD"
                        date_value = metadata_value.text[0:4]
                        date_values.add(date_value)
                        print(f"metadata: {metadata_field:<20} - mp3 key: {mp3_value:<10} - id3 key: {mp3_key} - value: {date_value}")
                        continue

                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    print(f"metadata: {metadata_field:<20} - mp3 key: {mp3_value:<10} - id3 key: {mp3_key} - value: {tag_value}")
                    id3_tags[mp3_key] = tag_value

            id3_tags = self.__update_id3(date_values, id3_tags)

        except Exception as e:
            raise Exception(f"Exception {e} converting mp3 tags to id3 tags")

        return id3_tags


    def map_wma_tags(self, input_tags):
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
            for metadata_field, wma_value in _WMA_KEYS.items():
                wma_tag = input_tags.get(wma_value)

                if wma_tag:
                    mp3_key = _MP3_KEYS[metadata_field]
                    metadata_value = input_tags[wma_value][0].value

                    # need to get all possible date years into set, but not add to output dict just yet
                    if isinstance(metadata_value, str) and (wma_value in _WMA_TIME_KEYS):
                        # just in case string is "YYYY-MM-DD"
                        date_value = metadata_value[0:4]
                        date_values.add(date_value)
                        print(f"metadata: {metadata_field:<20} - wma key: {wma_value:<35} - id3 key: {mp3_key} - value: {date_value}")
                        continue

                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    # track num is int
                    if isinstance(metadata_value, int):
                        tag_value = metadata_value

                    print(f"metadata: {metadata_field:<20} - wma key: {wma_value:<35} - id3 key: {mp3_key} - value: {tag_value}")
                    id3_tags[mp3_key] = tag_value

            id3_tags = self.__update_id3(date_values, id3_tags)

        except Exception as e:
            raise Exception(f"Exception {e} converting wma tags to id3 tags")

        return id3_tags


    # def peak_normalize_file(self, file_path):
    #     '''
    #     @brief Peak normalizes audio file level.

    #     @details Automatically finds peak amplitude ands scales entire audio to maximize peak without clipping.
    #     @details Audio file must be mp3 format.

    #     @param file_path {str} The full file path for audio file.
    #     @exception Exception A common baseclass exception to handle unforeseen errors.
    #     '''

    #     try:
    #         export_dir = None
    #         export_name = None
    #         export_path = None

    #         input_path = Path(file_path)

    #         input_ext = input_path.suffix
    #         if input_ext.lower() != _AUDIO_EXTS[0]:
    #             raise Exception(f"File {input_path} is not an {_AUDIO_TYPES[0]}")

    #         print(f"Beginning normalization on {input_path} using ffmpeg-normalize.")

    #         # get the full parent w/o filename so I can start removing unnecessary path components
    #         input_path_parent = input_path.parent
    #         # remove the anchor (ie. / or H:\), have no use for it
    #         input_path_parts = input_path_parent.parts[1:]

    #         # platform module doesn't help us here, ubuntu has differing paths for hdd (home) vs usb (media), unlike windows
    #         # to keep the artist dir and album dir we need to look at the 1st element of our anchor trimmed path parts
    #         if input_path_parts[0] == "media":
    #             # Ubuntu usb is going to have <mount point>/<usr>/<drive label>/<tld>/<artist dir>/<album dir>
    #             # so 6 elements, we don't want elements 0 to 3: 'media', 'gerald', 'Lexar', 'Music'
    #             input_path_components = input_path_parts[4:]
    #         elif input_path_parts[0] == "home":
    #             # Ubuntu hdd is going to have <mount point>/<usr>/<tld>/<artist dir>/<album dir>
    #             # so 5 elements, we don't want  elements 0 to 2: 'home', 'gerald', 'Music'
    #             input_path_components = input_path_parts[3:]
    #         else:
    #             # Windows is going to have <tld>/<artist dir>/<album dir>
    #             # so 3 elements, we don't want element 1: 'Music'
    #             input_path_components = input_path_parts[1:]

    #         # using fixed storage path because will always know project structure
    #         export_dir = os.path.join(generated_files, _EXPORT_TLD)

    #         for component in input_path_components:
    #             export_dir = os.path.join(export_dir, component)

    #         # directory is already extant if we are processing multiple songs for the same artist & album
    #         if not os.path.exists(export_dir):
    #             os.makedirs(export_dir)

    #         input_info = self.get_media_info(input_path)
    #         bitrate = input_info['bit_rate']

    #         # sample_rate = self.get_sample_rate(input_path)
    #         volume_info = self.get_volume_info(input_path)
    #         max_volume = volume_info['max_volume']
    #         if max_volume <= -1:
    #             target_level = -1 - max_volume
    #         else:
    #             target_level = -1

    #         export_name = input_path.name
    #         export_path = os.path.join(export_dir, export_name)

    #         # working ubuntu/windows cli:
    #         # ffmpeg-normalize ~/ProcessedMusic/Crush/Here/Crush-Live.mp3 -c:a libmp3lame -b:a 128k --extra-output-options "-id3v2_version 3" --normalization-type peak --target-level 0 -f -o ~/MusicProcessing/src/generated_files/Music/Crush/Here/Crush-Live.mp3
    #         # ffmpeg-normalize F:\ProcessedMusic\Crush\Here\Crush-Live.mp3 -c:a libmp3lame -b:a 128k --extra-output-options "-id3v2_version 3" --normalization-type peak --target-level 0 -f -o D:\MusicProcessing\src\generated_files\Music\Crush\Here\Crush-Live.mp3
    #         # album art and tags are preserved!!!
    #         # the extra output option setting the ID3v2.3 is necessary, else can't preserve embedded art
    #         command = [
    #             "ffmpeg-normalize",
    #             input_path,
    #             "-c:a", "libmp3lame",
    #             "-b:a", bitrate,
    #             "--extra-output-options", r"-id3v2_version 3",
    #             "--normalization-type", "peak",
    #             "--target-level", str(target_level),
    #             "-f", "-o", export_path
    #         ]

    #         text = f"Normalizing {input_path.stem}"
    #         with yaspin(Spinners.dots, text=text, timer=True) as sp:
    #             with open(os.devnull, 'rb') as devnull:
    #                 p = subprocess.Popen(
    #                     command,
    #                     stdin=devnull,
    #                     stdout=subprocess.PIPE,
    #                     stderr=subprocess.PIPE,
    #                     universal_newlines=True
    #                 )

    #             while True:
    #                 line = p.stderr.readline()
    #                 if not line:
    #                     break

    #             p_out, p_err = p.communicate()

    #         print(f"Successful normalization on {input_path.stem} in {sp.elapsed_time} secs\r\n")
    #     except subprocess.CalledProcessError:
    #         raise Exception(
    #             f"ffmpeg-normalize returned error code: {p.returncode}\n\n for command line: {command}\n\n Output from ffmpeg-normalize: {p_err.decode(errors='ignore')}")
    #     except Exception as e:
    #         raise Exception(f"Exception {e} normalizing audio file: {file_path}")


    # def peak_normalize_walk(self, file_path):
    #     '''
    #     @brief Peak normalizes mp3 audio files in under starting top level directory.

    #     @details Automatically finds peak amplitude ands scales entire audio to maximize peak without clipping.

    #     @param file_path {str} The starting point of the directory walk.
    #     @param file_pattern {str} Optional, the audio file pattern we want to get tags from.
    #     @exception Exception A common baseclass exception to handle unforeseen errors.
    #     '''

    #     input_file_ext = None

    #     try:
    #         input_path = Path(file_path)

    #         for dir_path, _, file_names in os.walk(input_path):
    #             for file in file_names:
    #                 _, input_file_ext = os.path.splitext(file)

    #                 # file is not mp3, carry on to next file
    #                 if input_file_ext.lower() != _AUDIO_EXTS[0]:
    #                     continue

    #                 input_file_path = os.path.join(dir_path, file)
    #                 self.peak_normalize_file(input_file_path)

    #     except Exception as e:
    #         raise Exception(f"Exception {e} walking {file_path} to normalize audio files")


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
