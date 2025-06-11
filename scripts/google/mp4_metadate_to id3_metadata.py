from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER, TRCK
import os

# MP4 file metadata to ID3 metadata example
# convert MP4 metadata to ID3 metadata python

def convert_mp4_to_mp3_with_metadata(mp4_file, mp3_file):
    try:
        # Load MP4 file
        mp4_tags = MP4(mp4_file)

        # Create ID3 tags
        id3_tags = ID3()

        # Map metadata (adjust based on your needs)
        if "©nam" in mp4_tags:
            id3_tags.add(TIT2(encoding=3, text=mp4_tags["©nam"][0]))  # Title
        if "©ART" in mp4_tags:
            id3_tags.add(TPE1(encoding=3, text=mp4_tags["©ART"][0]))  # Artist
        if "©alb" in mp4_tags:
            id3_tags.add(TALB(encoding=3, text=mp4_tags["©alb"][0]))  # Album
        if "©day" in mp4_tags:
            id3_tags.add(TYER(encoding=3, text=str(mp4_tags["©day"][0])))  # Year
        if "trkn" in mp4_tags:
            track_num = mp4_tags["trkn"][0][0]
            total_tracks = mp4_tags["trkn"][0][1]
            id3_tags.add(TRCK(encoding=3, text=f"{track_num}/{total_tracks}"))  # Track Number

        # Save ID3 tags to the MP3 file
        id3_tags.save(mp3_file)

    except Exception as e:
        print(f"Error processing {mp4_file}: {e}")


# Example usage
mp4_file = "input.mp4"
mp3_file = "output.mp3"

# Check if the MP4 file exists
if os.path.exists(mp4_file):
    convert_mp4_to_mp3_with_metadata(mp4_file, mp3_file)
else:
    print(f"Error: {mp4_file} not found.")
