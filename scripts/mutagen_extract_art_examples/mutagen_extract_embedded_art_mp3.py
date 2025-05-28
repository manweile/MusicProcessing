import platform

from mutagen.mp3 import MP3
from mutagen.id3 import ID3

_ART_FILE = "Folder.jpg"

def find_embedded_art(file_path):
    """
    Finds and extracts embedded album art from an MP3 file.

    Args:
        file_path (str): The path to the MP3 file.

    Returns:
        bytes or None: The image data if found, otherwise None.
    """
    try:
        audio = MP3(file_path, ID3=ID3)
        if 'APIC:' in audio.tags:
            for tag in audio.tags.getall('APIC'):
                return tag.data
        else:
            return None
    except Exception as e:
        print(f"Exception: {e} extracting embedded art from {file_path}")
        return None

# Example usage:
file_path = None
if platform.system() == "Linux":
    # file_path = r"/home/gerald/Music/38 Special/Special Forces/38 Special-Caught Up in You.mp3"      # no art
    file_path = r"/home/gerald/Music/3 Doors Down/3 Doors Down/3 Doors Down-It's Not My Time.mp3"  # has art
elif platform.system() == "Windows":
    # file_path = r"C:\Music\38 Special\Special Forces\38 Special-Caught Up in You.mp3"    # no art
    file_path = r"C:\Music\3 Doors Down\3 Doors Down\3 Doors Down-It's Not My Time.mp3"  # has art

image_data = find_embedded_art(file_path)

if image_data:
    with open(_ART_FILE, 'wb') as img_file:
        img_file.write(image_data)
    print(f"Album art extracted from {file_path} and saved as {_ART_FILE}")
else:
    print(f"No album art found in {file_path}")