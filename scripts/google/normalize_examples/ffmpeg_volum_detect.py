import platform
import re
import subprocess


'''
google search: "ffmpeg' python volumedetect example
https://superuser.com/questions/323119/how-can-i-normalize-audio-using-ffmpeg
'''


def get_volume_info(file_path):
    """
    Detects volume information (mean and max) from an audio/video file using FFmpeg.

    Args:
        file_path (str): The path to the input audio or video file.

    Returns:
        dict: A dictionary containing 'mean_volume' and 'max_volume' in dB, or None if detection fails.
    """

    command = [
        'ffmpeg',
        '-i', file_path,
        '-hide_banner',
        '-filter:a', 'volumedetect',
        '-f', 'null',
        '-'  # Send output to stdout
    ]

    try:
        # Run FFmpeg and capture stderr (where volumedetect output goes)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Decode stderr to string and search for volume information
        output_str = stderr.decode('utf-8')

        mean_volume_match = re.search(r'mean_volume: ([-]?\d+\.\d+) dB', output_str)
        max_volume_match = re.search(r'max_volume: ([-]?\d+\.\d+) dB', output_str)

        if mean_volume_match and max_volume_match:
            mean_volume = float(mean_volume_match.group(1))
            max_volume = float(max_volume_match.group(1))
            return {'mean_volume': mean_volume, 'max_volume': max_volume}
        else:
            print(f"Could not parse volume information from FFmpeg output: \n{output_str}")
            return None

    except FileNotFoundError:
        print("FFmpeg not found. Please ensure FFmpeg is installed and in your PATH.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage:
if __name__ == "__main__":

    if platform.system() == "Windows":
        audio_file = r"C:\Music\Crush\Here\Crush-Live.mp3"
    elif platform.system() == "Linux":
        audio_file = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"  # Replace with your audio/video file

    volume_data = get_volume_info(audio_file)

    if volume_data:
        print(f"Mean Volume: {volume_data['mean_volume']} dB")
        print(f"Max Volume: {volume_data['max_volume']} dB")
