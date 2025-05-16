from mutagen.mp4 import MP4

def find_embedded_art_m4a(file_path):
    """
    Finds and extracts embedded artwork from an M4A file using Mutagen.

    Args:
        file_path (str): The path to the M4A file.

    Returns:
        bytes or None: The raw bytes of the artwork if found, otherwise None.
    """
    try:
        audio = MP4(file_path)
        if "covr" in audio:
            # M4A files can have multiple 'covr' atoms, each containing a different image.
            # This example extracts the first one.
            artwork = audio["covr"][0]
            # Artwork data might be wrapped in format codes; extract the raw data.
            if isinstance(artwork, tuple):
                return artwork[1] # Return the image data
            return artwork
        else:
            print("No embedded artwork found in the file.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage:
file_path = r"D:\Music\Joshua Davis\The Voice Peformance\Joshua Davis-The Workingman's Hymn.m4a"
# file_path = r"D:\Music\The Eagles\Desperado\The Eagles-Desperado.m4a"
artwork_data = find_embedded_art_m4a(file_path)

if artwork_data:
    # Save the artwork to a file (e.g., as a JPEG)
    with open("Extracted.jpg", "wb") as f:
        f.write(artwork_data)
    print("Artwork saved to artwork.jpg")
else:
    print("No artwork to save.")