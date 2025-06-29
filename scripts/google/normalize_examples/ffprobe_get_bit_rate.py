import subprocess
import json
import platform

'''
google search: "ffmpeg" python get bit_rate example
'''


def get_bitrate(file_path):
    """
    @brief Retrieves the bitrate of a media file using ffprobe.

    @param file_path (str): The path to the media file.

    @return bit_rate {int} The bitrate in bits per second, or None if not found.
    """

    command = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_entries', 'format=bit_rate',
        file_path
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        if 'format' in data and 'bit_rate' in data['format']:
            return int(data['format']['bit_rate'])
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing ffprobe: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON output from ffprobe.")
        return None


# Example usage:
if __name__ == "__main__":

    # file = 'input.mp4'  # Replace with your media file
    if platform.system() == "Windows":
        audio_file = r"C:\Music\Crush\Here\Crush-Live.mp3"
    elif platform.system() == "Linux":
        audio_file = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"  # Replace with your audio/video file

    bitrate = get_bitrate(audio_file)

    if bitrate is not None:
        print(f"The bitrate of {audio_file} is: {bitrate} bps")
    else:
        print(f"Could not determine the bitrate for {audio_file}.")
