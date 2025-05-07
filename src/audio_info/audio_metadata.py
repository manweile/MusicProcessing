'''
@file audio_metadata.py
@brief Defines the audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import os

# third party modules
import mutagen
from pydub import AudioSegment
from pydub.utils import mediainfo
from tinytag import TinyTag

# local modules
from src import _AUDIO_EXTS, _AUDIO_TYPES
from src.generated_files import generated_files

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
        @brief Converts any non-mp3 audio file to mp3 audio file.

        @details FFMPEG does the actual conversion
        @details The "any" if def name means wma or m4a files
        @details Mutagen retrieves the info & metadata & cover art for FFMPEG
        @param file_path {str} The full path to audio file
        '''

        # get audio formats & extensions from package constants
        export_format = _AUDIO_TYPES[0]
        export_file_ext = _AUDIO_EXTS[0]

        # ensure input file is not an mp3 then create full export file path
        file_path_components = file_path.split(os.sep)
        file_name_and_extension = file_path_components[-1].rsplit('.', 1)
        file_name = file_name_and_extension[0]
        file_ext = file_name_and_extension[1]
        if file_ext != ".mp3":
            export_name = file_name + export_file_ext
            export_filepath = os.path.join(generated_files, export_name)
        else:
            raise IOError(f"source file {file_path} is already an {export_format}")

        # get the input file info - want the codec and bitrate so can preserve the quality in exported file
        file_media_info = mediainfo(file_path)
        # file_audio_codec = file_media_info['codec_name']
        # file_audio_bitrate = file_media_info['bit_rate']

        # get the input files metadata from pydub because doing so gives consistent schema
        pydub_file_tags = file_media_info['TAG']
        mutagen_file_tags = self.get_any_tags(file_path)
        tinytag_file_tags = TinyTag.get(file_path, image=True)
        tiny_tag_image = tinytag_file_tags.get_image()

        '''
        @todo decide what is best methodology
        I have wma and m4a metadata, which have different considerations
        1) the ASF (wma) and MP4 (m4a) metadata keys are different from both each other and ID3v2.3
        so I need to figure out how to acquire what I want from the source file then map it correctly for ID3v2.3 keys
        I want:
        title (song title)      TIT2
        artist (album artist)   TPE1
        album                   TALB
        genre                   TCON
        year
        - year looks to be a PITA, different metadata schemas have different definitions of year and how that definition is handled
        - for me, I am look ing to map to ID3v2.3
        - this means (in sec order of preference)
        TYER
            The 'Year' frame is a numeric string with a year of the recording. This
            frames is always four characters long (until the year 10000).
        TORY
            The 'Original release year' frame is intended for the year when the
            original recording, if for example the music in the file should be a
            cover of a previously released song, was released. The field is
            formatted as in the "TYER" frame
        TDRC
            This is actually from ID3v2.4
            If encountered needs to be mapped to ID3v2.3 TYER and then removed
        TXXX:original year
            This is what MusicBrainz Picard put in
        media source            TMED
        - recorded (from vinyl lp)      - ID3v2.3 frame TMED("TT33")
        - ripped (from a cd)            - ID3v2.3 frame TMED(")
        - downloaded (from a source)
        '''

        '''
        @todo cover art
        cover art needs to be sent as a separate input param
        pydub does NOT extract any existing cover art, I will need to use something else - probably mutagen
        save the extracted art as a separate file (named either folder.jpg or cover.jpg) in the same directory as the converted file
        and embed the cover art in the converted file - which I can do with pydub
        Of course, I may have to deal with different cover art schemas for different audio file
        ID3v2.3 tag album art   APIC
        3 denotes front cover
        - jpg or png acceptable
        - 200px x 200px to 600px x 600px
        - stored as separate file in same directory as the audio file it belongs to
        - cover art file name can be either Folder.jpg or Cover.jpg
        '''
        # check if input file path has a file "Folder.jpg"
        # if Folder.jpg, then cover=path_to_Folder.jpg
        # elseif check if the input audio file has embedded art then
        #   extract it
        #   save it as Extracted.jpg
        #   cover=path_to_Extracted.jpg
        # else leave cover=None

        try:
            audio_segment = AudioSegment.from_file(file_path)
            # @todo there are many more params I could send to export command
            # audio_segment.export(export_filepath, export_format, tags=mutagen_file_tags, id3v2_version='3')
            audio_segment.export(export_filepath, export_format, id3v2_version='3')
        except Exception as e:
            raise Exception(f"Exception {e} converting {file_path}")


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


    def get_mp3_art_type(self, file_path):
        '''
        @brief Returns the mime type of album art in mp3 file.

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

