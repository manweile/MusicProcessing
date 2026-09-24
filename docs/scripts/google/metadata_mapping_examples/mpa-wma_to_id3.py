from tinytag import TinyTag
from mutagen.easyid3 import EasyID3


def map_wma_to_id3(wma_file, mp3_file):
    try:
        tag = TinyTag.get(wma_file)
    except Exception as e:
        print(f"Error reading WMA metadata: {e}")
        return

    wma_to_id3_map = {
        'title': 'TIT2',
        'artist': 'TPE1',
        'album': 'TALB',
        'track': 'TRCK',
        'year': 'TYER',
        'genre': 'TCON',
        'comment': 'COMM',
        'composer': 'TCOM',
    }

    try:
        audio = EasyID3(mp3_file)
        for wma_key, id3_key in wma_to_id3_map.items():
            if wma_key in tag.__dict__ and tag.__dict__[wma_key] is not None:
                audio[id3_key] = str(tag.__dict__[wma_key])
        audio.save()
        print("ID3 tags written successfully.")
    except Exception as e:
        print(f"Error writing ID3 tags: {e}")


wma_file = r"/home/gerald/Music/Alejandro Escovedo/More Miles Than Money- Live 1994-1996/Alejandro Escovedo-Broken Bottle.wma"
mp3_file = r"/home/gerald/MusicProcessing/src/generated_files/Music/Alejandro Escovedo/More Miles Than Money- Live 1994-1996/Alejandro Escovedo-Broken Bottle.mp3"

map_wma_to_id3(wma_file, mp3_file)
