import subprocess
import json
import platform


def get_audio_sample_rate(file_path):
    """
    Retrieves the audio sample rate of a media file using ffprobe.

    Args:
        file_path (str): The path to the media file.

    Returns:
        int or None: The audio sample rate in Hz, or None if not found.
    """
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'a:0',  # Select the first audio stream
        '-show_entries', 'stream=sample_rate',
        '-of', 'json',
        file_path
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        if 'streams' in data and data['streams']:
            sample_rate = int(data['streams'][0]['sample_rate'])
            return sample_rate
    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {e}")
        print(f"Stderr: {e.stderr}")
    except json.JSONDecodeError:
        print("Error decoding JSON output from ffprobe.")
    except IndexError:
        print("No audio stream found or sample rate information missing.")

    return None


# Example usage:
if __name__ == "__main__":

    # file_to_check = "your_audio_file.mp3"  # Replace with your file path
    if platform.system() == "Windows":
        audio_file = r"C:\Music\Crush\Here\Crush-Live.mp3"
    elif platform.system() == "Linux":
        audio_file = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"  # Replace with your audio/video file

    sample_rate = get_audio_sample_rate(audio_file)

    if sample_rate is not None:
        print(f"The audio sample rate of '{audio_file}' is: {sample_rate} Hz")
    else:
        print(f"Could not determine the audio sample rate of '{audio_file}'.")