import os
import re
from mutagen import File

# Your package-level list of acceptable audio file extensions
AUDIO_EXTS = [".mp3", ".m4a", ".wma", ".flac"]


def _get_album_metadata(song_path):
    '''
    @brief Helper function to extract the album metadata from a given audio file.

    @details This function attempts to read the album metadata from the provided audio file.
    Uses Mutagen File with easy=True to map the metadata to case-insensitive ASCII-friendly strings.

    @param song_path The path to the audio file from which to extract album metadata.
    @return The album name as a string if found, otherwise None.

    @exception Silently skips unreadable or corrupted files.
    '''

    # Using a single level try-except here isolates the error handling per file
    try:
        # Attempt to read the audio file's metadata using Mutagen's easy interface
        audio = File(song_path, easy=True)

        # If the file couldn't be read, audio will be None
        if audio and 'album' in audio and audio['album']:
            # Extract the first value from the album metadata list if it exists
            first_val = audio['album']

            # Ensure we have a list or a single value to work with
            if isinstance(first_val, list) and first_val:
                return first_val[0].strip()
            return str(first_val).strip()
    except Exception:
        # Silently skip individual unreadable/corrupted files
        pass
    return None


def rename_album_directories(tld_path):
    """
    Traverses TLD -> Artist Folders -> Album Folders.
    Reads album metadata and renames the album folder if needed.
    """
    try:
        if not os.path.isdir(tld_path):
            print(f"Error: {tld_path} is not a valid directory.")
            return

        # Iterate through the Artist directories
        for artist_name in os.listdir(tld_path):
            artist_path = os.path.join(tld_path, artist_name)

            # Skip files in TLD (like playlist files)
            if not os.path.isdir(artist_path):
                continue

            print(f"Checking artist folder: {artist_name}")

            # Iterate through the Album directories inside the Artist folder
            for album_dir_name in os.listdir(artist_path):
                album_path = os.path.join(artist_path, album_dir_name)

                if not os.path.isdir(album_path):
                    continue

                metadata_album_name = None

                # Scan songs inside the album folder to find metadata
                for song_file in os.listdir(album_path):
                    _, ext = os.path.splitext(song_file.lower())
                    if ext in AUDIO_EXTS:
                        song_path = os.path.join(album_path, song_file)

                        # Call helper function (no nested try block here)
                        metadata_album_name = _get_album_metadata(song_path)
                        if metadata_album_name:
                            break  # Found a valid title, stop scanning this folder

                # If metadata was found, evaluate if a rename is needed
                if metadata_album_name:
                    # Sanitize the metadata to remove illegal filesystem characters
                    safe_album_name = re.sub(r'[\\/*?:"<>|]', "", metadata_album_name).strip()

                    if not safe_album_name:
                        print(f"  [Skipped] Sanitizing '{metadata_album_name}' resulted in an empty string.")
                        continue

                    # Only rename if the folder name doesn't match the metadata
                    if album_dir_name != safe_album_name:
                        new_album_path = os.path.join(artist_path, safe_album_name)

                        # Handle naming collisions gracefully (e.g. if the target folder exists)
                        counter = 1
                        original_new_path = new_album_path
                        while os.path.exists(new_album_path):
                            new_album_path = f"{original_new_path} ({counter})"
                            counter += 1

                        # Directory rename logic runs cleanly without a nested try block
                        os.rename(album_path, new_album_path)
                        print(f"  [Renamed] '{album_dir_name}' -> '{os.path.basename(new_album_path)}'")
                    else:
                        print(f"  [Match] '{album_dir_name}' already matches metadata.")
                else:
                    print(f"  [No Metadata] No album tags found in folder: '{album_dir_name}'")

    except Exception as global_error:
        print(f"An unexpected critical error occurred during execution: {global_error}")


if __name__ == "__main__":
    # Specify your top-level directory path here
    TOP_LEVEL_DIR = "F:\\Rick\\RickPrepped"

    print(f"Starting directory processing on: {TOP_LEVEL_DIR}\n")
    rename_album_directories(TOP_LEVEL_DIR)
    print("\nProcessing complete.")
