# from audio_info.audio_metadata import AudioMetadata
from audio_info import AudioMetadata

# eyed3 and mutagen can both read it
# and it has a date and album art
# but filename is not in my preferred format
# and mutagen can't read date
# file_path = "H:\\Music\\Kenny Rogers\\Daytime Friends - The Very Best of Kenny\\18 Lady.mp3"

# eyed3 and mutagen can both read it
# and it has a date but no album art
# mutagen can read the date cause its TDRC
# file_path = "H:\\Music\\Albert Collins\\Albert Collins - Trash Talkin'.mp3"

# eyed3 and mutagen can both read it
# and it has a date
# but mutagen can't read date while eyed3 can read date
# file_path = "H:\\Music\\4 Non Blondes\\Bigger, Better, Faster, More!\\4 Non Blondes-What's Up.mp3"

# eyed3 can't read it, mutagen can
# wma has different tag keys than mp3
# but there is a year tag present (WM/Year) that mutagen SHOULD be able to read
file_path = "H:\\Music\\Elton John\\Greatest Hits, Vol. 2\\Elton John-Island Girl.wma"

# eyed3 can't read it, mutagen can
# m4a has different tag keys than mp3 file
# but there is a year tag present '©day': ['2013'] that mutagen SHOULD be able to read
# file_path = "H:\\Music\\The Eagles\\The Eagles-Desperado.m4a"

metadata = AudioMetadata()
eyed3_audio_file, mutagen_audio_file = metadata.load_file(file_path)
# print(metadata.has_art(file_path))
audio_tag_info = metadata.get_tag_info(eyed3_audio_file)
metadata.show_metadata(mutagen_audio_file)
metadata.show_date(audio_tag_info)