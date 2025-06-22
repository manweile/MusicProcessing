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
        # <:little-endian byte order, b: signed char (1 byte), i: signed int (4 bytes)
        # unpacks first 5 bytes in tuple where type is C signed char (1 byte)/Python integer and size is C signed int (4 bytes)/Python integer
        # for an ASF WM/Picture, 3 = Front album cover
        # eg. b'\x03\x140\x00\x00i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00\x00\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`
        # image type and image size, elements 0-5: b'\x03\x140\x00\x00
        # image type, elements 0-1, b'\x03'
        # image size, elements 1-5, b'\x140\x00\x00 = 0x1403 little-endian, 0x3014 big-endian, decimal 12308
        # mime type, elements 5 to 25: b'i\x00m\x00a\x00g\x00e\x00/\x00j\x00p\x00e\x00g\x00'
        # null terminator, elements 25 to 27: b'\x00\x00'
        # description, elements 27 to 29: b'\x00\x00'
        # data, elements 29 to 29 + size: b'\xff\xe0\x...'
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
        audio = ASF(file_path)
        audio_tags = audio.tags
        if 'WM/Picture' in audio_tags:
            pic_tag = audio_tags["WM/Picture"]
            byte_attribute_array = pic_tag[0]
            picture_data = byte_attribute_array.value
            mime_type, image_data, type_indicator, image_description = unpack_asf_image(picture_data)
            return image_data
        else:
            print(f"No embedded art in {file_path}")
            return None
    except Exception as e:
        print(f"Exception: {e} extracting embedded art from {file_path}")
        return None


# Example Usage
file_path = None
if platform.system() == "Linux":
    # file_path = r"/home/gerald/Music/Elton John/Goodbye Yellow Brick Road/Elton John-Saturday Night's Alright for Fighting.wma"  # has art
    # file_path = r"/home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a"       # no art
    file_path = r"/home/gerald/Music/Buddy Guy/Bring 'Em In/Buddy Guy-Ain't No Sunshine.wma"
    # file_path = r"/home/gerald/Music/The Beach Boys/The Best of the Beach Boys, Vol. 1/The Beach Boys-Little Deuce Coupe.wma"
    # file_path = r"/home/gerald/Music/Elton John/Greatest Hits, Vol. 2/Elton John-Island Girl.wma"
    # file_path = r"/home/gerald/Music/Billie Holiday/Georgia On My Mind/Billie Holiday-Georgia On My Mind.wma"
elif platform.system() == "Windows":
    file_path = r"C:\Music\Billie Holiday\Georgia On My Mind\Billie Holiday-Georgia On My Mind.wma"     # has art, but not in a video stream, so ffmpeg fails
    # file_path = r"C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"  # has art
    # file_path = r"\\192.168.0.14\sambashare\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"
    # file_path = r"C:\Music\The Eagles\Hotel California\The Eagles-Hotel California.wma"       # no art

image_data = find_embedded_art(file_path)

if image_data:
    with open(_ART_FILE, 'wb') as img_file:
        img_file.write(image_data)
    print(f"Album art extracted from {file_path} and saved as {_ART_FILE}")
else:
    print("No embedded cover art found.")
