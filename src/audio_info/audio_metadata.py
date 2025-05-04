'''
@file audio_metadata.py
@brief Defines the audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# third party modules
import mutagen


'''
Music Files directory & file naming format:
<drive>:\\<top level dir\\<artist name>\\<album name>\\<artist name>-<song title>.mp3
Example source file path:
C:\\Music\\3 Doors Down\\3 Doors Down-Here Without You.mp3
This file path is an example of a mp3 without album sub-directories

H:\\Music\\4 Non Blondes\\Bigger, Better, Faster, More!\\4 Non Blondes-What's Up.mp3
This file path is an example of a mp3 with album sub-directories

D:\\ProcessedMusic\\
'''

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

    def convert_to_mp3(self, file_path):
        '''
        @todo finish
        @brief Converts an audio file to mp3 audio file.

        @param file_path {str} The full path to audio file
        '''

        export_format = "mp3"
        import_format = ""

        # get the filename of song without the extension

        # get the file type of input file

        # convert per file type of input file

        pass

    def get_album_name(self, file_path):
        '''
        @todo finish using mutagen
        @brief Gets album name from metadata.

        @param audio_file {object} The FileType instance for an audio file.
        @return album_info tuple({str}, {str}) Artist name and album name from audio file metadata.
        '''
        artist_name = None
        album_name = None

        # The artist name directory we get from the audio file path instead of metadata
        # after all we would not have successfully got the metadata if the artist directory was invalid

        # the album name we must get from metadata

        return artist_name, album_name


    def get_art_type(self, audio_file):
        '''
        @brief Returns the mime type of album art.

        @param audio_file {object} The FileType instance for an audio file.
        @return mime_type {str} The mime type of the album art
        '''

        mime_type = None
        if 'APIC:' in audio_file:
            apic_frame = audio_file['APIC:']
            mime_type = apic_frame.mime

        return mime_type

    def get_file_type(self, file_path):
        '''
        @todo finish using mutagen
        @brief Returns the file type of audio file.

        @details Returns the file type using audio metadata as opposed to getting it from os library.

        @param file_path {str} The full path to audio file
        @return file_type {str} The file type of audio file.
        '''

        pass


    def get_metadata_type(self, file_path):
        '''
        @brief Returns the metadata type of audio file.

        @param file_path {str} The full path to audio file
        @return metadata_type {str} The type of the audio file metadata tags
        '''

        metadata_type = None

        try:
            audio_file = mutagen.File(file_path)
            if audio_file is not None:
                # the built in class name of the filetype returned shows what metadata type
                metadata_type = audio_file.__class__.__name__.lower()
            else:
                return None
        except Exception as e:
            print(f"Error processing file: {e}")
            return None

        return metadata_type


    def get_mp3_tag_info(self, file_path):
        '''
        @todo finish using mutagen
        @brief gets tag information for an audio file.

        @param file_path {str} The full path to audio file
        @return tag_info {object} Tag object holding audio file tag info
        '''

        tag_info = None
        audio_file = self.load_mp3_file(file_path)
        tag_info = audio_file.tags
        return tag_info

    def mp3_has_art(self, file_path):
        '''
        @brief Checks if an mp3 audio file contains embedded album art.

        @param file_path {str} The full path to audio file
        @return art_present {boolean} Returns true if art is present, false otherwise
        '''

        art_present = False
        audio_file = self.load_mp3_file(file_path)

        if 'APIC:' in audio_file:
            art_present = True
            apic_frame = audio_file['APIC:']
            print(f"Image MIME type: {apic_frame.mime} in: {file_path}")

        return art_present

    def load_mp3_file(self, file_path):
        '''
        @brief Loads an mp3 audio file.

        @details Expects a valid filepath to a mp3 type audio file.

        @param file_path {str} The full file path for audio file
        @return audio_file {FileType} Containing objects for the input audio file path
        '''

        audio_file = None
        if file_path.endswith('.mp3'):
            audio_file = mutagen.File(file_path)

        return audio_file

    def show_mp3_metadata(self, file_path):
        '''
        @brief Shows mp3 audio file metadata.

        @details All mp3 files are presumed to be ID3v2.3 tags so we have consistent metadata fields.

        @param file_path {str} The full file path for audio file
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

