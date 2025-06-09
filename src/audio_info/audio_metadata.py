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
import shutil
import struct
from pathlib import Path

# third party modules
import mutagen
import pathvalidate
from mutagen.asf import ASF
# from mutagen.id3 import TALB, TPE2, TPE1, COMM, TCOM, TCOP, TYER, TPOS, TCON, TPUB, TIT2, TRCK
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from pydub import AudioSegment
from pydub.utils import mediainfo
from tqdm import tqdm

# local modules
from src import _AUDIO_EXTS, _AUDIO_TYPES
from src.dir_processing import DirectoryProcessing
from src.generated_files import generated_files

gc.enable()

_ALBUM_ART = "AlbumArt"
_EXPORT_TLD = "Music"
_FOLDER_ART = "Folder.jpg"

# the set of pydub generic metadata keys I want to copy to converted & normalized files
# these keys also correspond to what Windows displays as file information in File Explorer
_GEN_KEYS = {
    'album',                    # must have
    'artist',                   # must have
    'date',                     # must have
    'genre',                    # must have
    'title',                    # must have
    'album_artist',             # nice to have
    'comment',                  # nice to have
    'composer',                 # nice to have
    'copyright',                # nice to have
    'disc',                     # nice to have
    'publisher',                # nice to have
    'track'                     # nice to have
}

# set of known date keys in ID3, m4a, wma order
_TIME_KEYS = {
    'TYER',                     # ID3
    'TORY',                     # ID3
    '\xa9day',                  # m4a, MIGHT need to use bytes literal; b'\xa9day'
    'originalyear',             # m4a
    'originaldate',             # m4a
    'WM/OriginalReleaseYear',   # wma
    'WM/OriginalReleaseTime',   # wma
    'WM/Year'                   # wma
}

# set of known art keys in ID3, m4a, wma order
_ART_KEYS = {
    'APIC',                     # ID3
    'covr',                     # m4a
    'WM/Picture'                # wma
}

# dict of generic to ID3v2.3
_MP3_KEYS = {
    'album': 'TALB',
    'album_artist': 'TPE2',
    'artist': 'TPE1',
    'comment': 'COMM',
    'composer': 'TCOM',
    'copyright': 'TCOP',
    'date': 'TYER',
    'disc': 'TPOS',
    'genre': 'TCON',
    'publisher': 'TPUB',
    'title': 'TIT2',
    'track': 'TRCK'
}

# dict of generic to m4a
_M4A_KEYS = {
    'album': '\xa9alb',
    'album_artist': 'aART',
    'artist': '\xa9ART',
    'comment': '\xa9cmt',
    'composer': '\xa9wrt',
    'copyright': 'cprt',
    'date': '\xa9day',
    'disc': 'disk',
    'genre': '\xa9gen',
    'publisher': '\xa9pub',
    'title': '\xa9nam',
    'track': 'trkn'
}

# dict of generic to wma
_WMA_KEYS = {
    'album': 'WM/AlbumTitle',
    'album_artist': 'WM/AlbumArtist',
    'artist': 'Author',
    'comment': 'Description',
    'composer': 'WM/Composer',
    'copyright': 'Copyright',
    'date': 'WM/Year',
    'disc': 'WM/PartofSet',
    'genre': 'WM/Genre',
    'publisher': 'WM/Publisher',
    'title': 'Title',
    'track': 'WM/TrackNumber'
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
        @todo finish
        @brief Converts a wma, m4a or mp3 audio file to mp3 audio file.

        @details Converts m4a, mp3 & wma files to mp3 files with ID3v2.3 tags using FFMPEG.
        @details Only the Windows displayable subset of metadata key/values is preserved.

        @param file_path {str} The path for audio file to be converted.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        export_dir = None
        export_file_name = None
        export_file_path = None

        # get mp3 audio format & extension from package constants
        export_format = _AUDIO_TYPES[0]
        export_file_ext = _AUDIO_EXTS[0]

        r'''
        Ubuntu file path:
        <anchor><mount point>/<usr>/<drive label>/<tld>/<artist dir>/<album dir>/<song file.ext> = 8 elements
        <anchor><mount point>/<usr>/<tld>/<artist dir>/<album dir>/<song file.ext> = 7 elements
        anchor is drive (always an empty string) + root (always a forward slash) Eg. "" + "/" = "/"
        mount point is either "home" (a hdd) or "media" (an usb)
        if mount point is media, then usr is immediately followed by drive label, then top level directory
        if mount point is home, then usr is immediately followed by top level directory

        Windows file path:
        <anchor><tld>\<artist dir>\<album dir>\<song file.ext> = 5 elements
        anchor is always a drive letter + colon + backslash Eg. C:\, H:\

        Ubuntu from USB stick
        "/media/gerald/Lexar/Music/38 Special/Special Forces/38 Special-Caught Up in You.mp3"
        anchor = "/",
        mount point = "media",
        usr = "gerald",
        drive label = "Lexar",
        tld = "Music",
        artist = "38 Special",
        album = "Special Forces",
        file = '38 Special-Caught Up in You.mp3"

        Ubuntu from hdd
        "/home/gerald/Music/38 Special/Special Forces/38 Special-Caught Up in You.mp3"
        anchor = "/",
        mount point = "home",
        usr = "gerald",
        tld = "Music",
        artist = "38 Special",
        album = "Special Forces",
        file = '38 Special-Caught Up in You.mp3"

        Windows from USB stick
        "H:\Music\38 Special\Special Forces\38 Special-Caught Up in You.mp3"
        anchor = "H:\",
        tld = "Music",
        artist = "38 Special",
        album = "Special Forces",
        file = '38 Special-Caught Up in You.mp3"

        Windows from hdd
        "C:\Music\38 Special\Special Forces\38 Special-Caught Up in You.mp3"
        anchor = "C:\",
        tld = "Music",
        artist = "38 Special",
        album = "Special Forces",
        file = '38 Special-Caught Up in You.mp3"

        I don't need anchor, mount point, usr, drive label, tld
        I always need artist dir, album dir, and song file
        '''

        input_path = Path(file_path)
        # get the full parent w/o filename so I can start removing unnecessary path components
        input_path_parent = input_path.parent
        r'''
        /media/gerald/Lexar/Music/38 Special/Special Forces                          # ubuntu usb
        /home/gerald/Music/38 Special/Special Forces                                 # ubuntu hdd
        H:\Music\38 Special\Special Forces                                           # windows usb
        C:\Music\38 Special\Special Forces                                           # windows hdd
        '''

        # remove the anchor (ie. / or H:\), have no use for it
        input_path_parts = input_path_parent.parts[1:]
        '''
        ['media', 'gerald', 'Lexar', 'Music', '38 Special', 'Special Forces']       # ubuntu usb
        ['home', 'gerald', 'Music', '38 Special', 'Special Forces']                 # ubuntu hdd
        ['Music', '38 Special', 'Special Forces']                                   # windows hdd or usb
        '''
        # platform module doesn't help us here, ubuntu has differing paths for hdd (home) vs usb (media), unlike windows
        # to keep the artist dir and album dir we need to look at the 1st element of our anchor trimmed path parts
        if input_path_parts[0] == "media":
            # Ubuntu usb is going to have <mount point>/<usr>/<drive label>/<tld>/<artist dir>/<album dir>
            # so 6 elements, de don't want elements 0 to 3: 'media', 'gerald', 'Lexar', 'Music'
            input_path_components = input_path_parts[4:]
        elif input_path_parts[0] == "home":
            # Ubuntu hdd is going to have <mount point>/<usr>/<tld>/<artist dir>/<album dir>
            # so 5 elements, we don't want  elements 0 to 2: 'home', 'gerald', 'Music'
            input_path_components = input_path_parts[3:]
        else:
            # Windows is going to have <tld>/<artist dir>/<album dir>
            # so 3 elements, we don't want element 1: 'Music'
            input_path_components = input_path_parts[1:]

        # using fixed storage path because will always know project structure
        export_dir = os.path.join(generated_files, _EXPORT_TLD)

        for component in input_path_components:
            export_dir = os.path.join(export_dir, component)

        # directory is already extant if we are processing multiple songs for the same artist & album
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        input_file_name = input_path.stem
        input_file_ext = input_path.suffix
        # if file_ext:
        #     input_file_ext = file_ext
        # else:
        #     input_file_ext = input_path.suffix

        export_file_name = input_file_name + export_file_ext
        export_file_path = os.path.join(export_dir, export_file_name)

        # get the input file info - want bitrate so can preserve the quality in exported file
        file_media_info = mediainfo(file_path)
        file_audio_bitrate = file_media_info['bit_rate']

        '''
        @todo metadata transfer
        I dont want every possible tag that pydub returns, just the subset that Windows will display.
        Iterate over the reported metadata for the file, for every metadata key that is in my set of generic preferred keys,
        get the value and write it to corresponding ID3v2.3 tag
        Eg pydub reported: "album": "Desperado" -> "TALB": "Desperado"
        for key, value in file_media_tags.items():
            if key in _GEN_KEYS:
                print(f"key: {key}, value: {value}")
        '''

        # get the input files metadata from pydub because doing so gives consistent schema
        file_media_tags = file_media_info['TAG']
        export_metadata = {}
        for key, value in file_media_tags.items():
            if key in _GEN_KEYS:
                export_metadata[key] = value

        '''
        date info is most problematic part of metadata
        different audio file types have different date type tags
        and to make things worse, the date could be a full ISO date,
        or could just be a 4 digit year string

        I have manually edited all audio files with puddletag/MP3tag/MusicBrainz Picard to have YYYY date

        FFMPEG will return key 'date' by preference.
        So look for date key in FFMPEG return, if present use it.
        If not present, then look for the various date type tags for mp3, m4a, wma tags
        If multiple hits, use the oldest
        For all successful hits, strip out the YYYY
        If still nothing, then use default year 1963

        if m4a, look for key date, then originalYear, then originalDate
        once I have the info, need to check if is 4 chars or longer
        if longer, just need the 1st 4 chars
        eg from an m4a:
        'date': '2015-05-18T07:00:00Z'
        strip out the 2015

        'date': '2013'
        'originalyear': '1973'
        both are YYYY format, but use oldest date, ie 1973

        'originaldate': '1973-04-17'
        strip out the 1973

        if wma, look for key WM/Year
        'WM/Year': '1976'
        '''

        # get file tag per file type
        # mp3 = ID3v2.3
        # m4a = MP4
        # wma = ASF

        any_file_tags = self.get_any_tags(file_path)
        print(f"Mutagen tags for {file_path}")
        print(any_file_tags.pprint())

        '''
        If a song has does have embedded art, ffmpeg will NOT auto transfer it.
        Many songs have co-located hidden file art, this is a result from all the WMP processing I did.
        I have:
        - created all the required album sub directories with create_album_dir function.
        - moved the audio files
        - manually reviewed existing AlbumArt*.jpg and Folder.jpg files
        - manually moved Folder.jpg to correct album directory
        - if necessary, rename AlbumArt*.jpg to Folder.jpg
        - manually move the renamed Folder.jpg to proper album sub directory
        - create <album dir>.jpg in src/generated_files/Album Art for repeated album names
        End result:
        All album directories will contain a Folder.jpg cover art file
        '''
        cover_art = os.path.join(input_path_parent, _FOLDER_ART)
        try:
            audio_segment = AudioSegment.from_file(file_path)
            audio_segment.export(export_file_path, export_format, bitrate=file_audio_bitrate, tags=export_metadata, id3v2_version='3', cover=cover_art)
            print(f"{input_file_name} converted to {export_format}")
        except Exception as e:
            raise Exception(f"Exception {e} converting {file_path} to {export_file_path}")


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
                    # get the file extension
                    _, input_file_ext = os.path.splitext(file)

                    # file is not mp3, m4a, or wma, so carry on to next file
                    if input_file_ext.lower() not in _AUDIO_EXTS:
                        continue
                    else:
                        input_file_path = os.path.join(dir_path, file)
                        if file_pattern and fnmatch.fnmatch(file, file_pattern):
                            self.convert_file(input_file_path, input_file_ext)
                        elif not file_pattern:
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
        @details The album name for the directory is drawn from the metadata.
        @details Also creates csv of all audio file paths, raw album metadata and album directory names.

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
                        file_media_info = mediainfo(audio_file)
                        file_media_tags = file_media_info['TAG']
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


    def create_tag(self, metadata):
        '''
        @todo finish
        @brief Creates a an ID3v2.3 metadata tag

        @params metadata {dict} Metadata to create tag with.
        @return tag {object} ID3v2.3 tag object.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            pass
        except Exception as e:
            raise Exception(f"Exception {e} creating tag")


    def extract_album_art(self, file_path):
        '''
        @brief Extracts and saves embedded album art.

        @details Check if album folder does not have album art file, ensures file has embedded art, extracts and saves it to album directory.

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
                if metadata_type == "ASF":
                    self.extract_asf_art(file_path)
                elif metadata_type == "MP3":
                    self.extract_mp3_art(file_path)
                elif metadata_type == "MP4":
                    self.extract_m4a_art(file_path)
            else:
                print(f"No album art present in {file_path}")
                return
        except Exception as e:
            raise Exception(f"Exception {e} extracting art from {file_path}")


    def extract_asf_art(self, file_path):
        '''
        @brief Extracts cover art from wma files

        @details Input file is expected to have cover art.

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
        # results in only including the video stream from the first input file in the output, discarding any other streams (audio or video).
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
            # out, err = ffmpeg.run(output_stream, capture_stdout=True, capture_stderr=True, quiet=True, overwrite_output=True)
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

                    if file_pattern and not fnmatch.fnmatch(file, file_pattern):
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
        @brief gets tags for an audio file.

        @param file_path {str} The full path to audio file.
        @return tags {object} Tag object holding audio file tags or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            tags = None
            audio_file = self.load_any_file(file_path)
            if audio_file is not None and audio_file.tags:
                tags = audio_file.tags
            else:
                return None
        except Exception as e:
            raise Exception(f"Exception: {e} getting metadata type for file: {file_path}")

        return tags


    def get_m4a_tags(self, file_path):
        '''
        @brief gets tag information for an m4a audio file.

        @param file_path {str} The full path to m4a audio file.
        @return tag_info {object} Tag object holding audio file tag info or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            tag_info = None
            audio_file = self.load_m4a_file(file_path)
            if audio_file is not None:
                tag_info = audio_file.tags
            else:
                return None
        except Exception as e:
            raise Exception(f"Exception {e} getting tags for file {file_path}")

        return tag_info


    def get_media_info(self, file_path):
        '''
        @brief Gets media info.

        @details uses ffmpeg to get all media info from any valid audio file.

        @param file_path {str} The full path to audio file.
        @return media_info {dict} Media info (codec, duration, size, bitrate...) from filepath
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        media_info = None
        try:
            media_info = mediainfo(file_path)
        except Exception as e:
            raise Exception(f"Exception {e} getting media info for file {file_path}")

        return media_info


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
        @brief gets tag information for an mp3 audio file.

        @param file_path {str} The full path to mp3 audio file.
        @return tag_info {object} Tag object holding audio file tag info or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            tag_info = None
            audio_file = self.load_mp3_file(file_path)
            if audio_file is not None:
                tag_info = audio_file.tags
            else:
                return None
        except Exception as e:
            raise Exception(f"Exception {e} getting tags for file {file_path}")

        return tag_info


    def get_wma_tags(self, file_path):
        '''
        @brief gets tag information for an wma audio file.

        @param file_path {str} The full path to wma audio file.
        @return tag_info {object} Tag object holding audio file tag info or None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            tag_info = None
            audio_file = self.load_wma_file(file_path)
            if audio_file is not None:
                tag_info = audio_file.tags
            else:
                return None
        except Exception as e:
            raise Exception(f"Exception {e} getting tags for file {file_path}")

        return tag_info


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
            if file_path.endswith('.m4a'):
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
            if file_path.endswith('.mp3'):
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
            if file_path.endswith('.wma3'):
                audio_file = ASF(file_path)
                if audio_file is None:
                    return None
        except Exception as e:
            raise Exception(f"Exception {e} loading audio file: {file_path}")

        return audio_file


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


    def show_mp3_metadata(self, file_path):
        '''
        @todo add error handling
        @brief Shows mp3 audio file metadata.

        @details All mp3 files are presumed to be ID3v2.3 tags so we have consistent metadata fields.

        @param file_path {str} The full file path for mp3 audio file.
        '''

        audio_file = self.load_mp3_file(file_path)

        album = audio_file['TALB'].text[0]
        album_artist = audio_file['TPE2'].text[0]
        artist = audio_file['TPE1'].text[0]
        comment = audio_file['COMM'].text[0]
        composer = audio_file['TCOM'].text[0]
        copyright = audio_file['TCOP'].text[0]
        date = audio_file['TYER'].text[0]
        disc = audio_file['TPOS'].text[0]
        genre = audio_file['TCON'].text[0]
        publisher = audio_file['TPUB'].text[0]
        title = audio_file['TIT2'].text[0]
        track = audio_file['TRCK'].text[0]

        print(f"album: {album}")
        print(f"album artist: {album_artist}")
        print(f"artist: {artist}")
        print(f"comment: {comment}")
        print(f"composer: {composer}")
        print(f"copyright: {copyright}")
        print(f"date: {date}")
        print(f"disc: {disc}")
        print(f"genre: {genre}")
        print(f"publisher: {publisher}")
        print(f"title: {title}")
        print(f"track: {track}")
