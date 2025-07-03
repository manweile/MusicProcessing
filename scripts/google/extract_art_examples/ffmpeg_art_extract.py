import platform
import subprocess


def extract_album_art(input_audio_file, output_image_file):
    """
    Extracts album art from an audio file using FFmpeg.

    Args:
        input_audio_file (str): Path to the input audio file (e.g., 'song.mp3').
        output_image_file (str): Path to save the extracted album art (e.g., 'cover.jpg').
    """
    command = [
        'ffmpeg', '-hide_banner',
        '-i', input_audio_file,
        '-an',
        '-c:v', 'copy',
        output_image_file, '-y'
    ]
    try:
        subprocess.run(command, capture_output=True, text=True)
        print(f"Album art extracted successfully to {output_image_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting album art: {e}")
        print(f"FFmpeg output: {e.stderr}")


file_path = None
if platform.system() == "Linux":
    file_path = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"  # has art
elif platform.system() == "Windows":
    file_path = r"C:\Music\Crush\Here\Crush-Live.mp3"  # has art

extracted_art = r"/home/gerald/MusicProcessing/src/generated_files/Crush/Here/Extracted.jpg"

# Example usage:
extract_album_art(file_path, extracted_art)
