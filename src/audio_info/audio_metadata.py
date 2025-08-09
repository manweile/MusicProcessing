'''
@file audio_metadata.py
@brief Defines the audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import fnmatch
import gc
import logging
import os
import pprint
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
from src import AUDIO_EXTS, AUDIO_FILES, AUDIO_TYPES
from src import FOLDER_ART
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging constants
from src.generated_files import GENERATED_FILES
from src import PathInfoError
from src.audio_normalize import AudioNormalization
from src.dir_processing import DirectoryProcessing

gc.enable()

directory = DirectoryProcessing()
normalization = AudioNormalization()

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

# metadata class needs 2 file handlers:
# information for normal audio processing events
# error for abnormal situations

TPOS = "TPOS"
TYER = "TYER"

# the set of pydub generic metadata keys I want to copy to converted & normalized files
# these keys also correspond to what Windows displays as file information in File Explorer
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

# dict of generic to ID3v2.3 (MP3)
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

MP3_TIME_KEYS = {
    'TYER',                                                 # preferred key
    'TORY',
    'TDRC',
    'TDOR',
    'TXXX=originalyear'
}

# dict of possible m4a (MP4)
M4A_KEYS = {
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

M4A_TIME_KEYS = {
    '\xa9day',                                              # preferred key
    '----:com.apple.iTunes:originalyear'
}

# dict of possible wma (ASF)
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

WMA_TIME_KEYS = {

    'WM/Year',                                              # preferred key
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
                id3_tags[TYER] = max_date

            if TPOS not in id3_tags:
                id3_tags[TPOS] = "1/1"

            # @todo remove, this can be logged by calling function if needed
            # for key, value in id3_tags.items():
            #     print(f"key: {key}, value: {value}")

        except Exception as error:
            raise Exception(f"Exception: {error} updating tags")

        return id3_tags


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
            export_path = directory.path_info(file_path)

            if not export_path:
                logger.error(f"No export path created for {file_path}", exc_info=True)
                raise PathInfoError(f"No export path created for {file_path}")
            else:
                directory.make_dir(os.path.dirname(export_path))

            # @todo check for a Folder.jpg colocated with audio file

            # export format is always mp3
            export_format = AUDIO_TYPES[0]

            input_format = os.path.splitext(file_path)[1].lower()[1:]
            input_path_stem = os.path.splitext(os.path.basename(file_path))[0]
            input_path_parent = os.path.dirname(file_path)

            # @todo this needs to go to a txt file
            print(f"Beginning conversion on {input_path_stem} from {input_format} to {export_format}")
            print(f"Source directory path: {input_path_parent}")

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
            if metadata_type == AUDIO_FILES[2]:
                format = AUDIO_FILES[2]
                input_tags = self.get_wma_tags(file_path)
                tags = self.map_wma_tags(input_tags)
            elif metadata_type == AUDIO_FILES[0]:
                format = AUDIO_FILES[0]
                input_tags = self.get_mp3_tags(file_path)
                tags = self.map_mp3_tags(input_tags)
            elif metadata_type == AUDIO_FILES[1]:
                format = AUDIO_FILES[1]
                input_tags = self.get_m4a_tags(file_path)
                tags = self.map_m4a_tags(input_tags)
            else:
                # @todo log this
                print(f"Non-standard metadata type: {metadata_type} for file: {os.path.basename(file_path)}")
                return

            # get the input file info - want bitrate so can preserve the quality in exported file
            media_info = self.get_media_info(file_path)
            bitrate = media_info['bit_rate']

            '''
            If a song has does have embedded art, pydub will NOT auto transfer it while doing a conversion.
            Therefore all audio files must have co-located cover art.
            '''

            cover = os.path.join(input_path_parent, FOLDER_ART)
            if not os.path.exists(cover):
                # @todo log this
                print(f"album directory {input_path_parent} does not contain a {FOLDER_ART} file.")
                return

            if metadata_type == AUDIO_FILES[0]:
                # pydub has an MP3 file loader
                audio_segment = AudioSegment.from_mp3(file_path)
            elif metadata_type == AUDIO_FILES[1]:
                # pydub does know about MP4 format, so pass it in
                audio_segment = AudioSegment.from_file(file_path, format=format)
            elif metadata_type == AUDIO_FILES[2]:
                # pydub doesn't know about wma/asf, so no format forces an autodetect
                audio_segment = AudioSegment.from_file(file_path)

            # the id3v2 version = 3 is important, lack of is known ffmpeg(pydub)/mutagen bug
            # and both documentations don't really mention it
            audio_segment.export(export_path, export_format, bitrate=bitrate, tags=tags, id3v2_version='3')

            # Add or update album art
            try:
                audio_tags = MP3(export_path, ID3=ID3, v2_version=3)
                audio_tags.add_tags()
            except error:
                # Tags already exist, no worries
                pass

            # encoding/type = 3 specifies UTF-8/front cover
            with open(cover, "rb") as album_art_file:
                audio_tags.tags.add(
                    APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,
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
                    if input_file_ext.lower() not in AUDIO_EXTS:
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
                    # @todo log this
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
                        dir_processing.make_album_dir(tld_item_path, album_dir)

                        # now transfer the audio file to new album directory
                        destination_dir = os.path.join(tld_item_path, album_dir)
                        dir_processing.move_audio_file(audio_file, destination_dir)
                    else:
                        # @todo log this
                        print(f"{audio_file} is missing album metadata")
                        continue

                tld_bar.update(1)

            tld_bar.close()
            dir_processing.create_csv(csv_filename, data, GENERATED_FILES, header_row, 0)
            # @todo log this
            print(f"Created {len(album_dirs)} album dirs")

        except ValueError as e:
            raise Exception(f"ValueError {e} sanitizing album metadata {album}")
        except Exception as e:
            raise Exception(f"Exception {e} creating sub-dirs for {start_path}")


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
                    if input_file_ext.lower() not in AUDIO_EXTS:
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

                    #  @todo remove
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
                            if metadata_type == AUDIO_FILES[2]:
                                input_tags = self.get_wma_tags(tag_file_path)
                            elif metadata_type == AUDIO_FILES[0]:
                                input_tags = self.get_mp3_tags(tag_file_path)
                            elif metadata_type == AUDIO_FILES[1]:
                                input_tags = self.get_m4a_tags(tag_file_path)

                        if input_tags:
                            if ffprobe:
                                # @todo log this
                                print(f"{tag_file_path} has {len(input_tags)} ffprobe tags")
                                # want one key/value pair per line
                                # @todo log this
                                pprint.pprint(input_tags)
                                print()
                            else:
                                # @todo log this
                                print(f"{tag_file_path} has {len(input_tags)} {metadata_type} tags")
                                # mutagen returns tags as ASFTags, ID3Tags, MP4Tags objects
                                # not as a simple dict of string key/value
                                # so need mutagen pprint and splitlines to "format" into simple dict
                                pprint.pprint(input_tags.pprint().splitlines())
                                print()
                        else:
                            # @todo log this
                            print(f"{tag_file_path} has no metadata")

        except Exception as e:
            raise Exception(f"Exception {e} getting tags for file {file_path}")


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
                    if input_file_ext.lower() not in AUDIO_EXTS:
                        continue

                    tag_file_path = os.path.join(dir_path, file)
                    input_tags = self.get_media_tags(tag_file_path)
                    file_keys = input_tags.keys()
                    if file_keys:
                        unique_keys.update(file_keys)
            # @todo log this
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

            if file_ext.lower() not in AUDIO_EXTS:
                raise Exception(f"File: {file_name} has invalid extension: {file_ext}")

            audio_tags = self.get_any_tags(file_path)

            if audio_tags is None:
                raise Exception(f"File: {file_name} has no metadata")

            if 'WM/Picture' in audio_tags:
                has_art = True          # ASF/wma
            elif 'covr' in audio_tags:
                has_art = True          # MP4/m4a
            elif 'APIC:' in audio_tags:
                has_art = True          # ID3/mp3

        except Exception as e:
            raise Exception(f"Exception {e} checking for album art tag in file {file_path}")

        return has_art


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
                        # @todo log this
                        print(f"metadata: {metadata_field:<20} - m4a key: {m4a_value:<35} - id3 key: {mp3_key} - value: {date_value}")
                        continue

                    # m4a doesn't have a "native" original year field like "\xa9ory",
                    # relies on the iTunes field ----:com.apple.iTunes:originalyear,
                    # so need additional step to decode from MP4FreeForm
                    if isinstance(metadata_value, MP4FreeForm) and m4a_value in M4A_TIME_KEYS:
                        decode_value = input_tags[m4a_value][0].decode()
                        # just in case string is "YYYY-MM-DD"
                        date_value = decode_value[0:4]
                        date_values.add(date_value)
                        # @todo log this
                        print(f"metadata: {metadata_field:<20} - m4a key: {m4a_value:<35} - id3 key: {mp3_key} - value: {date_value}")
                        continue

                    # m4a supposedly has native publisher "\xa9pub", but not seen in my collection
                    # I do have iTunes "----:com.apple.iTunes:LABEL" field
                    if isinstance(metadata_value, MP4FreeForm) and m4a_value == "----:com.apple.iTunes:LABEL":
                        tag_value = input_tags[m4a_value][0].decode()

                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    # @todo log this
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
                        # @todo log this
                        print(f"metadata: {metadata_field:<20} - mp3 key: {mp3_value:<10} - id3 key: {mp3_key} - value: {date_value}")
                        continue

                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    # @todo log this
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
                        print(f"metadata: {metadata_field:<20} - wma key: {wma_value:<35} - id3 key: {mp3_key} - value: {date_value}")
                        continue

                    if isinstance(metadata_value, str):
                        tag_value = metadata_value

                    # track num is int
                    if isinstance(metadata_value, int):
                        tag_value = metadata_value

                    # @todo log this
                    print(f"metadata: {metadata_field:<20} - wma key: {wma_value:<35} - id3 key: {mp3_key} - value: {tag_value}")
                    id3_tags[mp3_key] = tag_value

            id3_tags = self.__update_id3(date_values, id3_tags)

        except Exception as e:
            raise Exception(f"Exception {e} converting wma tags to id3 tags")

        return id3_tags
