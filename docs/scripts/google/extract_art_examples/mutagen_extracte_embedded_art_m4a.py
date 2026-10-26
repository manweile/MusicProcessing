import platform
from mutagen.mp4 import MP4

_ART_FILE = "Folder.jpg"


def find_embedded_art(file_path):
    """
    Finds and extracts embedded artwork from an M4A file using Mutagen.

    Args:
        file_path (str): The path to the M4A file.

    Returns:
        bytes or None: The raw bytes of the artwork if found, otherwise None.
    """
    try:
        audio = MP4(file_path)
        audio_tags = audio.tags
        if "covr" in audio_tags:
            # M4A files can have multiple 'covr' atoms, each containing a different image.
            # This example extracts the first one.
            cover_tag = audio["covr"]
            artwork = cover_tag[0]
            # artwork = audio["covr"][0]
            # Artwork data might be wrapped in format codes; extract the raw data.
            if isinstance(artwork, tuple):
                return artwork[1]  # Return the image data
            return artwork
        else:
            return None
    except Exception as e:
        print(f"Exception: {e} extracting embedded art from {file_path}")
        return None


# Example usage:
file_path = None
if platform.system() == "Linux":
    file_path = r"/home/gerald/Music/Joshua Davis/The Voice Peformance/Joshua Davis-The Workingman's Hymn.m4a"  # has art
    # file_path = r"/home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a"       # no art
elif platform.system() == "Windows":
    file_path = r"C:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a"  # has art
    # file_path = r"C:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a"       # no art

image_data = find_embedded_art(file_path)

if image_data:
    with open(_ART_FILE, 'wb') as img_file:
        img_file.write(image_data)
    print(f"Album art extracted from {file_path} and saved as {_ART_FILE}")
else:
    print(f"No album art found in {file_path}")
