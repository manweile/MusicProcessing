#  standard modules
import os

# third part modules
from mutagen.asf import ASF, Picture, error

# local modules
from src import _AUDIO_EXTS, _AUDIO_TYPES
from src.generated_files import generated_files

def find_embedded_art_wma(file_path):
    try:
        audio = ASF(file_path)
        pictures = audio.pictures
        if pictures:
            for i, picture in enumerate(pictures):
                if picture.type == 3: # Check if it's cover art
                    image_data = picture.data
                    image_format = picture.mime
                    return image_data, image_format
        else:
            return None, None
    except error as e:
        print(f"Error processing {file_path}: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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
file_path = "example.wma" # Replace with your WMA file path
output_path = generated_files

image_data, image_format = find_embedded_art_wma(file_path)

if image_data and image_format:
    save_art(image_data,image_format, output_path)
else:
    print("No embedded cover art found.")
