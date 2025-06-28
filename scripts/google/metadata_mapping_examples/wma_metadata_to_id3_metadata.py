# from tinytag import TinyTag
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TYER
from pydub.utils import mediainfo

# convert wma metadata to ID3 metadata python
# wma metadata to ID3 metadata python
# map wma metadata to ID3 metadata python


def convert_wma_to_mp3_with_id3(wma_file_path, mp3_file_path):
    # Extract metadata from WMA file
    media_info = mediainfo(wma_file_path)
    tag = media_info['TAG']
    metadata = {
        'title': tag.title,
        'album': tag.album,
        'artist': tag.artist,
        'year': tag.year
    }

    # Convert WMA to MP3
    audio = AudioSegment.from_file(wma_file_path, format="wma")
    audio.export(mp3_file_path, format="mp3")

    # Write ID3 tags to the MP3 file
    audio = MP3(mp3_file_path, ID3=ID3)
    audio.tags.add(TIT2(encoding=3, text=metadata.get('title', '')))
    audio.tags.add(TALB(encoding=3, text=metadata.get('album', '')))
    audio.tags.add(TPE1(encoding=3, text=metadata.get('artist', '')))
    audio.tags.add(TYER(encoding=3, text=metadata.get('year', '')))
    audio.save()


# Example Usage
wma_file = r"/home/gerald/Music/Alejandro Escovedo/More Miles Than Money- Live 1994-1996/Alejandro Escovedo-Broken Bottle.wma"
mp3_file = r"/home/gerald/MusicProcessing/src/generated_files/Music/Alejandro Escovedo/More Miles Than Money- Live 1994-1996/Alejandro Escovedo-Broken Bottle.mp3"
convert_wma_to_mp3_with_id3(wma_file, mp3_file)
