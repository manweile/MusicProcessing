#  standard modules
import os
import platform

# third part modules
from mutagen.asf import ASF, ASFByteArrayAttribute
import mutagen
from pydub import AudioSegment
from pydub.utils import mediainfo
from tinytag import Image, Images, TinyTag

_ART_FILE = "Folder.jpg"

# see https://blog.1a23.com/2020/03/16/read-and-write-tags-of-music-files-with-ffmpeg/ for an
# ffmpeg cli that works!

def find_embedded_art(file_path):
    try:
        audio = ASF(file_path)
        if 'WM/Picture' in audio.tags:
            picture_data = audio['WM/Picture'][0].value
            image_data = ASFByteArrayAttribute().parse(picture_data)

            return image_data, None
        # pictures = audio.pictures
        # if pictures:
        #     for i, picture in enumerate(pictures):
        #         if picture.type == 3: # Check if it's cover art
        #             image_data = picture.data
        #             image_format = picture.mime
        #             return image_data, image_format
        else:
            return None, None
    except Exception as e:
        print(f"Exception: {e} extracting embedded art from {file_path}")
        return None, None

def save_art(image_data, image_format, output_path):
    if image_data and image_format:
        file_extension = image_format.split('/')[1]
        filename = f"Extracted.{file_extension}"
        filepath = os.path.join(output_path, filename)

        with open(filepath, "wb") as f:
            f.write(image_data)
        print(f"Cover art saved to {filepath}")
    else:
        print("No cover art found to save.")

#Example Usage
file_path = None
if platform.system() == "Linux":
    file_path = r"/home/gerald/Music/Elton John/Goodbye Yellow Brick Road/Elton John-Saturday Night's Alright for Fighting.wma"  # has art
    # file_path = r"/home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a"       # no art
elif platform.system() == "Windows":
    # file_path = r"C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"  # has art
    file_path = r"\\192.168.0.14\sambashare\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"
    # file_path = r"C:\Music\The Eagles\Hotel California\The Eagles-Hotel California.wma"       # no art

image_data, image_format = find_embedded_art(file_path)

if image_data:
    with open(_ART_FILE, 'wb') as img_file:
        img_file.write(image_data)
    print(f"Album art extracted from {file_path} and saved as {_ART_FILE}")
else:
    print("No embedded cover art found.")
