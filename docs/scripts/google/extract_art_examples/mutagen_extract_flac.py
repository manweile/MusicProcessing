from mutagen.flac import FLAC


def extract_flac_cover(flac_path, output_filename="cover"):
    """
    Extracts the embedded front cover art from a FLAC file and saves it.
    """
    # Load the FLAC file
    audio = FLAC(flac_path)

    # FLAC files store images in the 'pictures' attribute list
    if not audio.pictures:
        print(f"No embedded artwork found in: {flac_path}")
        return False

    # Look for the front cover (type 3 is the standard for Cover/Front)
    cover_picture = None
    for pic in audio.pictures:
        if pic.type == 3:
            cover_picture = pic
            break

    # If no specific front cover is found, fallback to the first available image
    if cover_picture is None:
        cover_picture = audio.pictures[0]
        print("Front cover type not specified. Using the first available image.")

    # Determine the file extension based on the image's mime type
    # Usually 'image/jpeg' or 'image/png'
    if "png" in cover_picture.mime:
        ext = ".png"
    elif "jpeg" in cover_picture.mime or "jpg" in cover_picture.mime:
        ext = ".jpg"
    else:
        # Fallback extension if it's something less common
        ext = cover_picture.mime.split("/")[-1]

    # Build the final output path
    output_path = f"{output_filename}{ext}"

    # Write the binary image data to a file
    with open(output_path, "wb") as f:
        f.write(cover_picture.data)

    print(f"Success! Artwork saved to: {output_path}")
    print(f"Image Details: {cover_picture.width}x{cover_picture.height}, Mime: {cover_picture.mime}")
    return True


# --- Example Usage ---
# Replace 'my_song.flac' with your actual FLAC file path
extract_flac_cover("F:\\RickPrepped\\Cream\\British Rock Power\\17. Dreaming.flac", "F:\\RickPrepped\\Cream\\British Rock Power")
