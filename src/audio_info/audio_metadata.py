'''
@file audio_metadata.py
@brief Defines the audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import csv
import errno
import gc
import os
from pathlib import Path
import platform
import sys

from operator import itemgetter

# third party modules
import mutagen
import pathvalidate
from mutagen.id3 import ID3, TALB, TPE2, TPE1, COMM, TCOM, TCOP, TYER, TPOS, TCON, TPUB, TIT2, TRCK, TMED
from pydub import AudioSegment
from pydub.utils import mediainfo
from tqdm import tqdm

# local modules
from src import _AUDIO_EXTS, _AUDIO_TYPES
from src.dir_processing import DirectoryProcessing
# generated files package does not have any modules,
# just a package variable the __all__ list exposes via __init__.py
from src.generated_files import generated_files

gc.enable()

_EXPORT_TLD = "Music"

# the set of pydub generic metadata keys I want to copy to converted files
# these keys also correspond to what Windows displays as file information in File Explorer
_GEN_KEYS = {
            'album',
            'album_artist',
            'artist',
            'comment',
            'composer',
            'copyright',
            'date',
            'disc',
            'genre',
            'publisher',
            'title',
            'track'
            }

# set of known media keys in ID3, m4a, wma order
_MEDIA_KEYS = {
            'TMED',                     # ID3
            'MEDIA',                    # m4a
            'WM/Media',                 # wma
            'media_type'                # wma
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

# dict of generic to ID3v2.3 for mp3 files
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

# dict of generic to m4a for mp3 files
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

# dict of generic to wma for mp3 files
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

        @return AudioMetadata {instance} An instance of the class
        '''

        pass

    def convert_any_to_mp3(self, file_path):
        '''
        @todo finish
        @brief Converts any audio file to mp3 audio file.

        @details FFMPEG does the actual conversion.
        @details The "any" if def name means wma, m4a, mp3 files.

        @param file_path {str} The full path to audio file
        '''

        export_dir = None
        export_file_name = None
        export_file_path = None

        # get mp3 audio format & extension from package constants
        export_format = _AUDIO_TYPES[0]
        export_file_ext = _AUDIO_EXTS[0]

        r'''
        Ubuntu file path:
        <root>/<mount point>/<usr>/[drive label]/<tld>/<artist dir>/[album dir]/<song file>.<ext>
        root is always /
        mount point is either home (a hdd) or media (an usb)
        if mount point is media then there will be a drive label
        album dir is optional

        Windows file path:
        <drive>\<tld>\<artist dir>\[album dir]\<song file>.<ext>
        drive is always a drive letter
        album dir is optional

        Ubuntu from USB stick, with an album directory
        "/media/gerald/Music/Music/.38 Special/Special Forces/.38 Special-Caught Up in You.mp3"
        Ubuntu from hdd, w/o album directory
        "/home/gerald/Music/Alejandro Escovedo/Alejandro Escovedo-Broken Bottle.wma"
        Windows from USB stick, with an album directory
        "H:\Music\.38 Special\Special Forces\.38 Special-Caught Up in You.mp3"
        Windows from hdd, w/o album directory
        "C:\Music\Alejandro Escovedo\Alejandro Escovedo-Broken Bottle.wma"

        I don't need drive/root, mount point, usr, drive label, tld
        I always need artist dir, album dir if it exists, and song file
        '''

        input_path = Path(file_path)
        # get the full parent w/o filename so I can start removing unnecessary path components
        input_path_parent = input_path.parent
        # remove the root or drive (ie. / or H:), have no use for it
        input_path_parts = input_path_parent.parts[1:]

        if input_path_parts[0] == "media":
            # Ubuntu usb is going to have <mount point>/<usr>/<drive label>/<tld>/<artist dir>/[album dir]
            input_path_components = input_path_parts[4:]
        elif input_path_parts[0] == "home":
            # Ubuntu hdd is going to have <mount point>/<usr>/<tld>/<artist dir>/[album dir]
            input_path_components = input_path_parts[3:]
        else:
            # Windows is going to have <tld>/<artist dir>/[album dir]
            input_path_components = input_path_parts[1:]

        # using fixed storage path because will always know project structure
        export_dir = os.path.join(generated_files, _EXPORT_TLD)

        for component in input_path_components:
            export_dir = os.path.join(export_dir, component)

        # directory is already extant if we are processing multiple songs for the same album
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        input_file_name = input_path.stem
        input_file_ext = input_path.suffix

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
        @todo date
        date info is most problematic part of metadata
        different audio file types have different date type tags
        and to make things worse, the date could be a full ISO date,
        or could just be a 4 digit year string
        Possible heuristic
        1) check for what "date" present
        2) normalize it to "YYYY" if necessary
        3) use the oldest "YYYY" value
        '''
        # need to massage the reported date info
        # if m4a, look for key date, then originalYear, then originalDate
        # once I have the info, need to check if is 4 chars or longer
        # if longer, just need the 1st 4 chars
        # eg from an m4a:
        # 'date': '2015-05-18T07:00:00Z'
        # strip out the 2015
        #
        # 'date': '2013'
        # 'originalyear': '1973'
        # both are YYYY format, but use oldest date, ie 1973
        #
        # 'originaldate': '1973-04-17'
        # strip out the 1973
        #
        # if wma, look for key WM/Year
        # 'WM/Year': '1976'

        mutagen_file_tags = self.get_any_tags(file_path)

        '''
        @todo cover art
        Most songs have hidden file art, this is a result from all the WMP processing I did.
        Unfortunately, many artist dirs also do NOT have album sub directories.

        Since most songs do not have embedded art, will need to use co-located Folder.jpg files as cover art.
        Can only do this with certainty where there is artist/album/song & a single Folder.jpg in album directory.

        So I have to decide if I am going to create all the required album sub directories,
        move the audio files, and then manually move the correct *.jpg to proper album sub directory.add()

        If a song has does have embedded art, ffmpeg will NOT auto transfer it.
        Will need to extract it, save it, then add it to export command.

        ID3v2.3 tag album art tag is APIC, where '3' denotes front cover
        '''

        try:
            audio_segment = AudioSegment.from_file(file_path)
            audio_segment.export(export_file_path, export_format, bitrate=file_audio_bitrate, tags=export_metadata, id3v2_version='3')
            print(f"{input_file_name} converted to {export_format}")
        except Exception as e:
            raise Exception(f"Exception {e} converting {file_path} to {export_file_path}")


    def create_album_dir(self, start_path, file_path=None):
        '''
        @brief Creates an album sub-directory in an artist directory.

        @details Creates the album sub directory for the artist if needed.
        @details The album name for the directory is drawn from the metadata.

        @param start_path {str} The tld holding music files
        @param file_path {str} The full path to audio file
        @exception OSError An os permission error
        @exception Exception A generic exception
        '''

        data = []
        dir_count = 0

        try:
            # get the generated files directory, that's where csv will be saved
            csv_dir = generated_files
            csv_filename = "created_album_dirs.csv"
            csv_path = os.path.join(csv_dir, csv_filename)

            # create csv file, overwrite any existing with same name if necessary
            csv_outfile = open(csv_path, 'w', newline='')
            csv_file_writer = csv.writer(csv_outfile, delimiter=';')
            header_row = ["audio file path", "album metadata", "album directory"]
            csv_file_writer.writerow(header_row)

            dir_processing = DirectoryProcessing(start_path)

            # get the artist dirs under tld
            tld_content = os.listdir(start_path)

            len_tld_content = len(tld_content)
            tld_bar = tqdm(desc=f'Processing {start_path} content', total=len_tld_content, unit=' items')

            # iterate through top level directory
            # consists of artist directories, playlist files and couple other sundry files
            for tld_item in tld_content:

                # we only want artist directories, playlist/sundry files don't count
                if os.path.isdir(os.path.join(start_path, tld_item)):
                    artist_path = os.path.join(start_path, tld_item)
                else:
                    continue

                # want to know if we have any empty artist directories
                # so we can deal with them later
                if os.path.isdir(artist_path) and not os.listdir(artist_path):
                    print(f"{artist_path} is an empty directory")
                    continue

                # update the progress bar before processing artist directory
                # else we will have a mismatch in the bar processed/total display
                tld_bar.update(1)

                # now we look at what's in the current artist directory
                artist_content = os.listdir(artist_path)

                for artist_item in artist_content:

                    # we don't care about album sub-dirs
                    if os.path.isdir(os.path.join(artist_path, artist_item)):
                        continue

                    # if we find a file, we may need a album sub-directory for it
                    # as artist dirs are supposed only contain album sub dirs
                    if os.path.isfile(os.path.join(artist_path, artist_item)):
                        _, file_ext = os.path.splitext(artist_item)

                        # audio files are supposed to be in an album sub dir
                        if file_ext.lower() in _AUDIO_EXTS:
                            audio_file = os.path.join(artist_path, artist_item)
                            file_media_info = mediainfo(audio_file)
                            file_media_tags = file_media_info['TAG']

                            if 'album' in file_media_tags.keys():
                                album = file_media_tags['album']
                                # dir_processing.make_album_dir(artist_path, album)
                                album_dir = pathvalidate.sanitize_filepath(album, platform=platform.system(), validate_after_sanitize=True)
                                # write file path, album metadata, album directory
                                data.append([audio_file, album, album_dir])
                                dir_count += 1
                            else:
                                print(f"{audio_file} is missing album metadata")
                                continue

            tld_bar.close()
            sorted_data = sorted(data, key=itemgetter(0))
            csv_file_writer.writerows(sorted_data)
            csv_outfile.close()
            print(f"Created {dir_count} album dirs")
        except Exception as e:
            raise Exception(f"Exception {e} creating sub-dirs for {start_path}")


    def get_any_metadata_type(self, file_path):
        '''
        @brief Returns the metadata type of any audio file.

        @param file_path {str} The full path to audio file
        @return metadata_type {str} The type of the audio file metadata tags
        '''

        metadata_type = None

        try:
            audio_file = mutagen.File(file_path)
            if audio_file is not None:
                # the built in class name of the filetype returned shows what metadata type
                metadata_type = audio_file.__class__.__name__
            else:
                return None
        except Exception as e:
            print(f"Error processing file: {e}")
            return None

        return metadata_type


    def get_mp3_album_name(self, file_path):
        '''
        @todo finish using mutagen
        @brief Gets album name from metadata in mp3 file.

        @param audio_file {object} The FileType instance for an mp3 audio file.
        @return album_info tuple({str}, {str}) Artist name and album name from audio file metadata.
        '''
        artist_name = None
        album_name = None

        # The artist name directory we get from the audio file path instead of metadata
        # after all we would not have successfully got the metadata if the artist directory was invalid

        # the album name we must get from metadata

        return artist_name, album_name


    def get_embedded_art_mime(self, file_path):
        '''
        @brief Returns the mime type of album art in audio file.

        @param file_path {str} The full path to mp3 audio file
        @return mime_type {str} The mime type of the album art
        '''

        audio_file = mutagen.File(file_path)
        mime_type = None
        if 'APIC:' in audio_file:
            apic_frame = audio_file['APIC:']
            mime_type = apic_frame.mime

        return mime_type


    def get_any_tags(self, file_path):
        '''
        @brief gets tags for an audio file.

        @param file_path {str} The full path to audio file
        @return tags {object} Tag object holding audio file tags
        '''

        tags = None
        audio_file = self.load_any_file(file_path)
        tags = audio_file.tags
        return tags


    def get_mp3_tag_info(self, file_path):
        '''
        @brief gets tag information for an mp3 audio file.

        @param file_path {str} The full path to mp3 audio file
        @return tag_info {object} Tag object holding audio file tag info
        '''

        tag_info = None
        audio_file = self.load_mp3_file(file_path)
        tag_info = audio_file.tags
        return tag_info


    def has_mp3_art(self, file_path):
        '''
        @brief Checks if an mp3 audio file contains embedded album art.

        @param file_path {str} The full path to mp3 audio file
        @return art_present {boolean} Returns true if art is present, false otherwise
        '''

        art_present = False
        audio_file = self.load_mp3_file(file_path)

        if 'APIC:' in audio_file:
            art_present = True
            # apic_frame = audio_file['APIC:']
            # print(f"Image MIME type: {apic_frame.mime} in: {file_path}")

        return art_present

    def load_any_file(self, file_path):
        '''
        @brief loads any valid audio file type

        @param file_path {str} The full file path for audio file
        @return audio_file {FileType} Containing objects for the input audio file path
        '''
        audio_file = None

        try:
            audio_file = mutagen.File(file_path)
        except Exception as e:
            print(f"Error processing file: {e}")
            return None

        return audio_file


    def load_mp3_file(self, file_path):
        '''
        @brief Loads an mp3 audio file.

        @details Expects a valid filepath to a mp3 type audio file.

        @param file_path {str} The full file path for audio file
        @return audio_file {FileType} Containing objects for the input audio file path
        '''

        audio_file = None
        if file_path.endswith('.mp3'):
            audio_file = mutagen.File(file_path, "MP3")

        return audio_file

    def show_mp3_metadata(self, file_path):
        '''
        @brief Shows mp3 audio file metadata.

        @details All mp3 files are presumed to be ID3v2.3 tags so we have consistent metadata fields.

        @param file_path {str} The full file path for mp3 audio file
        '''

        audio_file = self.load_mp3_file(file_path)

        artist_name = audio_file['TPE1'].text[0]
        album_name = audio_file['TALB'].text[0]
        song_title = audio_file['TIT2'].text[0]
        song_genre = audio_file['TCON'].text[0]

        print (artist_name)
        print (album_name)
        print (song_title)
        print(song_genre)


    def show_mp3_date(self, tag_info):
        '''
        @todo write using mutagen presuming ID3v2.3 metadata
        @brief Show metadata date info

        @param tag_info {object} Tag object holding audio file tag info
        '''

        pass

