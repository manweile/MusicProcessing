from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def find_embedded_art(mp3_filepath):
    """
    Finds and extracts embedded album art from an MP3 file.

    Args:
        mp3_filepath (str): The path to the MP3 file.

    Returns:
        bytes or None: The image data if found, otherwise None.
    """
    try:
        audio = MP3(mp3_filepath, ID3=ID3)
        if 'APIC:' in audio.tags:
            for tag in audio.tags.getall('APIC'):
               return tag.data
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage:
mp3_file = r"H:\Music\.38 Special\Special Forces\.38 Special-Caught Up in You.mp3" # Replace with the actual path to your MP3 file
image_data = find_embedded_art(mp3_file)

if image_data:
    with open('album_art.jpg', 'wb') as img_file:
        img_file.write(image_data)
    print("Album art extracted and saved as 'album_art.jpg'")
else:
    print("No album art found in the MP3 file.")