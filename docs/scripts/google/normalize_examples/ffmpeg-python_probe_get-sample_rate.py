import ffmpeg
import platform

'''
google search: "ffmpeg" python get sample_rate example
'''


def get_audio_sample_rate(file_path):
    """
    Retrieves the audio sample rate of a given media file.

    Args:
        file_path (str): The path to the media file.

    Returns:
        int or None: The sample rate in Hz if found, otherwise None.
    """

    try:
        probe = ffmpeg.probe(file_path)
        audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
        if audio_stream and 'sample_rate' in audio_stream:
            return int(audio_stream['sample_rate'])
        else:
            return None
    except ffmpeg.Error as e:
        print(f"Error probing file: {e.stderr.decode()}")
        return None


# Example usage:
if __name__ == "__main__":

    # audio_file = "your_audio_file.wav"  # Replace with your audio file path
    if platform.system() == "Windows":
        audio_file = r"C:\Music\Crush\Here\Crush-Live.mp3"
    elif platform.system() == "Linux":
        audio_file = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"  # Replace with your audio/video file

    sample_rate = get_audio_sample_rate(audio_file)

    if sample_rate:
        print(f"The sample rate of '{audio_file}' is: {sample_rate} Hz")
    else:
        print(f"Could not determine the sample rate for '{audio_file}'.")
