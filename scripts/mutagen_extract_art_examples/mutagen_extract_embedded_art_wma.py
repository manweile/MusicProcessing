#  standard modules
import platform
import struct

# third part modules
from mutagen.asf import ASF

_ART_FILE = "Folder.jpg"

def unpack_asf_image(data):
    '''
    @brief Unpack image data from a WM/Picture tag.

    @details https://github.com/beetbox/mediafile/blob/master/mediafile.py#L243
    @details This function is treated as "untrusted" and could throw all manner of exceptions (out-of-bounds, etc.).

    @return (mime, image_data, type, description) ({str}, {bytes}, {int}, {str}) Tuple containing the MIME type, the raw image data, a type indicator, and
    the image's description.
    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
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


def find_embedded_art(file_path):
    try:
        asf_audio = ASF(file_path)
        asf_audio_tags = asf_audio.tags
        if 'WM/Picture' in asf_audio_tags:
            asf_pic_tag = asf_audio_tags["WM/Picture"]
            asf_byte_attribute_array = asf_pic_tag[0]
            asf_picture_data = asf_byte_attribute_array.value
            mime_type, image_data, type_indicator, image_description = unpack_asf_image(asf_picture_data)
            return image_data
        else:
            print(f"No embedded art in {file_path}")
            return None
    except Exception as e:
        print(f"Exception: {e} extracting embedded art from {file_path}")
        return None

#Example Usage
file_path = None
if platform.system() == "Linux":
    file_path = r"/home/gerald/Music/Elton John/Goodbye Yellow Brick Road/Elton John-Saturday Night's Alright for Fighting.wma"  # has art
    # file_path = r"/home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a"       # no art
elif platform.system() == "Windows":
    # file_path = r"C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"  # has art
    file_path = r"\\192.168.0.14\sambashare\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"
    # file_path = r"C:\Music\The Eagles\Hotel California\The Eagles-Hotel California.wma"       # no art

image_data = find_embedded_art(file_path)

if image_data:
    with open(_ART_FILE, 'wb') as img_file:
        img_file.write(image_data)
    print(f"Album art extracted from {file_path} and saved as {_ART_FILE}")
else:
    print("No embedded cover art found.")
