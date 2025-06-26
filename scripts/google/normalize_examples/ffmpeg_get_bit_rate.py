import subprocess
import json

'''
google search: "ffmpeg" python get bit_rate example
'''
def get_bitrate(file_path):
    """
    Retrieves the bitrate of a media file using ffprobe.

    Args:
        file_path (str): The path to the media file.

    Returns:
        int: The bitrate in bits per second, or None if not found.
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
file = 'input.mp4'  # Replace with your media file
bitrate = get_bitrate(file)

if bitrate is not None:
    print(f"The bitrate of {file} is: {bitrate} bps")
else:
    print(f"Could not determine the bitrate for {file}.")