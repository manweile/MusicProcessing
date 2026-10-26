# import os
import eyed3

r'''
Music Files directory & file naming format:
<drive>:\\<top level dir\\<artist name>\\<album name>\\<artist name>-<song title>.mp3
Example source file path:
C:\\Music\\3 Doors Down\\3 Doors Down-Here Without You.mp3
This file path is an example of a mp3 without album sub-directories

H:\\Music\\4 Non Blondes\\Bigger, Better, Faster, More!\\4 Non Blondes-What's Up.mp3
This file path is an example of a mp3 with album sub-directories

D:\\ProcessedMusic\\
'''

# top level source music files directory
SOURCE_DIR = "Music"
# top level processed music files directory
PROCESSED_MUSIC = "ProcessedMusic"


def createDir(drive_letter, dir_path):
    '''
    @brief  Creates top level processed music files directory if it does not exist
    @param drive_letter String holding drive letter for top level directory
    @param dir_path String holding directory path
    '''


    # check if top level directory exists
    # create it
    # else return


def get_info(file_path):
    '''
    @brief Get the file info
    @param file_path String holding full file path
    @return tag_info Tag object holding pertinent info
    '''

    tag_info = None

    # get the concrete type of eyed3.core.AudioFile, which is an Mp3AudioFile object
    audio_file = eyed3.load(file_path)

    # @todo add IOError handling for file path  is not a file

    # @todo check for load returning a None - this indicates the file type (ie mime-type) is NOT an an mp3 file

    # the bulk of the info I want is best accessed from Tag object embedded in Mp3AudioFile object
    tag_info = audio_file.tag

    return tag_info


def show_info(tag_info):
    '''
    @brief Show audio file info
    @param tag_info Tag object holding audio file tag info
    '''

    artist_name = tag_info.artist
    album_name = tag_info.album
    song_title = tag_info.title
    song_genre = tag_info.genre.name
    # @todo getBestDate() perhaps not best method
    # look at other ways, at min, format print - all I really want is the YYYY
    song_date = tag_info.getBestDate()

    print(artist_name)
    print(album_name)
    print(song_title)
    print(song_genre)
    print(song_date)

    for image in tag_info.images:
        image_file = open("{0}-{1}.jpg".format(artist_name, song_title), "wb")
        print("Writing image file: {artist_name}-{song_title}.jpg")
        image_file.write(image.image_data)
        image_file.close()


# audio_info = get_info("H:\\Music\\38 Special\\.38 Special-Hold On Loosely.mp3")
# audio_info = get_info("H:\\Music\\Kenny Rogers\\Daytime Friends - The Very Best of Kenny\\18 Lady.mp3")
audio_info = get_info(r"H:\Music\Abba\Greatest Hits Volume 2\ABBA-Angeleyes.mp3")
show_info(audio_info)
