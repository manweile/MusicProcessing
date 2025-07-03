import platform
import subprocess
from subprocess import CalledProcessError


def extract_album_art(input_audio_file, output_image_file):
    """
    Extracts album art from an audio file using FFmpeg.

    Args:
        input_audio_file (str): Path to the input audio file (e.g., 'song.mp3').
        output_image_file (str): Path to save the extracted album art (e.g., 'cover.jpg').
    """
    # this results in 28 kB file cor Crush-Live.mp3
    command = [
        'ffmpeg', '-hide_banner',
        '-i', input_audio_file,
        '-an',
        '-vcodec', 'copy',
        "-update", "1",
        output_image_file, '-y'
    ]
    '''
    this results in 11.5 kb file for Crush-Live.mp3
    command = [
        'ffmpeg', '-hide_banner',
        '-i', input_audio_file,
        '-an',
        '-map', '0:v',
        '-map_metadata', '-1'
        '-update', '1',
        output_image_file, '-y'
    ]

    '''
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)

        print(f"Album art extracted successfully to {output_image_file}")
    except CalledProcessError as e:
        print(f"Error extracting album art: {e}")
        print(f"FFmpeg output: {e.stderr}")


if platform.system() == "Linux":
    file_path = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"  # has art
    extracted_art = r"/home/gerald/MusicProcessing/src/generated_files/Crush/Here/ffmpeg-Extracted.jpg"
elif platform.system() == "Windows":
    file_path = r"C:\Music\Crush\Here\Crush-Live.mp3"  # has art
    extracted_art = r"D:\MusicProcessing\src\generated_files\Music\Crush\Here\ffmpeg-Extracted.jpg"



# Example usage:
extract_album_art(file_path, extracted_art)
