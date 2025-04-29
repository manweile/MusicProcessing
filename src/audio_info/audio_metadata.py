'''
@file audio_metadata.py
@brief Defines the audio metadata class

@section description_audio_metadata Description
Defines the base class fort audio metadata processing
- AudioMetadata (base class)

@section libraries_audio_metadata Libraries/Modules
- eyed3 link
    - IPSUM LOREM
- mutagen link
    - IPSUM LOREM

@section author_audio_metadata Authour(s)
- Created by Gerald Manweiler on April 8, 2025
- Modified by Gerald Manweiler on April 22, 2025

Copyright (c) 2025 GWN Software. All rights reserved
'''

import eyed3
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
    @brief Contains metadata processing functionality
    @details Defines the base metadata processing used by project
    '''

    def __init__(self):
        '''
        @brief Initializes the AudioMetadata class
        @details A basic class implementation with no instantiation parameters

        @return AudioMetadata {object} An instance of the class
        '''

        pass


    # @todo finish, using mutagen
    def get_album_name(self, audio_file):
        '''
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
        @brief returns the mime type of album art

        @param audio_file {object} The FileType instance for an audio file
        @return mime_type {str} The mime type of the album art
        '''

        mime_type = None
        if 'APIC:' in audio_file:
            apic_frame = audio_file['APIC:']
            mime_type = apic_frame.mime

        return mime_type


    # @todo finish, using mutagen
    def get_metadata_type(self, audio_file):
        '''
        @brief Returns the metadata type of audio file

        @param audio_file {object} The mutagen FileType instance for an audio file
        @return metadata_type {str} The metadata type of the audio file
        '''

        pass


    def get_tag_info(self, audio_file):
        '''
        @brief gets tag information for an audio file

        @param audio_file  {object} The eyed3 Mp3AudioFile object for an audio file
        @return tag_info {object} Tag object holding audio file tag info
        '''

        tag_info = None
        if audio_file != None:
            tag_info = audio_file.tag

        return tag_info

    # @todo input a mutagen FileType instance instead of a file path
    def has_art(self, file_path):
        '''
        @brief Checks if an audio file contains embedded album art

        @param file_path {str} The full path to audio file
        @return art_present {boolean} Returns true if art is present, false otherwise
        '''

        art_present = False

        audio_file = mutagen.File(file_path)
        if 'APIC:' in audio_file:
            art_present = True
            apic_frame = audio_file['APIC:']
            print(f"Image MIME type: {apic_frame.mime}")

        return art_present

    def load_file(self, file_path):
        '''
        @brief loads an audio file

        @param file_path {str} The full file path for audio file
        @return Tuple [{Mp3AudioFile}, {FileType}] Containing objects for the input audio file path
        '''

        eyed3_audio_file = None
        mutagen_audio_file = None

        eyed3_audio_file = eyed3.load(file_path)
        mutagen_audio_file = mutagen.File(file_path)

        # @todo add IOError handling for file path  is not a file

        # @todo check for load returning a None - this indicates the file type (ie mime-type) is NOT an an mp3 file

        return eyed3_audio_file, mutagen_audio_file

    def show_metadata(self, audio_file):
        '''
        @brief Shows mutagen info

        @param audio_file {FileType} The mutagen FileType instance for an audio file
        '''

        artist_name = audio_file['TPE1'].text[0]
        album_name = audio_file['TALB'].text[0]
        song_title = audio_file['TIT2'].text[0]
        song_genre = audio_file['TCON'].text[0]

        print (artist_name)
        print (album_name)
        print (song_title)
        print(song_genre)


    def show_date(self, tag_info):
        '''
        @brief Show eyed3 tag date info

        @param tag_info {object} Tag object holding audio file tag info
        '''

        # @todo getBestDate() perhaps not best method
        # look at other ways, at min, format print - all I really want is the YYYY
        song_date = tag_info.getBestDate()

        print(song_date.year)

        # @todo possible write an album art extraction function
        # use mutagen if I do
        # this extracts album art, I just want to check if there is album art
        # also, artist name and song title metadata must have legal file name chars
        # eg. for $ Non Blondes, the song title What's Up? is illegal and will throw an error while trying to write image file.
        # for image in tag_info.images:
        #     image_file = open("{0}-{1}.jpg".format(artist_name, song_title), "wb")
        #     print("Writing image file: {0}-{1}.jpg".format(artist_name, song_title))
        #     image_file.write(image.image_data)
        #     image_file.close()

