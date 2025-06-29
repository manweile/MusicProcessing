# google search: Ffmpeg loudnorm filter output parsing python
import subprocess
import json
import platform
from subprocess import CalledProcessError


def loudnorm_two_pass(input_file):
    # first part, getting the information
    # Construct the FFmpeg command
    # since integrated loudness target, max true peak and loudness target range not set, defaults -24, -2 & 7 are used
    command = [
        "ffmpeg",
        "-hide_banner",
        "-i", input_file,
        "-af", "loudnorm=print_format=json",
        "-f", "null",                       # Output to null to avoid creating an actual output file
        "-"                                 # Direct output to stdout for the first pass (stderr for loudnorm stats)
    ]

    # Execute the command and capture stderr
    try:
        process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True               # Decode stdout/stderr as text
        )
        # ffmpeg outputs information to stderr
        loudnorm_output = process.stderr
    except CalledProcessError as e:
        raise CalledProcessError(f"FFmpeg error {e} Stderr: {e.stderr}")
    except Exception as e:
        raise Exception(f"Exception {e} getting loudnorm filter")


    # 2nd part, get the JSON in the stderr output
    json_start = loudnorm_output.find('{')
    json_end = loudnorm_output.rfind('}')

    if json_start != -1 and json_end != -1:
        json_string = loudnorm_output[json_start: json_end + 1]

        # Parse the JSON string
        try:
            loudnorm_data = json.loads(json_string)
            print("Parsed loudnorm data:")
            print(json.dumps(loudnorm_data, indent=4))  # Pretty print for readability

            # Access specific values, e.g., integrated loudness
            measured_i = loudnorm_data.get("input_i")
            print(f"Measured Integrated Loudness (input_i): {measured_i} LUFS")

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Problematic JSON string: {json_string}")
    else:
        print("Could not find JSON output in loudnorm stderr.")


if __name__ == "__main__":

    if platform.system() == "Windows":
        audio_file = r"C:\Music\Crush\Here\Crush-Live.mp3"
    elif platform.system() == "Linux":
        audio_file = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"  # Replace with your audio/video file

    loudnorm_two_pass(audio_file)
